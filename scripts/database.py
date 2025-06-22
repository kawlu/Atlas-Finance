import pymysql

class ConsultaSQL():
    def __init__(self):
        self.banco = pymysql.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="db_finance"
        )
        try:
            self.banco.ping(reconnect=True)  # Tenta reconectar
            print("Banco de dados conectado!")
        except pymysql.MySQLError:
            print("Falha na conexão com o banco de dados.")

    def consultar(self, query, params=None):
        """Executa SELECT"""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
            resultado = cursor.fetchall()
            return resultado

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

    