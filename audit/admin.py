from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'ticket_number', 'ip_address')
    list_filter = ('action', 'created_at')
    search_fields = ('ticket_number', 'details', 'user__username', 'user__employee_id')
    readonly_fields = ('user', 'action', 'ticket_number', 'ip_address', 'details', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
