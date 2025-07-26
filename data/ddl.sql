CREATE DATABASE IF NOT EXISTS db_finance;
USE db_finance;

CREATE TABLE IF NOT EXISTS tb_usuario(
	pk_usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(100) NOT NULL,
    celular VARCHAR(20) UNIQUE,
    ocupacao VARCHAR(100) NOT NULL,
    salario VARCHAR(50) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    nascimento DATE NOT NULL,
    foto LONGBLOB,
    situacao ENUM('ativa', 'desativada') NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_registro(
	transacao_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    tipo enum('entrada','saída'),
    categoria enum('alimentação','contas','estudo','lazer','saúde','outros','transporte'),
    data_realizada DATE NOT NULL,
    fk_usuario_id INT NOT NULL,
    FOREIGN KEY(fk_usuario_id) REFERENCES tb_usuario(pk_usuario_id) ON DELETE CASCADE
);