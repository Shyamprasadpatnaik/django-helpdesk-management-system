from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.urls import reverse

from .models import (
    Ticket, TicketPriority, TicketStatus, TicketAssignment,
    TicketComment, TicketAttachment, TicketHistory, Escalation
)
from .forms import (
    TicketCreateForm, TicketAssignForm, TicketResolveForm,
    TicketCommentForm, TicketReopenForm
)
from departments.models import Department, TicketCategory
from accounts.models import User, Role, TechnicianProfile
from accounts.decorators import hr_required, technician_required, super_admin_required
from notifications.services import create_notification
from notifications.models import NotificationType
from services.email_service import send_ticket_email
from services.sms_service import send_ticket_sms
from services.ocr_service import extract_text_from_file
from audit.services import log_audit_event

@login_required
def ticket_list(request):
    """
    Searchable, filterable list of tickets with role-based scoping.
    """
    user = request.user
    queryset = Ticket.objects.select_related('department', 'priority', 'created_by', 'assigned_to').all()

    # Role-based scoping
    if user.is_employee:
        queryset = queryset.filter(created_by=user)
    elif user.is_technician:
        queryset = queryset.filter(assigned_to=user)
    elif user.is_dept_manager:
        if user.department:
            queryset = queryset.filter(department=user.department)

    # Filtering parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    dept_filter = request.GET.get('department', '')
    tech_filter = request.GET.get('technician', '')
    query = request.GET.get('q', '').strip()

    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if priority_filter:
        queryset = queryset.filter(priority_id=priority_filter)
    if dept_filter:
        queryset = queryset.filter(department_id=dept_filter)
    if tech_filter:
        queryset = queryset.filter(assigned_to_id=tech_filter)
    if query:
        queryset = queryset.filter(
            Q(ticket_number__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(equipment_number__icontains=query) |
            Q(created_by__username__icontains=query) |
            Q(created_by__first_name__icontains=query) |
            Q(created_by__last_name__icontains=query)
        )

    # Pagination: 15 per page
    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)

    departments = Department.objects.filter(is_active=True)
    priorities = TicketPriority.objects.all().order_by('order')
    technicians = User.objects.filter(role=Role.TECHNICIAN, is_active=True)

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'departments': departments,
        'priorities': priorities,
        'technicians': technicians,
        'statuses': TicketStatus.choices,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'dept_filter': dept_filter,
        'tech_filter': tech_filter,
        'query': query,
    })


