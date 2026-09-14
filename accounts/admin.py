from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TechnicianProfile
from .forms import UserAdminCreationForm, UserAdminChangeForm

class TechnicianProfileInline(admin.StackedInline):
    model = TechnicianProfile
    can_delete = False
    verbose_name_plural = 'Technician Details'
    fk_name = 'user'
    filter_horizontal = ('departments',)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    list_display = ('employee_id', 'username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_active')
    list_filter = ('role', 'department', 'is_active', 'is_staff')
    search_fields = ('employee_id', 'username', 'first_name', 'last_name', 'email')
    ordering = ('employee_id',)
    inlines = (TechnicianProfileInline,)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Employee Information', {'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone', 'avatar')}),
        ('Organization & Role', {'fields': ('role', 'department', 'designation', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('employee_id', 'username', 'email', 'role', 'department', 'password', 'password2'),
        }),
    )


@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'is_available', 'current_workload')
    list_filter = ('is_available', 'departments')
    search_fields = ('user__username', 'user__employee_id', 'user__first_name', 'user__last_name', 'specialization')
    filter_horizontal = ('departments',)
