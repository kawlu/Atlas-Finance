import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6.QtCore import QTranslator

from src.util.language_manager import LanguageManager as lm
from src.util import icons_rc

from src.util.qt_util import MessageBox
from src.util.pdf_util import PDFGenerator

from pathlib import Path
import json

from dotenv import load_dotenv

load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

if DEBUG_MODE:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
else:
    BASE_DIR = Path(sys.executable).parent

DATA_PATH = BASE_DIR / "src" / "util" / "data_util.json"
UI_PATH = BASE_DIR / "ui" / "report.ui"

with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)
            translate = data_util['traducao']['mensage_box']

class ReportWindow(QDialog):
    def __init__(self, cliente_id, mes_selecionado, linguagem_atual):
        super().__init__()

        translator = QTranslator()
        self.linguagem_atual = linguagem_atual
        lm.trocar_linguagem(QApplication.instance(), translator, linguagem_atual)

        uic.loadUi(UI_PATH, self)
        self.cliente_id = cliente_id
        self.btn_sim.clicked.connect(self.gerar_pdf_e_popup)
        self.btn_nao.clicked.connect(self.close)
        self.mes_selecionado = mes_selecionado

    def gerar_pdf_e_popup(self):
        pdf = PDFGenerator(cliente_id=self.cliente_id, mes_selecionado=self.mes_selecionado, linguagem_atual=self.linguagem_atual)
        sucesso = pdf.gerar(self.linguagem_atual)

        if sucesso is True:
            MessageBox.show_custom_messagebox(parent=self, tipo="information", title=translate[self.linguagem_atual]['success'], message=translate[self.linguagem_atual]['pdf_generated_success'])
            self.close()
        elif sucesso is None:
            self.close()
        else:
            MessageBox.show_custom_messagebox(parent=self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['no_records_pdf'])
            self.close()