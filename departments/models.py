from django.db import models
from django.conf import settings

class Department(models.Model):
    """
    Department model for JK Paper Mill organization units.
    Fully manageable from Django Admin / Admin dashboard.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="e.g. PROD, MAINT, IT, HR")
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        help_text="Designated manager for this department"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_tickets_count(self):
        return self.tickets.count()

    @property
    def open_tickets_count(self):
        return self.tickets.exclude(status__in=['RESOLVED', 'CLOSED', 'CANCELLED']).count()


class TicketCategory(models.Model):
    """
    Category of issues specific to a department.
    Configurable by Super Admin / HR Admin.
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('department', 'name')
        ordering = ['department__name', 'name']
        verbose_name = 'Ticket Category'
        verbose_name_plural = 'Ticket Categories'

    def __str__(self):
        return f"{self.department.code} - {self.name}"
