from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PyQt6.QtCore import pyqtSignal

from datetime import datetime
import sys
import re

from src.util.qt_util import MessageBox
from src.util.db_manager import ConsultaSQL
from src.util import icons_rc
from src.util.formatter import Formatter

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "new_transaction.ui"

db = ConsultaSQL()

class NewTransactionWindow(QDialog):
    def __init__(self, balanco_window, cliente_id):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.input_Data.setDate(datetime.now())
        self.balanco_window = balanco_window
        self.cliente_id = cliente_id
        self.btn_Confirmar.clicked.connect(self.adicionar_registro)

    def adicionar_registro(self):
        nome = self.input_Nome.text()
        tipo = self.cbox_Tipo.currentText().lower()
        categoria = self.cbox_Categoria.currentText()
        data_realizada = self.input_Data.text()
        valor = self.input_Valor.text()

        if nome and tipo and categoria and data_realizada and valor:
            try:
                data_banco = Formatter.format_date_to_db(data_realizada)
                valor_banco = Formatter.format_value_to_db(valor)

                query = """
                    INSERT INTO tb_registro (nome, valor, tipo, categoria, data_realizada, fk_usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING transacao_id
                """
                valores = (nome, valor_banco, tipo, categoria.lower(), data_banco, int(self.cliente_id))
                transacao_id = db.executar_retorno(query, valores)[0]

                self.balanco_window.adicionar_na_tabela(
                    (transacao_id, nome, tipo, categoria, data_banco, valor_banco)
                )

                self.balanco_window.atualizar_saldo_total()
                self.balanco_window.grafico_atualizado.emit()
                self.balanco_window.transacoes_atualizadas.emit()
                self.balanco_window.totais_atualizados.emit()

                self.limpar_campos()
                self.close()
                

            except Exception as e:
                MessageBox.show_custom_messagebox(self, "error", "Erro", f"Erro ao inserir registro:\n{e}")
        else:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Preencha todos os campos corretamente.")

    def limpar_campos(self):
        self.input_Nome.clear()
        self.cbox_Tipo.setCurrentIndex(0)
        self.cbox_Categoria.setCurrentIndex(0)
        self.input_Data.setDate(datetime.now())
        self.input_Valor.clear()