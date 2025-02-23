-- Drop existing tables if they exist
DROP TABLE IF EXISTS `car_rentals`;
DROP TABLE IF EXISTS `cars`;
DROP TABLE IF EXISTS `users`;

-- Create Users Table
CREATE TABLE `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'client') DEFAULT 'client'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Cars Table
CREATE TABLE `cars` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `model` VARCHAR(255) NOT NULL,
  `year` INT NOT NULL,
  `status` ENUM('available', 'rented') DEFAULT 'available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Car Rentals Table
CREATE TABLE `car_rentals` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `car_id` INT NOT NULL,
  `pickup_date` DATE NOT NULL,
  `return_date` DATE NOT NULL,
  `qr_code` VARCHAR(255),
  `status` ENUM('pending', 'approved', 'picked_up', 'returned', 'rejected') DEFAULT 'pending',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`car_id`) REFERENCES `cars`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Admin User
INSERT INTO `users` (`name`, `email`, `password`, `role`) VALUES
('Admin', 'admin@gmail.com', '$2b$12$examplepasswordhash', 'admin');

-- Insert Sample Cars
INSERT INTO `cars` (`name`, `model`, `year`, `status`) VALUES
('Toyota Corolla', 'Sedan', 2020, 'available'),
('Honda Civic', 'Sedan', 2021, 'available'),
('Ford Mustang', 'Sports', 2022, 'available');

-- Insert Sample Rentals (for Testing)
INSERT INTO `car_rentals` (`user_id`, `car_id`, `pickup_date`, `return_date`, `qr_code`, `status`) VALUES
(1, 1, '2025-02-20', '2025-02-25', 'sampleQR1', 'pending'),
(1, 2, '2025-02-21', '2025-02-26', 'sampleQR2', 'approved'),
(1, 3, '2025-02-22', '2025-02-27', 'sampleQR3', 'picked_up');
