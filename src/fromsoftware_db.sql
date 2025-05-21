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
    numEmpregador INT,
    FOREIGN KEY(atividade) REFERENCES atividEmp(atividade),
    FOREIGN KEY(tipo) REFERENCES tipoEmp(tipo)
);

CREATE TABLE produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    ano_lancamento YEAR,
    tipo VARCHAR(255), -- Jogo ou Plataforma
    idEmpDev INT NOT NULL,
    FOREIGN KEY(idEmpDev) REFERENCES empresa(id),
);

CREATE TABLE publicacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idProduto INT NOT NULL,
    idEmpPub INT NOT NULL,
    FOREIGN KEY(idProduto) REFERENCES produto(id),
    FOREIGN KEY(idEmpPub) REFERENCES empresa(id)
)

CREATE TABLE compatibilidade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idProduto INT NOT NULL,
    idPlataforma INT NOT NULL,
    FOREIGN KEY(idProduto) REFERENCES produto(id),
    FOREIGN KEY(idPlataforma) REFERENCES produto(id)
);

CREATE TABLE expansao(
	idExpansao INT AUTO_INCREMENT,
    idJogo INT,
    nome VARCHAR(255),
    ano_lancamento YEAR,
    FOREIGN KEY(idJogo) REFERENCES produto(id),
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
*/