from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Notification, EmailLog, SMSLog
from .services import mark_all_notifications_read

@login_required
def notification_list(request):
    """Full notifications page with In-App Alerts, Email logs, and SMS Message logs."""
    notifications = Notification.objects.filter(recipient=request.user)

    if request.user.is_hr_admin or request.user.is_super_admin:
        email_logs = EmailLog.objects.all()[:50]
        sms_logs = SMSLog.objects.all()[:50]
    else:
        email_logs = EmailLog.objects.filter(recipient_email=request.user.email)[:30]
        sms_logs = SMSLog.objects.filter(recipient_phone=request.user.phone)[:30] if request.user.phone else []

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'email_logs': email_logs,
        'sms_logs': sms_logs,
    })


@login_required
def mark_as_read_api(request, pk):
    """AJAX API to mark a single notification as read."""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return JsonResponse({'status': 'ok', 'id': pk})


@login_required
def mark_all_read_view(request):
    """Marks all notifications as read and redirects back."""
    mark_all_notifications_read(request.user)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    messages.success(request, "All notifications marked as read.")
    return redirect('notification_list')
