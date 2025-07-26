from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PyQt6.QtCore import pyqtSignal

from datetime import datetime
import sys
import re

from src.util.qt_util import MessageBox
from src.util.db_manager import ConsultaSQL
from src.util import icons_rc

db = ConsultaSQL()

def tratar_data_para_banco(data_str):
    return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")

def tratar_data_para_exibir(data_str):
    return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")

def tratar_valor_para_banco(valor_str):
    valor_limpo = re.sub(r'[^\d,]', '', valor_str) 
    valor = valor_limpo.replace('.', '').replace(',', '.')
    return float(valor)

def tratar_valor_para_exibir(valor_float):
    return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

class NovoRegistroWindow(QDialog):
    def __init__(self, balanco_window, cliente_id):
        super().__init__()
        uic.loadUi("ui/NovoRegistroWindow.ui", self)
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
                data_banco = tratar_data_para_banco(data_realizada)
                valor_banco = tratar_valor_para_banco(valor)

                query = """
                    INSERT INTO tb_registro (nome, valor, tipo, categoria, data_realizada, fk_usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (nome, valor_banco, tipo, categoria, data_banco, self.cliente_id)

                db.editar(query, valores)

                transacao_id = db.consultar("SELECT LAST_INSERT_ID()")[0][0]

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

class BalancoWindow(QDialog):
    
    grafico_atualizado = pyqtSignal()
    transacoes_atualizadas = pyqtSignal()
    totais_atualizados = pyqtSignal()
        
    def __init__(self, cliente_id):
        super().__init__()
        uic.loadUi("ui/BalancoWindow.ui", self)
        
        self.novo_registro_window = None

        self.btn_add_registro.clicked.connect(self.abrir_novo_registro)
        self.btn_excluir_registro.clicked.connect(self.excluir_registro)

        self.cliente_id = cliente_id

        self.carregar_registros()

        self.tabela_Registros.setColumnHidden(0, True)

    def abrir_novo_registro(self):
        if not self.novo_registro_window:
            self.novo_registro_window = NovoRegistroWindow(self, self.cliente_id)
        self.novo_registro_window.exec()

    def carregar_registros(self):
        try:
            query = """
                SELECT transacao_id, nome, tipo, categoria, data_realizada, valor
                FROM tb_registro
                WHERE fk_usuario_id = %s
            """
            registros = db.consultar(query, self.cliente_id)

            self.tabela_Registros.setRowCount(0)

            for row_data in registros:
                self.adicionar_na_tabela(row_data)

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
        data_formatada = tratar_data_para_exibir(str(data_realizada))
        valor_formatado = tratar_valor_para_exibir(float(valor))

        itens = [transacao_id, nome, tipo, categoria, data_formatada, valor_formatado]

        for column_number, data in enumerate(itens):
            self.tabela_Registros.setItem(
                row_number, column_number, QTableWidgetItem(str(data))
            )


    def excluir_registro(self):
        linha_selecionada = self.tabela_Registros.currentRow()

        if linha_selecionada < 0:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Selecione um registro para excluir")
            return

        transacao_id = self.tabela_Registros.item(linha_selecionada, 0).text()
        nome_registro = self.tabela_Registros.item(linha_selecionada, 1).text()

        try:
            transacao_id = int(transacao_id)
        except ValueError:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "ID inválido para exclusão.")
            return

        confirmado = MessageBox.ask_confirmation(self, "Confirmação", f"Tem certeza que deseja excluir o registro \"{nome_registro}\"?")

        if confirmado:
            try:
                sql = "DELETE FROM tb_registro WHERE transacao_id = %s"
                db.editar(sql, transacao_id)

                self.tabela_Registros.removeRow(linha_selecionada)
                self.atualizar_saldo_total()
                self.grafico_atualizado.emit()
                self.transacoes_atualizadas.emit()
                self.totais_atualizados.emit()

                MessageBox.show_custom_messagebox(self, "information", "Sucesso", f"Registro \"{nome_registro}\" excluído com sucesso.")

            except Exception as erro:
                MessageBox.show_custom_messagebox(self, "error", "Erro", f"Erro ao excluir registro:\n{erro}")


    def atualizar_saldo_total(self):
        try:
            query = "SELECT tipo, valor FROM tb_registro WHERE fk_usuario_id = %s"
            df = db.pd_consultar(query, self.cliente_id)

            if df.empty:
                saldo = 0
            else:
                entradas = df[df['tipo'] == 'entrada']['valor'].sum()
                saidas = df[df['tipo'] == 'saída']['valor'].sum()
                saldo = entradas - saidas

            saldo_formatado = tratar_valor_para_exibir(saldo)

            self.lbl_valor_total.setText(saldo_formatado)

        except Exception as e:
            print("Erro ao atualizar saldo total:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BalancoWindow()
    window.show()
    sys.exit(app.exec())