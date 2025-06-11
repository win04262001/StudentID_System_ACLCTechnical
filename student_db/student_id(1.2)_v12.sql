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
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.students: ~1 rows (approximately)
INSERT INTO `students` (`id`, `student_id`, `email`, `name`, `first_name`, `middle_name`, `last_name`, `course`, `contact`, `guardian_name`, `address`, `barcode`, `profile_picture`, `phone`, `application_status`, `signature`) VALUES
	(93, '21000602410', 'zarwinm.villaro@aclcbutuan.edu.ph', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', '21000602400.png', 'i35.png', NULL, 'receive', '21000602400_signature.png'),
	(94, '21000602401', 'zarwin.villaro@aclcbutuan.edu.ph', 'Harvey P. Perater', 'Harvey', 'P.', 'Perater', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-4 Lumbocan, Butuan City', '21000602401.png', 'i21.png', NULL, 'receive', '21000602401_signature.png');

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
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.student_history: ~3 rows (approximately)
INSERT INTO `student_history` (`id`, `student_id`, `name`, `first_name`, `middle_name`, `last_name`, `course`, `contact`, `guardian_name`, `address`, `profile_picture`, `signature`, `barcode`, `received_date`, `academic_year`, `semester`) VALUES
	(51, '21000602200', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', 'i35.png', '21000602400_signature.png', '21000602400.png', '2025-06-06 16:07:42', '2025-2026', 1),
	(52, '21000602401', 'Harvey P. Perater', 'Harvey', 'P.', 'Perater', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-4 Lumbocan, Butuan City', 'i21.png', '21000602401_signature.png', '21000602401.png', '2025-06-07 12:27:28', '2025-2026', 1),
	(53, '21000602410', 'Zarwin K. Villaro', 'Zarwin', 'K.', 'Villaro', 'BS in INFORMATION TECHNOLOGY', '09510238720', 'Cecelia K. Villaro', 'P-5 Lumbocan, Butuan City', 'i35.png', '21000602400_signature.png', '21000602400.png', '2025-06-07 12:28:29', '2025-2026', 1);

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
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_messages: ~0 rows (approximately)
INSERT INTO `support_messages` (`id`, `student_id`, `subject`, `message`, `status`, `admin_response`, `created_at`, `updated_at`, `is_seen`, `auto_reply`) VALUES
	(23, '21000602401', 'aa', 'aa', 'in_progress', NULL, '2025-06-07 03:13:44', '2025-06-07 12:44:53', 0, 'Thank you for your message. Our support team will review your inquiry and respond as soon as possible. Please check back later for updates.');

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
) ENGINE=InnoDB AUTO_INCREMENT=183 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_message_history: ~22 rows (approximately)
INSERT INTO `support_message_history` (`id`, `message_id`, `response_by`, `responder_role`, `response`, `created_at`, `is_seen`) VALUES
	(178, 23, 'ADMIN_97', 'admin', 'lk;lk', '2025-06-07 04:34:54', 0),
	(179, 23, 'ADMIN_97', 'admin', 'sasasasa', '2025-06-07 04:43:54', 0),
	(180, 23, 'ADMIN_97', 'admin', 's\r\n', '2025-06-07 12:25:03', 0),
	(181, 23, '21000602401', 'student', 'a', '2025-06-07 12:25:33', 0),
	(182, 23, '21000602401', 'student', 'Hi sir\r\n', '2025-06-07 12:44:53', 0);

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
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.users: ~3 rows (approximately)
INSERT INTO `users` (`id`, `student_id`, `name`, `first_name`, `middle_name`, `last_name`, `password`, `role`, `email`, `is_verified`, `verification_token`, `created_at`) VALUES
	(95, '21000602410', NULL, NULL, NULL, NULL, 'pbkdf2:sha256:600000$xgcMC0HH89XFiwV7$e02e78161eaf2853c18f437d08617be26587f366c5aca4c8c63c7b6cb85e8f1c', 'student', 'zaewin.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-06-06 08:43:58'),
	(97, 'admin001', 'Admin User', NULL, NULL, NULL, 'scrypt:32768:8:1$3gmDQCDyhijiMdn4$c812f2cc2e0b8e7733090ecdf81b9576782af57ab517a7519eb2ba9d416da9fefbc5e4eeffc48249936d4473e1b1c9d7ae1f049b876bb8b14cc6165426d0cc19', 'admin', NULL, 0, NULL, '2025-06-06 16:04:36'),
	(98, '21000602401', 'Harvey P. Perater', NULL, NULL, NULL, 'pbkdf2:sha256:600000$4J5Ki7hgmUw6Q3mN$c6f648ad8b400e92d5c05b405e3f24d686c9a2b161536f04d5bbb0b004f72a17', 'student', 'zarwin.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-06-06 18:51:46');

-- Dumping structure for trigger studentid.sync_user_name_on_student_insert
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `sync_user_name_on_student_insert` AFTER INSERT ON `students` FOR EACH ROW BEGIN
    -- Update the corresponding user's name when a new student is inserted
    UPDATE users 
    SET name = NEW.name 
    WHERE student_id = NEW.student_id AND role = 'student';
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Dumping structure for trigger studentid.sync_user_name_on_student_update
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `sync_user_name_on_student_update` AFTER UPDATE ON `students` FOR EACH ROW BEGIN
    -- Update the corresponding user's name when student name changes
    IF OLD.name != NEW.name THEN
        UPDATE users 
        SET name = NEW.name 
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
