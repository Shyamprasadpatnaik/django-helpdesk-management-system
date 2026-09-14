from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from departments.models import Department, TicketCategory
from accounts.models import Role, TechnicianProfile
from tickets.models import Ticket, TicketPriority, TicketStatus, TicketHistory, TicketAssignment

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds initial JK Paper Mill departments, categories, priorities, users, and tickets."

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data for JK Paper Mill Ticket Management System...")

        # 1. Create Priorities with SLAs
        priorities_data = [
            {'name': 'CRITICAL', 'sla_hours': 1, 'warning_threshold_percent': 75, 'color_code': '#ef4444', 'badge_class': 'badge-danger', 'order': 1},
            {'name': 'HIGH', 'sla_hours': 4, 'warning_threshold_percent': 75, 'color_code': '#f97316', 'badge_class': 'badge-warning', 'order': 2},
            {'name': 'MEDIUM', 'sla_hours': 12, 'warning_threshold_percent': 75, 'color_code': '#eab308', 'badge_class': 'badge-info', 'order': 3},
            {'name': 'LOW', 'sla_hours': 24, 'warning_threshold_percent': 75, 'color_code': '#3b82f6', 'badge_class': 'badge-primary', 'order': 4},
        ]
        priority_objs = {}
        for p in priorities_data:
            obj, _ = TicketPriority.objects.get_or_create(name=p['name'], defaults=p)
            priority_objs[p['name']] = obj
        self.stdout.write(" [x] Seeded 4 Ticket Priorities.")

        # 2. Create Departments
        departments_data = [
            ('Human Resources', 'HR', 'Employee welfare, recruitment, payroll, and benefits'),
            ('IT', 'IT', 'Network infrastructure, servers, workstations, software, and printing systems'),
            ('Production', 'PROD', 'Pulp preparation, paper machines, finishing and packaging lines'),
            ('Maintenance', 'MAINT', 'Plant-wide mechanical maintenance, preventive inspection, and repairs'),
            ('Electrical', 'ELEC', 'High/medium voltage substations, motor control centers, and drives'),
            ('Mechanical', 'MECH', 'Heavy rotating equipment, gearboxes, pumps, and pipework'),
            ('Instrumentation', 'INST', 'Process automation, DCS sensors, transmitters, and valves'),
            ('Quality Control', 'QC', 'Paper grade testing, moisture, tensile, and opacity compliance'),
            ('Research & Development', 'RD', 'Fiber engineering, chemical recovery, and green energy innovations'),
            ('Finance', 'FIN', 'Budgeting, auditing, and corporate finance'),
            ('Accounts', 'ACCT', 'Vendor invoices, ledgers, and billing reconciliation'),
            ('Administration', 'ADMIN', 'Facility management, cafeteria, and housekeeping services'),
            ('Security', 'SEC', 'Plant gate access, surveillance, and loss prevention'),
            ('Stores', 'STORES', 'Spare parts inventory, engineering consumables, and tools'),
            ('Procurement', 'PROC', 'Raw wood pulp, chemicals, and equipment purchasing'),
            ('Sales', 'SALES', 'Domestic and international paper roll dispatches'),
            ('Marketing', 'MKTG', 'Corporate communication and client brand coordination'),
            ('Safety', 'SAFE', 'Occupational health, fire response, PPE, and OSHA compliance'),
            ('Environment', 'ENV', 'Effluent treatment, boiler emissions, and water recovery'),
            ('Transport', 'TRANS', 'Plant fleet, logistics vehicles, and forklift management'),
        ]
        dept_objs = {}
        for name, code, desc in departments_data:
            dept, _ = Department.objects.get_or_create(code=code, defaults={'name': name, 'description': desc})
            dept_objs[code] = dept
        self.stdout.write(" [x] Seeded 20 Industrial Departments.")

        # 3. Create Categories for Core Departments
        categories_data = {
            'IT': ['Computer problem', 'Network problem', 'Software problem', 'Printer problem', 'Email problem', 'Internet problem', 'Hardware problem'],
            'MAINT': ['Machine problem', 'Equipment problem', 'Building issue', 'Plumbing', 'Valve leak', 'Bearing failure'],
            'ELEC': ['Motor trip', 'Power outage', 'Control panel fault', 'Lighting failure', 'VFD drive fault'],
            'PROD': ['Production equipment', 'Production process', 'Safety issue', 'Machine downtime', 'Sheet break'],
            'HR': ['Employee issue', 'Attendance', 'Payroll', 'Leave', 'Employee documentation', 'Health insurance'],
            'SAFE': ['Hazardous condition', 'Fire extinguisher check', 'Chemical spill alert', 'PPE request'],
        }
        for code, cat_names in categories_data.items():
            dept = dept_objs.get(code)
            if dept:
                for c_name in cat_names:
                    TicketCategory.objects.get_or_create(department=dept, name=c_name)
        self.stdout.write(" [x] Seeded Categories for IT, Maintenance, Electrical, Production, HR, Safety.")

        # 4. Create Standard Users with Known Dev Credentials
        # Password for all sample users: devpass123 (or safe default)
        default_pwd = 'password123'

        users_meta = [
            {
                'username': 'admin',
                'email': 'admin@company.com',
                'employee_id': 'EMP-0001',
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'role': Role.SUPER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'designation': 'Chief Information Officer',
                'location': 'Corporate HQ / Plant Control Center',
            },
            {
                'username': 'hr_admin',
                'email': 'hr@company.com',
                'employee_id': 'EMP-1001',
                'first_name': 'Sunita',
                'last_name': 'Sharma',
                'role': Role.HR_ADMIN,
                'department': dept_objs['HR'],
                'is_staff': True,
                'designation': 'Helpdesk & HR Incharge',
                'location': 'Admin Block, Room 102',
            },
            {
                'username': 'prod_manager',
                'email': 'manager.prod@company.com',
                'employee_id': 'EMP-4001',
                'first_name': 'Rajesh',
                'last_name': 'Patel',
                'role': Role.DEPT_MANAGER,
                'department': dept_objs['PROD'],
                'designation': 'Production General Manager',
                'location': 'Paper Mill #2 Central Office',
            },
            {
                'username': 'technician',
                'email': 'technician@company.com',
                'employee_id': 'EMP-2001',
                'first_name': 'Ramesh',
                'last_name': 'Kumar',
                'role': Role.TECHNICIAN,
                'department': dept_objs['MAINT'],
                'designation': 'Senior Maintenance Technician',
                'location': 'Maintenance Workshop Bay A',
            },
            {
                'username': 'elec_tech',
                'email': 'technician.elec@company.com',
                'employee_id': 'EMP-2002',
                'first_name': 'Anil',
                'last_name': 'Verma',
                'role': Role.TECHNICIAN,
                'department': dept_objs['ELEC'],
                'designation': 'Electrical & Drives Technician',
                'location': 'Electrical Workshop Bay B',
            },
            {
                'username': 'employee',
                'email': 'employee@company.com',
                'employee_id': 'EMP-3001',
                'first_name': 'P.',
                'last_name': 'Shyamprasad',
                'role': Role.EMPLOYEE,
                'department': dept_objs['PROD'],
                'designation': 'Paper Machine Operator',
                'location': 'Paper Machine #1 Operating Floor',
            },
        ]

        created_users = {}
        for u in users_meta:
            user = User.objects.filter(email=u['email']).first()
            if not user:
                user = User.objects.create_user(
                    username=u['username'],
                    email=u['email'],
                    password=default_pwd,
                    employee_id=u['employee_id'],
                    first_name=u['first_name'],
                    last_name=u['last_name'],
                    role=u['role'],
                    department=u.get('department'),
                    designation=u.get('designation', ''),
                    location=u.get('location', ''),
                    is_staff=u.get('is_staff', False),
                    is_superuser=u.get('is_superuser', False),
                )
            created_users[u['username']] = user

        # Update Department Managers
        dept_objs['PROD'].manager = created_users['prod_manager']
        dept_objs['PROD'].save()
        dept_objs['HR'].manager = created_users['hr_admin']
        dept_objs['HR'].save()

        # Update Technician Profile Specializations
        tech_user = created_users['technician']
        tech_prof, _ = TechnicianProfile.objects.get_or_create(user=tech_user)
        tech_prof.departments.add(dept_objs['MAINT'], dept_objs['PROD'], dept_objs['MECH'])
        tech_prof.specialization = "Hydraulics, Bearings, Paper Machine Drive Mechanics"
        tech_prof.save()

        elec_user = created_users['elec_tech']
        elec_prof, _ = TechnicianProfile.objects.get_or_create(user=elec_user)
        elec_prof.departments.add(dept_objs['ELEC'], dept_objs['INST'])
        elec_prof.specialization = "VFD Inverters, Induction Motors, 415V Switchgear"
        elec_prof.save()

        self.stdout.write(" [x] Seeded standard users (admin, hr_admin, technician, employee, prod_manager).")

        # 5. Create Sample Realistic Tickets
        sample_emp = created_users['employee']
        sample_tech = created_users['technician']

        # Ticket 1: Active High Priority Issue (Production breakdown)
        t1, created1 = Ticket.objects.get_or_create(
            title="Production Paper Machine 2 Drive Motor Abnormal Vibration",
            defaults={
                'description': "During high-speed reeling, the main drive motor is producing high-frequency vibration and abnormal whining sound. Production speed reduced by 30%.",
                'created_by': sample_emp,
                'department': dept_objs['PROD'],
                'category': TicketCategory.objects.filter(department=dept_objs['PROD'], name='Production equipment').first(),
                'priority': priority_objs['HIGH'],
                'status': TicketStatus.IN_PROGRESS,
                'building': 'Paper Machine Section #2',
                'floor': 'Ground Floor',
                'room_area': 'Dry End Drive Section',
                'equipment_number': 'PM2-MTR-01',
                'assigned_to': sample_tech,
                'created_at': timezone.now() - timedelta(hours=2),
                'due_at': timezone.now() + timedelta(hours=2),
            }
        )
        if created1:
            TicketAssignment.objects.create(
                ticket=t1,
                technician=sample_tech,
                assigned_by=created_users['hr_admin'],
                status='ACCEPTED',
                accepted_at=timezone.now() - timedelta(hours=1, minutes=30),
                notes="Inspect vibration levels with portable FFT analyzer. Check coupling alignment."
            )
            TicketHistory.objects.create(
                ticket=t1,
                changed_by=sample_emp,
                action='Ticket Created',
                new_value='NEW',
                details="Ticket logged by operator."
            )
            TicketHistory.objects.create(
                ticket=t1,
                changed_by=created_users['hr_admin'],
                action='Technician Assigned',
                new_value='ASSIGNED',
                details="Assigned to Ramesh Kumar."
            )
            TicketHistory.objects.create(
                ticket=t1,
                changed_by=sample_tech,
                action='Assignment Accepted',
                new_value='IN_PROGRESS',
                details="Technician arrived on site with vibration meter."
            )

        # Ticket 2: Resolved Ticket (Waiting for Employee Confirmation)
        t2, created2 = Ticket.objects.get_or_create(
            title="Hydraulic Oil Pressure Drop on Press Section Rollers",
            defaults={
                'description': "Secondary nip press accumulator was losing pressure under load. Oil level low.",
                'created_by': sample_emp,
                'department': dept_objs['MAINT'],
                'category': TicketCategory.objects.filter(department=dept_objs['MAINT'], name='Machine problem').first(),
                'priority': priority_objs['MEDIUM'],
                'status': TicketStatus.RESOLVED,
                'building': 'Paper Mill #1',
                'floor': 'Operating Deck',
                'room_area': 'Press Section Bay 2',
                'equipment_number': 'PM1-HYD-03',
                'assigned_to': sample_tech,
                'resolution_summary': "Replaced worn high-pressure hydraulic hose line, topped up ISO VG 68 oil, and tested under 120 bar pressure. No leaks detected.",
                'employee_confirmation': 'PENDING',
                'created_at': timezone.now() - timedelta(hours=8),
                'due_at': timezone.now() + timedelta(hours=4),
                'resolved_at': timezone.now() - timedelta(minutes=45),
            }
        )

        # Ticket 3: Critical SLA Breached / Escalated Ticket
        t3, created3 = Ticket.objects.get_or_create(
            title="Substation 2 Main Transformer Breaker Trip",
            defaults={
                'description': "Total blackout across chemical recovery boiler feed pumps. Urgent power restoration needed.",
                'created_by': sample_emp,
                'department': dept_objs['ELEC'],
                'category': TicketCategory.objects.filter(department=dept_objs['ELEC'], name='Power outage').first(),
                'priority': priority_objs['CRITICAL'],
                'status': TicketStatus.ESCALATED,
                'building': 'Power House',
                'floor': 'Substation 2',
                'room_area': 'Transformer Yard Bay 1',
                'equipment_number': 'TR-02-11KV',
                'assigned_to': created_users['elec_tech'],
                'sla_breached': True,
                'sla_warning_sent': True,
                'escalation_level': 1,
                'created_at': timezone.now() - timedelta(hours=3),
                'due_at': timezone.now() - timedelta(hours=2),
            }
        )

        # Ticket 4: New Unassigned Ticket (Waiting in HR queue)
        t4, created4 = Ticket.objects.get_or_create(
            title="Control Room DCS Display #4 Screen Flickering and Freezing",
            defaults={
                'description': "Honeywell DCS workstation display intermittently blanks out during paper reel changeovers.",
                'created_by': sample_emp,
                'department': dept_objs['IT'],
                'category': TicketCategory.objects.filter(department=dept_objs['IT'], name='Computer problem').first(),
                'priority': priority_objs['LOW'],
                'status': TicketStatus.NEW,
                'building': 'Main Plant Control Tower',
                'floor': '3rd Floor',
                'room_area': 'Central DCS Room',
                'equipment_number': 'DCS-WS-04',
                'created_at': timezone.now() - timedelta(minutes=30),
                'due_at': timezone.now() + timedelta(hours=23, minutes=30),
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample data for JK Paper Mill!"))
        self.stdout.write("\n========================================================")
        self.stdout.write("TEST CREDENTIALS (Default password: password123):")
        self.stdout.write(" 1. Super Admin: admin@company.com / password123")
        self.stdout.write(" 2. HR / Helpdesk: hr@company.com / password123")
        self.stdout.write(" 3. Dept Manager: manager.prod@company.com / password123")
        self.stdout.write(" 4. Technician: technician@company.com / password123")
        self.stdout.write(" 5. Employee: employee@company.com / password123")
        self.stdout.write("========================================================\n")
