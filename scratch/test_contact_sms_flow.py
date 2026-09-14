import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from accounts.models import User, Role
from tickets.models import Ticket, TicketPriority, TicketStatus
from departments.models import Department, TicketCategory
from notifications.models import SMSLog, EmailLog, Notification

def run_test():
    print("=== STARTING COMPREHENSIVE EMPLOYEE CONTACT & SMS/EMAIL TEST ===")
    client = Client()

    # 1. Setup Employee and HR user
    employee = User.objects.filter(role=Role.EMPLOYEE).first()
    hr_admin = User.objects.filter(role=Role.HR_ADMIN).first()
    technician = User.objects.filter(role=Role.TECHNICIAN).first()

    assert employee is not None, "Employee user not found"
    assert hr_admin is not None, "HR admin user not found"
    assert technician is not None, "Technician user not found"

    # Set initial phone on HR and Tech
    hr_admin.phone = "+91 98765 00001"
    hr_admin.save(update_fields=['phone'])
    technician.phone = "+91 98765 00002"
    technician.save(update_fields=['phone'])

    # Reset employee phone and session to trigger login prompt
    employee.phone = ""
    employee.save(update_fields=['phone'])

    # Clear logs for clean counts
    SMSLog.objects.all().delete()

    print("\n[Step 1] Employee Login & Prompt for Contact Info")
    login_res = client.post('/login/', {'username': employee.username, 'password': 'password123'}, follow=False)
    assert login_res.status_code == 302, f"Expected 302 redirect, got {login_res.status_code}"
    assert '/confirm-contact/' in login_res.url, f"Expected redirect to /confirm-contact/, got {login_res.url}"
    print(" -> PASSED: Employee login redirected to /accounts/confirm-contact/")

    # Follow to confirm-contact page
    confirm_page = client.get('/accounts/confirm-contact/')
    assert confirm_page.status_code == 200, f"Expected 200, got {confirm_page.status_code}"
    assert b"Confirm Alert & Notification Channels" in confirm_page.content
    print(" -> PASSED: /accounts/confirm-contact/ page rendered cleanly with HTTP 200")

    print("\n[Step 2] Employee Submits Email and Phone Number")
    post_contact = client.post('/accounts/confirm-contact/', {
        'email': 'employee.verified@company.com',
        'phone': '+91 98765 43210',
        'email_alerts': True,
        'sms_alerts': True,
    }, follow=True)
    assert post_contact.status_code == 200
    employee.refresh_from_db()
    assert employee.email == 'employee.verified@company.com', f"Email not updated: {employee.email}"
    assert employee.phone == '+919876543210' or employee.phone == '+91 98765 43210', f"Phone not updated: {employee.phone}"
    
    welcome_sms = SMSLog.objects.filter(recipient_phone__contains='9876543210').first()
    assert welcome_sms is not None, "Welcome SMS not logged in SMSLog"
    print(f" -> PASSED: Phone updated to {employee.phone} and Welcome SMS dispatched: '{welcome_sms.message[:60]}...'")

    print("\n[Step 3] Employee Creates a Support Ticket")
    dept = Department.objects.first()
    priority = TicketPriority.objects.filter(name='HIGH').first()
    category = TicketCategory.objects.filter(department=dept).first()
    
    tkt_post = client.post('/tickets/create/', {
        'title': 'Conveyor Belt Motor Jammed in Pulp Unit',
        'department': dept.pk,
        'category': category.pk if category else '',
        'priority': priority.pk,
        'description': 'Belt #3 has stalled with high motor vibration. Immediate maintenance inspection required.',
        'location': 'Pulp Mill Section B'
    }, follow=True)
    assert tkt_post.status_code == 200
    ticket = Ticket.objects.filter(title__contains='Conveyor Belt Motor Jammed').latest('id')
    print(f" -> PASSED: Ticket created: {ticket.ticket_number}")

    # Verify SMS was sent on creation to Employee and HR
    emp_creation_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=employee.display_name).first()
    hr_creation_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=hr_admin.display_name).first()
    assert emp_creation_sms is not None, "Creation SMS not sent to Employee"
    assert hr_creation_sms is not None, "Creation SMS not sent to HR"
    print(f" -> PASSED: Ticket creation SMS logged for both Employee and HR ({hr_creation_sms.recipient_phone})")

    print("\n[Step 4] Assign Technician to Ticket")
    ticket.assigned_to = technician
    ticket.status = TicketStatus.ASSIGNED
    ticket.save()

    print("\n[Step 5] Technician Responds to Ticket (Comment/Response)")
    tech_client = Client()
    tech_client.force_login(technician)
    comment_res = tech_client.post(f'/tickets/{ticket.ticket_number}/comment/', {
        'comment': 'I am bringing the diagnostic multimeter and replacement bearing to Pulp Mill Section B now.'
    }, follow=True)
    assert comment_res.status_code == 200

    # Verify SMS sent to Employee and HR on technician response
    emp_reply_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=employee.display_name, message__contains='diagnostic multimeter').first()
    hr_reply_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=hr_admin.display_name, message__contains='replied').first()
    assert emp_reply_sms is not None, "Response SMS not sent to Employee"
    assert hr_reply_sms is not None, "Response SMS not sent to HR"
    print(f" -> PASSED: Technician response triggered SMS to Employee: '{emp_reply_sms.message[:65]}...'")
    print(f" -> PASSED: Technician response triggered SMS to HR: '{hr_reply_sms.message[:65]}...'")

    print("\n[Step 6] Employee Responds Back")
    emp_comment_res = client.post(f'/tickets/{ticket.ticket_number}/comment/', {
        'comment': 'Thanks Ramesh, our unit supervisor is waiting by the feeder console.'
    }, follow=True)
    assert emp_comment_res.status_code == 200

    tech_got_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=technician.display_name, message__contains='feeder console').first()
    hr_got_emp_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=hr_admin.display_name, message__contains='feeder console').first()
    assert tech_got_sms is not None, "Employee reply SMS not sent to Technician"
    assert hr_got_emp_sms is not None, "Employee reply SMS not sent to HR"
    print(f" -> PASSED: Employee reply triggered SMS to Technician: '{tech_got_sms.message[:65]}...'")
    print(f" -> PASSED: Employee reply triggered SMS to HR: '{hr_got_emp_sms.message[:65]}...'")

    print("\n[Step 7] Technician Resolves the Ticket (Issue Done)")
    resolve_res = tech_client.post(f'/tickets/{ticket.ticket_number}/resolve/', {
        'resolution_summary': 'Replaced bearing set #4B, adjusted belt tension, and tested motor under load successfully.',
        'root_cause': 'Bearing wear due to pulp dust ingress.'
    }, follow=True)
    assert resolve_res.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == TicketStatus.RESOLVED

    emp_resolve_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=employee.display_name, message__contains='RESOLVED').first()
    hr_resolve_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=hr_admin.display_name, message__contains='RESOLVED').first()
    assert emp_resolve_sms is not None, "Resolution SMS not sent to Employee"
    assert hr_resolve_sms is not None, "Resolution SMS not sent to HR"
    print(f" -> PASSED: Ticket Resolution triggered SMS to Employee: '{emp_resolve_sms.message[:65]}...'")
    print(f" -> PASSED: Ticket Resolution triggered SMS to HR: '{hr_resolve_sms.message[:65]}...'")

    # Verify Emails for resolution
    emp_resolve_email = EmailLog.objects.filter(ticket_number=ticket.ticket_number, recipient_email=employee.email).first()
    hr_resolve_email = EmailLog.objects.filter(ticket_number=ticket.ticket_number, recipient_email=hr_admin.email).first()
    assert emp_resolve_email is not None, "Resolution Email not logged for Employee"
    assert hr_resolve_email is not None, "Resolution Email not logged for HR"
    print(f" -> PASSED: Resolution Email sent to Employee ({emp_resolve_email.recipient_email}) & HR ({hr_resolve_email.recipient_email})")

    print("\n[Step 8] Employee Confirms & Closes Ticket")
    confirm_res = client.post(f'/tickets/{ticket.ticket_number}/confirm/', follow=True)
    assert confirm_res.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == TicketStatus.CLOSED

    emp_closed_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=employee.display_name, message__contains='CLOSED').first()
    hr_closed_sms = SMSLog.objects.filter(ticket_number=ticket.ticket_number, recipient_name=hr_admin.display_name, message__contains='CLOSED').first()
    assert emp_closed_sms is not None, "Closed SMS not sent to Employee"
    assert hr_closed_sms is not None, "Closed SMS not sent to HR"
    print(f" -> PASSED: Ticket Closure triggered SMS to Employee: '{emp_closed_sms.message[:65]}...'")
    print(f" -> PASSED: Ticket Closure triggered SMS to HR: '{hr_closed_sms.message[:65]}...'")

    print("\n[Step 9] Notifications List Page Verification")
    notif_page = client.get('/notifications/')
    assert notif_page.status_code == 200
    assert b"Dispatched Mobile Text Messages" in notif_page.content
    assert b"Dispatched SMTP System Emails" in notif_page.content
    print(" -> PASSED: /notifications/ page displays In-App, SMS, and Email logs seamlessly!")

    print("\n=======================================================")
    print(" ALL 9 VERIFICATION STEPS PASSED WITH 100% SUCCESS! ")
    print("=======================================================")

if __name__ == '__main__':
    run_test()
