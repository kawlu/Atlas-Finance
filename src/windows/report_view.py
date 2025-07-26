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

from datetime import datetime as dt
import os

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "report.ui"

class RelatorioWindow(QDialog):
    def __init__(self, cliente_id):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.cliente_id = cliente_id
        self.btn_sim.clicked.connect(self.gerar_pdf_e_popup)
        self.btn_nao.clicked.connect(self.close)

    def gerar_pdf_e_popup(self):
        
        pdf_sucesso = GerarPDF(self.cliente_id).gerar()
        if pdf_sucesso:
            MessageBox.show_custom_messagebox(self, "information", "Sucesso", "PDF foi gerado com sucesso!")
            self.close()
        elif pdf_sucesso == None:
            self.close()
        else:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "Não há registros disponíveis.")
            self.close()

class GerarPDF:
    def __init__(self, cliente_id):
        self.cliente_id = cliente_id
        self.largura_pagina, self.altura_pagina = A4
        self.margem_esquerda = 50
        self.margem_topo = self.altura_pagina - 50
        self.linha_altura = 25
        self.fonte_titulo = "Helvetica-Bold"
        self.fonte_texto = "Helvetica"
        self.tamanho_titulo = 26
        self.tamanho_cabecalho = 14
        self.tamanho_texto = 12

        self.colunas = ["Nome", "Valor", "Tipo", "Categoria", "Data"]
        self.col_x = [self.margem_esquerda, 180, 260, 350, 460]
        self.col_widths = [
            self.col_x[i+1] - self.col_x[i] if i+1 < len(self.col_x) else 100
            for i in range(len(self.col_x))
        ]

    def quebrar_texto(self, texto, largura_max, fonte, tamanho):
        palavras = texto.split()
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            tentativa = linha_atual + " " + palavra if linha_atual else palavra
            if stringWidth(tentativa, fonte, tamanho) <= largura_max:
                linha_atual = tentativa
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def draw_centered_text(self, pdf, text, x_left, x_right, y, font, size, cor=colors.black):
        largura_texto = stringWidth(text, font, size)
        x_centro = x_left + (x_right - x_left) / 2
        x_texto = x_centro - largura_texto / 2
        pdf.setFont(font, size)
        pdf.setFillColor(cor)
        pdf.drawString(x_texto, y, text)

    def gerar(self, nome_arquivo="relatorio_atlas_finance.pdf"):
        db = ConsultaSQL()
        query = "SELECT * FROM tb_registro WHERE fk_usuario_id = %s"
        dados_lidos = db.pd_consultar(query, self.cliente_id)

        if dados_lidos.empty:
            return False
        
        caminho_inicial = os.environ.get('USERPROFILE', os.getcwd())
        
        caminho_arquivo, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Salvar Relatório em PDF",
            os.path.join(caminho_inicial, nome_arquivo),
            "PDF Files (*.pdf);"
        )

        if not caminho_arquivo:
            return None  # Usuário cancelou

        pdf = canvas.Canvas(caminho_arquivo, pagesize=A4)
        numero_pagina = 1

        def desenhar_cabecalho():
            pdf.setFillColor(colors.HexColor("#0D192B"))
            pdf.setFont(self.fonte_titulo, self.tamanho_titulo)
            pdf.drawString(self.margem_esquerda, self.margem_topo, "Atlas Finance")
            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(1)
            pdf.line(self.margem_esquerda, self.margem_topo - 10, self.largura_pagina - self.margem_esquerda, self.margem_topo - 10)
            pdf.setFont(self.fonte_texto, 16)
            pdf.setFillColor(colors.black)
            pdf.drawString(self.margem_esquerda, self.margem_topo - 40, "Relatório de Transações Registradas")

        def desenhar_titulos_tabela(y_inicio):
            pdf.setFont(self.fonte_titulo, self.tamanho_cabecalho)
            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(1)
            for i, titulo in enumerate(self.colunas):
                largura_coluna = self.col_widths[i]
                pdf.setFillColor(colors.HexColor("#0D192B"))
                pdf.rect(self.col_x[i], y_inicio, largura_coluna, self.linha_altura, fill=1, stroke=1)
                pdf.setFillColor(colors.white)
                pdf.drawString(self.col_x[i] + 5, y_inicio + 7, titulo)

        def desenhar_rodape():
            pdf.setFont("Helvetica", 9)
            pdf.setFillColor(colors.black)
            data_hora = dt.now().strftime("Gerado em %d/%m/%Y às %H:%M:%S")
            texto_pagina = f"Página {numero_pagina}"
            pdf.drawString(self.margem_esquerda, 30, data_hora)
            pdf.drawRightString(self.largura_pagina - self.margem_esquerda, 30, texto_pagina)

        desenhar_cabecalho()
        y_inicio = self.margem_topo - 80
        desenhar_titulos_tabela(y_inicio)
        y = y_inicio - self.linha_altura
        pdf.setFont(self.fonte_texto, self.tamanho_texto)
        desenhar_rodape()

        for _, linha in dados_lidos.iterrows():
            nome = str(linha["nome"]).title()
            valor = f'R$ {linha["valor"]:.2f}'.replace('.', ',')
            tipo = str(linha["tipo"]).capitalize()
            categoria = str(linha["categoria"]).capitalize()
            data = str(linha["data_realizada"])

            largura_nome_coluna = self.col_widths[0] - 10
            linhas_nome = self.quebrar_texto(nome, largura_nome_coluna, self.fonte_texto, self.tamanho_texto)
            altura_nome = self.linha_altura * len(linhas_nome)

            if y - altura_nome < 100:
                numero_pagina += 1
                pdf.showPage()
                desenhar_cabecalho()
                desenhar_titulos_tabela(self.margem_topo - 80)
                y = self.margem_topo - 80 - self.linha_altura
                pdf.setFont(self.fonte_texto, self.tamanho_texto)
                desenhar_rodape()

            for i in range(len(self.colunas)):
                largura_coluna = self.col_widths[i]
                pdf.setFillColor(colors.white)
                pdf.rect(self.col_x[i], y, largura_coluna, altura_nome, fill=1, stroke=1)

            pdf.setFillColor(colors.black)
            text_obj = pdf.beginText()
            text_obj.setTextOrigin(self.col_x[0] + 5, y + (len(linhas_nome) - 1) * 12 + 5)
            text_obj.setFont(self.fonte_texto, self.tamanho_texto)
            for linha_nome in linhas_nome:
                text_obj.textLine(linha_nome)
            pdf.drawText(text_obj)

            alinhamento_y = y + (len(linhas_nome) - 1) * 12 + 5
            self.draw_centered_text(pdf, valor, self.col_x[1], self.col_x[2], alinhamento_y, self.fonte_texto, self.tamanho_texto)
            self.draw_centered_text(pdf, tipo, self.col_x[2], self.col_x[3], alinhamento_y, self.fonte_texto, self.tamanho_texto)
            self.draw_centered_text(pdf, categoria, self.col_x[3], self.col_x[4], alinhamento_y, self.fonte_texto, self.tamanho_texto)
            self.draw_centered_text(pdf, data, self.col_x[4], self.col_x[4] + 100, alinhamento_y, self.fonte_texto, self.tamanho_texto)

            y -= altura_nome

        desenhar_rodape()
        pdf.save()
        return True
