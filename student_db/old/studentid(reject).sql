-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 22, 2025 at 08:23 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

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
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `student_id` varchar(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `course` varchar(100) DEFAULT NULL,
  `contact` varchar(15) DEFAULT NULL,
  `mother_name` varchar(100) DEFAULT NULL,
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

INSERT INTO `students` (`id`, `student_id`, `name`, `course`, `contact`, `mother_name`, `address`, `barcode`, `profile_picture`, `phone`, `application_status`, `signature`) VALUES
(24, '21000102400', 'charnelyn estal', 'BSCS', '09510238720', 'Eleazar Villaro', 'dadada', NULL, 'PURPLE.jpg', NULL, 'receive', 'IMG_20250220_110544.jpg'),
(25, '21000112400', 'Zarwin K. Villaro', 'BSIT', '09510238720', 'Shakoy Bihag', 'adadad', NULL, 'ID_face_.png', NULL, 'pending', 'IMG_20250220_110544.jpg');

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
(10, '21000102400', 'charnelyn estal', 'BSCS', '09510238720', 'Eleazar Villaro', 'dadada', 'PURPLE.jpg', 'IMG_20250220_110544.jpg', NULL, '2025-02-22 19:05:42');

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
(29, '21000102400', 'charnelyn estal', 'scrypt:32768:8:1$VtUT2TXZAv1PFSpO$adb68cd75263e07ebd6b2c0c6863aa7ea186e771909d699d5b6552a49aa380d9fdd098a16a6d84935eba563232ce5a690980d79c32e151c2ab9ebf6df5894f51', 'student'),
(30, '21000112400', 'Zarwin K. Villaro', 'scrypt:32768:8:1$z6HNWeFBmc80jJzX$ac42552c5f1736a3151086bd3f7ac3348eef0f2eea16fb1e623c1cc0fcc0651934d9b1842b7b369d3dfe18197553fb714ed54a746e617d95f0ef0e8e46512703', 'student');

--
-- Indexes for dumped tables
--

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
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `student_history`
--
ALTER TABLE `student_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `fk_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`student_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