@login_required
def ticket_create(request):
    """
    Multi-section form allowing employees to report an issue.
    Immediately dispatches notifications, emails, and logs audit events.
    """
    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            # Handle file attachment if provided
            uploaded_file = form.cleaned_data.get('attachment')
            if uploaded_file:
                attachment = TicketAttachment.objects.create(
                    ticket=ticket,
                    uploaded_by=request.user,
                    file=uploaded_file,
                    file_size=uploaded_file.size,
                    file_type='image' if uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png')) else 'document'
                )
                # Attempt modular OCR
                try:
                    ocr_text = extract_text_from_file(attachment.file.path)
                    if ocr_text:
                        attachment.ocr_extracted_text = ocr_text
                        attachment.save(update_fields=['ocr_extracted_text'])
                except Exception:
                    pass

            # Record in TicketHistory
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='Ticket Created',
                new_value=ticket.status,
                details=f"Ticket submitted by {request.user.display_name} with priority {ticket.priority.name}."
            )

            # Record in AuditLog
            log_audit_event(
                user=request.user,
                action='TICKET_CREATED',
                ticket_number=ticket.ticket_number,
                details=f"Ticket created for {ticket.department.name} - {ticket.title}",
                request=request
            )

            # In-App Notification to HR/Helpdesk Admins
            hr_admins = User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True)
            for admin in hr_admins:
                create_notification(
                    recipient=admin,
                    title=f"New Ticket: {ticket.ticket_number}",
                    message=f"{request.user.display_name} reported '{ticket.title}' in {ticket.department.name}.",
                    ticket=ticket,
                    notification_type=NotificationType.INFO
                )

            # Notification to Department Manager if assigned
            if ticket.department.manager and ticket.department.manager != request.user:
                create_notification(
                    recipient=ticket.department.manager,
                    title=f"New Dept Issue: {ticket.ticket_number}",
                    message=f"A ticket was opened for your department: '{ticket.title}'.",
                    ticket=ticket,
                    notification_type=NotificationType.INFO
                )

            # In-App Confirmation for Employee
            create_notification(
                recipient=request.user,
                title="Ticket Submitted Successfully",
                message=f"Your ticket {ticket.ticket_number} has been logged. Our helpdesk will assign a technician shortly.",
                ticket=ticket,
                notification_type=NotificationType.INFO
            )

            # Dispatch Emails
            ticket_url = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.ticket_number]))

            # 1. Confirmation email to Employee
            send_ticket_email(
                recipient_email=request.user.email,
                recipient_name=request.user.display_name,
                subject=f"[{ticket.ticket_number}] Support Request Logged: {ticket.title}",
                template_name="ticket_created.html",
                context={'ticket': ticket, 'ticket_url': ticket_url, 'recipient_name': request.user.display_name},
                ticket_number=ticket.ticket_number
            )

            # 2. Alert email to HR Helpdesk
            for admin in hr_admins[:2]:  # Dispatch to primary HR admins
                send_ticket_email(
                    recipient_email=admin.email,
                    recipient_name=admin.display_name,
                    subject=f"[{ticket.ticket_number}] New {ticket.priority.name} Priority Ticket: {ticket.title}",
                    template_name="ticket_created.html",
                    context={'ticket': ticket, 'ticket_url': ticket_url, 'recipient_name': admin.display_name},
                    ticket_number=ticket.ticket_number
                )

            # Dispatch SMS Alerts
            if request.user.phone:
                send_ticket_sms(
                    recipient_phone=request.user.phone,
                    recipient_name=request.user.display_name,
                    message=f"Ticket {ticket.ticket_number} created: '{ticket.title[:30]}'. Priority: {ticket.priority.name}. Helpdesk notified.",
                    ticket_number=ticket.ticket_number
                )
            for admin in hr_admins:
                if admin.phone:
                    send_ticket_sms(
                        recipient_phone=admin.phone,
                        recipient_name=admin.display_name,
                        message=f"HR Alert: New ticket {ticket.ticket_number} ({ticket.priority.name}) reported by {request.user.display_name}.",
                        ticket_number=ticket.ticket_number
                    )

            messages.success(request, f"Ticket {ticket.ticket_number} created successfully! Our helpdesk has been notified.")
            return redirect('ticket_detail', ticket_number=ticket.ticket_number)
    else:
        # Pre-fill department from query params if passed (e.g. from chatbot)
        initial = {}
        dept_code = request.GET.get('dept')
        if dept_code:
            dept = Department.objects.filter(code__iexact=dept_code).first()
            if dept:
                initial['department'] = dept.pk
        form = TicketCreateForm(initial=initial)

    return render(request, 'tickets/ticket_create.html', {'form': form})


