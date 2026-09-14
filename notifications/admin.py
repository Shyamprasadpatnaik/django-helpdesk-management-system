from django.contrib import admin
from .models import Notification, EmailLog, SMSLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'recipient', 'title', 'notification_type', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__employee_id', 'title', 'message')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'recipient_email', 'subject', 'ticket_number', 'status')
    list_filter = ('status', 'sent_at')
    search_fields = ('recipient_email', 'subject', 'ticket_number')


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'recipient_phone', 'recipient_name', 'ticket_number', 'channel', 'status')
    list_filter = ('status', 'channel', 'sent_at')
    search_fields = ('recipient_phone', 'recipient_name', 'ticket_number', 'message')

