from django.contrib import admin
from .models import Department, TicketCategory

class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'manager', 'is_active', 'total_tickets_count', 'open_tickets_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'manager__username', 'manager__first_name', 'manager__last_name')
    inlines = [TicketCategoryInline]


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'is_active', 'created_at')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'department__name')