@login_required
def ticket_detail(request, ticket_number):
    """
    Comprehensive ticket view displaying status timeline, metadata, conversation, and action modals.
    """
    ticket = get_object_or_404(
        Ticket.objects.select_related('department', 'category', 'priority', 'created_by', 'assigned_to'),
        ticket_number=ticket_number
    )

    # Check permission
    user = request.user
    if user.is_employee and ticket.created_by != user and not user.is_superuser:
        messages.error(request, "You are not authorized to view this ticket.")
        return redirect('ticket_list')

    comments = ticket.comments.select_related('author').order_by('created_at')
    # Filter internal comments for normal employees
    if user.is_employee and not user.is_superuser:
        comments = comments.filter(is_internal=False)

    attachments = ticket.attachments.select_related('uploaded_by').all()
    history = ticket.history.select_related('changed_by').order_by('timestamp')
    escalations = ticket.escalations.select_related('escalated_from', 'escalated_to').all()

    comment_form = TicketCommentForm()
    resolve_form = TicketResolveForm()
    reopen_form = TicketReopenForm()

    # Recommended technicians for HR assignment
    available_technicians = User.objects.filter(
        role=Role.TECHNICIAN,
        is_active=True
    ).select_related('technician_profile')

    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'history': history,
        'escalations': escalations,
        'comment_form': comment_form,
        'resolve_form': resolve_form,
        'reopen_form': reopen_form,
        'available_technicians': available_technicians,
        'can_assign': user.is_hr_admin or user.is_super_admin,
        'can_accept': user.is_technician and ticket.assigned_to == user and ticket.status == TicketStatus.ASSIGNED,
        'can_resolve': (user.is_technician and ticket.assigned_to == user) or user.is_hr_admin or user.is_super_admin,
        'can_confirm': (user == ticket.created_by or user.is_super_admin) and ticket.status == TicketStatus.RESOLVED,
        'can_reopen': (user == ticket.created_by or user.is_hr_admin or user.is_super_admin) and ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED],
    }
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
@hr_required
def ticket_assign(request, ticket_number):
    """
    HR assigns or reassigns technician to ticket.
    Shows recommended technicians matching department and workload.
    """
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    if request.method == 'POST':
        form = TicketAssignForm(request.POST)
        if form.is_valid():
            technician = form.cleaned_data['technician']
            priority = form.cleaned_data.get('priority')
            notes = form.cleaned_data.get('notes', '')

            old_assigned = ticket.assigned_to
            ticket.assigned_to = technician
            ticket.status = TicketStatus.ASSIGNED
            if priority:
                ticket.priority = priority
            ticket.save()

            # Record assignment
            TicketAssignment.objects.create(
                ticket=ticket,
                technician=technician,
                assigned_by=request.user,
                notes=notes,
                status='ASSIGNED'
            )

            # Record history
            old_val = old_assigned.display_name if old_assigned else "None"
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='Technician Assigned',
                old_value=old_val,
                new_value=technician.display_name,
                details=f"Assigned by HR ({request.user.display_name}). Notes: {notes or 'None'}"
            )

            # Audit log
            log_audit_event(
                user=request.user,
                action='TICKET_ASSIGNED',
                ticket_number=ticket.ticket_number,
                details=f"Assigned to {technician.display_name} ({technician.employee_id})",
                request=request
            )

            # In-App Notification to Technician
            create_notification(
                recipient=technician,
                title=f"New Assignment: {ticket.ticket_number}",
                message=f"You have been assigned to ticket '{ticket.title}' ({ticket.priority.name} priority).",
                ticket=ticket,
                notification_type=NotificationType.ASSIGNMENT
            )

            # In-App Notification to Ticket Creator
            create_notification(
                recipient=ticket.created_by,
                title=f"Technician Assigned: {ticket.ticket_number}",
                message=f"Technician {technician.display_name} from Maintenance has been assigned to your ticket.",
                ticket=ticket,
                notification_type=NotificationType.UPDATE
            )

            # Dispatch Emails
            ticket_url = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.ticket_number]))

            # 1. Email to Technician
            send_ticket_email(
                recipient_email=technician.email,
                recipient_name=technician.display_name,
                subject=f"[{ticket.ticket_number}] Assigned: {ticket.title}",
                template_name="ticket_assigned.html",
                context={
                    'ticket': ticket,
                    'technician': technician,
                    'notes': notes,
                    'ticket_url': ticket_url,
                    'recipient_name': technician.display_name
                },
                ticket_number=ticket.ticket_number
            )

            # 2. Email to Employee
            send_ticket_email(
                recipient_email=ticket.created_by.email,
                recipient_name=ticket.created_by.display_name,
                subject=f"[{ticket.ticket_number}] Technician Assigned to your ticket",
                template_name="ticket_updated.html",
                context={
                    'ticket': ticket,
                    'updated_by': request.user.display_name,
                    'message': f"Technician {technician.display_name} has been assigned to resolve your issue.",
                    'ticket_url': ticket_url,
                    'recipient_name': ticket.created_by.display_name
                },
                ticket_number=ticket.ticket_number
            )

            messages.success(request, f"Ticket assigned to {technician.display_name} successfully.")
            return redirect('ticket_detail', ticket_number=ticket.ticket_number)
    else:
        form = TicketAssignForm(initial={'priority': ticket.priority})

    # Recommended technicians filtered by department
    technicians = User.objects.filter(
        role=Role.TECHNICIAN,
        is_active=True
    ).select_related('technician_profile')

    return render(request, 'tickets/ticket_assign.html', {
        'ticket': ticket,
        'form': form,
        'technicians': technicians
    })


