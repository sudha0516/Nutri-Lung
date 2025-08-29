DROP DATABASE IF EXISTS lung_db;
CREATE DATABASE lung_db;
USE lung_db;

CREATE TABLE users(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NULL,   -- ✅ allow null so registration works
    email VARCHAR(50) UNIQUE,
    password VARCHAR(255)    -- ✅ larger size, if later you use hashing
);
