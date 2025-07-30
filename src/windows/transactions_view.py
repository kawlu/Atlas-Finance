from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import pyqtSignal, QTranslator

import json

from src.util.qt_util import MessageBox
from src.util.db_manager import ConsultaSQL
from src.util.language_manager import LanguageManager as lm
from src.util.formatter import Formatter
from src.util import icons_rc

from src.windows.transaction_form_view import NewTransactionWindow

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "transactions.ui"
DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)
            translate = data_util['traducao']['mensage_box']

db = ConsultaSQL()

class TransactionsWindow(QDialog):
    grafico_atualizado = pyqtSignal()
    transacoes_atualizadas = pyqtSignal()
    totais_atualizados = pyqtSignal()
        
    def __init__(self, cliente_id, linguagem_atual):
        super().__init__()

        translator = QTranslator()
        self.linguagem_atual = linguagem_atual
        lm.trocar_linguagem(QApplication.instance(), translator, linguagem_atual)

        uic.loadUi(UI_PATH, self)

        self.tabela_Registros.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tabela_Registros.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        self.novo_registro_window = None

        self.btn_add_registro.clicked.connect(self.abrir_novo_registro)
        self.btn_excluir_registro.clicked.connect(self.excluir_registro)

        self.cliente_id = cliente_id

        self.carregar_registros()

        self.tabela_Registros.setColumnHidden(0, True)

    def abrir_novo_registro(self):
        if not self.novo_registro_window:
            self.novo_registro_window = NewTransactionWindow(self, self.cliente_id, self.linguagem_atual)
        self.novo_registro_window.exec()

    def traduzir_registro(self, tipo, categoria):
        traducao = data_util['traducao']['categoria'][self.linguagem_atual]
        tipo_traduzido = traducao.get(tipo, tipo)
        categoria_traduzida = traducao.get(categoria, categoria)
        return tipo_traduzido, categoria_traduzida

    def carregar_registros(self):
        try:
            query = """
                SELECT transacao_id, nome, tipo, categoria, data_realizada, valor
                FROM tb_registro
                WHERE fk_usuario_id = %s
            """
            registros = db.consultar(query, int(self.cliente_id))


            self.tabela_Registros.setRowCount(0)

            for row_data in registros:
                transacao_id, nome, tipo, categoria, data_realizada, valor = row_data
                tipo_traduzido, categoria_traduzida = self.traduzir_registro(tipo, categoria)
                self.adicionar_na_tabela((transacao_id, nome, tipo_traduzido, categoria_traduzida, data_realizada, valor))

            self.atualizar_saldo_total()

        except Exception as e:
            print("Erro ao carregar registros:", e)

    def adicionar_na_tabela(self, dados):
        row_number = self.tabela_Registros.rowCount()
        self.tabela_Registros.insertRow(row_number)

        transacao_id, nome, tipo, categoria, data_realizada, valor = dados

        nome = str(nome).title()
        tipo = str(tipo).capitalize()
        categoria = str(categoria).capitalize()
        data_formatada = Formatter.format_date_to_display(str(data_realizada))
        valor_formatado = Formatter.format_value_to_display(float(valor))

        itens = [transacao_id, nome, tipo, categoria, data_formatada, valor_formatado]

        for column_number, data in enumerate(itens):
            self.tabela_Registros.setItem(
                row_number, column_number, QTableWidgetItem(str(data))
            )


    def excluir_registro(self):
        linha_selecionada = self.tabela_Registros.currentRow()

        if linha_selecionada < 0:
            MessageBox.show_custom_messagebox(
                parent=self,
                tipo="warning",
                title=translate[self.linguagem_atual]['warning'],
                message=translate[self.linguagem_atual]['select_record_to_delete'])
            return

        transacao_id = self.tabela_Registros.item(linha_selecionada, 0).text()
        nome_registro = self.tabela_Registros.item(linha_selecionada, 1).text()

        try:
            transacao_id = int(transacao_id)
        except ValueError:
            MessageBox.show_custom_messagebox(parent=self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['invalid_id_delete'])
            return

        confirmado = MessageBox.ask_confirmation(
            parent=self,
            title="confirmation",
            message=translate[self.linguagem_atual]['delete_confirmation'].format(nome_registro=nome_registro))
    
        if confirmado:
            try:
                sql = "DELETE FROM tb_registro WHERE transacao_id = %s"
                db.editar(sql, transacao_id)

                self.tabela_Registros.removeRow(linha_selecionada)
                self.atualizar_saldo_total()
                self.grafico_atualizado.emit()
                self.transacoes_atualizadas.emit()
                self.totais_atualizados.emit()

                MessageBox.show_custom_messagebox(
                parent=self,
                tipo="information",
                title=translate[self.linguagem_atual]['success'],
                message=translate[self.linguagem_atual]['delete_success'].format(nome_registro=nome_registro))

            except Exception as erro:
                MessageBox.show_custom_messagebox(
                parent=self,
                tipo="error",
                title=translate[self.linguagem_atual]['error'], 
                message=translate[self.linguagem_atual]['delete_error'])
                print(erro)

    def atualizar_saldo_total(self):
        try:
            query = "SELECT tipo, valor FROM tb_registro WHERE fk_usuario_id = %s"
            df = db.pd_consultar(query, int(self.cliente_id))

            if df.empty:
                saldo = 0
            else:
                entradas = df[df['tipo'] == 'entrada']['valor'].sum()
                saidas = df[df['tipo'] == 'saida']['valor'].sum()
                saldo = entradas - saidas

            saldo_formatado = Formatter.format_value_to_display(saldo)

            self.lbl_valor_total.setText(saldo_formatado)

        except Exception as e:
            print("Erro ao atualizar saldo total:", e)