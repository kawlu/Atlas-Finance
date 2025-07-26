import os
import json
from pathlib import Path
from datetime import datetime as dt

from PyQt6 import QtWidgets
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from src.util.db_manager import ConsultaSQL

DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"

class PDFGenerator:
    def __init__(self, cliente_id, mes_selecionado):
        self.cliente_id = cliente_id
        self.mes_selecionado = mes_selecionado
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

    def gerar(self):
        dados_lidos, nome_mes = self._buscar_dados()
        if dados_lidos.empty:
            return False

        nome_arquivo = self._montar_nome_arquivo(nome_mes)
        caminho = self._obter_caminho_salvar(nome_arquivo)
        if not caminho:
            return None

        self._gerar_pdf(dados_lidos, caminho, nome_mes)
        return True

    def _buscar_dados(self):
        db = ConsultaSQL()
        nome_mes = None

        if self.mes_selecionado:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data_util = json.load(f)
            meses_traduzidos = data_util["list"]["lista_meses"]["PT_BR"]
            nome_mes = meses_traduzidos[self.mes_selecionado]

            query = """
                SELECT nome, valor, tipo, categoria, data_realizada
                FROM tb_registro
                WHERE EXTRACT(MONTH FROM data_realizada) = %s AND fk_usuario_id = %s
                ORDER BY data_realizada DESC
            """
            dados = db.pd_consultar(query, (self.mes_selecionado, int(self.cliente_id)))
        else:
            query = """
                SELECT nome, valor, tipo, categoria, data_realizada
                FROM tb_registro
                WHERE fk_usuario_id = %s
                ORDER BY data_realizada DESC
            """
            dados = db.pd_consultar(query, int(self.cliente_id))
        return dados, nome_mes

    def _montar_nome_arquivo(self, nome_mes):
        base = "relatorio_financeiro"
        return f"{base}_{nome_mes.lower()}" if nome_mes else f"{base}_completo"

    def _obter_caminho_salvar(self, nome_arquivo):
        downloads_path = Path(os.environ['USERPROFILE']) / 'Downloads'
        caminho, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Salvar Relatório em PDF",
            os.path.join(downloads_path, f"{nome_arquivo}.pdf"),
            "PDF Files (*.pdf);"
        )
        return caminho

    def _gerar_pdf(self, dados, caminho, nome_mes):
        pdf = canvas.Canvas(caminho, pagesize=A4)
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
            subtitulo = f"Relatório de Transações Registradas - {nome_mes}" if nome_mes else "Relatório de Todas Transações Registradas"
            pdf.drawString(self.margem_esquerda, self.margem_topo - 40, subtitulo)

        def desenhar_titulos_tabela(y_inicio):
            pdf.setFont(self.fonte_titulo, self.tamanho_cabecalho)
            pdf.setStrokeColor(colors.black)
            pdf.setLineWidth(1)
            for i, titulo in enumerate(self.colunas):
                largura = self.col_widths[i]
                pdf.setFillColor(colors.HexColor("#0D192B"))
                pdf.rect(self.col_x[i], y_inicio, largura, self.linha_altura, fill=1, stroke=1)
                pdf.setFillColor(colors.white)
                pdf.drawString(self.col_x[i] + 5, y_inicio + 7, titulo)

        def desenhar_rodape():
            pdf.setFont("Helvetica", 9)
            pdf.setFillColor(colors.black)
            data_hora = dt.now().strftime("Gerado em %d/%m/%Y às %H:%M:%S")
            pdf.drawString(self.margem_esquerda, 30, data_hora)
            pdf.drawRightString(self.largura_pagina - self.margem_esquerda, 30, f"Página {numero_pagina}")

        def draw_centered_text(text, x1, x2, y):
            largura = stringWidth(text, self.fonte_texto, self.tamanho_texto)
            centro = x1 + (x2 - x1) / 2 - largura / 2
            pdf.setFont(self.fonte_texto, self.tamanho_texto)
            pdf.setFillColor(colors.black)
            pdf.drawString(centro, y, text)

        def wrap_text(texto, largura_max):
            palavras = texto.split()
            linhas, linha_atual = [], ""
            for palavra in palavras:
                tentativa = f"{linha_atual} {palavra}".strip()
                if stringWidth(tentativa, self.fonte_texto, self.tamanho_texto) <= largura_max:
                    linha_atual = tentativa
                else:
                    linhas.append(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual)
            return linhas

        desenhar_cabecalho()
        y_inicio = self.margem_topo - 80
        desenhar_titulos_tabela(y_inicio)
        y = y_inicio - self.linha_altura
        pdf.setFont(self.fonte_texto, self.tamanho_texto)
        desenhar_rodape()

        for _, linha in dados.iterrows():
            nome = str(linha.get("nome") or "Sem nome").title()
            valor = f'R$ {linha["valor"]:.2f}'.replace('.', ',')
            tipo = str(linha["tipo"]).capitalize()
            categoria = str(linha["categoria"]).capitalize()
            data = str(linha["data_realizada"])

            linhas_nome = wrap_text(nome, self.col_widths[0] - 10)
            altura = self.linha_altura * len(linhas_nome)

            if y - altura < 100:
                numero_pagina += 1
                pdf.showPage()
                desenhar_cabecalho()
                desenhar_titulos_tabela(self.margem_topo - 80)
                y = self.margem_topo - 80 - self.linha_altura
                pdf.setFont(self.fonte_texto, self.tamanho_texto)
                desenhar_rodape()

            for i in range(len(self.colunas)):
                pdf.setFillColor(colors.white)
                pdf.rect(self.col_x[i], y, self.col_widths[i], altura, fill=1, stroke=1)

            text_obj = pdf.beginText()
            text_obj.setTextOrigin(self.col_x[0] + 5, y + (len(linhas_nome) - 1) * 12 + 5)
            text_obj.setFont(self.fonte_texto, self.tamanho_texto)
            text_obj.setFillColor(colors.black)
            for linha_nome in linhas_nome:
                text_obj.textLine(linha_nome)
            pdf.drawText(text_obj)

            alinh_y = y + (len(linhas_nome) - 1) * 12 + 5
            draw_centered_text(valor, self.col_x[1], self.col_x[2], alinh_y)
            draw_centered_text(tipo, self.col_x[2], self.col_x[3], alinh_y)
            draw_centered_text(categoria, self.col_x[3], self.col_x[4], alinh_y)
            draw_centered_text(data, self.col_x[4], self.col_x[4] + 100, alinh_y)

            y -= altura

        desenhar_rodape()
        pdf.save()