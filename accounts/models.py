from django.db import models
from django.contrib.auth.models import AbstractUser
from departments.models import Department

class Role(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    HR_ADMIN = 'HR_ADMIN', 'HR / Helpdesk Admin'
    DEPT_MANAGER = 'DEPT_MANAGER', 'Department Manager'
    TECHNICIAN = 'TECHNICIAN', 'Technician'
    EMPLOYEE = 'EMPLOYEE', 'Employee'


class User(AbstractUser):
    """
    Custom User Model for JK Paper Mill Ticket Management System.
    Stores enterprise employee details, role, department, and contact info.
    """
    employee_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Unique Employee ID (e.g. EMP-1001)"
    )
    email = models.EmailField(unique=True, help_text="Official company email address")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Internal extension or mobile")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="Primary department employee works in"
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        db_index=True,
        help_text="Access control role in the ticket system"
    )
    designation = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Production Incharge, Mechanical Engineer")
    location = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. Rayagada Plant / Paper Machine 1")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'employee_id']

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        full_name = self.get_full_name()
        return f"{self.employee_id} - {full_name or self.username} ({self.get_role_display()})"

    @property
    def display_name(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    # Role check helpers
    @property
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_hr_admin(self):
        return self.role == Role.HR_ADMIN

    @property
    def is_dept_manager(self):
        return self.role == Role.DEPT_MANAGER

    @property
    def is_technician(self):
        return self.role == Role.TECHNICIAN

    @property
    def is_employee(self):
        return self.role == Role.EMPLOYEE

    @property
    def role_badge_class(self):
        badges = {
            Role.SUPER_ADMIN: 'badge-danger',
            Role.HR_ADMIN: 'badge-primary',
            Role.DEPT_MANAGER: 'badge-warning',
            Role.TECHNICIAN: 'badge-info',
            Role.EMPLOYEE: 'badge-secondary',
        }
        return badges.get(self.role, 'badge-light')


class TechnicianProfile(models.Model):
    """
    Profile extension for Technicians.
    Associates technician with one or more departments they can service,
    tracks current active workload and availability.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='technician_profile'
    )
    departments = models.ManyToManyField(
        Department,
        related_name='technicians',
        help_text="Departments this technician is authorized to service"
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="e.g. Hydraulic Systems, High-voltage Electrical, Network Infrastructure"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Whether technician is currently on-duty/available for assignments"
    )
    max_concurrent_tickets = models.PositiveIntegerField(
        default=5,
        help_text="Threshold for active concurrent tickets before considered fully loaded"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Technician Profile'
        verbose_name_plural = 'Technician Profiles'

    def __str__(self):
        return f"Tech: {self.user.display_name} ({self.specialization or 'General'})"

    @property
    def current_workload(self):
        """Returns number of active assigned/in-progress tickets."""
        return self.user.assigned_tickets.filter(
            status__in=['ASSIGNED', 'IN_PROGRESS', 'WAITING_FOR_TECHNICIAN']
        ).count()

    @property
    def workload_status(self):
        count = self.current_workload
        if not self.is_available:
            return 'Unavailable'
        elif count >= self.max_concurrent_tickets:
            return 'Overloaded'
        elif count > 0:
            return f'Busy ({count})'
        else:
            return 'Available'
