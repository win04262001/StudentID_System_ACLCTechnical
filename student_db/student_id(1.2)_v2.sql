-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 26, 2025 at 03:59 AM
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
(32, '21000602400', 'zarwin', 'BSIT', '09510238720', 'Eleazar Villaro', 'puajak', '21000602400.png', 'ID_face_.png', NULL, 'receive', 'IMG_20250220_110544.jpg'),
(33, '21000246000', 'Mark', 'BSIT', '09510238720', 'Daryll Bajao', 'hahash', '21000246000.png', '364611658_2167526846775107_4682785096370128021_n.jpg', NULL, 'receive', 'IMG_20250220_110544.jpg'),
(34, '21000602100', 'harvey perater', 'BSCS', '09510238720', NULL, 'hvjh', '21000602100.png', 'istockphoto-1176772006-1024x1024.jpg', NULL, 'receive', 'Screenshot_2025-02-24_121707.png'),
(35, '21000602200', 'jayson amper', 'BSIT', '09510238720', NULL, 'hjhvjhv', '21000602200.png', '364611658_2167526846775107_4682785096370128021_n.jpg', NULL, 'done', 'Screenshot_2025-02-24_121707.png'),
(36, '21000602300', 'wawang', 'BSIT', '09510238720', NULL, 'asdas', '21000602300.png', 'istockphoto-1176772006-1024x1024.jpg', NULL, 'done', 'Screenshot_2025-02-24_121707.png'),
(37, '21000602500', 'carl', 'BSIT', '09287300', 'Zarwin K. Villaro', 'dada', '21000602500.png', 'istockphoto-1176772006-1024x1024.jpg', NULL, 'receive', 'Screenshot_2025-02-24_121707.png'),
(38, '22000602400', 'zarwin', 'BSIT', '09463293862', 'Zarwin K. Villaro', 'dasd', '22000602400.png', '240_F_490754831_vpBty3FR8AJnnkcpHkqsPbYZTAdcHw0e.jpg', NULL, 'receive', '240_F_167891246_T1ZQmA94SwkXF2iUW0kGPbyDbKFybOnu.jpg'),
(39, '22000598400', 'earl james yonson', 'BSIT', '0076835694', 'john cocon', 'p-4 lumbocan', '22000598400.png', '240_F_214746128_31JkeaP6rU0NzzzdFC4khGkmqc8noe6h.jpg', NULL, 'processing', '240_F_167891246_T1ZQmA94SwkXF2iUW0kGPbyDbKFybOnu.jpg'),
(40, '21000607000', 'Nole M tangere', 'BSIT', '09510238720', 'Daryll Bajao', 'adadads', '21000607000.png', '240_F_518645134_N68vzf6CpP0JuK8nvrHtmmOr54bjQ6jO.jpg', NULL, 'pending', '240_F_266276069_Di60G7vQI2sgbTbknticYJLYid5uJgKM.jpg');

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
(14, '21000602400', 'zarwin', 'BSIT', '09510238720', 'Eleazar Villaro', 'puajak', 'ID_face_.png', 'IMG_20250220_110544.jpg', '21000602400.png', '2025-02-23 09:02:15'),
(15, '21000246000', 'Mark', 'BSIT', '09510238720', 'Daryll Bajao', 'hahash', '364611658_2167526846775107_4682785096370128021_n.jpg', 'IMG_20250220_110544.jpg', '21000246000.png', '2025-02-24 00:24:27'),
(16, '21000602100', 'harvey perater', 'BSCS', '09510238720', NULL, 'hvjh', 'istockphoto-1176772006-1024x1024.jpg', 'Screenshot_2025-02-24_121707.png', '21000602100.png', '2025-02-24 04:45:39'),
(17, '21000602300', 'wawang', 'BSIT', '09510238720', NULL, 'asdas', 'istockphoto-1176772006-1024x1024.jpg', 'Screenshot_2025-02-24_121707.png', '21000602300.png', '2025-02-24 09:37:47'),
(18, '21000602500', 'carl', 'BSIT', '09287300', 'Zarwin K. Villaro', 'dada', 'istockphoto-1176772006-1024x1024.jpg', 'Screenshot_2025-02-24_121707.png', '21000602500.png', '2025-02-24 09:54:25'),
(19, '22000602400', 'zarwin', 'BSIT', '09463293862', 'Zarwin K. Villaro', 'dasd', '240_F_490754831_vpBty3FR8AJnnkcpHkqsPbYZTAdcHw0e.jpg', '240_F_167891246_T1ZQmA94SwkXF2iUW0kGPbyDbKFybOnu.jpg', '22000602400.png', '2025-02-25 11:18:03');

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
(37, '21000602400', 'zarwin', 'scrypt:32768:8:1$EtVvW2omiZIqAFwo$3df73ea06fa5c2370566ef3fafde428d753deea1c41c7674ddbdd5b621381da0489ee714175238f53f6f7089ddd804471a12f6b1082fd9b6e9252b3e1a374da1', 'student'),
(38, '21000246000', 'Mark', 'scrypt:32768:8:1$2Px8FiRjkIITMdoA$bea588bc74957d4ffa72cac0db29459e0ee7951d8e9bc5da4d4e3f74f5d70d7c69b74cdfca8cc6f37d1e1b63d0b0d67ec6ff993d6912422c4cbbc05c148bb2bf', 'student'),
(39, '21000602100', 'harvey perater', 'scrypt:32768:8:1$OKy0TlEJrnYhbv7T$7e5eaa206cd36cbc24e2b6b0ae70aa87a26ed2677b1b3e95c912cd0dcd65c45607c2aa766b12f62bdfbdce6ac791b223d476028c70a511fe50697a88f88b8452', 'student'),
(40, '21000602200', 'jayson amper', 'scrypt:32768:8:1$XOFd6EwqushGpiUv$80c897fc5410f266cb0df2a427dd17ec9e0a2ee8deed4b230fa6d11081020903bc77c6e66cb5b858aae2a0fba51814594e5e2176661b1201f4124048ef146194', 'student'),
(41, '21000602300', 'wawang', 'scrypt:32768:8:1$sEer7sLY8uaLMY3i$9c1a5a8c747f7fcc6bdad8031028bd7ac63c7314d54bc3cde684464b9946dbb56eb38dc3ceced44af581a788205d730b412f036f9bf590a106af26a48a97af19', 'student'),
(42, '21000602500', 'carl', 'scrypt:32768:8:1$SctemDdmGLjf7KG2$e7baa6b3d53038c2d1e9c0d97cf8ba324353e9fb36cc2f5c5a01396fe25fb2dced00524f61d71aa3d7832f86f621a95a85de336339e10c38fe6fdecc91c7716a', 'student'),
(43, '22000602400', 'zarwin', 'scrypt:32768:8:1$hb5nzBp5Z3Tdj7XM$912a76ee15ed98de11f1451ab6872e126a678f95a9921a5d5a570275d0deafb43934413738c30e4defc0e66f680d745f89776b35e1e6b5cd81a3db0484f50996', 'student'),
(44, '22000598400', 'earl james', 'scrypt:32768:8:1$UMEOaZdyrkg9lL46$b4ab861ca04d29ebf4f8ce518ce4739bb339f21d8a1682233b4d171c54dbabf60b23a2799c8440eb59544dc7b19b09416da0cf1545de145a8a7c6a10d899358d', 'student'),
(45, '21000607000', 'charnelyn estal', 'scrypt:32768:8:1$PK5wKEMHDDJw6Cjk$a73ee315eb4ad706d89636d86aaa744a625a96ddb811efe750402f0fad4d74dd7cbb7c4a5c222489af7132a61b81a929db0ee5b8d4175ab15b16055797bbf415', 'student');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT for table `student_history`
--
ALTER TABLE `student_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

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
