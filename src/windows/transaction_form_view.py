import os
import sys
import json
from pathlib import Path
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QTranslator

from src.util.qt_util import MessageBox
from src.util.db_manager import ConsultaSQL
from src.util.language_manager import LanguageManager as lm
from src.util import icons_rc
from src.util.formatter import Formatter

from dotenv import load_dotenv

load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

if DEBUG_MODE:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
else:
    BASE_DIR = Path(sys.executable).parent

UI_PATH = BASE_DIR / "ui" / "new_transaction.ui"
DATA_PATH = BASE_DIR / "src" / "util" / "data_util.json"

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
        
        # seta tipo categorias por tipo
        tipo_inicial = self.cbox_Tipo.currentText()
        self.on_tipo_changed(tipo_inicial)
        
        self.input_Data.setDate(datetime.now())
        self.balanco_window = balanco_window
        self.cliente_id = cliente_id
        self.btn_Confirmar.clicked.connect(self.adicionar_registro)
        self.cbox_Tipo.currentTextChanged.connect(self.on_tipo_changed)

    def add_categorias_traduzidas(self, tipo):
        traducao = data_util['traducao']['categoria'][self.linguagem_atual]
        
        categorias_por_tipo = {
            "entrada": ["salario", "bonus", "freelance", "comissao", "investimento", "vendas", "reembolso", "outros"],
            "saida": ["alimentacao", "contas", "moradia", "transporte", "saude", "educacao", "lazer", "impostos", "assinaturas", "outros"]
        }
        
        categorias_validas = categorias_por_tipo.get(tipo, [])
        
        categorias_traduzidas = [
            traducao[cat] for cat in categorias_validas if cat in traducao
        ]

        self.categorias_map = {
            traducao[cat]: cat for cat in categorias_validas if cat in traducao
        }

        self.cbox_Categoria.clear()
        self.cbox_Categoria.addItems(categorias_traduzidas)

    def on_tipo_changed(self, texto_tipo):
        traducao = data_util['traducao']['categoria'][self.linguagem_atual]
        # Inverte o dicionário (valor para chave) com case insensitive
        inverso = {v.lower(): k for k, v in traducao.items()}
        tipo_interno = inverso.get(texto_tipo.lower(), None)
        if tipo_interno:
            self.add_categorias_traduzidas(tipo_interno)

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