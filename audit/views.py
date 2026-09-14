from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import super_admin_required
from .models import AuditLog

@login_required
@super_admin_required
def audit_log_list(request):
    """Viewable exclusively by Super Admin."""
    action_filter = request.GET.get('action', '')
    query = request.GET.get('q', '').strip()

    logs = AuditLog.objects.select_related('user').all()

    if action_filter:
        logs = logs.filter(action=action_filter)
    if query:
        logs = logs.filter(ticket_number__icontains=query) | logs.filter(details__icontains=query)

    logs = logs[:100]  # Paginate/limit to recent 100 entries

    return render(request, 'audit/audit_list.html', {
        'logs': logs,
        'action_choices': AuditLog.ACTION_CHOICES,
        'action_filter': action_filter,
        'query': query,
    })
