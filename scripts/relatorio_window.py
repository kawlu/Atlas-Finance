from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

from database import ConsultaSQL

from reportlab.pdfgen import canvas
"""
POPUP que vai confirmar e gerar o pdf
"""
    
class RelatorioWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/RelatorioWindow.ui", self)  # type: ignore[attr-defined]
        
        self.btn_sim.clicked.connect(self.gerar_pdf_e_popup) # type: ignore[attr-defined]
        self.btn_nao.clicked.connect(self.close) # type: ignore[attr-defined]
        
    def gerar_pdf_e_popup(self):
        self.gerar_pdf()
        self.abrir_popup_sucesso()
        
    def abrir_popup_sucesso(self):
        popup = SucessPDFWindow()
        popup.exec()
        self.close()
        
        
    #TODO Adaptar
    def gerar_pdf(self):
        db = ConsultaSQL()
        dados_lidos = db.consultar_PDF(query="SELECT * FROM tb_registro")
        
        y = 0 # variavel  é a coordenada y para escrever no pdf
        pdf = canvas.Canvas("teste.pdf")
        pdf.setFont("Times-Bold", 25)
        pdf.drawString(200,800, "Produtos cadastrados:")
        pdf.setFont("Times-Bold", 18)

        pdf.drawString(10,750, "nome")
        pdf.drawString(110,750, "valor")
        pdf.drawString(210,750, "moeda")
        pdf.drawString(310,750, "data_realizada")
        pdf.drawString(410,750, "categoria")

        for i in range(0, len(dados_lidos)):
            y = y + 50
            pdf.drawString(10,750 - y, str(dados_lidos[i][0]))
            pdf.drawString(110,750 - y, str(dados_lidos[i][1]))
            pdf.drawString(210,750 - y, str(dados_lidos[i][2]))
            pdf.drawString(310,750 - y, str(dados_lidos[i][3]))
            pdf.drawString(410,750 - y, str(dados_lidos[i][4]))

        pdf.save()
        
class SucessPDFWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/SucessPDFWindow.ui", self)  # type: ignore[attr-defined]
        
        self.btn_ok.clicked.connect(self.close) # type: ignore[attr-defined]
        