from django.db import models
from django.conf import settings

class NotificationType(models.TextChoices):
    INFO = 'INFO', 'Information'
    ASSIGNMENT = 'ASSIGNMENT', 'Technician Assignment'
    UPDATE = 'UPDATE', 'Status Update'
    SLA_WARNING = 'SLA_WARNING', 'SLA Warning'
    ESCALATION = 'ESCALATION', 'Ticket Escalated'
    RESOLVED = 'RESOLVED', 'Ticket Resolved'
    CLOSED = 'CLOSED', 'Ticket Closed'
    REOPENED = 'REOPENED', 'Ticket Reopened'


class Notification(models.Model):
    """
    In-app alert notification delivered to users.
    Displays in the top navbar with live unread badge.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    ticket = models.ForeignKey(
        'tickets.Ticket',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.recipient.display_name} - {self.title}"

    @property
    def icon_class(self):
        icons = {
            NotificationType.INFO: 'bi-info-circle text-primary',
            NotificationType.ASSIGNMENT: 'bi-person-check text-info',
            NotificationType.UPDATE: 'bi-arrow-repeat text-warning',
            NotificationType.SLA_WARNING: 'bi-exclamation-triangle text-warning',
            NotificationType.ESCALATION: 'bi-lightning-charge text-danger',
            NotificationType.RESOLVED: 'bi-check2-circle text-success',
            NotificationType.CLOSED: 'bi-shield-check text-success',
            NotificationType.REOPENED: 'bi-arrow-counterclockwise text-danger',
        }
        return icons.get(self.notification_type, 'bi-bell text-secondary')


class EmailLog(models.Model):
    """
    Audit log of all system-generated SMTP emails dispatched.
    """
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=150, blank=True, null=True)
    subject = models.CharField(max_length=255)
    ticket_number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[('SENT', 'Sent'), ('FAILED', 'Failed')],
        default='SENT'
    )
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'

    def __str__(self):
        return f"[{self.status}] {self.recipient_email}: {self.subject}"


class SMSLog(models.Model):
    """
    Audit log of all SMS / instant mobile text notifications dispatched.
    """
    recipient_phone = models.CharField(max_length=30)
    recipient_name = models.CharField(max_length=150, blank=True, null=True)
    message = models.TextField()
    ticket_number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    channel = models.CharField(max_length=20, default='SMS')
    status = models.CharField(
        max_length=20,
        choices=[('SENT', 'Sent'), ('FAILED', 'Failed'), ('SIMULATED', 'Simulated')],
        default='SENT'
    )
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'

    def __str__(self):
        return f"[{self.status}] {self.recipient_phone} ({self.recipient_name}): {self.ticket_number or 'Alert'}"

