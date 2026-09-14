# JK Paper Mill - Enterprise Ticket Management System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-Proprietary%20Enterprise-red.svg)](#)

A centralized, production-grade internal Ticket Management System tailored for **JK Paper Mill**. It enables any employee across manufacturing sections and corporate offices to report issues to specific departments (IT, Maintenance, Electrical, Mechanical, Production, Safety, HR), with real-time technician dispatching, automated SLA enforcement, multi-level escalation, in-app and SMTP email notifications, file attachments with image preview & OCR, and an AI triage assistant.

---

## Table of Contents
1. [Architecture & System Overview](#architecture--system-overview)
2. [Key Features](#key-features)
3. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
4. [Database Design & ER Diagram](#database-design--er-diagram)
5. [Technology Stack](#technology-stack)
6. [Windows Setup & Installation Guide](#windows-setup--installation-guide)
7. [MySQL Configuration](#mysql-configuration)
8. [Sample Test Accounts](#sample-test-accounts)
9. [SLA & Automatic Escalation Engine](#sla--automatic-escalation-engine)
10. [AI Troubleshooting Assistant](#ai-troubleshooting-assistant)
11. [Reporting & Analytics](#reporting--analytics)
12. [Audit Trail & Enterprise Security](#audit-trail--enterprise-security)
13. [Project Directory Tree](#project-directory-tree)
14. [Future Enhancements](#future-enhancements)

---

## Architecture & System Overview

The system follows clean modular Django architecture separating presentation, business services, and database persistence:

```
                            [ Web Browser (Desktop / Mobile) ]
                                            │
                                            ▼
                             [ Django Application Gateway ]
                                            │
   ┌────────────────┬───────────────┼───────────────┬────────────────┬───────────────┐
   ▼                ▼               ▼               ▼                ▼               ▼
[ accounts ] [ departments ]   [ tickets ]   [ notifications ]   [ chatbot ]     [ reports ]
  Custom User   20 Dept Units   Sequential IDs  In-app Alerts      Multi-provider  CSV / Excel /
  5 RBAC Roles  Dynamic Cats    SLA State Mach. SMTP Mail Logs     Offline Triage  PDF Exports
   │                │               │               │                │               │
   └────────────────┴───────────────┼───────────────┴────────────────┴───────────────┘
                                    ▼
                         [ services / Layer ]
                         ├── ai_service.py (Gemini / OpenAI / Groq / Triage)
                         ├── email_service.py (HTML templates & SMTP)
                         ├── ocr_service.py (Optional text extraction)
                         └── sla_service.py (75% warning & 100% breach escalation)
                                    │
                                    ▼
                       [ MySQL Relational Database ]
```

---

## Key Features

1. **Sequential Ticket Numbering**: Automated atomic format `TKT-YYYY-XXXXXX` (e.g. `TKT-2026-000001`).
2. **Interactive 4-Step Ticket Wizard**:
   - Step 1: Issue title, description, department, and dynamic category loading.
   - Step 2: Plant location specifics (Building, Floor, Bay/Room, Machine/Equipment Tag ID).
   - Step 3: Priority selection (CRITICAL, HIGH, MEDIUM, LOW) with transparent SLA commit times.
   - Step 4: Drag-and-drop file upload with client-side image preview and 10MB limit.
3. **5-Stage Ticket Lifecycle State Machine**:
   `NEW` ➔ `ASSIGNED` ➔ `IN_PROGRESS` ➔ `RESOLVED` ➔ `CLOSED` (or `REOPENED`).
4. **Technician Workload Balancing**:
   - HR sees active technician ticket counts (e.g. "Available", "Busy (2)", "Overloaded").
   - Recommended technicians auto-filtered by department specialization.
5. **Work Completion & Before/After Proofs**:
   - Technicians upload proof photographs and resolution summaries.
   - Employee verifies work and clicks **Confirm Resolution** (closes ticket) or **Reopen Ticket**.
6. **Automated SLA Tracking & Escalation**:
   - Warnings at 75% elapsed SLA timeframe.
   - Automated Level 1 & Level 2 escalations at 100% breach with notifications to Department Managers and Senior Admins.
7. **Modular AI Assistant**:
   - Preliminary industrial triage for paper machine paper jams, roller bearing overheat, drive trips, hydraulic pressure loss, IT disconnects.
   - Safe advisory mode with a one-click *"Create Ticket with this Context"* button.
8. **Multi-Format Reports**:
   - Direct export to **CSV**, formatted **Excel (.xlsx)** with headers and zebra striping, and printable **PDF** summary tables.

---

## Role-Based Access Control (RBAC)

| Role | Permissions & Workspace |
|---|---|
| **Super Admin** | Full governance: manage users, configure roles/departments/SLAs, view system-wide analytics, inspect immutable audit logs. |
| **HR / Helpdesk Admin** | Triage radar: assign/reassign technicians, adjust ticket priorities, monitor SLA compliance, view department health reports. |
| **Department Manager** | Department command: view all tickets in their plant unit, track machinery downtime, monitor technician progress. |
| **Technician** | Field workbench: view assigned repair jobs, accept assignments, update progress, upload before/after photos, mark work resolved. |
| **Employee** | Self-service portal: submit issues in 1-2 minutes, track live progress, chat with technicians, confirm resolution or reopen tickets. |

---

## Database Design & ER Diagram

The database schema is fully normalized in MySQL with foreign keys and indexes:

- **`accounts_user`**: Custom user inheriting `AbstractUser` with unique `employee_id`, `role`, `department_id`, `phone`, `location`.
- **`accounts_technicianprofile`**: 1-to-1 extension with Many-to-Many link to authorized departments and `specialization`.
- **`departments_department`**: Department master (`code`, `name`, `manager_id`, `is_active`).
- **`departments_ticketcategory`**: Issue classifications linked to departments.
- **`tickets_ticketpriority`**: Priority master (`name`, `sla_hours`, `warning_threshold_percent`, `color_code`).
- **`tickets_ticket`**: Core issue table with timestamps (`created_at`, `due_at`, `resolved_at`, `closed_at`), location tags, status choices, and SLA flags.
- **`tickets_ticketassignment`**: History of assignments, acceptance timestamps, and instructions.
- **`tickets_ticketcomment`**: Threaded communication with optional internal staff flag.
- **`tickets_ticketattachment`**: Uploaded photos and documents with OCR extracted text.
- **`tickets_tickethistory`**: Immutable audit timeline of every state transition.
- **`tickets_escalation`**: Escalation hierarchy logging reasons and escalation levels.
- **`notifications_notification`**: Live navbar in-app alerts with unread flags.
- **`notifications_emaillog`**: History of sent/failed SMTP emails.
- **`chatbot_chatbotconversation` & `chatmessage`**: Dialogue history for AI triage.
- **`audit_auditlog`**: Enterprise security log capturing user, action, ticket, IP address, and details.

---

## Technology Stack

- **Backend**: Python 3.12, Django 5.1
- **Database**: MySQL 8.0+ (with SQLite development fallback via `.env`)
- **Driver**: PyMySQL with `cryptography`
- **Frontend**: HTML5, CSS3 Custom Properties, Vanilla JavaScript (ES6+)
- **UI Components**: Bootstrap Icons, Chart.js 4.4
- **Document Services**: OpenPyXL (Excel), ReportLab (PDF), Pillow (Image Processing)
- **AI Triage**: Google Gemini API, OpenAI-compatible APIs, Groq, or built-in industrial offline triage fallback

---

## Windows Setup & Installation Guide

### Prerequisites
- Windows 10/11
- Python 3.11 or 3.12

### 1. Clone or Extract Project
Open PowerShell and navigate to the project directory:
```powershell
cd ticket_management
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Modify `.env` to configure MySQL credentials or leave `USE_SQLITE=True` for instant development.

### 5. Run Database Migrations
```powershell
python manage.py migrate
```

### 6. Seed Sample Data (Departments, Users, Tickets)
```powershell
python manage.py seed_data
```

### 7. Start the Development Server
```powershell
python manage.py runserver
```
Visit: **`http://127.0.0.1:8000/`**

---

## MySQL Configuration

To connect the application to a local or remote MySQL Server:

1. Create the MySQL database:
   ```sql
   CREATE DATABASE ticket_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. In `.env`, set:
   ```env
   USE_SQLITE=False
   DB_NAME=ticket_management
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Run migrations:
   ```powershell
   python manage.py migrate
   ```

---

## Sample Test Accounts

The `python manage.py seed_data` command generates pre-configured users with the safe default password: **`password123`**

| Role | Email / Username | Employee ID | Name | Department |
|---|---|---|---|---|
| **Super Admin** | `admin@company.com` | `EMP-0001` | Chief Administrator | Plant Administration |
| **HR / Helpdesk** | `hr@company.com` | `EMP-1001` | Sunita Sharma | Human Resources |
| **Dept Manager** | `manager.prod@company.com` | `EMP-4001` | Rajesh Patel | Production |
| **Technician (Maint)** | `technician@company.com` | `EMP-2001` | Ramesh Kumar | Maintenance |
| **Technician (Elec)** | `technician.elec@company.com` | `EMP-2002` | Anil Verma | Electrical |
| **Employee** | `employee@company.com` | `EMP-3001` | P. Shyamprasad | Production Machine Operator |

*(The login page also provides 1-click Fast-Fill demo chips to immediately sign in as any role.)*

---

## SLA & Automatic Escalation Engine

SLA turnaround targets:
- **CRITICAL**: 1 Hour (Warning at 45m)
- **HIGH**: 4 Hours (Warning at 3h)
- **MEDIUM**: 12 Hours (Warning at 9h)
- **LOW**: 24 Hours (Warning at 18h)

### Periodic Background Scanner
To scan tickets and execute automated SLA warnings and escalations in background jobs or Windows Task Scheduler:
```powershell
python manage.py check_sla
```
- Tickets at 75% SLA trigger warnings to technicians and HR.
- Tickets past due are automatically flagged `sla_breached=True`, transitioned to `ESCALATED`, escalated to Level 1 (HR Manager) or Level 2 (Senior Admin), and logged in the audit trail.

---

## AI Troubleshooting Assistant

The AI Assistant helps employees troubleshoot common workplace and machinery issues before logging a ticket.

### Configuration (`.env`)
```env
AI_PROVIDER=gemini       # Options: gemini, openai, groq
AI_API_KEY=your_key_here
AI_MODEL=gemini-1.5-flash
```

### Safety Guardrails
- Advisory role only: cannot change ticket status, close tickets, or assign personnel.
- Immediately directs high-voltage electrical, boiler, chemical, or rotating equipment hazards to emergency security.
- Features intelligent offline industrial fallback when API keys are not provided.

---

## Reporting & Analytics

Accessible at `/reports/`:
- **Metrics**: Total volume, resolved tickets, SLA breach rate, SLA compliance percentage.
- **Cross-Filters**: Date range, department, priority, status, and technician.
- **Export Options**:
  - **CSV Export**: Standard spreadsheet data.
  - **Excel (.xlsx) Export**: Formatted tables with color headers and alternating row styles.
  - **PDF Export**: Landscape printable executive summary with company header.

---

## Project Directory Tree

```
ticket_management/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── decorators.py
│   └── admin.py
├── departments/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── tickets/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── tests.py
│   └── management/commands/
│       ├── check_sla.py
│       └── seed_data.py
├── notifications/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   └── context_processors.py
├── chatbot/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── reports/
│   ├── views.py
│   └── urls.py
├── audit/
│   ├── models.py
│   ├── services.py
│   └── views.py
├── services/
│   ├── ai_service.py
│   ├── email_service.py
│   └── ocr_service.py
├── templates/
│   ├── base.html
│   ├── 400.html, 403.html, 404.html, 500.html
│   ├── accounts/
│   ├── dashboards/
│   ├── tickets/
│   ├── departments/
│   ├── reports/
│   ├── chatbot/
│   ├── emails/
│   └── partials/
├── static/
│   ├── css/style.css
│   └── js/
├── requirements.txt
├── .env
├── .env.example
└── .gitignore
```

---

## Future Enhancements
1. **Celery & Redis Worker**: Asynchronous queue processing for large-scale enterprise email dispatches and periodic cron execution of `check_sla`.
2. **WebSocket Live Updates**: Real-time push notifications using Django Channels.
3. **Barcode / QR Code Asset Scanning**: Camera scanner to auto-fill equipment tag numbers during ticket creation.
4. **Active Directory / LDAP / SSO**: Corporate Single Sign-On integration with Microsoft Azure AD.
