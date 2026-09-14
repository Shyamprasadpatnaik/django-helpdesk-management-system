from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.core.management import call_command

from accounts.models import User, Role, TechnicianProfile
from departments.models import Department, TicketCategory
from tickets.models import Ticket, TicketPriority, TicketStatus, TicketAssignment, Escalation
from notifications.models import Notification

class TicketWorkflowTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Priority
        self.priority_high = TicketPriority.objects.create(
            name='HIGH',
            sla_hours=4,
            warning_threshold_percent=75,
            order=2
        )
        self.priority_critical = TicketPriority.objects.create(
            name='CRITICAL',
            sla_hours=1,
            warning_threshold_percent=75,
            order=1
        )

        # Create Department
        self.dept_prod = Department.objects.create(name='Production', code='PROD')
        self.dept_maint = Department.objects.create(name='Maintenance', code='MAINT')

        # Create Categories
        self.cat_machine = TicketCategory.objects.create(department=self.dept_prod, name='Machine Breakdown')

        # Create Users
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            employee_id='TEST-001',
            role=Role.SUPER_ADMIN
        )
        self.hr_user = User.objects.create_user(
            username='hr_test',
            email='hr@test.com',
            password='password123',
            employee_id='TEST-101',
            role=Role.HR_ADMIN,
            department=self.dept_prod
        )
        self.tech_user = User.objects.create_user(
            username='tech_test',
            email='tech@test.com',
            password='password123',
            employee_id='TEST-201',
            role=Role.TECHNICIAN,
            department=self.dept_maint
        )
        self.emp_user = User.objects.create_user(
            username='emp_test',
            email='emp@test.com',
            password='password123',
            employee_id='TEST-301',
            role=Role.EMPLOYEE,
            department=self.dept_prod
        )

    def test_01_ticket_creation_and_sla_due_date(self):
        """Verify ticket creation, ticket_number sequencing, and due_at calculation."""
        ticket = Ticket.objects.create(
            title="Paper Machine 1 Roller Stuck",
            description="Bearing seizure on felt roll",
            created_by=self.emp_user,
            department=self.dept_prod,
            category=self.cat_machine,
            priority=self.priority_high
        )

        # Verify sequential number format
        year = timezone.now().year
        self.assertTrue(ticket.ticket_number.startswith(f"TKT-{year}-"))
        self.assertEqual(ticket.status, TicketStatus.NEW)

        # Verify SLA due_at = created_at + 4 hours
        expected_due = ticket.created_at + timedelta(hours=4)
        # Allow 5 seconds tolerance
        self.assertAlmostEqual(ticket.due_at.timestamp(), expected_due.timestamp(), delta=5)

    def test_02_full_lifecycle_workflow(self):
        """Test complete workflow: Assign -> Accept -> Resolve -> Confirm -> Closed."""
        ticket = Ticket.objects.create(
            title="Conveyor Belt Alignment Issue",
            description="Belt tracking off towards operator side",
            created_by=self.emp_user,
            department=self.dept_prod,
            priority=self.priority_high
        )

        # 1. HR assigns technician
        self.client.login(username='hr_test', password='password123')
        response = self.client.post(f"/tickets/{ticket.ticket_number}/assign/", {
            'technician': self.tech_user.pk,
            'priority': self.priority_high.pk,
            'notes': 'Inspect guide roller mechanism'
        })
        self.assertEqual(response.status_code, 302)

        ticket.refresh_from_db()
        self.assertEqual(ticket.assigned_to, self.tech_user)
        self.assertEqual(ticket.status, TicketStatus.ASSIGNED)

        # 2. Technician accepts assignment
        self.client.login(username='tech_test', password='password123')
        response = self.client.get(f"/tickets/{ticket.ticket_number}/accept/")
        self.assertEqual(response.status_code, 302)

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, TicketStatus.IN_PROGRESS)

        # 3. Technician marks work completed
        response = self.client.post(f"/tickets/{ticket.ticket_number}/resolve/", {
            'resolution_summary': 'Adjusted pneumatics guide sensor and realigned felt rolls.'
        })
        self.assertEqual(response.status_code, 302)

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, TicketStatus.RESOLVED)
        self.assertIsNotNone(ticket.resolved_at)

        # 4. Employee confirms resolution
        self.client.login(username='emp_test', password='password123')
        response = self.client.get(f"/tickets/{ticket.ticket_number}/confirm/")
        self.assertEqual(response.status_code, 302)

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, TicketStatus.CLOSED)
        self.assertEqual(ticket.employee_confirmation, 'CONFIRMED')
        self.assertIsNotNone(ticket.closed_at)

    def test_03_ticket_reopening(self):
        """Test ticket reopening when employee rejects resolution."""
        ticket = Ticket.objects.create(
            title="DCS Screen Freezing",
            description="Display freeze",
            created_by=self.emp_user,
            department=self.dept_prod,
            priority=self.priority_high,
            status=TicketStatus.RESOLVED
        )

        self.client.login(username='emp_test', password='password123')
        response = self.client.post(f"/tickets/{ticket.ticket_number}/reopen/", {
            'reopen_reason': 'Display froze again 10 minutes after shift restart.'
        })
        self.assertEqual(response.status_code, 302)

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, TicketStatus.REOPENED)
        self.assertEqual(ticket.employee_confirmation, 'REJECTED')
        self.assertEqual(ticket.reopened_count, 1)

    def test_04_sla_check_and_escalation_command(self):
        """Verify check_sla command flags overdue tickets as ESCALATED and sla_breached."""
        # Create ticket that is already past due
        past_time = timezone.now() - timedelta(hours=3)
        due_time = timezone.now() - timedelta(hours=1)

        ticket = Ticket.objects.create(
            title="Boiler High Pressure Sensor Alarm",
            description="Overpressure trip sensor intermittent",
            created_by=self.emp_user,
            department=self.dept_prod,
            priority=self.priority_critical,
            status=TicketStatus.NEW,
            due_at=due_time
        )
        Ticket.objects.filter(pk=ticket.pk).update(created_at=past_time)

        # Run management command
        call_command('check_sla')

        ticket.refresh_from_db()
        self.assertTrue(ticket.sla_breached)
        self.assertEqual(ticket.status, TicketStatus.ESCALATED)
        self.assertEqual(ticket.escalation_level, 1)
        self.assertEqual(ticket.escalations.count(), 1)
