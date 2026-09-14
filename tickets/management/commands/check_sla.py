from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.urls import reverse

from tickets.models import Ticket, TicketStatus, Escalation, TicketHistory
from accounts.models import User, Role
from notifications.services import create_notification
from notifications.models import NotificationType
from services.email_service import send_ticket_email
from audit.services import log_audit_event

class Command(BaseCommand):
    help = "Periodic SLA scanner: detects SLA threshold warnings (75%) and triggers automated escalations (100%)."

    def handle(self, *args, **options):
        now = timezone.now()
        active_tickets = Ticket.objects.exclude(
            status__in=[TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.CANCELLED]
        ).select_related('department', 'priority', 'assigned_to', 'created_by')

        self.stdout.write(f"Scanning {active_tickets.count()} active tickets for SLA compliance at {now.strftime('%Y-%m-%d %H:%M:%S')}...")

        warnings_issued = 0
        breaches_escalated = 0

        for ticket in active_tickets:
            if not ticket.due_at or not ticket.created_at:
                continue

            total_seconds = (ticket.due_at - ticket.created_at).total_seconds()
            if total_seconds <= 0:
                continue

            elapsed_seconds = (now - ticket.created_at).total_seconds()
            percentage = (elapsed_seconds / total_seconds) * 100

            # 1. SLA Warning Check (>= 75% elapsed and not yet notified)
            if percentage >= ticket.priority.warning_threshold_percent and not ticket.sla_warning_sent and now < ticket.due_at:
                ticket.sla_warning_sent = True
                ticket.save(update_fields=['sla_warning_sent'])
                warnings_issued += 1

                # In-app warning
                target_recipients = []
                if ticket.assigned_to:
                    target_recipients.append(ticket.assigned_to)
                hr_admins = User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True)
                target_recipients.extend(list(hr_admins[:2]))

                for recipient in set(target_recipients):
                    create_notification(
                        recipient=recipient,
                        title=f"SLA Warning: {ticket.ticket_number}",
                        message=f"Ticket '{ticket.title}' has reached 75% of its SLA commitment.",
                        ticket=ticket,
                        notification_type=NotificationType.SLA_WARNING
                    )
                    send_ticket_email(
                        recipient_email=recipient.email,
                        recipient_name=recipient.display_name,
                        subject=f"[SLA WARNING] {ticket.ticket_number}: {ticket.title}",
                        template_name="sla_warning.html",
                        context={'ticket': ticket, 'recipient_name': recipient.display_name},
                        ticket_number=ticket.ticket_number
                    )

                TicketHistory.objects.create(
                    ticket=ticket,
                    action='SLA Warning Sent',
                    details=f"Reached {int(percentage)}% of SLA timeframe. Warning dispatched to technician and helpdesk."
                )
                self.stdout.write(self.style.WARNING(f" [WARN] SLA Warning sent for {ticket.ticket_number} ({int(percentage)}% elapsed)"))

            # 2. SLA Breach and Automatic Escalation Check (>= 100% or now > due_at)
            if now >= ticket.due_at and not ticket.sla_breached:
                with transaction.atomic():
                    ticket.sla_breached = True
                    ticket.escalation_level += 1
                    old_status = ticket.status
                    ticket.status = TicketStatus.ESCALATED
                    ticket.save(update_fields=['sla_breached', 'escalation_level', 'status', 'updated_at'])
                    breaches_escalated += 1

                    # Create Escalation record
                    escalate_target = None
                    if ticket.escalation_level == 1:
                        # Escalate to HR Manager
                        escalate_target = User.objects.filter(role=Role.HR_ADMIN, is_active=True).first()
                        escalate_reason = "SLA breached without resolution. Escalated to HR Helpdesk Incharge."
                    else:
                        # Escalate to Admin / Senior Management
                        escalate_target = User.objects.filter(role=Role.SUPER_ADMIN, is_active=True).first()
                        escalate_reason = f"Prolonged SLA breach (Escalation Level {ticket.escalation_level}). Escalated to Senior Plant Administration."

                    Escalation.objects.create(
                        ticket=ticket,
                        escalated_from=ticket.assigned_to or ticket.created_by,
                        escalated_to=escalate_target,
                        escalation_level=ticket.escalation_level,
                        reason=escalate_reason
                    )

                    TicketHistory.objects.create(
                        ticket=ticket,
                        action='Automated SLA Breach & Escalation',
                        old_value=old_status,
                        new_value='ESCALATED',
                        details=f"SLA breached (Deadline was {ticket.due_at.strftime('%Y-%m-%d %H:%M')}). Level {ticket.escalation_level} escalation triggered."
                    )

                    log_audit_event(
                        user=None,
                        action='SLA_BREACHED',
                        ticket_number=ticket.ticket_number,
                        details=f"Ticket auto-escalated to Level {ticket.escalation_level}"
                    )

                    # Notify stakeholders
                    stakeholders = set(User.objects.filter(role__in=[Role.HR_ADMIN, Role.SUPER_ADMIN], is_active=True))
                    if ticket.department.manager:
                        stakeholders.add(ticket.department.manager)

                    for person in stakeholders:
                        create_notification(
                            recipient=person,
                            title=f"ESCALATION: {ticket.ticket_number}",
                            message=f"Ticket '{ticket.title}' has breached its SLA and is now Escalated to Level {ticket.escalation_level}.",
                            ticket=ticket,
                            notification_type=NotificationType.ESCALATION
                        )
                        send_ticket_email(
                            recipient_email=person.email,
                            recipient_name=person.display_name,
                            subject=f"[ESCALATION LEVEL {ticket.escalation_level}] {ticket.ticket_number} Breached SLA",
                            template_name="ticket_escalated.html",
                            context={
                                'ticket': ticket,
                                'reason': escalate_reason,
                                'recipient_name': person.display_name
                            },
                            ticket_number=ticket.ticket_number
                        )

                    self.stdout.write(self.style.ERROR(f" [BREACH] Ticket {ticket.ticket_number} breached SLA and ESCALATED to Level {ticket.escalation_level}"))

        self.stdout.write(self.style.SUCCESS(
            f"SLA Scan Complete: {warnings_issued} warnings issued, {breaches_escalated} tickets escalated."
        ))
