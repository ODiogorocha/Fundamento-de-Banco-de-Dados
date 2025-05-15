CREATE DATABASE IF NOT EXISTS fromsoftware_db;

USE fromsoftware_db;

CREATE TABLE IF NOT EXISTS fromsoftware_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    atributo VARCHAR(255),
    valor TEXT
);
