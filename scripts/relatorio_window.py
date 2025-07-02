from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QDialog

from database import ConsultaSQL

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
"""
POPUP que vai confirmar e gerar o pdf
"""
    
class RelatorioWindow(QDialog):
    def __init__(self, cliente_id):
        super().__init__()
        uic.loadUi("ui/RelatorioWindow.ui", self)
        
        self.cliente_id = cliente_id

        self.btn_sim.clicked.connect(self.gerar_pdf_e_popup)
        self.btn_nao.clicked.connect(self.close)
        
    def gerar_pdf_e_popup(self):
        self.gerar_pdf()
        self.abrir_popup_sucesso()
        
    def abrir_popup_sucesso(self):
        popup = SucessPDFWindow()
        popup.exec()
        self.close()


    def gerar_pdf(self):
        db = ConsultaSQL()
        query = "SELECT * FROM tb_registro WHERE fk_usuario_id = %s"
        dados_lidos = db.pd_consultar(query, self.cliente_id)

        if dados_lidos.empty:
            QtWidgets.QMessageBox.warning(self, "Erro", "A senha deve ter ao menos 6 caracteres.")
            return
        
        y = 0 # variavel  é a coordenada y para escrever no pdf
        pdf = canvas.Canvas("teste.pdf")
        pdf.setFont("Times-Bold", 25)
        pdf.drawString(200,800, "Produtos cadastrados:")

        pdf.setFont("Times-Bold", 18)

        def medir_largura(texto, fonte="Times-Bold", tamanho=18):
            return pdfmetrics.stringWidth(texto, fonte, tamanho)

        largura_nome = medir_largura("nome")
        largura_valor = medir_largura("valor")
        largura_tipo = medir_largura("tipo")
        largura_categoria = medir_largura("categoria")
        largura_data_realizada = medir_largura("data_realizada")

        for _, linha in dados_lidos.iterrows():
            largura_nome = max(largura_nome, medir_largura(str(linha["nome"])))
            largura_valor = max(largura_valor, medir_largura(str(linha["valor"])))
            largura_tipo = max(largura_tipo, medir_largura(str(linha["tipo"])))
            largura_categoria = max(largura_categoria, medir_largura(str(linha["categoria"])))
            largura_data_realizada = max(largura_data_realizada, medir_largura(str(linha["data_realizada"])))

        x_nome = 10
        x_valor = x_nome + largura_nome + 20
        x_tipo = x_valor + largura_valor + 20
        x_categoria = x_tipo + largura_tipo + 20
        x_data_realizada = x_categoria + largura_categoria + 20

        pdf.drawString(x_nome, 750, "nome")
        pdf.drawString(x_valor, 750, "valor")
        pdf.drawString(x_tipo, 750, "tipo")
        pdf.drawString(x_categoria, 750, "categoria")
        pdf.drawString(x_data_realizada, 750, "data_realizada")

        for _, linha in dados_lidos.iterrows():
            y = y + 50
            
            nome = str(linha["nome"])
            valor = str(linha["valor"])
            tipo = str(linha["tipo"])
            categoria = str(linha["categoria"])
            data_realizada = str(linha["data_realizada"])

            pdf.drawString(x_nome, 750 - y, nome)
            pdf.drawString(x_valor, 750 - y, valor)
            pdf.drawString(x_tipo, 750 - y, tipo)
            pdf.drawString(x_categoria, 750 - y, categoria)
            pdf.drawString(x_data_realizada, 750 - y, data_realizada)

        pdf.save()
        
class SucessPDFWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/SucessPDFWindow.ui", self) 
        
        self.btn_ok.clicked.connect(self.close)
        