from .models import AuditLog

def log_audit_event(user, action, ticket_number=None, details="", request=None):
    """
    Central helper to log immutable audit events across the platform.
    Extracts client IP from request if provided.
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    return AuditLog.objects.create(
        user=user if (user and user.is_authenticated) else None,
        action=action,
        ticket_number=ticket_number,
        ip_address=ip_address,
        details=details
    )
