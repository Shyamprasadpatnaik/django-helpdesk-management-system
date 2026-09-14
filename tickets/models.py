from datetime import timedelta
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from departments.models import Department, TicketCategory

class TicketPriority(models.Model):
    """
    Priority levels with SLA turnaround commitments.
    Configurable via Admin panel.
    """
    name = models.CharField(max_length=50, unique=True)
    sla_hours = models.PositiveIntegerField(help_text="Standard SLA resolution turnaround in hours")
    warning_threshold_percent = models.PositiveIntegerField(
        default=75,
        help_text="Percentage of SLA time elapsed before triggering warning notification"
    )
    color_code = models.CharField(max_length=20, default="#3b82f6", help_text="Hex color for UI badges")
    badge_class = models.CharField(max_length=50, default="badge-primary")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'sla_hours']
        verbose_name = 'Ticket Priority'
        verbose_name_plural = 'Ticket Priorities'

    def __str__(self):
        return f"{self.name} ({self.sla_hours}h SLA)"


class TicketStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    WAITING_FOR_EMPLOYEE = 'WAITING_FOR_EMPLOYEE', 'Waiting For Employee'
    WAITING_FOR_TECHNICIAN = 'WAITING_FOR_TECHNICIAN', 'Waiting For Technician'
    RESOLVED = 'RESOLVED', 'Resolved'
    CLOSED = 'CLOSED', 'Closed'
    REOPENED = 'REOPENED', 'Reopened'
    ESCALATED = 'ESCALATED', 'Escalated'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Ticket(models.Model):
    """
    Main Ticket Model tracking issue lifecycle, technician assignment,
    SLA commitments, and resolution confirmation.
    """
    ticket_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        blank=True,
        help_text="Sequential Ticket Number (e.g. TKT-2026-000001)"
    )
    title = models.CharField(max_length=200, help_text="Concise description of the problem")
    description = models.TextField(help_text="Detailed problem description")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='tickets',
        help_text="Department responsible for resolving this issue"
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    priority = models.ForeignKey(
        TicketPriority,
        on_delete=models.PROTECT,
        related_name='tickets'
    )
    status = models.CharField(
        max_length=30,
        choices=TicketStatus.choices,
        default=TicketStatus.NEW,
        db_index=True
    )

    # Location specifics inside plant/office
    building = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Paper Machine Section, Administrative Block")
    floor = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. Ground Floor, Operating Floor")
    room_area = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Control Room 3, Pulp Preparation")
    equipment_number = models.CharField(max_length=100, blank=True, null=True, help_text="Machine or equipment ID / Tag No.")

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        help_text="Technician assigned to work on this ticket"
    )

    # Lifecycle Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Calculated SLA deadline")
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Resolution & Confirmation
    resolution_summary = models.TextField(blank=True, null=True, help_text="Technician notes on how issue was solved")
    employee_confirmation = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending Confirmation'), ('CONFIRMED', 'Confirmed Resolved'), ('REJECTED', 'Rejected / Reopened')],
        default='PENDING'
    )
    reopened_count = models.PositiveIntegerField(default=0)
    escalation_level = models.PositiveIntegerField(default=0)

    # SLA Tracking Flags
    sla_breached = models.BooleanField(default=False, db_index=True)
    sla_warning_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f"{self.ticket_number} - {self.title} [{self.get_status_display()}]"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Auto-generate ticket number if not assigned: TKT-YYYY-000001
        if not self.ticket_number:
            current_year = timezone.now().year
            prefix = f"TKT-{current_year}-"
            with transaction.atomic():
                last_ticket = Ticket.objects.filter(ticket_number__startswith=prefix).order_by('-ticket_number').first()
                if last_ticket:
                    try:
                        last_seq = int(last_ticket.ticket_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                self.ticket_number = f"{prefix}{next_seq:06d}"

        # Calculate SLA due_at if not set and priority is provided
        if not self.due_at and self.priority:
            sla_hours = self.priority.sla_hours
            base_time = self.created_at if self.created_at else timezone.now()
            self.due_at = base_time + timedelta(hours=sla_hours)

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.CANCELLED]:
            return False
        if self.due_at and timezone.now() > self.due_at:
            return True
        return False

    @property
    def sla_percentage_elapsed(self):
        """Calculates percentage of SLA time passed."""
        if not self.due_at or not self.created_at:
            return 0
        total_time = (self.due_at - self.created_at).total_seconds()
        if total_time <= 0:
            return 100
        elapsed_time = (timezone.now() - self.created_at).total_seconds()
        percent = int((elapsed_time / total_time) * 100)
        return min(percent, 100)

    @property
    def status_badge_class(self):
        classes = {
            TicketStatus.NEW: 'badge-primary',
            TicketStatus.UNDER_REVIEW: 'badge-secondary',
            TicketStatus.ASSIGNED: 'badge-info',
            TicketStatus.IN_PROGRESS: 'badge-warning',
            TicketStatus.WAITING_FOR_EMPLOYEE: 'badge-secondary',
            TicketStatus.WAITING_FOR_TECHNICIAN: 'badge-secondary',
            TicketStatus.RESOLVED: 'badge-success',
            TicketStatus.CLOSED: 'badge-dark',
            TicketStatus.REOPENED: 'badge-danger',
            TicketStatus.ESCALATED: 'badge-danger',
            TicketStatus.CANCELLED: 'badge-light',
        }
        return classes.get(self.status, 'badge-secondary')

    @property
    def priority_badge_class(self):
        if self.priority:
            return self.priority.badge_class
        return 'badge-secondary'


class TicketAssignment(models.Model):
    """
    Tracks assignment history of tickets to technicians.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='assignments')
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket_assignments')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_by_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('ASSIGNED', 'Assigned'), ('ACCEPTED', 'Accepted'), ('COMPLETED', 'Completed'), ('REASSIGNED', 'Reassigned')],
        default='ASSIGNED'
    )

    class Meta:
        ordering = ['-assigned_at']


class TicketComment(models.Model):
    """
    Ticket-scoped communication between employees, HR, and technicians.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket_comments')
    comment = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal note visible only to HR and technicians")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.display_name} on {self.ticket.ticket_number}"


class TicketAttachment(models.Model):
    """
    Uploaded photographs, scanned documents, before/after resolution proofs.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_attachments')
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/')
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")
    ocr_extracted_text = models.TextField(blank=True, null=True, help_text="Optional text extracted from document")
    is_resolution_proof = models.BooleanField(default=False, help_text="Whether this is a technician before/after proof")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Attachment: {self.file.name} for {self.ticket.ticket_number}"

    @property
    def is_image(self):
        name = self.file.name.lower()
        return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))


class TicketHistory(models.Model):
    """
    Comprehensive timeline tracking every state change, assignment, and action.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    old_value = models.CharField(max_length=150, blank=True, null=True)
    new_value = models.CharField(max_length=150, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.action} at {self.timestamp}"


class Escalation(models.Model):
    """
    Escalation history tracking when ticket breaches SLA or requires senior intervention.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='escalations')
    escalated_from = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_from_set')
    escalated_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_to_set')
    escalation_level = models.PositiveIntegerField(default=1)
    reason = models.TextField()
    escalated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-escalated_at']


class SLAConfiguration(models.Model):
    """
    Fine-grained SLA configuration per department and priority.
    """
    priority = models.ForeignKey(TicketPriority, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, null=True, blank=True)
    resolution_hours = models.PositiveIntegerField()
    warning_hours = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'SLA Configuration'
        verbose_name_plural = 'SLA Configurations'
