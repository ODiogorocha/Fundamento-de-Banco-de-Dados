CREATE DATABASE IF NOT EXISTS fromsoftware_db;
USE fromsoftware_db;

CREATE TABLE atividade (,
    nome VARCHAR(255) PRIMARY KEY,
);

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    fundacao DATE,
    sede VARCHAR(255),
    head VARCHAR(255),
    FOREIGN KEY atividade REFERENCES atividade(nome)
);

CREATE TABLE plataforma (
    idPlataforma INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    ano_lancamento YEAR,
    FOREIGN KEY (idEmpresa) REFERENCES empresa(id)
);

CREATE TABLE produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    ano_lancamento YEAR,
    FOREIGN KEY idEmpresa REFERENCES empresa(id),
    FOREIGN KEY idPlataforma REFERENCES empresa(id)
);

/* CHANGELOG

15/05 - Gabriel: 
  - remodelei o banco de dados para se encaixar com os dados fornecidos pela wikipedia
  - criei as tabelas atividade (necessário pelo domínio flexível), empresa, plataforma e produto
  - criei os relacionamentos entre as tabelas
*/