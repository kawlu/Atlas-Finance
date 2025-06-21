import pymysql

class ConsultaSQL():
    def __init__(self):
        self.banco = pymysql.connect( 
            host="localhost",
            user="root",
            passwd='root',
            database="db_finance"
        )

        try:
            self.banco.ping(reconnect=True)  # Tenta reconectar se necessário
            print(f"Banco de dados conectado!")
        except pymysql.MySQLError:
            print("Falha na conexão com o banco de dados.")

    def consultar(self, query):
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        
        with self.banco.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    