

-- Drop existing `students` table if it exists
DROP TABLE IF EXISTS students;

-- Create the `students` table with the correct structure
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(11) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(100),
    contact VARCHAR(15),
    mother_name VARCHAR(100),
    address VARCHAR(255),
    barcode TEXT,
    profile_picture VARCHAR(255),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    application_status ENUM('pending', 'processing', 'approved', 'rejected') DEFAULT 'pending'
);

-- Drop existing `users` table if it exists
DROP TABLE IF EXISTS users;

-- Create the `users` table with the correct structure
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(11) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') DEFAULT 'student'
);

-- Insert a default admin account
INSERT INTO users (name, email, password, role, student_id) 
VALUES ('Admin User', 'admin@example.com', 'hashed_password_here', 'admin', '00000000000')
ON DUPLICATE KEY UPDATE email=email;

