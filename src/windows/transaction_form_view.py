from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QTranslator

from datetime import datetime
import json

from src.util.qt_util import MessageBox
from src.util.db_manager import ConsultaSQL
from src.util.language_manager import LanguageManager as lm
from src.util import icons_rc
from src.util.formatter import Formatter

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "new_transaction.ui"
DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)
            translate = data_util['traducao']['mensage_box']

db = ConsultaSQL()

class NewTransactionWindow(QDialog):
    def __init__(self, balanco_window, cliente_id, linguagem_atual):
        super().__init__()

        translator = QTranslator()
        self.linguagem_atual = linguagem_atual
        lm.trocar_linguagem(QApplication.instance(), translator, linguagem_atual)

        uic.loadUi(UI_PATH, self)
        
        self.add_categorias_traduzidas()
        
        self.input_Data.setDate(datetime.now())
        self.balanco_window = balanco_window
        self.cliente_id = cliente_id
        self.btn_Confirmar.clicked.connect(self.adicionar_registro)

    def add_categorias_traduzidas(self):
        db = data_util['traducao']['categoria']['database']
        traducao = data_util['traducao']['categoria'][self.linguagem_atual]
        
        categorias_traduzidas = [
            traducao[db[k]] for k in sorted(db.keys(), key=int) if db[k] in traducao
        ]

        # Salva mapeamento reverso (visível → interno)
        self.categorias_map = {
            traducao[db[k]]: db[k] for k in sorted(db.keys(), key=int) if db[k] in traducao
        }

        self.cbox_Categoria.addItems(categorias_traduzidas)

    def adicionar_registro(self):
        traducao_tipo = data_util['traducao']['categoria'][self.linguagem_atual]
        
        self.tipo_map = {
            traducao_tipo[k]: k for k in ['entrada', 'saida']
        }
        
        nome = self.input_Nome.text()
        data_realizada = self.input_Data.text()
        valor = self.input_Valor.text()
        
        tipo = self.cbox_Tipo.currentText()
        valor_interno_tipo = self.tipo_map[tipo] 
        
        categoria = self.cbox_Categoria.currentText()
        valor_categoria_interna = self.categorias_map[categoria]

        if nome and tipo and categoria and data_realizada and valor:
            try:
                data_banco = Formatter.format_date_to_db(data_realizada)
                valor_banco = Formatter.format_value_to_db(valor)

                query = """
                    INSERT INTO tb_registro (nome, valor, tipo, categoria, data_realizada, fk_usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING transacao_id
                """

                valores = (nome, valor_banco, valor_interno_tipo, valor_categoria_interna, data_banco, int(self.cliente_id))
                    
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
                MessageBox.show_custom_messagebox(parent=self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['insert_error'])
                print(e)
        else:
            MessageBox.show_custom_messagebox(parent=self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['fill_fields_correctly'])

    def limpar_campos(self):
        self.input_Nome.clear()
        self.cbox_Tipo.setCurrentIndex(0)
        self.cbox_Categoria.setCurrentIndex(0)
        self.input_Data.setDate(datetime.now())
        self.input_Valor.clear()