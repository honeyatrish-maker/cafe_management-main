-- Cafe Management System Database Schema

CREATE DATABASE IF NOT EXISTS cafe_management;
USE cafe_management;

-- Users table for admin login
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'staff') DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu items table
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables table for table management
CREATE TABLE tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_number INT UNIQUE NOT NULL,
    capacity INT DEFAULT 4,
    status ENUM('available', 'occupied', 'reserved') DEFAULT 'available'
);

-- Customers table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    table_id INT,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'preparing', 'ready', 'served', 'cancelled') DEFAULT 'pending',
    total_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (table_id) REFERENCES tables(id)
);

-- Order items table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- Payments table
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'card', 'online') DEFAULT 'cash',
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Insert sample data

-- Admin user (password: admin123)
INSERT INTO users (username, password, role) VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6fMJyUq7K6', 'admin');

-- Sample menu items
INSERT INTO menu_items (name, description, price, category) VALUES
('Espresso', 'Strong coffee shot', 3.50, 'Beverages'),
('Cappuccino', 'Coffee with steamed milk and foam', 4.50, 'Beverages'),
('Latte', 'Coffee with steamed milk', 4.00, 'Beverages'),
('Americano', 'Diluted espresso', 3.00, 'Beverages'),
('Croissant', 'Buttery pastry', 2.50, 'Bakery'),
('Muffin', 'Fresh baked muffin', 3.00, 'Bakery'),
('Sandwich', 'Ham and cheese sandwich', 6.50, 'Food'),
('Salad', 'Fresh garden salad', 7.00, 'Food'),
('Pasta', 'Creamy pasta dish', 8.50, 'Food'),
('Burger', 'Classic beef burger', 9.00, 'Food');

-- Sample tables
INSERT INTO tables (table_number, capacity) VALUES
(1, 2), (2, 4), (3, 6), (4, 2), (5, 4), (6, 8);

-- Sample customers
INSERT INTO customers (name, phone, email) VALUES
('John Doe', '123-456-7890', 'john@example.com'),
('Jane Smith', '098-765-4321', 'jane@example.com');