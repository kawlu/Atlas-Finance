from datetime import datetime
import re

class Formatter:
    @staticmethod
    def format_date_to_db(date: str) -> str:
        """
        Converte data do formato 'dd/mm/YYYY' para 'YYYY-mm-dd' (formato banco).
        """
        return datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

    @staticmethod
    def format_date_to_display(date: str) -> str:
        """
        Converte data do formato 'YYYY-mm-dd' para 'dd/mm/YYYY' (exibição).
        """
        return datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")

    @staticmethod
    def format_value_to_db(value: str) -> float:
        """
        Converte um valor que seja aceitável para o banco de dados (decimal).

        Remove caracteres não numéricos e converte vírgula decimal para ponto.
        Exemplo: 'R$ 1.234,56' -> 1234.56
        """
        valor_limpo = re.sub(r'[^\d,]', '', value)
        valor_formatado = valor_limpo.replace('.', '').replace(',', '.')
        return float(valor_formatado)
    
    @staticmethod
    def format_value_to_display(value: float) -> str:
        """
        Converte um valor que seja aceitável para o banco de dados (decimal).

        Adiciona caracteres não numéricos e converte ponto para vírgula decimal.
        Exemplo: 1234.56 -> 'R$ 1.234,56'
        """
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")