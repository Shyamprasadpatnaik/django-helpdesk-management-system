import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from notifications.models import EmailLog

logger = logging.getLogger(__name__)

def send_ticket_email(recipient_email, recipient_name, subject, template_name, context, ticket_number=None):
    """
    Robust HTML email dispatcher for JK Paper Mill Ticket System.
    Renders rich HTML templates, logs to EmailLog table, and handles SMTP errors gracefully.
    """
    if not recipient_email:
        return False

    context.update({
        'company_name': getattr(settings, 'COMPANY_NAME', 'JK Paper Mill'),
        'system_name': getattr(settings, 'SYSTEM_NAME', 'Enterprise Ticket Management'),
        'ticket_number': ticket_number,
    })

    try:
        html_content = render_to_string(f"emails/{template_name}", context)
        text_content = strip_tags(html_content)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'helpdesk@jkpaper.com')

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        # Log successful email
        EmailLog.objects.create(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            ticket_number=ticket_number,
            status='SENT'
        )
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email} for ticket {ticket_number}: {str(e)}")
        EmailLog.objects.create(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            ticket_number=ticket_number,
            status='FAILED',
            error_message=str(e)
        )
        return False
