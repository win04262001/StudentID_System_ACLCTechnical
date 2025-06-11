-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for studentid
CREATE DATABASE IF NOT EXISTS `studentid` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `studentid`;

-- Dumping structure for table studentid.admin_profiles
CREATE TABLE IF NOT EXISTS `admin_profiles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_admin_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.admin_profiles: ~0 rows (approximately)

-- Dumping structure for table studentid.communication_logs
CREATE TABLE IF NOT EXISTS `communication_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `request_id` int NOT NULL,
  `type` enum('email','sms','system') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sent_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sent_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_comm_request` (`request_id`),
  CONSTRAINT `fk_comm_request` FOREIGN KEY (`request_id`) REFERENCES `lost_id_requests` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.communication_logs: ~1 rows (approximately)
INSERT INTO `communication_logs` (`id`, `request_id`, `type`, `subject`, `message`, `sent_by`, `sent_at`) VALUES
	(1, 1, 'email', 'Update on your Lost ID Request #1', 'Dear None,\n\nWe are writing regarding your Lost ID Request (Request #1).\n\n[Your message here]\n\nBest regards,\nTechnical Support Department\nACLC College', 'Admin User', '2025-06-07 23:35:56');

-- Dumping structure for table studentid.lost_id_requests
CREATE TABLE IF NOT EXISTS `lost_id_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `affidavit_file` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` enum('pending','verified','approved','rejected') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `osas_verified` tinyint(1) DEFAULT '0',
  `admin_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `rejection_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `processed_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `processed_at` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_lost_id_student` (`student_id`),
  KEY `idx_lost_id_status` (`status`),
  CONSTRAINT `fk_lost_id_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.lost_id_requests: ~1 rows (approximately)
INSERT INTO `lost_id_requests` (`id`, `student_id`, `reason`, `affidavit_file`, `status`, `osas_verified`, `admin_notes`, `rejection_reason`, `processed_by`, `processed_at`, `created_at`, `updated_at`) VALUES
	(1, '21000602409', 'Nayawa na dugay ra', '21000602409_affidavit_1749364466.png', 'approved', 1, 'jhvbjhjbhjhb', NULL, 'Admin User', '2025-06-08 00:06:59', '2025-06-08 06:34:26', '2025-06-08 07:06:59');

