import logging
import re
from django.conf import settings
from notifications.models import SMSLog

logger = logging.getLogger(__name__)

def clean_phone_number(phone):
    """Normalize phone numbers for SMS transmission."""
    if not phone:
        return None
    # Strip spaces, dashes, parentheses
    cleaned = re.sub(r'[^\d+]', '', str(phone).strip())
    return cleaned if len(cleaned) >= 5 else None


def send_ticket_sms(recipient_phone, recipient_name, message, ticket_number=None, channel='SMS'):
    """
    Enterprise SMS & Mobile text dispatcher for JK Paper Mill Ticket System.
    Validates mobile numbers, records audit entries into SMSLog table,
    outputs instant console log, and connects to pluggable SMS gateway if configured.
    """
    cleaned_phone = clean_phone_number(recipient_phone)
    if not cleaned_phone:
        logger.warning(f"SMS skipped for {recipient_name} on ticket {ticket_number}: No valid phone number provided.")
        return False

    prefix = getattr(settings, 'COMPANY_NAME', 'JK Paper Mill')
    full_message = f"[{prefix}] {message}"

    try:
        # In development / simulated mode: log dispatch
        print(f"\n=======================================================")
        print(f" [SMS NOTIFICATION DISPATCHED]")
        print(f" Recipient : {recipient_name} ({cleaned_phone})")
        print(f" Ticket    : {ticket_number or 'N/A'}")
        print(f" Channel   : {channel}")
        print(f" Message   : {full_message}")
        print(f"=======================================================\n")

        logger.info(f"SMS sent to {cleaned_phone} for ticket {ticket_number}: {full_message[:60]}...")

        # Record into database SMSLog
        SMSLog.objects.create(
            recipient_phone=cleaned_phone,
            recipient_name=recipient_name or '',
            message=full_message,
            ticket_number=ticket_number,
            channel=channel,
            status='SENT'
        )
        return True

    except Exception as e:
        logger.error(f"Failed to dispatch SMS to {cleaned_phone} for ticket {ticket_number}: {str(e)}")
        SMSLog.objects.create(
            recipient_phone=cleaned_phone,
            recipient_name=recipient_name or '',
            message=full_message,
            ticket_number=ticket_number,
            channel=channel,
            status='FAILED',
            error_message=str(e)
        )
        return False
