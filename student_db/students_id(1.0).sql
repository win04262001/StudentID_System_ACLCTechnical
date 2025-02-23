-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 22, 2025 at 07:24 PM
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
(15, '21000602400', 'charnelyn estal', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pending', NULL),
(16, '21000502400', 'charnelyn estal', 'BSCS', '09463293862', 'Zarwin K. Villaro', 'Libertad, Butuan City', NULL, 'PURPLE.jpg', NULL, 'receive', 'IMG_20250220_110544.jpg'),
(17, '18000602400', 'Daryll Cabagay', 'BSCS', '09463293862', 'Juan Cabagay', 'Masao', NULL, 'PngItem_223968.png', NULL, 'receive', 'IMG_20250220_110544.jpg'),
(18, '21000102400', 'Elmer Bihag', 'BSFM', '091010101010', 'Shakoy Bihag', 'Purok 4 Lumbocan, Butun city', NULL, 'istockphoto-1176772006-1024x1024.jpg', NULL, 'processing', 'IMG_20250220_110544.jpg'),
(19, '21000112400', 'Zoren Bajao', 'BSCS', '09510238720', 'Daryll Bajao', 'Purok 10 Masao', NULL, 'istockphoto-1176772006-1024x1024.jpg', NULL, 'receive', 'IMG_20250220_110544.jpg'),
(20, '21000122400', 'Zelmar Obediente', 'BSIT', '091010101010', 'Daryll Bajao', 'adada', NULL, 'PngItem_223968.png', NULL, 'processing', 'IMG_20250220_110544.jpg'),
(21, '21000132400', 'Alejandro Bataluna', 'BSIT', '091010101010', 'Daryll Bataluna', 'sasasa', NULL, '364611658_2167526846775107_4682785096370128021_n.jpg', NULL, 'done', 'charnelyn_estal_ID_History_2.png'),
(22, '21000142400', 'Ian Bajao', 'BSCS', '09510238720', 'Daryll Bajao', 'daa', NULL, 'charnelyn_estal_ID_History_2.png', NULL, 'pending', 'charnelyn_estal_ID_History_2.png');

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
(7, '21000122400', 'Zelmar Obediente', 'BSIT', '091010101010', 'Daryll Bajao', 'adada', 'PngItem_223968.png', 'IMG_20250220_110544.jpg', '21000122400.png', '2025-02-22 16:13:00'),
(8, '21000112400', 'Zoren Bajao', 'BSCS', '09510238720', 'Daryll Bajao', 'Purok 10 Masao', 'istockphoto-1176772006-1024x1024.jpg', 'IMG_20250220_110544.jpg', '21000112400.png', '2025-02-22 16:13:31'),
(9, '21000132400', 'Alejandro Bataluna', 'BSIT', '091010101010', 'Daryll Bataluna', 'sasasa', '364611658_2167526846775107_4682785096370128021_n.jpg', 'charnelyn_estal_ID_History_2.png', '21000132400.png', '2025-02-22 16:42:52');

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
(20, '21000602400', 'charnelyn estal', 'scrypt:32768:8:1$kM8AFqgfBRmf8ytd$26e5123a3f9d48ccbbbe33ce018a2e06f1b906fb35d9e55121c3be3eb3a14466e97771744e658f13ea9fea8d87b1ccda197e9770c6949f2ef8949455a076e076', 'student'),
(21, '21000502400', 'charnelyn estal', 'scrypt:32768:8:1$LtZHAKGdIwvagQ2Q$e78509fb17d23cf3dabe4b3f6fb3f859f80e021036e96990942726d3cd337807c655dca49bbd09f7624c12f42eee41baeb0a692edde8fa4db59cf925a768fd4f', 'student'),
(22, '18000602400', 'Daryll Cabagay', 'scrypt:32768:8:1$MzMj6jKXjVzWYCsz$fbe8804fa03409955e9b45f3ae2f289dae94c9ded3834a1f1a7bc96f23732f0692361f1a9ff880ce6f520b1f63345296c885d989b351fac65291eec30526f361', 'student'),
(23, '21000102400', 'Elmer Bihag', 'scrypt:32768:8:1$AIFTfI71hs4KTEgv$55b8aad5eac93d92ee07fed44bc081a1bc122f7cccaaf3590a4b7f6df002e0308f6bc2ed2cfce68f895593ae1ce8d3bb0ec2bc3eb3dbabdf5cd8f6ebfa2ffb3f', 'student'),
(24, '21000112400', 'Zoren Bajao', 'scrypt:32768:8:1$f2BfTRDPM47GKvcx$ab7e4caab2c16de759cf2fa87bb51e1762f0cc51880fae637d02204e7b34c3f184581a9ae60daa2e7ed040ccc93faa8a11928cf564a7e7fc518faa5937803a7c', 'student'),
(25, '21000122400', 'Zelmar Obediente', 'scrypt:32768:8:1$BVdwlnHx694B0j7v$ad4eec535d04c57e3ec9af6b73dc85362545bf29aa8e4c9bf86deab483a1c4bfc209f73400822174c9103fd3f7c22e0442cbd2799e009db96ba87750c0711e5d', 'student'),
(26, '21000132400', 'Alejandro Bataluna', 'scrypt:32768:8:1$ckucJrtiObBa7ATY$7006f5f14581839acfc1440b778547a5dae5d3c664712583026bf9017b1df51bf54ca0d4d6508f34396c0f770a3d7791c0a2213c77e82a11629858a3d7fff6e7', 'student'),
(27, '21000142400', 'Ian Bajao', 'scrypt:32768:8:1$ADj2lxPlZ0vHYtnX$72b6e61ebb94220493df042be297e86324b615519282150b9ef56ec9eeba455c226a0487d0c3c962499a5708801916b71860bb252310ef947fef3e74ddd31bc7', 'student');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `student_history`
--
ALTER TABLE `student_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

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
