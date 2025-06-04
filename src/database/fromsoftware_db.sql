DROP DATABASE IF EXISTS fromsoftware_db;
CREATE DATABASE fromsoftware_db;
USE fromsoftware_db;

CREATE TABLE atividEmp (
    atividade VARCHAR(255) PRIMARY KEY
);

CREATE TABLE tipoEmp(
    tipo VARCHAR(255) PRIMARY KEY
);

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    fundacao DATE,
    sede VARCHAR(255),
    head VARCHAR(255), -- Pessoa no comando
    atividade VARCHAR(255),
    tipo VARCHAR(255),
    numEmpregados INT,
    FOREIGN KEY(atividade) REFERENCES atividEmp(atividade),
    FOREIGN KEY(tipo) REFERENCES tipoEmp(tipo)
);

CREATE TABLE jogo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    idEmpDev INT NOT NULL,
    FOREIGN KEY(idEmpDev) REFERENCES empresa(id)
);

CREATE TABLE publisher(
    idPublisher INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255)
);

CREATE TABLE publicacoes(
    idJogo INT,
    idPublisher INT,
    ano YEAR,
    FOREIGN KEY(idJogo) REFERENCES jogo(id),
    FOREIGN KEY(idPublisher) REFERENCES publisher(idPublisher),
    PRIMARY KEY(idJogo, idPublisher)
);

CREATE TABLE plataforma(
    idPlataforma INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255)
);

CREATE TABLE compatibilidade(
    idJogo INT,
    idPlataforma INT,
    FOREIGN KEY(idJogo) REFERENCES jogo(id),
    FOREIGN KEY(idPlataforma) REFERENCES plataforma(idPlataforma),
    PRIMARY KEY(idJogo, idPlataforma)
);

CREATE TABLE expansao(
	idExpansao INT AUTO_INCREMENT,
    idJogo INT,
    nome VARCHAR(255),
    ano_lancamento YEAR,
    FOREIGN KEY(idJogo) REFERENCES jogo(id),
    PRIMARY KEY(idExpansao)
);

/* CHANGELOG

15/05 - Gabriel: 
  - remodelei o banco de dados para se encaixar com os dados fornecidos pela wikipedia
  - criei as tabelas atividEmp, tipoEmp, empresa e produto
  - criei os relacionamentos entre as tabelas
16/05 - Gabriel:
  - remodelei o banco de dados, pois não estava completo
  - criei a tabela compatibilidade
  - criei a tabela expansao
19/05 - Gabriel:
  - criei a tabela publicacoes
  - Renomeei o campo idEmpresa para idEmpDev na tabela produto
30/05 - Gabriel:
  - criei as tabelas publisher, plataforma, compatibilidade e publicacoes
  - produto -> jogo
  - adicionei o campo ano_lancamento na tabela expansao e retirei do jogo
*/