from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from .forms import LoginForm, UserProfileForm, UserManagementForm, ContactVerificationForm
from .models import User, Role, TechnicianProfile
from .decorators import role_required, super_admin_required
from departments.models import Department
from audit.services import log_audit_event

def login_view(request):
    """
    Enterprise login supporting login by Username or Employee ID or Email.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        user = None
        if form.is_valid():
            user = form.get_user()
        else:
            # Check if user entered employee_id or email instead of username
            username_or_id = request.POST.get('username')
            password = request.POST.get('password')
            try:
                candidate = User.objects.filter(
                    Q(username=username_or_id) | Q(employee_id=username_or_id) | Q(email=username_or_id)
                ).first()
                if candidate:
                    authenticated_user = authenticate(request, username=candidate.username, password=password)
                    if authenticated_user and authenticated_user.is_active:
                        user = authenticated_user
            except Exception:
                pass

        if user:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if not next_url or next_url == '/':
                next_url = 'dashboard'

            # Prompt employee to verify email & phone for real-time alerts
            if not user.phone or not request.session.get('contact_confirmed'):
                request.session['post_contact_redirect'] = next_url
                messages.info(request, f"Welcome, {user.display_name}! Please verify your Email and Mobile Phone number so you receive instant updates and SMS alerts.")
                return redirect('confirm_contact')

            messages.success(request, f"Welcome back, {user.display_name}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid Employee ID, Username, or Password. Please try again.")

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def confirm_contact_view(request):
    """
    Prompts employee on login to verify their Email and Phone number
    for real-time Email and SMS ticket updates and resolution alerts.
    """
    user = request.user
    next_url = request.session.get('post_contact_redirect') or 'dashboard'

    # Allow skip if user already has an existing phone configured
    if request.GET.get('skip') == '1':
        request.session['contact_confirmed'] = True
        if 'post_contact_redirect' in request.session:
            del request.session['post_contact_redirect']
        messages.info(request, "Contact verification skipped. You can update your details anytime in Profile.")
        return redirect(next_url)

    if request.method == 'POST':
        form = ContactVerificationForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email'].strip().lower()
            new_phone = form.cleaned_data['phone'].strip()

            # Check email uniqueness if changed
            if new_email != user.email:
                if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                    messages.error(request, "This email address is already registered to another employee.")
                    return render(request, 'accounts/confirm_contact.html', {'form': form, 'next_url': next_url})
                user.email = new_email

            user.phone = new_phone
            user.save(update_fields=['email', 'phone'])

            request.session['contact_confirmed'] = True
            if 'post_contact_redirect' in request.session:
                del request.session['post_contact_redirect']

            log_audit_event(
                user=user,
                action='CONTACT_VERIFIED',
                details=f"Employee verified alert contact details (Email: {user.email}, Phone: {user.phone}).",
                request=request
            )

            # Send a confirmation SMS notification
            from services.sms_service import send_ticket_sms
            send_ticket_sms(
                user.phone,
                user.display_name,
                "Welcome to JK Paper Mill Ticket Alerts! You will now receive instant SMS updates for all ticket responses and resolutions."
            )

            messages.success(request, f"Contact details verified! Real-time SMS and Email alerts are now active for {user.phone}.")
            return redirect(next_url)
    else:
        form = ContactVerificationForm(initial={
            'email': user.email or '',
            'phone': user.phone or '',
            'email_alerts': True,
            'sms_alerts': True,
        })

    return render(request, 'accounts/confirm_contact.html', {'form': form, 'next_url': next_url})



def logout_view(request):
    """Logs out current user."""
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Central intelligent dashboard router.
    Renders tailored workspace depending on user role.
    """
    user = request.user

    # Lazy import tickets model to prevent circular imports
    from tickets.models import Ticket

    if user.is_super_admin:
        # SUPER ADMIN DASHBOARD
        total_employees = User.objects.filter(is_active=True).count()
        total_departments = Department.objects.filter(is_active=True).count()
        all_tickets = Ticket.objects.all()
        total_tickets = all_tickets.count()
        open_tickets = all_tickets.exclude(status__in=['RESOLVED', 'CLOSED', 'CANCELLED']).count()
        critical_tickets = all_tickets.filter(priority__name='CRITICAL').exclude(status__in=['RESOLVED', 'CLOSED']).count()
        sla_breached_count = all_tickets.filter(sla_breached=True).exclude(status__in=['RESOLVED', 'CLOSED']).count()
        resolved_tickets = all_tickets.filter(status__in=['RESOLVED', 'CLOSED']).count()

        # Distribution charts data
        dept_distribution = list(
            Department.objects.annotate(t_count=Count('tickets')).values('name', 't_count')[:10]
        )
        priority_distribution = list(
            all_tickets.values('priority__name').annotate(count=Count('id'))
        )
        status_distribution = list(
            all_tickets.values('status').annotate(count=Count('id'))
        )
        technicians = TechnicianProfile.objects.select_related('user').all()[:8]

        recent_tickets = all_tickets.select_related('created_by', 'department', 'priority', 'assigned_to')[:8]

        context = {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'critical_tickets': critical_tickets,
            'sla_breached_count': sla_breached_count,
            'resolved_tickets': resolved_tickets,
            'dept_distribution': dept_distribution,
            'priority_distribution': priority_distribution,
            'status_distribution': status_distribution,
            'technicians': technicians,
            'recent_tickets': recent_tickets,
        }
        return render(request, 'dashboards/admin_dashboard.html', context)

    elif user.is_hr_admin:
        # HR / HELPDESK DASHBOARD
        all_tickets = Ticket.objects.all()
        new_tickets = all_tickets.filter(status='NEW')
        assigned_tickets = all_tickets.filter(status__in=['ASSIGNED', 'IN_PROGRESS'])
        escalated_tickets = all_tickets.filter(status='ESCALATED')
        sla_breached = all_tickets.filter(sla_breached=True).exclude(status__in=['RESOLVED', 'CLOSED'])
        resolved_today = all_tickets.filter(
            status__in=['RESOLVED', 'CLOSED'],
            resolved_at__date=timezone.now().date()
        ).count()

        departments = Department.objects.filter(is_active=True)
        technicians = TechnicianProfile.objects.select_related('user').filter(is_available=True)

        recent_tickets = all_tickets.select_related('created_by', 'department', 'priority', 'assigned_to')[:10]

        context = {
            'new_count': new_tickets.count(),
            'assigned_count': assigned_tickets.count(),
            'escalated_count': escalated_tickets.count(),
            'sla_breached_count': sla_breached.count(),
            'resolved_today': resolved_today,
            'total_tickets': all_tickets.count(),
            'departments': departments,
            'technicians': technicians,
            'recent_tickets': recent_tickets,
        }
        return render(request, 'dashboards/hr_dashboard.html', context)

    elif user.is_dept_manager:
        # DEPARTMENT MANAGER DASHBOARD
        manager_depts = Department.objects.filter(Q(manager=user) | Q(pk=user.department_id if user.department else None))
        dept_tickets = Ticket.objects.filter(department__in=manager_depts)

        total_dept_tickets = dept_tickets.count()
        open_tickets = dept_tickets.exclude(status__in=['RESOLVED', 'CLOSED', 'CANCELLED']).count()
        in_progress = dept_tickets.filter(status='IN_PROGRESS').count()
        resolved = dept_tickets.filter(status__in=['RESOLVED', 'CLOSED']).count()
        critical_issues = dept_tickets.filter(priority__name='CRITICAL').exclude(status__in=['RESOLVED', 'CLOSED']).count()
        sla_breached = dept_tickets.filter(sla_breached=True).exclude(status__in=['RESOLVED', 'CLOSED']).count()

        recent_tickets = dept_tickets.select_related('created_by', 'priority', 'assigned_to')[:10]

        context = {
            'departments': manager_depts,
            'total_tickets': total_dept_tickets,
            'open_tickets': open_tickets,
            'in_progress': in_progress,
            'resolved': resolved,
            'critical_issues': critical_issues,
            'sla_breached': sla_breached,
            'recent_tickets': recent_tickets,
        }
        return render(request, 'dashboards/department_dashboard.html', context)

    elif user.is_technician:
        # TECHNICIAN DASHBOARD
        my_tickets = Ticket.objects.filter(assigned_to=user)
        assigned = my_tickets.filter(status='ASSIGNED')
        in_progress = my_tickets.filter(status='IN_PROGRESS')
        completed = my_tickets.filter(status__in=['RESOLVED', 'CLOSED'])

        context = {
            'assigned_count': assigned.count(),
            'in_progress_count': in_progress.count(),
            'completed_count': completed.count(),
            'total_count': my_tickets.count(),
            'assigned_tickets': assigned[:5],
            'active_tickets': in_progress[:10],
            'recent_completed': completed[:5],
        }
        return render(request, 'dashboards/technician_dashboard.html', context)

    else:
        # EMPLOYEE DASHBOARD
        my_tickets = Ticket.objects.filter(created_by=user)
        open_tickets = my_tickets.exclude(status__in=['RESOLVED', 'CLOSED', 'CANCELLED']).count()
        in_progress = my_tickets.filter(status='IN_PROGRESS').count()
        resolved = my_tickets.filter(status='RESOLVED').count()
        closed = my_tickets.filter(status='CLOSED').count()

        recent_tickets = my_tickets.select_related('department', 'priority', 'assigned_to')[:8]

        # Tickets waiting for employee confirmation
        pending_confirmation = my_tickets.filter(
            status='RESOLVED',
            employee_confirmation='PENDING'
        )

        context = {
            'total_tickets': my_tickets.count(),
            'open_tickets': open_tickets,
            'in_progress': in_progress,
            'resolved': resolved,
            'closed': closed,
            'recent_tickets': recent_tickets,
            'pending_confirmation': pending_confirmation,
        }
        return render(request, 'dashboards/employee_dashboard.html', context)


@login_required
def profile_view(request):
    """User profile management."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@super_admin_required
def user_list_view(request):
    """Admin view for listing and searching enterprise users."""
    role_filter = request.GET.get('role', '')
    dept_filter = request.GET.get('department', '')
    query = request.GET.get('q', '').strip()

    users = User.objects.select_related('department').all()

    if role_filter:
        users = users.filter(role=role_filter)
    if dept_filter:
        users = users.filter(department_id=dept_filter)
    if query:
        users = users.filter(
            Q(employee_id__icontains=query) |
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    departments = Department.objects.filter(is_active=True)

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'departments': departments,
        'role_filter': role_filter,
        'dept_filter': dept_filter,
        'query': query,
        'roles': Role.choices,
    })


# Error Views
def error_400(request, exception=None):
    return render(request, '400.html', status=400)

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)
