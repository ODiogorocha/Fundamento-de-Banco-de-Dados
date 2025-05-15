CREATE DATABASE IF NOT EXISTS fromsoftware_db;
USE fromsoftware_db;

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    fundacao VARCHAR(100),
    sede VARCHAR(255),
    industria VARCHAR(255),
    produtos TEXT,
    receita VARCHAR(100),
    funcionarios VARCHAR(100)
);

CREATE TABLE jogos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    ano_lancamento YEAR,
    genero VARCHAR(100),
    desenvolvedor_id INT,
    FOREIGN KEY (desenvolvedor_id) REFERENCES empresa(id)
);

CREATE TABLE funcionarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    cargo VARCHAR(100),
    data_inicio VARCHAR(100),
    empresa_id INT,
    FOREIGN KEY (empresa_id) REFERENCES empresa(id)
);

CREATE TABLE paises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE plataformas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE jogo_plataforma (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jogo_id INT,
    plataforma_id INT,
    FOREIGN KEY (jogo_id) REFERENCES jogos(id),
    FOREIGN KEY (plataforma_id) REFERENCES plataformas(id)
);

CREATE TABLE jogo_pais_publicacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jogo_id INT,
    pais_id INT,
    FOREIGN KEY (jogo_id) REFERENCES jogos(id),
    FOREIGN KEY (pais_id) REFERENCES paises(id)
);
