from django.conf import settings
from .models import Notification

def unread_notifications(request):
    """
    Context processor making unread notification count and recent notifications
    available globally to the top navbar and layout templates.
    """
    if request.user.is_authenticated:
        qs = Notification.objects.filter(recipient=request.user)
        unread_count = qs.filter(is_read=False).count()
        recent = qs[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent,
            'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'JK Paper Mill'),
            'SYSTEM_NAME': getattr(settings, 'SYSTEM_NAME', 'Enterprise Ticket Management'),
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'JK Paper Mill'),
        'SYSTEM_NAME': getattr(settings, 'SYSTEM_NAME', 'Enterprise Ticket Management'),
    }
