-- MySQL database dump for ticket_management
SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `accounts_technicianprofile`;
CREATE TABLE `accounts_technicianprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `specialization` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_available` tinyint(1) NOT NULL,
  `max_concurrent_tickets` int unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `accounts_technicianprofile_user_id_857ea88c_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `accounts_technicianprofile_chk_1` CHECK ((`max_concurrent_tickets` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `accounts_technicianprofile` (`id`, `specialization`, `is_available`, `max_concurrent_tickets`, `created_at`, `updated_at`, `user_id`) VALUES (1, 'Hydraulics, Bearings, Paper Machine Drive Mechanics', 1, 5, '2026-09-14 08:15:18.377350', '2026-09-14 08:15:21.508560', 4);
INSERT INTO `accounts_technicianprofile` (`id`, `specialization`, `is_available`, `max_concurrent_tickets`, `created_at`, `updated_at`, `user_id`) VALUES (2, 'VFD Inverters, Induction Motors, 415V Switchgear', 1, 5, '2026-09-14 08:15:19.930942', '2026-09-14 08:15:21.532562', 5);

DROP TABLE IF EXISTS `accounts_technicianprofile_departments`;
CREATE TABLE `accounts_technicianprofile_departments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `technicianprofile_id` bigint NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_technicianprofi_technicianprofile_id_dep_014721f0_uniq` (`technicianprofile_id`,`department_id`),
  KEY `accounts_technicianp_department_id_906f3c30_fk_departmen` (`department_id`),
  CONSTRAINT `accounts_technicianp_department_id_906f3c30_fk_departmen` FOREIGN KEY (`department_id`) REFERENCES `departments_department` (`id`),
  CONSTRAINT `accounts_technicianp_technicianprofile_id_f3b21e3b_fk_accounts_` FOREIGN KEY (`technicianprofile_id`) REFERENCES `accounts_technicianprofile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `accounts_technicianprofile_departments` (`id`, `technicianprofile_id`, `department_id`) VALUES (1, 1, 3);
INSERT INTO `accounts_technicianprofile_departments` (`id`, `technicianprofile_id`, `department_id`) VALUES (2, 1, 4);
INSERT INTO `accounts_technicianprofile_departments` (`id`, `technicianprofile_id`, `department_id`) VALUES (3, 1, 6);
INSERT INTO `accounts_technicianprofile_departments` (`id`, `technicianprofile_id`, `department_id`) VALUES (4, 2, 5);
INSERT INTO `accounts_technicianprofile_departments` (`id`, `technicianprofile_id`, `department_id`) VALUES (5, 2, 7);

