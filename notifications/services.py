from .models import Notification, NotificationType

def create_notification(recipient, title, message, ticket=None, notification_type=NotificationType.INFO):
    """
    Central helper to spawn in-app notifications.
    """
    if not recipient:
        return None
    return Notification.objects.create(
        recipient=recipient,
        ticket=ticket,
        title=title,
        message=message,
        notification_type=notification_type
    )


def mark_all_notifications_read(user):
    """Marks all unread notifications for user as read."""
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
