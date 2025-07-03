from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QDialog, QMessageBox

from database import ConsultaSQL

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from datetime import datetime


class RelatorioWindow(QDialog):
    def __init__(self, cliente_id):
        super().__init__()
        uic.loadUi("ui/RelatorioWindow.ui", self)

        self.cliente_id = cliente_id

        self.btn_sim.clicked.connect(self.gerar_pdf_e_popup)
        self.btn_nao.clicked.connect(self.close)

    def gerar_pdf_e_popup(self):
        pdf_sucesso = self.gerar_pdf()
        if pdf_sucesso:
            QMessageBox.information(self, "Sucesso", "PDF foi gerado com sucesso!")
            self.close()

    def gerar_pdf(self):
        db = ConsultaSQL()
        query = "SELECT * FROM tb_registro WHERE fk_usuario_id = %s"
        dados_lidos = db.pd_consultar(query, self.cliente_id)

        if dados_lidos.empty:
            QtWidgets.QMessageBox.warning(self, "Erro", "Não há registros disponíveis.")
            return False

        # Layout
        largura_pagina, altura_pagina = A4
        margem_esquerda = 50
        margem_topo = altura_pagina - 50
        linha_altura = 25
        fonte_titulo = "Helvetica-Bold"
        fonte_texto = "Helvetica"
        tamanho_titulo = 26
        tamanho_cabecalho = 14
        tamanho_texto = 12

        # Colunas
        colunas = ["Nome", "Valor", "Tipo", "Categoria", "Data"]
        col_x = [margem_esquerda, 180, 260, 350, 460]
        col_widths = [col_x[i+1] - col_x[i] if i+1 < len(col_x) else 100 for i in range(len(col_x))]

        def quebrar_texto(texto, largura_max, fonte, tamanho):
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

        def draw_centered_text(pdf, text, x_left, x_right, y, font, size, cor=colors.black):
            largura_texto = stringWidth(text, font, size)
            x_centro = x_left + (x_right - x_left) / 2
            x_texto = x_centro - largura_texto / 2
            pdf.setFont(font, size)
            pdf.setFillColor(cor)
            pdf.drawString(x_texto, y, text)

        pdf = canvas.Canvas("relatorio_atlas_finance.pdf", pagesize=A4)

        def desenhar_cabecalho():
            pdf.setFillColor(colors.HexColor("#0D192B"))
            pdf.setFont(fonte_titulo, tamanho_titulo)
            pdf.drawString(margem_esquerda, margem_topo, "Atlas Finance")

            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(1)
            pdf.line(margem_esquerda, margem_topo - 10, largura_pagina - margem_esquerda, margem_topo - 10)

            pdf.setFont(fonte_texto, 16)
            pdf.setFillColor(colors.black)
            pdf.drawString(margem_esquerda, margem_topo - 40, "Relatório de Transações Registradas")

        def desenhar_titulos_tabela(y_inicio):
            pdf.setFont(fonte_titulo, tamanho_cabecalho)
            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(1)

            for i, titulo in enumerate(colunas):
                largura_coluna = col_widths[i]
                pdf.setFillColor(colors.HexColor("#0D192B"))  # fundo azul
                pdf.rect(col_x[i], y_inicio, largura_coluna, linha_altura, fill=1, stroke=1)
                pdf.setFillColor(colors.white)  # texto branco
                pdf.drawString(col_x[i] + 5, y_inicio + 7, titulo)

        def desenhar_rodape(numero_pagina):
            pdf.setFont("Helvetica", 9)
            pdf.setFillColor(colors.black)
            data_hora = datetime.now().strftime("Gerado em %d/%m/%Y às %H:%M:%S")
            texto_pagina = f"Página {numero_pagina}"
            pdf.drawString(margem_esquerda, 30, data_hora)
            pdf.drawRightString(largura_pagina - margem_esquerda, 30, texto_pagina)

        # Início da geração
        numero_pagina = 1
        desenhar_cabecalho()
        y_inicio = margem_topo - 80
        desenhar_titulos_tabela(y_inicio)
        y = y_inicio - linha_altura
        pdf.setFont(fonte_texto, tamanho_texto)
        desenhar_rodape(numero_pagina)

        for _, linha in dados_lidos.iterrows():
            # Capitalização dos dados
            nome = str(linha["nome"]).title()
            valor = f'R$ {linha["valor"]:.2f}'.replace('.', ',')
            tipo = str(linha["tipo"]).capitalize()
            categoria = str(linha["categoria"]).capitalize()
            data = str(linha["data_realizada"])

            largura_nome_coluna = col_widths[0] - 10
            linhas_nome = quebrar_texto(nome, largura_nome_coluna, fonte_texto, tamanho_texto)
            altura_nome = linha_altura * len(linhas_nome)

            if y - altura_nome < 100:
                numero_pagina += 1
                pdf.showPage()
                desenhar_cabecalho()
                desenhar_titulos_tabela(margem_topo - 80)
                y = margem_topo - 80 - linha_altura
                pdf.setFont(fonte_texto, tamanho_texto)
                desenhar_rodape(numero_pagina)

            # Células com fundo branco e borda preta
            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(1)
            for i in range(len(colunas)):
                largura_coluna = col_widths[i]
                pdf.setFillColor(colors.white)
                pdf.rect(col_x[i], y, largura_coluna, altura_nome, fill=1, stroke=1)

            # Nome (esquerdo, com múltiplas linhas)
            pdf.setFillColor(colors.black)
            text_obj = pdf.beginText()
            text_obj.setTextOrigin(col_x[0] + 5, y + (len(linhas_nome) - 1) * 12 + 5)
            text_obj.setFont(fonte_texto, tamanho_texto)
            for linha_nome in linhas_nome:
                text_obj.textLine(linha_nome)
            pdf.drawText(text_obj)

            # Outras colunas (centralizado)
            alinhamento_y = y + (len(linhas_nome) - 1) * 12 + 5
            draw_centered_text(pdf, valor, col_x[1], col_x[2], alinhamento_y, fonte_texto, tamanho_texto)
            draw_centered_text(pdf, tipo, col_x[2], col_x[3], alinhamento_y, fonte_texto, tamanho_texto)
            draw_centered_text(pdf, categoria, col_x[3], col_x[4], alinhamento_y, fonte_texto, tamanho_texto)
            draw_centered_text(pdf, data, col_x[4], col_x[4] + 100, alinhamento_y, fonte_texto, tamanho_texto)

            y -= altura_nome

        desenhar_rodape(numero_pagina)
        pdf.save()
        return True
