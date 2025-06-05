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
  `email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
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
  UNIQUE KEY `student_id_3` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.students: ~7 rows (approximately)
INSERT INTO `students` (`id`, `student_id`, `email`, `name`, `course`, `contact`, `guardian_name`, `address`, `barcode`, `profile_picture`, `phone`, `application_status`, `signature`) VALUES
	(58, '22000444000', NULL, 'Ruperto Bernales', 'BSBA-Financial Management', '09504274037', 'Marian Bernales', 'P-8B Ambago,Butuan City', '22000444000.png', 'ID_face_.png', NULL, 'receive', '22000444000_signature.png'),
	(60, '21001282200', NULL, 'Devine Grace G. Pacaña', 'BS in INFORMATION TECHNOLOGY', '09916090143', 'Rolando A. Pacaña', 'P-3A Taligaman Butuan City ', '21001282200.png', '1000006864.png', NULL, 'receive', '21001282200_signature.png'),
	(82, '21000362701', 'zarwinc.villaro@aclcbutuan.edu.ph', 'Zarwin Villaro', 'BS in INFORMATION TECHNOLOGY', '09916090141', 'Matherland', 'Pojjjs', '21000362700.png', 'i2.png', NULL, 'receive', '21000362700_signature.png'),
	(85, '21000602610', 'zarwinn.villaro@aclcbutuan.edu.ph', 'Zarwin K. Villaro', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Jeronimo O. Luyahan Sr', 'butuan city', '21000602600.png', 'i9.png', NULL, 'receive', '21000602600_signature.png'),
	(86, '17007146000', 'gino.abatayo@aclcbutuan.edu.ph', 'Gino Abatayo', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Jeronimo O. Luyahan Sr', 'butuan city', '17007146000.png', 'i4.png', NULL, 'receive', '17007146000_signature.png'),
	(87, '21000602400', 'zarwin.villaro@aclcbutuan.edu.ph', 'Zarwin K. Villaro', 'BS in INFORMATION TECHNOLOGY', '09467406702', 'Eleazar Villaro', 'butuan city', '21000602400.png', 'i6.png', NULL, 'done', '21000602400_signature.png'),
	(88, '12000602400', 'alejandro.bataluna@aclcbutuan.edu.ph', 'Alejandro Bataluna', 'BS in INFORMATION TECHNOLOGY', '09510238727', 'Jerome Bataluna', 'butuan city', '12000602400.png', 'i10.png', NULL, 'done', '12000602400_signature.png');

-- Dumping structure for table studentid.student_history
CREATE TABLE IF NOT EXISTS `student_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `course` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contact` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `guardian_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `profile_picture` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `signature` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `barcode` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `received_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.student_history: ~5 rows (approximately)
INSERT INTO `student_history` (`id`, `student_id`, `name`, `course`, `contact`, `guardian_name`, `address`, `profile_picture`, `signature`, `barcode`, `received_date`) VALUES
	(39, '21001282200', 'Devine Grace G. Pacaña', 'BS in INFORMATION TECHNOLOGY', '09916090143', 'Rolando A. Pacaña', 'P-3A Taligaman Butuan City ', '1000006864.png', '21001282200_signature.png', '21001282200.png', '2025-05-05 01:08:36'),
	(41, '17007146000', 'Gino Abatayo', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Jeronimo O. Luyahan Sr', 'butuan city', 'i4.png', '17007146000_signature.png', '17007146000.png', '2025-05-29 09:59:58'),
	(42, '21000362701', 'Zarwin Villaro', 'BS in INFORMATION TECHNOLOGY', '09916090141', 'Matherland', 'Pojjjs', 'i2.png', '21000362700_signature.png', '21000362700.png', '2025-05-29 14:51:08'),
	(43, '22000444000', 'Ruperto Bernales', 'BSBA-Financial Management', '09504274037', 'Marian Bernales', 'P-8B Ambago,Butuan City', 'ID_face_.png', '22000444000_signature.png', '22000444000.png', '2025-05-29 14:51:16'),
	(44, '21000602610', 'Zarwin K. Villaro', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Jeronimo O. Luyahan Sr', 'butuan city', 'i9.png', '21000602600_signature.png', '21000602600.png', '2025-05-29 14:51:29');

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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_messages: ~2 rows (approximately)
INSERT INTO `support_messages` (`id`, `student_id`, `subject`, `message`, `status`, `admin_response`, `created_at`, `updated_at`, `is_seen`, `auto_reply`) VALUES
	(14, '22000444000', 'Update', 'Hi sir maki update lang ko', 'in_progress', NULL, '2025-04-20 13:20:04', '2025-04-20 15:03:14', 0, 'Thank you for requesting an update. Our team will review your inquiry and provide you with the latest information as soon as possible. For faster assistance, please specify which matter you need an update on.'),
	(19, '17007146000', 'sasasa', 'sasa', 'pending', NULL, '2025-05-26 12:25:43', NULL, 0, NULL),
	(20, '21000602600', 'ID status update', 'Update', 'in_progress', NULL, '2025-05-26 14:25:53', '2025-05-29 15:02:00', 0, 'Thank you for your inquiry about student IDs. Your ID application status can be checked in your dashboard. If you\'re experiencing issues with your ID, please provide more details so we can assist you better.');

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
) ENGINE=InnoDB AUTO_INCREMENT=176 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.support_message_history: ~41 rows (approximately)
INSERT INTO `support_message_history` (`id`, `message_id`, `response_by`, `responder_role`, `response`, `created_at`, `is_seen`) VALUES
	(132, 14, '22000444000', 'student', 'Update lang ko sir', '2025-04-20 13:20:31', 1),
	(133, 14, 'ADMIN_17', 'admin', 'about sa?\r\n', '2025-04-20 13:20:43', 0),
	(134, 14, 'ADMIN_17', 'admin', 'sa?\r\n', '2025-04-20 13:22:02', 0),
	(135, 14, '22000444000', 'student', 'Sir', '2025-04-20 13:25:24', 1),
	(136, 14, 'ADMIN_17', 'admin', 'yes don?', '2025-04-20 13:25:44', 0),
	(137, 14, 'ADMIN_17', 'admin', 'hahahaha', '2025-04-20 13:28:04', 0),
	(138, 14, '22000444000', 'student', 'Katawa man ka kol?', '2025-04-20 13:28:55', 1),
	(139, 14, 'ADMIN_17', 'admin', 'bawal dong?', '2025-04-20 13:29:18', 0),
	(140, 14, '22000444000', 'student', 'Wala kay buot kol', '2025-04-20 13:30:39', 0),
	(141, 14, 'ADMIN_17', 'admin', 'ali be kay bagon ulo\r\n', '2025-04-20 13:31:00', 0),
	(142, 14, 'ADMIN_17', 'admin', 'hahaha', '2025-04-20 13:32:17', 0),
	(143, 14, '22000444000', 'student', 'Yawa jd ka ba', '2025-04-20 13:32:59', 0),
	(144, 14, 'ADMIN_17', 'admin', 'bahoo', '2025-04-20 13:33:26', 0),
	(145, 14, 'ADMIN_17', 'admin', 'gdfgdfgd', '2025-04-20 13:36:08', 0),
	(147, 14, '22000444000', 'student', 'Send', '2025-04-20 13:41:44', 0),
	(150, 14, 'ADMIN_17', 'admin', 'fsfsfsfsdf', '2025-04-20 13:50:20', 0),
	(152, 14, 'ADMIN_17', 'admin', 'fsdfsss', '2025-04-20 15:03:08', 0),
	(153, 14, 'ADMIN_17', 'admin', 'fsfstertrhyjyuuy', '2025-04-20 15:03:14', 0),
	(174, 20, '21000602600', 'student', 'Update', '2025-05-26 14:26:03', 0),
	(175, 20, 'ADMIN_17', 'admin', 'sasasa', '2025-05-29 15:02:00', 0);

-- Dumping structure for table studentid.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `role` enum('student','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'student',
  `email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT '0',
  `verification_token` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `student_id_2` (`student_id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table studentid.users: ~7 rows (approximately)
INSERT INTO `users` (`id`, `student_id`, `name`, `password`, `role`, `email`, `is_verified`, `verification_token`, `created_at`) VALUES
	(17, 'admin001', 'Admin User', 'scrypt:32768:8:1$3gmDQCDyhijiMdn4$c812f2cc2e0b8e7733090ecdf81b9576782af57ab517a7519eb2ba9d416da9fefbc5e4eeffc48249936d4473e1b1c9d7ae1f049b876bb8b14cc6165426d0cc19', 'admin', NULL, 0, NULL, '2025-05-25 01:41:28'),
	(63, '22000444000', 'Ruperto Bernales', 'pbkdf2:sha256:600000$4HCMPcEyq15K2SiA$2da1f494f75c6810746a4d79c930f0c1fea01f6bf006494e1efe5f78958466a4', 'student', NULL, 0, NULL, '2025-05-25 01:41:28'),
	(65, '21001282200', 'Devine Grace G. Pacaña', 'pbkdf2:sha256:600000$FCAlkEgt8r2jnWZQ$6b0ba2504810957c7e2154df0f18b61a6745b3aef0b95f9eb3d481f498c8eb49', 'student', NULL, 0, NULL, '2025-05-25 01:41:28'),
	(87, '21000602600', NULL, 'pbkdf2:sha256:600000$s96QdXmu2rTkdBAz$e7ba5c64db61a436fd458740820d99bebe6e4cd66b3edabc6dac6b35e85b1ac8', 'student', 'zarwiin.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-05-25 21:47:09'),
	(88, '17007146000', NULL, 'pbkdf2:sha256:600000$y3reyVQEU0g7SSJO$a495fa5dd96f8aef5e16934c5c9de477c52bb068c5b1c3cf6168fdf992840265', 'student', 'gino.abatayo@aclcbutuan.edu.ph', 1, NULL, '2025-05-26 17:21:16'),
	(89, '21000602400', NULL, 'pbkdf2:sha256:600000$MqRLbZHTlJ5X36ii$be1358118ac48352175bc76c273e2df5400ad4bcd1698c63d57cf97987f6cbe8', 'student', 'zarwin.villaro@aclcbutuan.edu.ph', 1, NULL, '2025-05-29 19:35:38'),
	(90, '12000602400', NULL, 'pbkdf2:sha256:600000$zZmIgPoQb32Spqks$bbedd903b8c4b7ed48d974a4d355c93b9ba9736130c63c2ffd67c2faf88f963d', 'student', 'alejandro.bataluna@aclcbutuan.edu.ph', 1, NULL, '2025-06-03 13:05:08');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