@login_required
def ticket_accept(request, ticket_number):
    """
    Technician accepts assigned ticket. Transitions status to IN_PROGRESS.
    """
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    if request.user != ticket.assigned_to and not request.user.is_superuser:
        messages.error(request, "Only the assigned technician can accept this ticket.")
        return redirect('ticket_detail', ticket_number=ticket.ticket_number)

    ticket.status = TicketStatus.IN_PROGRESS
    ticket.save(update_fields=['status', 'updated_at'])

    # Update assignment
    assignment = ticket.assignments.filter(technician=request.user, status='ASSIGNED').first()
    if assignment:
        assignment.status = 'ACCEPTED'
        assignment.accepted_at = timezone.now()
        assignment.save()

    # Record history
    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=request.user,
        action='Assignment Accepted',
        old_value='ASSIGNED',
        new_value='IN_PROGRESS',
        details=f"Technician {request.user.display_name} accepted the task and started investigation."
    )

    # In-App Notification to Employee
    create_notification(
        recipient=ticket.created_by,
        title=f"Work In Progress: {ticket.ticket_number}",
        message=f"Technician {request.user.display_name} has accepted the assignment and is visiting the location.",
        ticket=ticket,
        notification_type=NotificationType.UPDATE
    )

    # Audit log
    log_audit_event(
        user=request.user,
        action='STATUS_CHANGED',
        ticket_number=ticket.ticket_number,
        details="Status transitioned from ASSIGNED to IN_PROGRESS",
        request=request
    )

    messages.success(request, f"You have accepted ticket {ticket.ticket_number}. Status is now In Progress.")
    return redirect('ticket_detail', ticket_number=ticket.ticket_number)


@login_required
def ticket_resolve(request, ticket_number):
    """
    Technician records work completed and uploads before/after proof.
    Transitions status to RESOLVED and requests employee confirmation.
    """
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    if request.method == 'POST':
        form = TicketResolveForm(request.POST, request.FILES)
        if form.is_valid():
            ticket.status = TicketStatus.RESOLVED
            ticket.resolved_at = timezone.now()
            ticket.resolution_summary = form.cleaned_data['resolution_summary']
            ticket.employee_confirmation = 'PENDING'
            ticket.save()

            # Handle proof upload
            proof_file = form.cleaned_data.get('proof_image')
            if proof_file:
                TicketAttachment.objects.create(
                    ticket=ticket,
                    uploaded_by=request.user,
                    file=proof_file,
                    file_size=proof_file.size,
                    file_type='image' if proof_file.name.lower().endswith(('.jpg', '.jpeg', '.png')) else 'document',
                    is_resolution_proof=True
                )

            # Update assignment
            assignment = ticket.assignments.filter(technician=ticket.assigned_to).first()
            if assignment:
                assignment.status = 'COMPLETED'
                assignment.completed_at = timezone.now()
                assignment.save()

            # Record history
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='Marked Resolved',
                old_value='IN_PROGRESS',
                new_value='RESOLVED',
                details=f"Technician marked resolved. Summary: {ticket.resolution_summary}"
            )

            # Audit log
            log_audit_event(
                user=request.user,
                action='TICKET_RESOLVED',
                ticket_number=ticket.ticket_number,
                details=f"Resolution: {ticket.resolution_summary}",
                request=request
            )

            # In-App Notifications
            create_notification(
                recipient=ticket.created_by,
                title=f"Ticket Resolved: {ticket.ticket_number}",
                message="Technician completed the work. Please test and confirm resolution.",
                ticket=ticket,
                notification_type=NotificationType.RESOLVED
            )
            hr_admins = User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True)
            for admin in hr_admins:
                create_notification(
                    recipient=admin,
                    title=f"Ticket Resolved: {ticket.ticket_number}",
                    message=f"Technician {request.user.display_name} marked ticket '{ticket.title}' as Resolved.",
                    ticket=ticket,
                    notification_type=NotificationType.RESOLVED
                )

            # Dispatch Emails to Employee & HR
            ticket_url = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.ticket_number]))
            send_ticket_email(
                recipient_email=ticket.created_by.email,
                recipient_name=ticket.created_by.display_name,
                subject=f"[{ticket.ticket_number}] Issue Resolved - Please Confirm",
                template_name="ticket_resolved.html",
                context={
                    'ticket': ticket,
                    'ticket_url': ticket_url,
                    'recipient_name': ticket.created_by.display_name
                },
                ticket_number=ticket.ticket_number
            )
            for admin in hr_admins[:2]:
                send_ticket_email(
                    recipient_email=admin.email,
                    recipient_name=admin.display_name,
                    subject=f"[{ticket.ticket_number}] Issue Resolved: {ticket.title}",
                    template_name="ticket_resolved.html",
                    context={
                        'ticket': ticket,
                        'ticket_url': ticket_url,
                        'recipient_name': admin.display_name
                    },
                    ticket_number=ticket.ticket_number
                )

            # Dispatch SMS Alerts to Employee & HR
            if ticket.created_by.phone:
                send_ticket_sms(
                    recipient_phone=ticket.created_by.phone,
                    recipient_name=ticket.created_by.display_name,
                    message=f"Your ticket {ticket.ticket_number} ({ticket.title[:30]}) has been RESOLVED by technician {request.user.display_name}. Summary: {ticket.resolution_summary[:50]}. Please log in to verify.",
                    ticket_number=ticket.ticket_number
                )
            for admin in hr_admins:
                if admin.phone:
                    send_ticket_sms(
                        recipient_phone=admin.phone,
                        recipient_name=admin.display_name,
                        message=f"HR Alert: Ticket {ticket.ticket_number} marked RESOLVED by technician {request.user.display_name}.",
                        ticket_number=ticket.ticket_number
                    )

            messages.success(request, f"Ticket {ticket.ticket_number} marked as Resolved. Awaiting employee confirmation.")
            return redirect('ticket_detail', ticket_number=ticket.ticket_number)

    return redirect('ticket_detail', ticket_number=ticket.ticket_number)


