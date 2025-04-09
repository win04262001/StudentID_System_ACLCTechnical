-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 07, 2025 at 02:37 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `studentid`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_profiles`
--

CREATE TABLE `admin_profiles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `student_id` varchar(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `course` varchar(100) DEFAULT NULL,
  `contact` varchar(15) DEFAULT NULL,
  `guardian_name` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `barcode` text DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `application_status` enum('pending','processing','done','receive') DEFAULT 'pending',
  `signature` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `student_id`, `name`, `course`, `contact`, `guardian_name`, `address`, `barcode`, `profile_picture`, `phone`, `application_status`, `signature`) VALUES
(46, '21000811700', 'jared b. burdeos', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Eleazar Villaro', 'ahahahahahah', '21000811700.png', '240_F_495736434_5MYUmSzmYBo4TRMggQ41gLi8A6BepZJt.jpg', NULL, 'receive', 'signature_21000811700_1742791256.png'),
(47, '21000602500', 'Alejandro Bataluna', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Jeronimo O. Luyahan Sr', 'HAHAHAH', '21000602500.png', '240_F_518645134_N68vzf6CpP0JuK8nvrHtmmOr54bjQ6jO.jpg', NULL, 'receive', '21000602500_signature.png'),
(48, '21000637900', 'chacha', 'BS in INFORMATION TECHNOLOGY', '84923842983', 'Jeronimo O. Luyahan Sr', 's', '21000637900.png', '240_F_490754831_vpBty3FR8AJnnkcpHkqsPbYZTAdcHw0e.jpg', NULL, 'receive', '21000637900_signature.png'),
(49, '22001044200', 'Donald Thrump', NULL, NULL, NULL, NULL, '22001044200.png', NULL, NULL, 'receive', NULL),
(52, '18000402560', 'Daryll Cabagay', NULL, NULL, NULL, NULL, '18000402560.png', NULL, NULL, 'pending', '18000402560_signature.png'),
(53, '21000607072', 'Lord Ian', 'BS in INFORMATION TECHNOLOGY', '09504274037', 'Jeronimo O. Luyahan Sr', 'dasdasdaa', '21000607072.png', 'worldface-japanese-guy-white-background_53876-31202_-_Copy.jpg', NULL, 'pending', '21000607072_signature.png');

-- --------------------------------------------------------

--
-- Table structure for table `student_history`
--

CREATE TABLE `student_history` (
  `id` int(11) NOT NULL,
  `student_id` varchar(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `course` varchar(100) DEFAULT NULL,
  `contact` varchar(15) DEFAULT NULL,
  `guardian_name` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `signature` varchar(255) DEFAULT NULL,
  `barcode` varchar(255) DEFAULT NULL,
  `received_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `student_history`
--

INSERT INTO `student_history` (`id`, `student_id`, `name`, `course`, `contact`, `guardian_name`, `address`, `profile_picture`, `signature`, `barcode`, `received_date`) VALUES
(35, '21000606060', 'Zoren Bataluna', 'BS in INFORMATION TECHNOLOGY', '84923842983', 'Jeronimo O. Luyahan Sr', 'lll', 'close-up-saleswoman_13339-30976.webp', '21000606060_signature.png', '21000606060.png', '2025-04-05 14:32:16'),
(36, '21000607072', 'jeronimo Luyahan', 'BS in INFORMATION TECHNOLOGY', '84923842983', 'Jeronimo O. Luyahan Sr', 'hghhf', 'istockphoto-877022826-612x612_-_Copy.jpg', '21000607072_signature.png', '21000607072.png', '2025-04-06 03:52:30');

-- --------------------------------------------------------

--
-- Table structure for table `support_messages`
--

CREATE TABLE `support_messages` (
  `id` int(11) NOT NULL,
  `student_id` varchar(11) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `status` enum('pending','in_progress','resolved') DEFAULT 'pending',
  `admin_response` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `support_messages`
--

INSERT INTO `support_messages` (`id`, `student_id`, `subject`, `message`, `status`, `admin_response`, `created_at`, `updated_at`) VALUES
(1, '21000607072', 'Hi', 'HUHUH', 'in_progress', 'hu', '2025-04-06 04:30:27', '2025-04-07 12:35:26'),
(2, '21000607072', 'PAGSASALING PAMPANITIKAN', 'hi', 'resolved', 'Done', '2025-04-06 05:06:38', '2025-04-06 05:10:33');

-- --------------------------------------------------------

--
-- Table structure for table `support_message_history`
--

CREATE TABLE `support_message_history` (
  `id` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `response_by` varchar(11) NOT NULL,
  `response` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `support_message_history`
--

INSERT INTO `support_message_history` (`id`, `message_id`, `response_by`, `response`, `created_at`) VALUES
(1, 1, 'ADMIN_17', 'What happen?', '2025-04-06 05:05:29'),
(2, 2, 'ADMIN_17', 'HElloo', '2025-04-06 05:07:33'),
(3, 2, 'ADMIN_17', 'Done', '2025-04-06 05:10:33'),
(4, 1, '21000607072', 'Hi sir please help me', '2025-04-07 12:24:03'),
(5, 1, 'ADMIN_17', 'what happen?', '2025-04-07 12:24:48'),
(6, 1, '21000607072', 'Hi sir', '2025-04-07 12:32:01'),
(7, 1, 'ADMIN_17', 'What happen to you?\r\n', '2025-04-07 12:32:35'),
(8, 1, 'ADMIN_17', 'Hello', '2025-04-07 12:34:27'),
(9, 1, 'ADMIN_17', 'hu', '2025-04-07 12:35:26');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `student_id` varchar(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','admin') NOT NULL DEFAULT 'student'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `student_id`, `name`, `password`, `role`) VALUES
(17, 'admin001', 'Admin User', 'scrypt:32768:8:1$3gmDQCDyhijiMdn4$c812f2cc2e0b8e7733090ecdf81b9576782af57ab517a7519eb2ba9d416da9fefbc5e4eeffc48249936d4473e1b1c9d7ae1f049b876bb8b14cc6165426d0cc19', 'admin'),
(51, '21000811700', 'jared b. burdeos', 'scrypt:32768:8:1$GlJrpRfZKuZ4SNeq$3d1722f1ecbf316c87e57e2e8d6018e0688e5b48e1f1239257affba2007932efe0468ad0dea3d8a1c5be2f9befe2185b99ce9b51c7184162fe0fc57c18368727', 'student'),
(52, '21000602500', 'Alejandro Bataluna', 'scrypt:32768:8:1$b9jLxcC5Y7HLa1N5$79ad45d12f870700fbe691b81bf727f49bba08429bc4d8c02e5eb7d1a5bfdac1ab7b2fa0e48dfa37cfd63635ab780946666f54426583ea6e78c81788d8e519ec', 'student'),
(53, '21000637900', 'chacha', 'pbkdf2:sha256:600000$O22QFRFbAeakCmbx$4e56e961323902d42ff5987ff3f2955417b02e124cf669d69608ae322ec3d443', 'student'),
(54, '22001044200', 'Donald Thrump', 'pbkdf2:sha256:600000$YXDcVGK82gd7xpMK$4bb162d806519399a9b092c13e5155da3405dd40f0321439e9d2c9373e707525', 'student'),
(57, '18000402560', 'Daryll Cabagay', 'pbkdf2:sha256:600000$ki46SePljw2KiTUu$1a86c93a0a63b396d83ac8200fbf4e7b22b52ea91c5b74df355ebd0073465c08', 'student'),
(58, '21000607072', 'jeronimo Luyahan', 'pbkdf2:sha256:600000$BjflEhCT90OSXhN6$c22ce0e2a2a55a895cf77fbb29dd8f014a5a7a62f184d5ef68cc4e54201a11d9', 'student');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_profiles`
--
ALTER TABLE `admin_profiles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD UNIQUE KEY `student_id_2` (`student_id`),
  ADD UNIQUE KEY `student_id_3` (`student_id`);

--
-- Indexes for table `student_history`
--
ALTER TABLE `student_history`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `support_messages`
--
ALTER TABLE `support_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_support_student` (`student_id`);

--
-- Indexes for table `support_message_history`
--
ALTER TABLE `support_message_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_history_message` (`message_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD UNIQUE KEY `student_id_2` (`student_id`),
  ADD KEY `idx_student_id` (`student_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_profiles`
--
ALTER TABLE `admin_profiles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT for table `student_history`
--
ALTER TABLE `student_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `support_messages`
--
ALTER TABLE `support_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `support_message_history`
--
ALTER TABLE `support_message_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin_profiles`
--
ALTER TABLE `admin_profiles`
  ADD CONSTRAINT `fk_admin_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `fk_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`student_id`) ON DELETE CASCADE;

--
-- Constraints for table `support_messages`
--
ALTER TABLE `support_messages`
  ADD CONSTRAINT `fk_support_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`student_id`) ON DELETE CASCADE;

--
-- Constraints for table `support_message_history`
--
ALTER TABLE `support_message_history`
  ADD CONSTRAINT `fk_history_message` FOREIGN KEY (`message_id`) REFERENCES `support_messages` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
