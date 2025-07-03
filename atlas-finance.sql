CREATE DATABASE IF NOT EXISTS db_finance;
USE db_finance;

CREATE TABLE IF NOT EXISTS tb_usuario(
	pk_usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(100) NOT NULL,
    celular VARCHAR(20) UNIQUE,
    ocupacao VARCHAR(100) NOT NULL,
    salario DECIMAL(10,2) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    nascimento DATE NOT NULL,
    path_foto VARCHAR(255),
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

INSERT INTO tb_usuario(nome, email, senha, celular, ocupacao, salario, pais, nascimento, situacao) VALUES(
	'Daniel',
    'Daniel@gmail.com',
    'senhasecreta',
    '+55 (21) 21999-5930',
    'Matador de Porco',
    1600.00,
    'Brasil',
    '2000-01-01',
    'ativa'
);

INSERT INTO tb_registro(nome, valor, tipo, categoria, data_realizada, fk_usuario_id) VALUES(
	'Propina',
    '630.00',
    'entrada',
    'outros',
    CURRENT_DATE(),
    '1'
);

SELECT * FROM tb_usuario;
SELECT * FROM tb_registro;

SELECT U.nome AS 'Nome', R.nome AS 'Nome-Da-Transação', R.valor AS 'Valor', R.data_realizada AS 'Data-Realizada' 
FROM tb_registro AS R
INNER JOIN tb_usuario AS U ON R.fk_usuario_id = U.pk_usuario_id
ORDER BY U.nome;

# Join pra pegar valor total
SELECT U.nome 'Nome', SUM(R.valor) 'Soma-Total'
FROM tb_registro AS R
INNER JOIN tb_usuario AS U ON R.fk_usuario_id = U.pk_usuario_id
GROUP BY U.nome