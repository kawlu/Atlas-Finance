import json
from pathlib import Path
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QDialog

from src.util.db_manager import ConsultaSQL
from src.util import icons_rc

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from src.util.qt_util import MessageBox
from src.util.pdf_util import PDFGenerator

DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"
UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "report.ui"

class ReportWindow(QDialog):
    def __init__(self, cliente_id, mes_selecionado):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.cliente_id = cliente_id
        self.btn_sim.clicked.connect(self.gerar_pdf_e_popup)
        self.btn_nao.clicked.connect(self.close)
        self.mes_selecionado = mes_selecionado

    def gerar_pdf_e_popup(self):
        pdf = PDFGenerator(cliente_id=self.cliente_id, mes_selecionado=self.mes_selecionado)
        sucesso = pdf.gerar()

        if sucesso is True:
            MessageBox.show_custom_messagebox(self, "information", "Sucesso", "PDF foi gerado com sucesso!")
            self.close()
        elif sucesso is None:
            self.close()
        else:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "Não há registros disponíveis.")
            self.close()