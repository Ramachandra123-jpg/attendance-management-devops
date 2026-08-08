-- ============================================================
-- Employee Management System (Python) - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS ems_db;
USE ems_db;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    role          ENUM('ADMIN', 'HR') NOT NULL DEFAULT 'HR',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS departments (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS employees (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    employee_code    VARCHAR(20) NOT NULL UNIQUE,
    first_name       VARCHAR(50) NOT NULL,
    last_name        VARCHAR(50) NOT NULL,
    email            VARCHAR(120) NOT NULL UNIQUE,
    phone            VARCHAR(20),
    department       VARCHAR(100),
    designation      VARCHAR(100),
    date_of_joining  DATE,
    salary           DECIMAL(12,2) DEFAULT 0,
    status           ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    address          VARCHAR(255),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attendance (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    employee_id   INT NOT NULL,
    date          DATE NOT NULL,
    status        ENUM('PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE') NOT NULL DEFAULT 'PRESENT',
    check_in      TIME NULL,
    check_out     TIME NULL,
    remarks       VARCHAR(255),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id)
        REFERENCES employees(id) ON DELETE CASCADE,
    CONSTRAINT uq_employee_date UNIQUE (employee_id, date)
) ENGINE=InnoDB;

-- Default admin login -> username: admin / password: admin123
-- (password_hash = SHA-256 of "admin123", verified correct 64-char hash)
INSERT INTO users (username, password_hash, full_name, role)
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'System Administrator', 'ADMIN')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

INSERT INTO departments (name) VALUES
    ('Human Resources'), ('Engineering'), ('Sales'), ('Marketing'), ('Finance')
ON DUPLICATE KEY UPDATE name = name;

INSERT INTO employees (employee_code, first_name, last_name, email, phone, department, designation, date_of_joining, salary, status, address)
VALUES
 ('EMP001', 'Asha', 'Menon', 'asha.menon@example.com', '9876543210', 'Engineering', 'Software Engineer', '2023-01-15', 65000, 'ACTIVE', 'Kochi, Kerala'),
 ('EMP002', 'Rahul', 'Nair', 'rahul.nair@example.com', '9876543211', 'Sales', 'Sales Executive', '2022-06-01', 45000, 'ACTIVE', 'Trivandrum, Kerala'),
 ('EMP003', 'Priya', 'Iyer', 'priya.iyer@example.com', '9876543212', 'Human Resources', 'HR Manager', '2021-03-10', 72000, 'ACTIVE', 'Kozhikode, Kerala')
ON DUPLICATE KEY UPDATE employee_code = employee_code;
