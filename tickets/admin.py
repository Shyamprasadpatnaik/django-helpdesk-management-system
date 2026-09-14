from django.contrib import admin
from .models import (
    Ticket, TicketPriority, TicketAssignment, TicketComment,
    TicketAttachment, TicketHistory, Escalation, SLAConfiguration
)

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ('uploaded_by', 'file_size', 'created_at')

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ('author', 'created_at')

class TicketAssignmentInline(admin.TabularInline):
    model = TicketAssignment
    extra = 0
    readonly_fields = ('assigned_at', 'accepted_at', 'completed_at')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number', 'title', 'department', 'priority', 'status',
        'created_by', 'assigned_to', 'created_at', 'due_at', 'sla_breached'
    )
    list_filter = ('status', 'priority', 'department', 'sla_breached', 'created_at')
    search_fields = ('ticket_number', 'title', 'description', 'created_by__username', 'created_by__employee_id')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'due_at')
    inlines = [TicketAttachmentInline, TicketCommentInline, TicketAssignmentInline]


@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'sla_hours', 'warning_threshold_percent', 'badge_class', 'order')
    ordering = ('order',)


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'file', 'uploaded_by', 'file_size', 'created_at')


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'changed_by', 'action', 'old_value', 'new_value', 'timestamp')
    readonly_fields = ('ticket', 'changed_by', 'action', 'old_value', 'new_value', 'details', 'timestamp')


@admin.register(Escalation)
class EscalationAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'escalation_level', 'escalated_from', 'escalated_to', 'escalated_at')


@admin.register(SLAConfiguration)
class SLAConfigurationAdmin(admin.ModelAdmin):
    list_display = ('priority', 'department', 'category', 'resolution_hours', 'warning_hours')
