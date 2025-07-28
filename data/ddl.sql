-- PSQL

CREATE TABLE IF NOT EXISTS tb_usuario (
    pk_usuario_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(100) NOT NULL,
    celular VARCHAR(20) UNIQUE,
    ocupacao VARCHAR(100) NOT NULL,
    salario VARCHAR(50) NOT NULL,
    pais VARCHAR(100) NOT NULL,
    nascimento DATE NOT NULL,
    foto BYTEA,
    situacao VARCHAR(20) NOT NULL CHECK (situacao IN ('ativa', 'desativada'))
);

CREATE TABLE IF NOT EXISTS tb_registro (
    transacao_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    tipo VARCHAR(10) CHECK (tipo IN ('in','out')),
    categoria VARCHAR(20) CHECK (categoria IN ('alimentacao', 'contas', 'estudo', 'lazer', 'saude', 
    'transporte', 'outros', 'investimento', 'comissao', 'freelance')),
    data_realizada DATE NOT NULL,
    fk_usuario_id INT NOT NULL,
    FOREIGN KEY (fk_usuario_id) REFERENCES tb_usuario(pk_usuario_id) ON DELETE CASCADE
);