@login_required
def ticket_confirm(request, ticket_number):
    """
    Employee verifies the fix and confirms resolution.
    Transitions status to CLOSED.
    """
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    if request.user != ticket.created_by and not request.user.is_superuser:
        messages.error(request, "Only the reporting employee can confirm resolution.")
        return redirect('ticket_detail', ticket_number=ticket.ticket_number)

    ticket.status = TicketStatus.CLOSED
    ticket.closed_at = timezone.now()
    ticket.employee_confirmation = 'CONFIRMED'
    ticket.save()

    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=request.user,
        action='Resolution Confirmed',
        old_value='RESOLVED',
        new_value='CLOSED',
        details=f"Employee {request.user.display_name} verified and confirmed resolution. Ticket closed."
    )

    log_audit_event(
        user=request.user,
        action='TICKET_CONFIRMED',
        ticket_number=ticket.ticket_number,
        details="Resolution verified and closed by employee.",
        request=request
    )

    # In-App Notifications
    if ticket.assigned_to:
        create_notification(
            recipient=ticket.assigned_to,
            title=f"Ticket Closed: {ticket.ticket_number}",
            message=f"Employee confirmed your resolution for '{ticket.title}'. Excellent work!",
            ticket=ticket,
            notification_type=NotificationType.CLOSED
        )
    hr_admins = User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True)
    for admin in hr_admins:
        create_notification(
            recipient=admin,
            title=f"Ticket Closed: {ticket.ticket_number}",
            message=f"Employee {request.user.display_name} verified resolution and closed ticket '{ticket.title}'.",
            ticket=ticket,
            notification_type=NotificationType.CLOSED
        )

    # Dispatch Emails to Employee & HR
    ticket_url = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.ticket_number]))
    send_ticket_email(
        recipient_email=ticket.created_by.email,
        recipient_name=ticket.created_by.display_name,
        subject=f"[{ticket.ticket_number}] Ticket Verified & Closed",
        template_name="ticket_updated.html",
        context={
            'ticket': ticket,
            'updated_by': request.user.display_name,
            'message': "Resolution verified and ticket closed. Thank you for your feedback.",
            'ticket_url': ticket_url,
            'recipient_name': ticket.created_by.display_name
        },
        ticket_number=ticket.ticket_number
    )
    for admin in hr_admins[:2]:
        send_ticket_email(
            recipient_email=admin.email,
            recipient_name=admin.display_name,
            subject=f"[{ticket.ticket_number}] Ticket Closed by Employee",
            template_name="ticket_updated.html",
            context={
                'ticket': ticket,
                'updated_by': request.user.display_name,
                'message': f"Employee {ticket.created_by.display_name} verified and closed ticket {ticket.ticket_number}.",
                'ticket_url': ticket_url,
                'recipient_name': admin.display_name
            },
            ticket_number=ticket.ticket_number
        )

    # Dispatch SMS Alerts to Employee & HR
    if ticket.created_by.phone:
        send_ticket_sms(
            recipient_phone=ticket.created_by.phone,
            recipient_name=ticket.created_by.display_name,
            message=f"Ticket {ticket.ticket_number} resolution verified and ticket CLOSED. Thank you for your feedback.",
            ticket_number=ticket.ticket_number
        )
    for admin in hr_admins:
        if admin.phone:
            send_ticket_sms(
                recipient_phone=admin.phone,
                recipient_name=admin.display_name,
                message=f"HR Alert: Ticket {ticket.ticket_number} verified and CLOSED by {ticket.created_by.display_name}.",
                ticket_number=ticket.ticket_number
            )

    messages.success(request, f"Thank you! Resolution for ticket {ticket.ticket_number} confirmed and ticket closed.")
    return redirect('ticket_detail', ticket_number=ticket.ticket_number)


