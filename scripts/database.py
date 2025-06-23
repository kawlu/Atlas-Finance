import pymysql
import pandas as pd

class ConsultaSQL:
    def __init__(self):
        self.banco = pymysql.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="db_finance"
        )
        try:
            self.banco.ping(reconnect=True)  # Tenta reconectar
        except pymysql.MySQLError:
            print("Falha na conexão com o banco de dados.")

    def consultar(self, query, params=None):
        """Executa SELECT e retorna lista de tuplas"""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def consultar_PDF(self, query, params=None) -> pd.DataFrame:
        """Executa SELECT e retorna DataFrame"""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
            colunas = [desc[0] for desc in cursor.description]
            dados = cursor.fetchall()
            return pd.DataFrame(dados, columns=colunas)

    def editar(self, query, params=None):
        """Executa INSERT, UPDATE ou DELETE"""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
        self.banco.commit()

    def fechar_conexao(self):
        """Fecha a conexão com o banco"""
        self.banco.close()