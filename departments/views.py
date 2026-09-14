from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Department, TicketCategory
from accounts.decorators import hr_required, super_admin_required

@login_required
def department_list(request):
    """List all company departments and their health."""
    departments = Department.objects.prefetch_related('tickets', 'members').all()
    return render(request, 'departments/department_list.html', {'departments': departments})


@login_required
def department_detail(request, pk):
    """View details, categories and active tickets for a specific department."""
    dept = get_object_or_404(Department, pk=pk)
    categories = dept.categories.filter(is_active=True)
    tickets = dept.tickets.select_related('priority', 'created_by', 'assigned_to').order_by('-created_at')[:20]
    return render(request, 'departments/department_detail.html', {
        'department': dept,
        'categories': categories,
        'tickets': tickets
    })


@login_required
def get_categories_api(request, department_id):
    """
    JSON API used by the interactive Ticket Create form to dynamically
    fetch categories belonging to the selected department.
    """
    categories = TicketCategory.objects.filter(department_id=department_id, is_active=True).values('id', 'name')
    return JsonResponse(list(categories), safe=False)