@login_required
def ticket_reopen(request, ticket_number):
    """
    Employee reopens ticket if problem persists.
    Transitions status to REOPENED and notifies HR / Technician.
    """
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    if request.method == 'POST':
        form = TicketReopenForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reopen_reason']
            ticket.status = TicketStatus.REOPENED
            ticket.employee_confirmation = 'REJECTED'
            ticket.reopened_count += 1
            ticket.save()

            # Record history
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='Ticket Reopened',
                old_value='RESOLVED',
                new_value='REOPENED',
                details=f"Reopened by employee. Reason: {reason}"
            )

            # Audit log
            log_audit_event(
                user=request.user,
                action='TICKET_REOPENED',
                ticket_number=ticket.ticket_number,
                details=f"Reopened (Count {ticket.reopened_count}). Reason: {reason}",
                request=request
            )

            # In-App Notification to HR Admins
            hr_admins = User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True)
            for admin in hr_admins:
                create_notification(
                    recipient=admin,
                    title=f"Ticket Reopened: {ticket.ticket_number}",
                    message=f"{request.user.display_name} reopened ticket '{ticket.title}'. Reason: {reason}",
                    ticket=ticket,
                    notification_type=NotificationType.REOPENED
                )

            if ticket.assigned_to:
                create_notification(
                    recipient=ticket.assigned_to,
                    title=f"Ticket Reopened: {ticket.ticket_number}",
                    message=f"Employee reopened ticket '{ticket.title}'. Reason: {reason}",
                    ticket=ticket,
                    notification_type=NotificationType.REOPENED
                )

            messages.warning(request, f"Ticket {ticket.ticket_number} has been reopened and returned to HR review.")
            return redirect('ticket_detail', ticket_number=ticket.ticket_number)

    return redirect('ticket_detail', ticket_number=ticket.ticket_number)