DROP TABLE IF EXISTS `accounts_user`;
CREATE TABLE `accounts_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `employee_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `avatar` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `employee_id` (`employee_id`),
  UNIQUE KEY `email` (`email`),
  KEY `accounts_user_role_57e97df0` (`role`),
  KEY `accounts_user_department_id_8dc06840_fk_departmen` (`department_id`),
  CONSTRAINT `accounts_user_department_id_8dc06840_fk_departmen` FOREIGN KEY (`department_id`) REFERENCES `departments_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `employee_id`, `email`, `phone`, `role`, `designation`, `location`, `avatar`, `department_id`) VALUES (1, 'pbkdf2_sha256$870000$HVORVzggtBaoNFdni6b0Zd$t/U7QogrjyRsWrXRuKDnDRp9lC1a98xcs5izIOPuDws=', '2026-09-14 08:32:29.114108', 1, 'admin', 'Chief', 'Administrator', 1, 1, '2026-09-14 08:15:12.727652', 'EMP-0001', 'admin@company.com', '9348009036', 'SUPER_ADMIN', 'Chief Information Officer', 'Corporate HQ / Plant Control Center', '', NULL);
INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `employee_id`, `email`, `phone`, `role`, `designation`, `location`, `avatar`, `department_id`) VALUES (2, 'pbkdf2_sha256$870000$VhFpu6vq2esWiA58Wmo71x$bpzuOOPkJwoOApMKiwa3ymQsIKzAxxUpRbKTqTv+MYM=', NULL, 0, 'hr_admin', 'Sunita', 'Sharma', 1, 1, '2026-09-14 08:15:13.904273', 'EMP-1001', 'hr@company.com', NULL, 'HR_ADMIN', 'Helpdesk & HR Incharge', 'Admin Block, Room 102', '', 1);
INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `employee_id`, `email`, `phone`, `role`, `designation`, `location`, `avatar`, `department_id`) VALUES (3, 'pbkdf2_sha256$870000$Lo7hrSP2eK8YXGIV8phsIH$0DXj1eVOId8R32vDjPTGkNsU3FgkyMTAhpA8/quAa8M=', NULL, 0, 'prod_manager', 'Rajesh', 'Patel', 0, 1, '2026-09-14 08:15:15.419578', 'EMP-4001', 'manager.prod@company.com', NULL, 'DEPT_MANAGER', 'Production General Manager', 'Paper Mill #2 Central Office', '', 3);
INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `employee_id`, `email`, `phone`, `role`, `designation`, `location`, `avatar`, `department_id`) VALUES (4, 'pbkdf2_sha256$870000$kidhe8SRfY40dts4Per4u4$Px/F9lxkOo7jufkqitTwqr8gdkrv0juD9XbHp9l+sLA=', NULL, 0, 'technician', 'Ramesh', 'Kumar', 0, 1, '2026-09-14 08:15:16.858318', 'EMP-2001', 'technician@company.com', NULL, 'TECHNICIAN', 'Senior Maintenance Technician', 'Maintenance Workshop Bay A', '', 4);
INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `employee_id`, `email`, `phone`, `role`, `designation`, `location`, `avatar`, `department_id`) VALUES (5, 'pbkdf2_sha256$870000$XzBzwoBvHIMTffYlzGyx5K$/sPTdNCTm16+fjTUGF59eTiPANefdCEw2nqtPaZaCqY=', NULL, 0, 'elec_tech', 'Anil', 'Verma', 0, 1, '2026-09-14 08:15:18.393925', 'EMP-2002', 'technician.elec@company.com', NULL, 'TECHNICIAN', 'Electrical & Drives Technician', 'Electrical Workshop Bay B', '', 5);
INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `employee_id`, `email`, `phone`, `role`, `designation`, `location`, `avatar`, `department_id`) VALUES (6, 'pbkdf2_sha256$870000$LiOVBSVl16dyOBaAfo1fYf$zpbgxMUGh7E3clHjyfKteO6HXFwCR0p4A9lwlDg/zak=', NULL, 0, 'employee', 'P.', 'Shyamprasad', 0, 1, '2026-09-14 08:15:19', 'EMP-3001', 'employee@company.com', NULL, 'EMPLOYEE', 'Paper Machine Operator', 'Paper Machine #1 Operating Floor', '', 3);

DROP TABLE IF EXISTS `accounts_user_groups`;
CREATE TABLE `accounts_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `audit_auditlog`;
CREATE TABLE `audit_auditlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ticket_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `details` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `audit_auditlog_user_id_c1cca96c_fk_accounts_user_id` (`user_id`),
  KEY `audit_auditlog_action_dc562e21` (`action`),
  KEY `audit_auditlog_ticket_number_2d07bede` (`ticket_number`),
  KEY `audit_auditlog_created_at_5c532845` (`created_at`),
  CONSTRAINT `audit_auditlog_user_id_c1cca96c_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `audit_auditlog` (`id`, `action`, `ticket_number`, `ip_address`, `details`, `created_at`, `user_id`) VALUES (1, 'CONTACT_VERIFIED', NULL, '127.0.0.1', 'Employee verified alert contact details (Email: admin@company.com, Phone: 9348009036).', '2026-09-14 08:32:56.740378', 1);

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (21, 'Can add User', 6, 'add_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (22, 'Can change User', 6, 'change_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (23, 'Can delete User', 6, 'delete_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (24, 'Can view User', 6, 'view_user');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (25, 'Can add Technician Profile', 7, 'add_technicianprofile');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (26, 'Can change Technician Profile', 7, 'change_technicianprofile');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (27, 'Can delete Technician Profile', 7, 'delete_technicianprofile');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (28, 'Can view Technician Profile', 7, 'view_technicianprofile');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (29, 'Can add Department', 8, 'add_department');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (30, 'Can change Department', 8, 'change_department');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (31, 'Can delete Department', 8, 'delete_department');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (32, 'Can view Department', 8, 'view_department');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (33, 'Can add Ticket Category', 9, 'add_ticketcategory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (34, 'Can change Ticket Category', 9, 'change_ticketcategory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (35, 'Can delete Ticket Category', 9, 'delete_ticketcategory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (36, 'Can view Ticket Category', 9, 'view_ticketcategory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (37, 'Can add Ticket Priority', 10, 'add_ticketpriority');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (38, 'Can change Ticket Priority', 10, 'change_ticketpriority');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (39, 'Can delete Ticket Priority', 10, 'delete_ticketpriority');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (40, 'Can view Ticket Priority', 10, 'view_ticketpriority');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (41, 'Can add Ticket', 11, 'add_ticket');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (42, 'Can change Ticket', 11, 'change_ticket');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (43, 'Can delete Ticket', 11, 'delete_ticket');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (44, 'Can view Ticket', 11, 'view_ticket');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (45, 'Can add escalation', 12, 'add_escalation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (46, 'Can change escalation', 12, 'change_escalation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (47, 'Can delete escalation', 12, 'delete_escalation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (48, 'Can view escalation', 12, 'view_escalation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (49, 'Can add ticket assignment', 13, 'add_ticketassignment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (50, 'Can change ticket assignment', 13, 'change_ticketassignment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (51, 'Can delete ticket assignment', 13, 'delete_ticketassignment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (52, 'Can view ticket assignment', 13, 'view_ticketassignment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (53, 'Can add ticket attachment', 14, 'add_ticketattachment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (54, 'Can change ticket attachment', 14, 'change_ticketattachment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (55, 'Can delete ticket attachment', 14, 'delete_ticketattachment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (56, 'Can view ticket attachment', 14, 'view_ticketattachment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (57, 'Can add ticket comment', 15, 'add_ticketcomment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (58, 'Can change ticket comment', 15, 'change_ticketcomment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (59, 'Can delete ticket comment', 15, 'delete_ticketcomment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (60, 'Can view ticket comment', 15, 'view_ticketcomment');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (61, 'Can add ticket history', 16, 'add_tickethistory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (62, 'Can change ticket history', 16, 'change_tickethistory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (63, 'Can delete ticket history', 16, 'delete_tickethistory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (64, 'Can view ticket history', 16, 'view_tickethistory');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (65, 'Can add SLA Configuration', 17, 'add_slaconfiguration');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (66, 'Can change SLA Configuration', 17, 'change_slaconfiguration');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (67, 'Can delete SLA Configuration', 17, 'delete_slaconfiguration');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (68, 'Can view SLA Configuration', 17, 'view_slaconfiguration');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (69, 'Can add Email Log', 18, 'add_emaillog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (70, 'Can change Email Log', 18, 'change_emaillog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (71, 'Can delete Email Log', 18, 'delete_emaillog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (72, 'Can view Email Log', 18, 'view_emaillog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (73, 'Can add Notification', 19, 'add_notification');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (74, 'Can change Notification', 19, 'change_notification');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (75, 'Can delete Notification', 19, 'delete_notification');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (76, 'Can view Notification', 19, 'view_notification');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (77, 'Can add SMS Log', 20, 'add_smslog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (78, 'Can change SMS Log', 20, 'change_smslog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (79, 'Can delete SMS Log', 20, 'delete_smslog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (80, 'Can view SMS Log', 20, 'view_smslog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (81, 'Can add chatbot conversation', 21, 'add_chatbotconversation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (82, 'Can change chatbot conversation', 21, 'change_chatbotconversation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (83, 'Can delete chatbot conversation', 21, 'delete_chatbotconversation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (84, 'Can view chatbot conversation', 21, 'view_chatbotconversation');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (85, 'Can add chat message', 22, 'add_chatmessage');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (86, 'Can change chat message', 22, 'change_chatmessage');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (87, 'Can delete chat message', 22, 'delete_chatmessage');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (88, 'Can view chat message', 22, 'view_chatmessage');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (89, 'Can add Audit Log', 23, 'add_auditlog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (90, 'Can change Audit Log', 23, 'change_auditlog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (91, 'Can delete Audit Log', 23, 'delete_auditlog');
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (92, 'Can view Audit Log', 23, 'view_auditlog');

DROP TABLE IF EXISTS `chatbot_chatbotconversation`;
CREATE TABLE `chatbot_chatbotconversation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`),
  KEY `chatbot_chatbotconversation_user_id_b85b403b_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `chatbot_chatbotconversation_user_id_b85b403b_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `chatbot_chatbotconversation` (`id`, `session_id`, `title`, `created_at`, `updated_at`, `user_id`) VALUES (1, 'bef332785f584fb4b41db42ab9648629', 'Issue Troubleshooting Session', '2026-09-14 08:51:58.448925', '2026-09-14 08:51:58.448925', 1);
INSERT INTO `chatbot_chatbotconversation` (`id`, `session_id`, `title`, `created_at`, `updated_at`, `user_id`) VALUES (2, '3fc8ee2fb03f446493536f6a40af2956', 'Issue Troubleshooting Session', '2026-09-14 08:52:13.046199', '2026-09-14 08:52:13.046199', 1);
INSERT INTO `chatbot_chatbotconversation` (`id`, `session_id`, `title`, `created_at`, `updated_at`, `user_id`) VALUES (3, 'c3d9f4f6173143b48641b1a703422fe4', 'Issue Troubleshooting Session', '2026-09-14 08:52:26.032923', '2026-09-14 08:52:26.032923', 1);
INSERT INTO `chatbot_chatbotconversation` (`id`, `session_id`, `title`, `created_at`, `updated_at`, `user_id`) VALUES (4, '76157b99eb914b34afe0f6b0fac21624', 'Issue Troubleshooting Session', '2026-09-14 08:52:29.094769', '2026-09-14 08:52:29.094769', 1);

DROP TABLE IF EXISTS `chatbot_chatmessage`;
CREATE TABLE `chatbot_chatmessage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `conversation_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `chatbot_chatmessage_conversation_id_c1458541_fk_chatbot_c` (`conversation_id`),
  CONSTRAINT `chatbot_chatmessage_conversation_id_c1458541_fk_chatbot_c` FOREIGN KEY (`conversation_id`) REFERENCES `chatbot_chatbotconversation` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `chatbot_chatmessage` (`id`, `role`, `content`, `created_at`, `conversation_id`) VALUES (1, 'user', 'can u give me he datails of employees', '2026-09-14 08:52:13.102806', 2);
INSERT INTO `chatbot_chatmessage` (`id`, `role`, `content`, `created_at`, `conversation_id`) VALUES (2, 'assistant', 'I have analyzed your query. For best resolution, please ensure you check physical power and basic connectivity. If the issue persists, I recommend creating a formal support ticket with photos or error details so the relevant department technician can inspect it.', '2026-09-14 08:52:13.111757', 2);
INSERT INTO `chatbot_chatmessage` (`id`, `role`, `content`, `created_at`, `conversation_id`) VALUES (3, 'user', 'g', '2026-09-14 08:52:26.088819', 3);
INSERT INTO `chatbot_chatmessage` (`id`, `role`, `content`, `created_at`, `conversation_id`) VALUES (4, 'assistant', 'I have analyzed your query. For best resolution, please ensure you check physical power and basic connectivity. If the issue persists, I recommend creating a formal support ticket with photos or error details so the relevant department technician can inspect it.', '2026-09-14 08:52:26.099219', 3);
INSERT INTO `chatbot_chatmessage` (`id`, `role`, `content`, `created_at`, `conversation_id`) VALUES (5, 'user', 'f', '2026-09-14 08:52:29.158413', 4);
INSERT INTO `chatbot_chatmessage` (`id`, `role`, `content`, `created_at`, `conversation_id`) VALUES (6, 'assistant', 'I have analyzed your query. For best resolution, please ensure you check physical power and basic connectivity. If the issue persists, I recommend creating a formal support ticket with photos or error details so the relevant department technician can inspect it.', '2026-09-14 08:52:29.170419', 4);

DROP TABLE IF EXISTS `departments_department`;
CREATE TABLE `departments_department` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `manager_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`),
  KEY `departments_department_manager_id_54b667cc_fk_accounts_user_id` (`manager_id`),
  CONSTRAINT `departments_department_manager_id_54b667cc_fk_accounts_user_id` FOREIGN KEY (`manager_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (1, 'Human Resources', 'HR', 'Employee welfare, recruitment, payroll, and benefits', 1, '2026-09-14 08:15:12.051881', '2026-09-14 08:15:21.484465', 2);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (2, 'IT', 'IT', 'Network infrastructure, servers, workstations, software, and printing systems', 1, '2026-09-14 08:15:12.063065', '2026-09-14 08:15:12.064067', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (3, 'Production', 'PROD', 'Pulp preparation, paper machines, finishing and packaging lines', 1, '2026-09-14 08:15:12.075383', '2026-09-14 08:15:21.473427', 3);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (4, 'Maintenance', 'MAINT', 'Plant-wide mechanical maintenance, preventive inspection, and repairs', 1, '2026-09-14 08:15:12.098952', '2026-09-14 08:15:12.098952', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (5, 'Electrical', 'ELEC', 'High/medium voltage substations, motor control centers, and drives', 1, '2026-09-14 08:15:12.112466', '2026-09-14 08:15:12.112466', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (6, 'Mechanical', 'MECH', 'Heavy rotating equipment, gearboxes, pumps, and pipework', 1, '2026-09-14 08:15:12.125984', '2026-09-14 08:15:12.125984', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (7, 'Instrumentation', 'INST', 'Process automation, DCS sensors, transmitters, and valves', 1, '2026-09-14 08:15:12.140990', '2026-09-14 08:15:12.140990', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (8, 'Quality Control', 'QC', 'Paper grade testing, moisture, tensile, and opacity compliance', 1, '2026-09-14 08:15:12.151986', '2026-09-14 08:15:12.151986', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (9, 'Research & Development', 'RD', 'Fiber engineering, chemical recovery, and green energy innovations', 1, '2026-09-14 08:15:12.164516', '2026-09-14 08:15:12.165520', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (10, 'Finance', 'FIN', 'Budgeting, auditing, and corporate finance', 1, '2026-09-14 08:15:12.190001', '2026-09-14 08:15:12.190001', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (11, 'Accounts', 'ACCT', 'Vendor invoices, ledgers, and billing reconciliation', 1, '2026-09-14 08:15:12.202804', '2026-09-14 08:15:12.202804', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (12, 'Administration', 'ADMIN', 'Facility management, cafeteria, and housekeeping services', 1, '2026-09-14 08:15:12.219148', '2026-09-14 08:15:12.219148', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (13, 'Security', 'SEC', 'Plant gate access, surveillance, and loss prevention', 1, '2026-09-14 08:15:12.236299', '2026-09-14 08:15:12.236299', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (14, 'Stores', 'STORES', 'Spare parts inventory, engineering consumables, and tools', 1, '2026-09-14 08:15:12.255160', '2026-09-14 08:15:12.255160', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (15, 'Procurement', 'PROC', 'Raw wood pulp, chemicals, and equipment purchasing', 1, '2026-09-14 08:15:12.270606', '2026-09-14 08:15:12.270606', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (16, 'Sales', 'SALES', 'Domestic and international paper roll dispatches', 1, '2026-09-14 08:15:12.290486', '2026-09-14 08:15:12.290486', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (17, 'Marketing', 'MKTG', 'Corporate communication and client brand coordination', 1, '2026-09-14 08:15:12.309634', '2026-09-14 08:15:12.309634', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (18, 'Safety', 'SAFE', 'Occupational health, fire response, PPE, and OSHA compliance', 1, '2026-09-14 08:15:12.326194', '2026-09-14 08:15:12.326194', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (19, 'Environment', 'ENV', 'Effluent treatment, boiler emissions, and water recovery', 1, '2026-09-14 08:15:12.344204', '2026-09-14 08:15:12.344204', NULL);
INSERT INTO `departments_department` (`id`, `name`, `code`, `description`, `is_active`, `created_at`, `updated_at`, `manager_id`) VALUES (20, 'Transport', 'TRANS', 'Plant fleet, logistics vehicles, and forklift management', 1, '2026-09-14 08:15:12.363989', '2026-09-14 08:15:12.363989', NULL);

DROP TABLE IF EXISTS `departments_ticketcategory`;
CREATE TABLE `departments_ticketcategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `departments_ticketcategory_department_id_name_79a0a6d6_uniq` (`department_id`,`name`),
  CONSTRAINT `departments_ticketca_department_id_69503bd7_fk_departmen` FOREIGN KEY (`department_id`) REFERENCES `departments_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (1, 'Computer problem', NULL, 1, '2026-09-14 08:15:12.388466', '2026-09-14 08:15:12.388466', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (2, 'Network problem', NULL, 1, '2026-09-14 08:15:12.407752', '2026-09-14 08:15:12.407752', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (3, 'Software problem', NULL, 1, '2026-09-14 08:15:12.431176', '2026-09-14 08:15:12.431176', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (4, 'Printer problem', NULL, 1, '2026-09-14 08:15:12.456630', '2026-09-14 08:15:12.456630', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (5, 'Email problem', NULL, 1, '2026-09-14 08:15:12.466908', '2026-09-14 08:15:12.466908', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (6, 'Internet problem', NULL, 1, '2026-09-14 08:15:12.475531', '2026-09-14 08:15:12.475531', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (7, 'Hardware problem', NULL, 1, '2026-09-14 08:15:12.482078', '2026-09-14 08:15:12.482078', 2);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (8, 'Machine problem', NULL, 1, '2026-09-14 08:15:12.490714', '2026-09-14 08:15:12.490714', 4);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (9, 'Equipment problem', NULL, 1, '2026-09-14 08:15:12.498001', '2026-09-14 08:15:12.498001', 4);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (10, 'Building issue', NULL, 1, '2026-09-14 08:15:12.505603', '2026-09-14 08:15:12.505603', 4);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (11, 'Plumbing', NULL, 1, '2026-09-14 08:15:12.515299', '2026-09-14 08:15:12.515299', 4);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (12, 'Valve leak', NULL, 1, '2026-09-14 08:15:12.523668', '2026-09-14 08:15:12.523668', 4);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (13, 'Bearing failure', NULL, 1, '2026-09-14 08:15:12.533670', '2026-09-14 08:15:12.533670', 4);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (14, 'Motor trip', NULL, 1, '2026-09-14 08:15:12.542980', '2026-09-14 08:15:12.542980', 5);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (15, 'Power outage', NULL, 1, '2026-09-14 08:15:12.554631', '2026-09-14 08:15:12.554631', 5);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (16, 'Control panel fault', NULL, 1, '2026-09-14 08:15:12.566683', '2026-09-14 08:15:12.566683', 5);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (17, 'Lighting failure', NULL, 1, '2026-09-14 08:15:12.574775', '2026-09-14 08:15:12.574775', 5);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (18, 'VFD drive fault', NULL, 1, '2026-09-14 08:15:12.583330', '2026-09-14 08:15:12.583330', 5);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (19, 'Production equipment', NULL, 1, '2026-09-14 08:15:12.590825', '2026-09-14 08:15:12.590825', 3);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (20, 'Production process', NULL, 1, '2026-09-14 08:15:12.599824', '2026-09-14 08:15:12.599824', 3);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (21, 'Safety issue', NULL, 1, '2026-09-14 08:15:12.608828', '2026-09-14 08:15:12.608828', 3);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (22, 'Machine downtime', NULL, 1, '2026-09-14 08:15:12.617827', '2026-09-14 08:15:12.617827', 3);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (23, 'Sheet break', NULL, 1, '2026-09-14 08:15:12.626822', '2026-09-14 08:15:12.626822', 3);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (24, 'Employee issue', NULL, 1, '2026-09-14 08:15:12.637041', '2026-09-14 08:15:12.637041', 1);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (25, 'Attendance', NULL, 1, '2026-09-14 08:15:12.643065', '2026-09-14 08:15:12.643065', 1);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (26, 'Payroll', NULL, 1, '2026-09-14 08:15:12.650062', '2026-09-14 08:15:12.650062', 1);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (27, 'Leave', NULL, 1, '2026-09-14 08:15:12.658067', '2026-09-14 08:15:12.658067', 1);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (28, 'Employee documentation', NULL, 1, '2026-09-14 08:15:12.671426', '2026-09-14 08:15:12.671426', 1);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (29, 'Health insurance', NULL, 1, '2026-09-14 08:15:12.682547', '2026-09-14 08:15:12.682547', 1);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (30, 'Hazardous condition', NULL, 1, '2026-09-14 08:15:12.692431', '2026-09-14 08:15:12.692431', 18);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (31, 'Fire extinguisher check', NULL, 1, '2026-09-14 08:15:12.698460', '2026-09-14 08:15:12.698460', 18);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (32, 'Chemical spill alert', NULL, 1, '2026-09-14 08:15:12.705734', '2026-09-14 08:15:12.706248', 18);
INSERT INTO `departments_ticketcategory` (`id`, `name`, `description`, `is_active`, `created_at`, `updated_at`, `department_id`) VALUES (33, 'PPE request', NULL, 1, '2026-09-14 08:15:12.714366', '2026-09-14 08:15:12.714366', 18);

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES (1, '2026-09-14 08:49:40.551631', '6', 'EMP-3001 - P. Shyamprasad (Employee)', 2, '[]', 6, 1);

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (7, 'accounts', 'technicianprofile');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (6, 'accounts', 'user');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (23, 'audit', 'auditlog');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (3, 'auth', 'group');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (2, 'auth', 'permission');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (21, 'chatbot', 'chatbotconversation');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (22, 'chatbot', 'chatmessage');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (8, 'departments', 'department');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (9, 'departments', 'ticketcategory');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (18, 'notifications', 'emaillog');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (19, 'notifications', 'notification');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (20, 'notifications', 'smslog');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (5, 'sessions', 'session');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (12, 'tickets', 'escalation');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (17, 'tickets', 'slaconfiguration');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (11, 'tickets', 'ticket');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (13, 'tickets', 'ticketassignment');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (14, 'tickets', 'ticketattachment');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (15, 'tickets', 'ticketcomment');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (16, 'tickets', 'tickethistory');
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (10, 'tickets', 'ticketpriority');

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (1, 'accounts', '0001_initial', '2026-09-14 08:14:17.220890');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (2, 'departments', '0001_initial', '2026-09-14 08:14:17.775555');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (3, 'contenttypes', '0001_initial', '2026-09-14 08:14:17.896330');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (4, 'contenttypes', '0002_remove_content_type_name', '2026-09-14 08:14:18.136230');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (5, 'auth', '0001_initial', '2026-09-14 08:14:18.874772');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (6, 'auth', '0002_alter_permission_name_max_length', '2026-09-14 08:14:19.049275');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (7, 'auth', '0003_alter_user_email_max_length', '2026-09-14 08:14:19.062820');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (8, 'auth', '0004_alter_user_username_opts', '2026-09-14 08:14:19.079240');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (9, 'auth', '0005_alter_user_last_login_null', '2026-09-14 08:14:19.096525');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (10, 'auth', '0006_require_contenttypes_0002', '2026-09-14 08:14:19.105731');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (11, 'auth', '0007_alter_validators_add_error_messages', '2026-09-14 08:14:19.124323');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (12, 'auth', '0008_alter_user_username_max_length', '2026-09-14 08:14:19.143490');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (13, 'auth', '0009_alter_user_last_name_max_length', '2026-09-14 08:14:19.165893');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (14, 'auth', '0010_alter_group_name_max_length', '2026-09-14 08:14:19.206952');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (15, 'auth', '0011_update_proxy_permissions', '2026-09-14 08:14:19.241685');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (16, 'auth', '0012_alter_user_first_name_max_length', '2026-09-14 08:14:19.259553');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (17, 'accounts', '0002_initial', '2026-09-14 08:14:20.845145');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (18, 'admin', '0001_initial', '2026-09-14 08:14:21.379164');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (19, 'admin', '0002_logentry_remove_auto_add', '2026-09-14 08:14:21.396698');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (20, 'admin', '0003_logentry_add_action_flag_choices', '2026-09-14 08:14:21.417310');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (21, 'audit', '0001_initial', '2026-09-14 08:14:21.754133');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (22, 'chatbot', '0001_initial', '2026-09-14 08:14:22.167328');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (23, 'tickets', '0001_initial', '2026-09-14 08:14:25.926661');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (24, 'notifications', '0001_initial', '2026-09-14 08:14:26.363146');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (25, 'notifications', '0002_smslog', '2026-09-14 08:14:26.441946');
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (26, 'sessions', '0001_initial', '2026-09-14 08:14:26.522750');

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES ('q2pagfz79d5p95ojr5os0dpxvnbxsp1a', '.eJxVTkkOwiAUvQtrQyh0oC7dewby-YPUoU0oXRnvLk260NVL3vxWAbaSwrZyDhOps2rU6ZeLgA-ed4HuMN8Wjctc8hT1btGHuurrQvy8HN6_ggRrqmmhkVCYLEsvbWts3_NgvUX0riEzRt8KRBids0zoETsnxC4O1nRYw7V0XwYsoaJM-cX1VMkbf74gG0Kb:1x627U:UqjZpc7oyIXvVoWUFUFGr_kOAD0LqujNWwn03gL3Z_k', '2026-09-28 08:32:56.758942');

DROP TABLE IF EXISTS `notifications_emaillog`;
CREATE TABLE `notifications_emaillog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recipient_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `recipient_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subject` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ticket_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_message` longtext COLLATE utf8mb4_unicode_ci,
  `sent_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_emaillog_ticket_number_04425c0d` (`ticket_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `notifications_notification`;
CREATE TABLE `notifications_notification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `notification_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `recipient_id` bigint NOT NULL,
  `ticket_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_notifi_recipient_id_d055f3f0_fk_accounts_` (`recipient_id`),
  KEY `notifications_notifi_ticket_id_422ab224_fk_tickets_t` (`ticket_id`),
  KEY `notifications_notification_is_read_21b215ac` (`is_read`),
  KEY `notifications_notification_created_at_10160fdd` (`created_at`),
  CONSTRAINT `notifications_notifi_recipient_id_d055f3f0_fk_accounts_` FOREIGN KEY (`recipient_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `notifications_notifi_ticket_id_422ab224_fk_tickets_t` FOREIGN KEY (`ticket_id`) REFERENCES `tickets_ticket` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `notifications_smslog`;
CREATE TABLE `notifications_smslog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recipient_phone` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `recipient_name` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `ticket_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `channel` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_message` longtext COLLATE utf8mb4_unicode_ci,
  `sent_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_smslog_ticket_number_c3966b52` (`ticket_number`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `notifications_smslog` (`id`, `recipient_phone`, `recipient_name`, `message`, `ticket_number`, `channel`, `status`, `error_message`, `sent_at`) VALUES (1, '9348009036', 'Chief Administrator', '[JK Paper Mill] Welcome to JK Paper Mill Ticket Alerts! You will now receive instant SMS updates for all ticket responses and resolutions.', NULL, 'SMS', 'SENT', NULL, '2026-09-14 08:32:56.748386');

DROP TABLE IF EXISTS `tickets_escalation`;
CREATE TABLE `tickets_escalation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `escalation_level` int unsigned NOT NULL,
  `reason` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `escalated_at` datetime(6) NOT NULL,
  `escalated_from_id` bigint DEFAULT NULL,
  `escalated_to_id` bigint DEFAULT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tickets_escalation_escalated_from_id_56ccd73f_fk_accounts_` (`escalated_from_id`),
  KEY `tickets_escalation_escalated_to_id_22e1e12d_fk_accounts_user_id` (`escalated_to_id`),
  KEY `tickets_escalation_ticket_id_92a2c79a_fk_tickets_ticket_id` (`ticket_id`),
  CONSTRAINT `tickets_escalation_escalated_from_id_56ccd73f_fk_accounts_` FOREIGN KEY (`escalated_from_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_escalation_escalated_to_id_22e1e12d_fk_accounts_user_id` FOREIGN KEY (`escalated_to_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_escalation_ticket_id_92a2c79a_fk_tickets_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `tickets_ticket` (`id`),
  CONSTRAINT `tickets_escalation_chk_1` CHECK ((`escalation_level` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `tickets_slaconfiguration`;
CREATE TABLE `tickets_slaconfiguration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `resolution_hours` int unsigned NOT NULL,
  `warning_hours` int unsigned NOT NULL,
  `category_id` bigint DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  `priority_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tickets_slaconfigura_category_id_32d5f0ca_fk_departmen` (`category_id`),
  KEY `tickets_slaconfigura_department_id_0b26913f_fk_departmen` (`department_id`),
  KEY `tickets_slaconfigura_priority_id_9a7aede8_fk_tickets_t` (`priority_id`),
  CONSTRAINT `tickets_slaconfigura_category_id_32d5f0ca_fk_departmen` FOREIGN KEY (`category_id`) REFERENCES `departments_ticketcategory` (`id`),
  CONSTRAINT `tickets_slaconfigura_department_id_0b26913f_fk_departmen` FOREIGN KEY (`department_id`) REFERENCES `departments_department` (`id`),
  CONSTRAINT `tickets_slaconfigura_priority_id_9a7aede8_fk_tickets_t` FOREIGN KEY (`priority_id`) REFERENCES `tickets_ticketpriority` (`id`),
  CONSTRAINT `tickets_slaconfiguration_chk_1` CHECK ((`resolution_hours` >= 0)),
  CONSTRAINT `tickets_slaconfiguration_chk_2` CHECK ((`warning_hours` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `tickets_ticket`;
CREATE TABLE `tickets_ticket` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ticket_number` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `building` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `floor` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `room_area` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipment_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `due_at` datetime(6) DEFAULT NULL,
  `resolved_at` datetime(6) DEFAULT NULL,
  `closed_at` datetime(6) DEFAULT NULL,
  `resolution_summary` longtext COLLATE utf8mb4_unicode_ci,
  `employee_confirmation` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reopened_count` int unsigned NOT NULL,
  `escalation_level` int unsigned NOT NULL,
  `sla_breached` tinyint(1) NOT NULL,
  `sla_warning_sent` tinyint(1) NOT NULL,
  `assigned_to_id` bigint DEFAULT NULL,
  `category_id` bigint DEFAULT NULL,
  `created_by_id` bigint NOT NULL,
  `department_id` bigint NOT NULL,
  `priority_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_number` (`ticket_number`),
  KEY `tickets_ticket_assigned_to_id_142e13bf_fk_accounts_user_id` (`assigned_to_id`),
  KEY `tickets_ticket_category_id_710dbfd0_fk_departmen` (`category_id`),
  KEY `tickets_ticket_created_by_id_c418a145_fk_accounts_user_id` (`created_by_id`),
  KEY `tickets_ticket_department_id_32e39a8e_fk_departmen` (`department_id`),
  KEY `tickets_ticket_priority_id_f3f0911d_fk_tickets_ticketpriority_id` (`priority_id`),
  KEY `tickets_ticket_status_384e643a` (`status`),
  KEY `tickets_ticket_created_at_95bb8d8e` (`created_at`),
  KEY `tickets_ticket_due_at_c037a0bd` (`due_at`),
  KEY `tickets_ticket_sla_breached_8c4c4258` (`sla_breached`),
  CONSTRAINT `tickets_ticket_assigned_to_id_142e13bf_fk_accounts_user_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_ticket_category_id_710dbfd0_fk_departmen` FOREIGN KEY (`category_id`) REFERENCES `departments_ticketcategory` (`id`),
  CONSTRAINT `tickets_ticket_created_by_id_c418a145_fk_accounts_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_ticket_department_id_32e39a8e_fk_departmen` FOREIGN KEY (`department_id`) REFERENCES `departments_department` (`id`),
  CONSTRAINT `tickets_ticket_priority_id_f3f0911d_fk_tickets_ticketpriority_id` FOREIGN KEY (`priority_id`) REFERENCES `tickets_ticketpriority` (`id`),
  CONSTRAINT `tickets_ticket_chk_1` CHECK ((`reopened_count` >= 0)),
  CONSTRAINT `tickets_ticket_chk_2` CHECK ((`escalation_level` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tickets_ticket` (`id`, `ticket_number`, `title`, `description`, `status`, `building`, `floor`, `room_area`, `equipment_number`, `created_at`, `updated_at`, `due_at`, `resolved_at`, `closed_at`, `resolution_summary`, `employee_confirmation`, `reopened_count`, `escalation_level`, `sla_breached`, `sla_warning_sent`, `assigned_to_id`, `category_id`, `created_by_id`, `department_id`, `priority_id`) VALUES (1, 'TKT-2026-000001', 'Production Paper Machine 2 Drive Motor Abnormal Vibration', 'During high-speed reeling, the main drive motor is producing high-frequency vibration and abnormal whining sound. Production speed reduced by 30%.', 'IN_PROGRESS', 'Paper Machine Section #2', 'Ground Floor', 'Dry End Drive Section', 'PM2-MTR-01', '2026-09-14 08:15:21.571563', '2026-09-14 08:15:21.571563', '2026-09-14 10:15:21.550559', NULL, NULL, NULL, 'PENDING', 0, 0, 0, 0, 4, 19, 6, 3, 2);
INSERT INTO `tickets_ticket` (`id`, `ticket_number`, `title`, `description`, `status`, `building`, `floor`, `room_area`, `equipment_number`, `created_at`, `updated_at`, `due_at`, `resolved_at`, `closed_at`, `resolution_summary`, `employee_confirmation`, `reopened_count`, `escalation_level`, `sla_breached`, `sla_warning_sent`, `assigned_to_id`, `category_id`, `created_by_id`, `department_id`, `priority_id`) VALUES (2, 'TKT-2026-000002', 'Hydraulic Oil Pressure Drop on Press Section Rollers', 'Secondary nip press accumulator was losing pressure under load. Oil level low.', 'RESOLVED', 'Paper Mill #1', 'Operating Deck', 'Press Section Bay 2', 'PM1-HYD-03', '2026-09-14 08:15:21.641108', '2026-09-14 08:15:21.642119', '2026-09-14 12:15:21.625117', '2026-09-14 07:30:21.625117', NULL, 'Replaced worn high-pressure hydraulic hose line, topped up ISO VG 68 oil, and tested under 120 bar pressure. No leaks detected.', 'PENDING', 0, 0, 0, 0, 4, 8, 6, 4, 3);
INSERT INTO `tickets_ticket` (`id`, `ticket_number`, `title`, `description`, `status`, `building`, `floor`, `room_area`, `equipment_number`, `created_at`, `updated_at`, `due_at`, `resolved_at`, `closed_at`, `resolution_summary`, `employee_confirmation`, `reopened_count`, `escalation_level`, `sla_breached`, `sla_warning_sent`, `assigned_to_id`, `category_id`, `created_by_id`, `department_id`, `priority_id`) VALUES (3, 'TKT-2026-000003', 'Substation 2 Main Transformer Breaker Trip', 'Total blackout across chemical recovery boiler feed pumps. Urgent power restoration needed.', 'ESCALATED', 'Power House', 'Substation 2', 'Transformer Yard Bay 1', 'TR-02-11KV', '2026-09-14 08:15:21.675146', '2026-09-14 08:15:21.676141', '2026-09-14 06:15:21.659114', NULL, NULL, NULL, 'PENDING', 0, 1, 1, 1, 5, 15, 6, 5, 1);
INSERT INTO `tickets_ticket` (`id`, `ticket_number`, `title`, `description`, `status`, `building`, `floor`, `room_area`, `equipment_number`, `created_at`, `updated_at`, `due_at`, `resolved_at`, `closed_at`, `resolution_summary`, `employee_confirmation`, `reopened_count`, `escalation_level`, `sla_breached`, `sla_warning_sent`, `assigned_to_id`, `category_id`, `created_by_id`, `department_id`, `priority_id`) VALUES (4, 'TKT-2026-000004', 'Control Room DCS Display #4 Screen Flickering and Freezing', 'Honeywell DCS workstation display intermittently blanks out during paper reel changeovers.', 'NEW', 'Main Plant Control Tower', '3rd Floor', 'Central DCS Room', 'DCS-WS-04', '2026-09-14 08:15:21.708285', '2026-09-14 08:15:21.708285', '2026-09-15 07:45:21.691513', NULL, NULL, NULL, 'PENDING', 0, 0, 0, 0, NULL, 1, 6, 2, 4);

DROP TABLE IF EXISTS `tickets_ticketassignment`;
CREATE TABLE `tickets_ticketassignment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `assigned_at` datetime(6) NOT NULL,
  `accepted_at` datetime(6) DEFAULT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `assigned_by_id` bigint DEFAULT NULL,
  `technician_id` bigint NOT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tickets_ticketassign_assigned_by_id_deada486_fk_accounts_` (`assigned_by_id`),
  KEY `tickets_ticketassign_technician_id_58bca17e_fk_accounts_` (`technician_id`),
  KEY `tickets_ticketassignment_ticket_id_5eb91da6_fk_tickets_ticket_id` (`ticket_id`),
  CONSTRAINT `tickets_ticketassign_assigned_by_id_deada486_fk_accounts_` FOREIGN KEY (`assigned_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_ticketassign_technician_id_58bca17e_fk_accounts_` FOREIGN KEY (`technician_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_ticketassignment_ticket_id_5eb91da6_fk_tickets_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `tickets_ticket` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tickets_ticketassignment` (`id`, `assigned_at`, `accepted_at`, `completed_at`, `notes`, `status`, `assigned_by_id`, `technician_id`, `ticket_id`) VALUES (1, '2026-09-14 08:15:21.582583', '2026-09-14 06:45:21.581578', NULL, 'Inspect vibration levels with portable FFT analyzer. Check coupling alignment.', 'ACCEPTED', 2, 4, 1);

DROP TABLE IF EXISTS `tickets_ticketattachment`;
CREATE TABLE `tickets_ticketattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int unsigned NOT NULL,
  `ocr_extracted_text` longtext COLLATE utf8mb4_unicode_ci,
  `is_resolution_proof` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `ticket_id` bigint NOT NULL,
  `uploaded_by_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tickets_ticketattachment_ticket_id_55842ab7_fk_tickets_ticket_id` (`ticket_id`),
  KEY `tickets_ticketattach_uploaded_by_id_3ee58633_fk_accounts_` (`uploaded_by_id`),
  CONSTRAINT `tickets_ticketattach_uploaded_by_id_3ee58633_fk_accounts_` FOREIGN KEY (`uploaded_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_ticketattachment_ticket_id_55842ab7_fk_tickets_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `tickets_ticket` (`id`),
  CONSTRAINT `tickets_ticketattachment_chk_1` CHECK ((`file_size` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `tickets_ticketcomment`;
CREATE TABLE `tickets_ticketcomment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_internal` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `author_id` bigint NOT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tickets_ticketcomment_author_id_b65344b0_fk_accounts_user_id` (`author_id`),
  KEY `tickets_ticketcomment_ticket_id_ef1ee786_fk_tickets_ticket_id` (`ticket_id`),
  CONSTRAINT `tickets_ticketcomment_author_id_b65344b0_fk_accounts_user_id` FOREIGN KEY (`author_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_ticketcomment_ticket_id_ef1ee786_fk_tickets_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `tickets_ticket` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `tickets_tickethistory`;
CREATE TABLE `tickets_tickethistory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_value` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_value` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `details` longtext COLLATE utf8mb4_unicode_ci,
  `timestamp` datetime(6) NOT NULL,
  `changed_by_id` bigint DEFAULT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tickets_tickethistory_changed_by_id_fe543666_fk_accounts_user_id` (`changed_by_id`),
  KEY `tickets_tickethistory_ticket_id_fb0c86a4_fk_tickets_ticket_id` (`ticket_id`),
  CONSTRAINT `tickets_tickethistory_changed_by_id_fe543666_fk_accounts_user_id` FOREIGN KEY (`changed_by_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `tickets_tickethistory_ticket_id_fb0c86a4_fk_tickets_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `tickets_ticket` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tickets_tickethistory` (`id`, `action`, `old_value`, `new_value`, `details`, `timestamp`, `changed_by_id`, `ticket_id`) VALUES (1, 'Ticket Created', NULL, 'NEW', 'Ticket logged by operator.', '2026-09-14 08:15:21.592584', 6, 1);
INSERT INTO `tickets_tickethistory` (`id`, `action`, `old_value`, `new_value`, `details`, `timestamp`, `changed_by_id`, `ticket_id`) VALUES (2, 'Technician Assigned', NULL, 'ASSIGNED', 'Assigned to Ramesh Kumar.', '2026-09-14 08:15:21.601123', 2, 1);
INSERT INTO `tickets_tickethistory` (`id`, `action`, `old_value`, `new_value`, `details`, `timestamp`, `changed_by_id`, `ticket_id`) VALUES (3, 'Assignment Accepted', NULL, 'IN_PROGRESS', 'Technician arrived on site with vibration meter.', '2026-09-14 08:15:21.611119', 4, 1);

DROP TABLE IF EXISTS `tickets_ticketpriority`;
CREATE TABLE `tickets_ticketpriority` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sla_hours` int unsigned NOT NULL,
  `warning_threshold_percent` int unsigned NOT NULL,
  `color_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `badge_class` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `tickets_ticketpriority_chk_1` CHECK ((`sla_hours` >= 0)),
  CONSTRAINT `tickets_ticketpriority_chk_2` CHECK ((`warning_threshold_percent` >= 0)),
  CONSTRAINT `tickets_ticketpriority_chk_3` CHECK ((`order` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tickets_ticketpriority` (`id`, `name`, `sla_hours`, `warning_threshold_percent`, `color_code`, `badge_class`, `order`) VALUES (1, 'CRITICAL', 1, 75, '#ef4444', 'badge-danger', 1);
INSERT INTO `tickets_ticketpriority` (`id`, `name`, `sla_hours`, `warning_threshold_percent`, `color_code`, `badge_class`, `order`) VALUES (2, 'HIGH', 4, 75, '#f97316', 'badge-warning', 2);
INSERT INTO `tickets_ticketpriority` (`id`, `name`, `sla_hours`, `warning_threshold_percent`, `color_code`, `badge_class`, `order`) VALUES (3, 'MEDIUM', 12, 75, '#eab308', 'badge-info', 3);
INSERT INTO `tickets_ticketpriority` (`id`, `name`, `sla_hours`, `warning_threshold_percent`, `color_code`, `badge_class`, `order`) VALUES (4, 'LOW', 24, 75, '#3b82f6', 'badge-primary', 4);

SET FOREIGN_KEY_CHECKS=1;
