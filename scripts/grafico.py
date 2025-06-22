from database import ConsultaSQL

import matplotlib.pyplot as plt
import numpy as np
import calendar
import locale
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Exibir_Grafico():
    def __init__(self, destino_layout):
        self.destino_layout = destino_layout
        self.update_grafico()
        
        
    def update_grafico(self):
        sql = ConsultaSQL()
        df = sql.consultar("""
        SELECT 
        MONTH(data_realizada) AS mes,
        tipo,
        SUM(valor) AS total
        FROM tb_registro
        GROUP BY MONTH(data_realizada), tipo
        ORDER BY mes, tipo
        """)

        # Garante que há dados antes de tentar plotar
        if df.empty:
            print("Nenhum dado disponível para gerar o gráfico.")

        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Linux/Mac
        except:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')  # Windows fallback

        # Aplica os nomes dos meses em pt-br abreviados
        df["mes_nome"] = df["mes"].apply(lambda x: calendar.month_abbr[x].capitalize())

        # Lista única dos meses (ordenada)
        meses_unicos = df["mes"].unique()
        mes_labels = [calendar.month_abbr[m].capitalize() for m in meses_unicos]
        x = np.arange(len(meses_unicos))  # [0, 1, 2, ..., n]

        # Separa os dados por tipo
        df_pos = df[df["tipo"] == 'entrada'].set_index("mes")
        df_neg = df[df["tipo"] == 'saída'].set_index("mes")

        # Obtém os totais alinhados com os meses
        valores_entrada = [df_pos.loc[m, "total"] if m in df_pos.index else 0 for m in meses_unicos]
        valores_saida = [df_neg.loc[m, "total"] if m in df_neg.index else 0 for m in meses_unicos]

        # Tamanho da barra
        width = 0.35

        fig, ax = plt.subplots()

        # Barras lado a lado
        ax.bar(x - width/2, valores_entrada, width, label='Entradas', color='#0D192B')
        ax.bar(x + width/2, valores_saida, width, label='Saídas', color='#B40606')

        # Eixos e legenda
        ax.set_xticks(x)
        ax.set_xticklabels(mes_labels)
        ax.set_title("Receita Mensal", fontsize=14)
        ax.set_xlabel("Mês")
        ax.set_ylabel("Total R$")
        ax.legend()
        fig.tight_layout()
        
        
        canvas = FigureCanvas(fig)
        canvas.updateGeometry()

        #Redimensiona gráfico
        self.destino_layout.addWidget(canvas, stretch=1)
