import psycopg2
import pandas as pd

class ConsultaSQL:
    def __init__(self):
        self.banco = psycopg2.connect(
            "postgresql://neondb_owner:npg_IBv8FpAe3YMD@ep-orange-sun-ac4zcq1w-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )

    def _normalize_params(self, params):
        if params is None:
            return None
        if not isinstance(params, (tuple, list)):
            return (params,)
        return tuple(params)

    def consultar(self, query, params=None):
        """Executa SELECT e retorna tuplas de resultado."""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        
        params = self._normalize_params(params)
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def pd_consultar(self, query, params=None):
        """Executa SELECT e retorna um DataFrame pandas."""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        
        params = self._normalize_params(params)
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
            colunas = [desc[0] for desc in cursor.description]
            dados = cursor.fetchall()
            return pd.DataFrame(dados, columns=colunas)

    def editar(self, query, params=None):
        """Executa INSERT/UPDATE/DELETE sem retorno, com commit."""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        
        params = self._normalize_params(params)
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
        self.banco.commit()

    def executar_retorno(self, query, params=None):
        """Executa INSERT/UPDATE/DELETE com RETURNING, com commit, e retorna resultado."""
        if not self.banco:
            raise ConnectionError("Banco de dados não conectado.")
        
        params = self._normalize_params(params)
        with self.banco.cursor() as cursor:
            cursor.execute(query, params)
            resultado = cursor.fetchone()
        self.banco.commit()
        return resultado

    def fechar_conexao(self):
        if self.banco:
            self.banco.close()