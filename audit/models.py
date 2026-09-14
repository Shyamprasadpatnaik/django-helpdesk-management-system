from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    """
    Complete immutable audit log recording every important action in the organization.
    """
    ACTION_CHOICES = [
        ('LOGIN', 'User Logged In'),
        ('LOGOUT', 'User Logged Out'),
        ('TICKET_CREATED', 'Ticket Created'),
        ('TICKET_UPDATED', 'Ticket Updated'),
        ('TICKET_ASSIGNED', 'Ticket Assigned'),
        ('TICKET_REASSIGNED', 'Ticket Reassigned'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('COMMENT_ADDED', 'Comment Added'),
        ('ATTACHMENT_UPLOADED', 'Attachment Uploaded'),
        ('TICKET_RESOLVED', 'Ticket Resolved'),
        ('TICKET_CONFIRMED', 'Resolution Confirmed'),
        ('TICKET_REOPENED', 'Ticket Reopened'),
        ('TICKET_ESCALATED', 'Ticket Escalated'),
        ('SLA_WARNING', 'SLA Warning Triggered'),
        ('SLA_BREACHED', 'SLA Breached'),
        ('SETTINGS_CHANGED', 'System Settings Modified'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    ticket_number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        user_str = self.user.display_name if self.user else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {user_str}: {self.get_action_display()} ({self.ticket_number or 'N/A'})"