@login_required
def ticket_comment_add(request, ticket_number):
    """
    Adds a message/comment to the ticket conversation.
    """
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

    if request.method == 'POST':
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            # Only staff/tech can create internal notes
            if not (request.user.is_hr_admin or request.user.is_technician or request.user.is_super_admin):
                comment.is_internal = False
            comment.save()

            # Handle comment attachment
            att_file = form.cleaned_data.get('attachment')
            if att_file:
                TicketAttachment.objects.create(
                    ticket=ticket,
                    uploaded_by=request.user,
                    file=att_file,
                    file_size=att_file.size,
                    file_type='image' if att_file.name.lower().endswith(('.jpg', '.jpeg', '.png')) else 'document'
                )

            # Record history
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=request.user,
                action='Comment Added',
                details=f"{'Internal note' if comment.is_internal else 'Message'} added by {request.user.display_name}."
            )

            # Notifications & Multi-Channel Alert Dispatch
            if not comment.is_internal:
                ticket_url = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.ticket_number]))
                hr_admins = User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True)

                if request.user == ticket.created_by:
                    # Employee commented -> notify assigned technician & HR
                    if ticket.assigned_to:
                        create_notification(
                            recipient=ticket.assigned_to,
                            title=f"New Message on {ticket.ticket_number}",
                            message=f"{request.user.display_name}: {comment.comment[:100]}",
                            ticket=ticket,
                            notification_type=NotificationType.UPDATE
                        )
                        send_ticket_email(
                            recipient_email=ticket.assigned_to.email,
                            recipient_name=ticket.assigned_to.display_name,
                            subject=f"[{ticket.ticket_number}] Employee Response: {ticket.title}",
                            template_name="ticket_updated.html",
                            context={
                                'ticket': ticket,
                                'updated_by': request.user.display_name,
                                'message': comment.comment,
                                'ticket_url': ticket_url,
                                'recipient_name': ticket.assigned_to.display_name
                            },
                            ticket_number=ticket.ticket_number
                        )
                        if ticket.assigned_to.phone:
                            send_ticket_sms(
                                recipient_phone=ticket.assigned_to.phone,
                                recipient_name=ticket.assigned_to.display_name,
                                message=f"Employee {request.user.display_name} replied to {ticket.ticket_number}: {comment.comment[:120]}",
                                ticket_number=ticket.ticket_number
                            )

                    # Notify HR Admins
                    for admin in hr_admins:
                        create_notification(
                            recipient=admin,
                            title=f"New Message on {ticket.ticket_number}",
                            message=f"{request.user.display_name}: {comment.comment[:100]}",
                            ticket=ticket,
                            notification_type=NotificationType.UPDATE
                        )
                    for admin in hr_admins[:2]:
                        send_ticket_email(
                            recipient_email=admin.email,
                            recipient_name=admin.display_name,
                            subject=f"[{ticket.ticket_number}] Employee Update: {ticket.title}",
                            template_name="ticket_updated.html",
                            context={
                                'ticket': ticket,
                                'updated_by': request.user.display_name,
                                'message': comment.comment,
                                'ticket_url': ticket_url,
                                'recipient_name': admin.display_name
                            },
                            ticket_number=ticket.ticket_number
                        )
                    for admin in hr_admins:
                        if admin.phone:
                            send_ticket_sms(
                                recipient_phone=admin.phone,
                                recipient_name=admin.display_name,
                                message=f"HR Alert: Employee {request.user.display_name} replied to {ticket.ticket_number}: {comment.comment[:120]}",
                                ticket_number=ticket.ticket_number
                            )

                else:
                    # Technician or HR commented -> notify reporting Employee
                    create_notification(
                        recipient=ticket.created_by,
                        title=f"Response on {ticket.ticket_number}",
                        message=f"{request.user.display_name}: {comment.comment[:100]}",
                        ticket=ticket,
                        notification_type=NotificationType.UPDATE
                    )
                    send_ticket_email(
                        recipient_email=ticket.created_by.email,
                        recipient_name=ticket.created_by.display_name,
                        subject=f"[{ticket.ticket_number}] New Response on Your Ticket",
                        template_name="ticket_updated.html",
                        context={
                            'ticket': ticket,
                            'updated_by': request.user.display_name,
                            'message': comment.comment,
                            'ticket_url': ticket_url,
                            'recipient_name': ticket.created_by.display_name
                        },
                        ticket_number=ticket.ticket_number
                    )
                    if ticket.created_by.phone:
                        send_ticket_sms(
                            recipient_phone=ticket.created_by.phone,
                            recipient_name=ticket.created_by.display_name,
                            message=f"New reply on ticket {ticket.ticket_number} from {request.user.display_name}: '{comment.comment[:120]}'. Check portal.",
                            ticket_number=ticket.ticket_number
                        )

                    # If responder is not HR, also keep HR informed
                    if not request.user.is_hr_admin and not request.user.is_super_admin:
                        for admin in hr_admins:
                            create_notification(
                                recipient=admin,
                                title=f"Technician Response on {ticket.ticket_number}",
                                message=f"{request.user.display_name}: {comment.comment[:100]}",
                                ticket=ticket,
                                notification_type=NotificationType.UPDATE
                            )
                        for admin in hr_admins[:2]:
                            send_ticket_email(
                                recipient_email=admin.email,
                                recipient_name=admin.display_name,
                                subject=f"[{ticket.ticket_number}] Technician Update: {ticket.title}",
                                template_name="ticket_updated.html",
                                context={
                                    'ticket': ticket,
                                    'updated_by': request.user.display_name,
                                    'message': comment.comment,
                                    'ticket_url': ticket_url,
                                    'recipient_name': admin.display_name
                                },
                                ticket_number=ticket.ticket_number
                            )
                        for admin in hr_admins:
                            if admin.phone:
                                send_ticket_sms(
                                    recipient_phone=admin.phone,
                                    recipient_name=admin.display_name,
                                    message=f"HR Alert: Tech {request.user.display_name} replied to {ticket.ticket_number}: {comment.comment[:120]}",
                                    ticket_number=ticket.ticket_number
                                )

            messages.success(request, "Your message has been posted.")
            return redirect('ticket_detail', ticket_number=ticket.ticket_number)

    return redirect('ticket_detail', ticket_number=ticket.ticket_number)