-- Dumping structure for table studentid.students
CREATE TABLE IF NOT EXISTS `students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `middle_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `course` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contact` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `guardian_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `barcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `profile_picture` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `application_status` enum('pending','processing','done','receive') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `signature` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `student_id_2` (`student_id`),
  UNIQUE KEY `student_id_3` (`student_id`),
  KEY `idx_students_first_name` (`first_name`),
  KEY `idx_students_last_name` (`last_name`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.students: ~3 rows (approximately)
INSERT INTO `students` (`id`, `student_id`, `email`, `name`, `first_name`, `middle_name`, `last_name`, `course`, `contact`, `guardian_name`, `address`, `barcode`, `profile_picture`, `phone`, `application_status`, `signature`) VALUES
	(93, '21000602410', 'zarwinm.villaro@aclcbutuan.edu.ph', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', '21000602400.png', 'i35.png', NULL, 'receive', '21000602400_signature.png'),
	(94, '21000602421', 'zarwinb.villaro@aclcbutuan.edu.ph', 'Harvey P. Perater', 'Harvey', 'P.', 'Perater', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-4 Lumbocan, Butuan City', '21000602401.png', 'i21.png', NULL, 'receive', '21000602401_signature.png'),
	(95, '21000602409', 'zasrwin.villaro@aclcbutuan.edu.ph', 'Darwin K. Villaro', 'Darwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', '21000602409.png', 'i6.png', NULL, 'receive', '21000602409_signature.png'),
	(96, '21000602400', 'zarwin.villaro@aclcbutuan.edu.ph', 'Charnelyn Maria E. Estalion', 'Charnelyn', 'Maria E.', 'Estalion', 'BS in COMPUTER SCIENCE', '09510238720', 'Romanito Cuartero Elpidang', 'P-4 Lumbocan, Butuan City', '21000602400.png', 'i5.png', NULL, 'pending', '21000602400_signature.png');

-- Dumping structure for table studentid.student_history
CREATE TABLE IF NOT EXISTS `student_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `middle_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `course` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contact` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `guardian_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `profile_picture` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `signature` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `barcode` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `received_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `academic_year` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '2025-2026',
  `semester` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `idx_student_history_academic_year` (`academic_year`),
  KEY `idx_student_history_semester` (`semester`),
  KEY `idx_student_history_filters` (`semester`,`academic_year`),
  KEY `idx_student_history_first_name` (`first_name`),
  KEY `idx_student_history_last_name` (`last_name`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.student_history: ~4 rows (approximately)
INSERT INTO `student_history` (`id`, `student_id`, `name`, `first_name`, `middle_name`, `last_name`, `course`, `contact`, `guardian_name`, `address`, `profile_picture`, `signature`, `barcode`, `received_date`, `academic_year`, `semester`) VALUES
	(51, '21000602200', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', 'i35.png', '21000602400_signature.png', '21000602400.png', '2025-06-06 16:07:42', '2025-2026', 1),
	(52, '21000602451', 'Harvey P. Perater', 'Harvey', 'P.', 'Perater', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-4 Lumbocan, Butuan City', 'i21.png', '21000602401_signature.png', '21000602401.png', '2025-06-07 12:27:28', '2025-2026', 1),
	(53, '21000602415', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', 'i35.png', '21000602400_signature.png', '21000602400.png', '2025-06-07 12:28:29', '2025-2026', 1),
	(54, '21000602409', 'Darwin K. Villaro', 'Darwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', 'i6.png', '21000602409_signature.png', '21000602409.png', '2025-06-08 11:57:53', '2025-2026', 1);

-- Dumping structure for table studentid.support_messages
CREATE TABLE IF NOT EXISTS `support_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `status` enum('pending','in_progress','resolved') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'pending',
  `admin_response` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `is_seen` tinyint(1) DEFAULT '0',
  `auto_reply` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`),
  KEY `fk_support_student` (`student_id`),
  CONSTRAINT `fk_support_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_messages: ~2 rows (approximately)
INSERT INTO `support_messages` (`id`, `student_id`, `subject`, `message`, `status`, `admin_response`, `created_at`, `updated_at`, `is_seen`, `auto_reply`) VALUES
	(23, '21000602401', 'aa', 'aa', 'in_progress', NULL, '2025-06-07 03:13:44', '2025-06-07 12:44:53', 0, 'Thank you for your message. Our support team will review your inquiry and respond as soon as possible. Please check back later for updates.'),
	(25, '21000602409', 'Technical Issue', 'I\'m experiencing a technical issue with...', 'in_progress', NULL, '2025-06-08 07:12:55', '2025-06-08 07:17:02', 0, 'Thank you for your inquiry about student IDs. Your ID application status can be checked in your dashboard. If you\'re experiencing issues with your ID, please provide more details so we can assist you better.');

-- Dumping structure for table studentid.support_message_history
CREATE TABLE IF NOT EXISTS `support_message_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` int NOT NULL,
  `response_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `responder_role` enum('student','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `response` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_seen` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_history_message` (`message_id`),
  CONSTRAINT `fk_history_message` FOREIGN KEY (`message_id`) REFERENCES `support_messages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=186 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_message_history: ~6 rows (approximately)
INSERT INTO `support_message_history` (`id`, `message_id`, `response_by`, `responder_role`, `response`, `created_at`, `is_seen`) VALUES
	(178, 23, 'ADMIN_97', 'admin', 'lk;lk', '2025-06-07 04:34:54', 0),
	(179, 23, 'ADMIN_97', 'admin', 'sasasasa', '2025-06-07 04:43:54', 0),
	(180, 23, 'ADMIN_97', 'admin', 's\r\n', '2025-06-07 12:25:03', 0),
	(181, 23, '21000602401', 'student', 'a', '2025-06-07 12:25:33', 0),
	(182, 23, '21000602401', 'student', 'Hi sir\r\n', '2025-06-07 12:44:53', 0),
	(184, 25, 'ADMIN_97', 'admin', 'about sa?\r\n', '2025-06-08 07:16:21', 0),
	(185, 25, '21000602409', 'student', 'My face in the ID is not gwapo', '2025-06-08 07:17:02', 0);

-- Dumping structure for table studentid.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `middle_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `role` enum('student','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'student',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT '0',
  `verification_token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `student_id_2` (`student_id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.users: ~4 rows (approximately)
INSERT INTO `users` (`id`, `student_id`, `name`, `first_name`, `middle_name`, `last_name`, `password`, `role`, `email`, `is_verified`, `verification_token`, `created_at`) VALUES
	(95, '21000602410', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'pbkdf2:sha256:600000$xgcMC0HH89XFiwV7$e02e78161eaf2853c18f437d08617be26587f366c5aca4c8c63c7b6cb85e8f1c', 'student', 'zaewin.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-06-06 08:43:58'),
	(97, 'admin001', 'Admin User', 'Admin', NULL, 'User', 'scrypt:32768:8:1$3gmDQCDyhijiMdn4$c812f2cc2e0b8e7733090ecdf81b9576782af57ab517a7519eb2ba9d416da9fefbc5e4eeffc48249936d4473e1b1c9d7ae1f049b876bb8b14cc6165426d0cc19', 'admin', NULL, 0, NULL, '2025-06-06 16:04:36'),
	(98, '21000602001', 'Harvey P. Perater', 'Harvey', 'P.', 'Perater', 'pbkdf2:sha256:600000$4J5Ki7hgmUw6Q3mN$c6f648ad8b400e92d5c05b405e3f24d686c9a2b161536f04d5bbb0b004f72a17', 'student', 'zarwion.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-06-06 18:51:46'),
	(99, '21000602409', 'Darwin K. Villaro', 'Darwin', 'K.', 'Villaro', 'pbkdf2:sha256:600000$BLZvYvumJxS6xvWX$f74e7c7185c7ddb6b8ecb97f80c59d0ca4c2d75ddc309ced48bbfb1d5c866537', 'student', 'zarwin.villsaro@aclcbutuan.edu.ph', 1, NULL, '2025-06-07 09:01:27'),
	(100, '21000602400', 'Charnelyn Maria E. Estalion', 'Charnelyn', 'Maria E.', 'Estalion', 'pbkdf2:sha256:600000$iMYgkmsugyXa8y7H$41ce56a937834c4fba2ce6cff5521191c8880addbceac65e3cd0566a88144176', 'student', 'zarwin.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-06-08 05:05:39');

-- Dumping structure for trigger studentid.sync_user_names_on_student_insert
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `sync_user_names_on_student_insert` AFTER INSERT ON `students` FOR EACH ROW BEGIN
    UPDATE users 
    SET 
        name = NEW.name,
        first_name = NEW.first_name,
        middle_name = NEW.middle_name,
        last_name = NEW.last_name
    WHERE student_id = NEW.student_id AND role = 'student';
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Dumping structure for trigger studentid.sync_user_names_on_student_update
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `sync_user_names_on_student_update` AFTER UPDATE ON `students` FOR EACH ROW BEGIN
    IF (OLD.name != NEW.name OR 
        OLD.first_name != NEW.first_name OR 
        OLD.middle_name != NEW.middle_name OR 
        OLD.last_name != NEW.last_name) THEN
        
        UPDATE users 
        SET 
            name = NEW.name,
            first_name = NEW.first_name,
            middle_name = NEW.middle_name,
            last_name = NEW.last_name
        WHERE student_id = NEW.student_id AND role = 'student';
    END IF;
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
