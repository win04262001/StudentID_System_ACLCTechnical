-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 13, 2025 at 04:03 AM
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
-- Database: `appointment_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `appointment_date` date DEFAULT NULL,
  `qr_code` varchar(255) DEFAULT NULL,
  `check_in_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`id`, `user_id`, `name`, `appointment_date`, `qr_code`, `check_in_time`) VALUES
(2, 0, 'Test User', '2025-02-21', 'Test User-2025-02-21', NULL),
(11, 0, 'jared', '2025-02-13', 'jared-2025-02-13', NULL),
(14, 0, 'zarwin', '2025-02-21', 'zarwin-2025-02-21', NULL),
(16, 0, 'cha', '2025-02-13', 'cha-2025-02-13', NULL),
(18, 5, 'zarwin', '2025-02-13', 'zarwin-2025-02-13', NULL),
(19, 6, 'Nole M tangere', '2025-02-14', 'Nole M tangere-2025-02-14', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('client','admin') NOT NULL DEFAULT 'client'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`) VALUES
(1, 'user1', 'user1@gmail.com', 'scrypt:32768:8:1$WqQkIXA019PAF51T$90c8ae7f6d06212b90fd30937e0f3ad63d2187da567ec9d63f556bde61d5911bd41751b68e6b06631172ab5ba797bb4398d1f8e7b53e1f458c6ed0a619df8169', 'client'),
(2, 'admin', 'admin@gmail.com', 'scrypt:32768:8:1$tLff1rkwE5jg3XUs$a6088e13214286d05679944073de7b02dfb1779de570b79ba3daaddfa4feae3bc53d4b77734af99b724d6001d83d48042e86bf2720ec9d7e140a7fe3c06ace10', 'admin'),
(3, 'cha', 'cha@gmail.com', 'scrypt:32768:8:1$e309yWN69EcUkXYj$712f31084b4e02ba7494b6b17efaa25799c0774ebdb2d95e83f93462bbf735ee9f2381b0f714504f085e56de25169fca571a15b0eb2ee8ab96c83f0d48bca6ff', 'client'),
(5, 'chacha', 'chacha@gmail.com', 'scrypt:32768:8:1$AgYkJ25kvvucx1Qy$a2fb51cdcbb70beb63fef0a544b3488ba8e66b97f3c9ef6988e6f116b498348706ff8d4a40c81593c92294e78ca3ef24dd8464b48a25655f3e52bdf258558e7c', 'client'),
(6, 'harvey', 'harvey@gmail.com', 'scrypt:32768:8:1$3jhReLv1skw3lbnH$94973f035ee9b4066c0017d00f25b46b06ef0bc7b7e724450206206f3a500a30c4f8a1631cebef3dda7568369a2149b5520160047a46a68b51f67805951b112d', 'client');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `qr_code` (`qr_code`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
