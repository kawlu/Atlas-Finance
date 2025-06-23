from database import ConsultaSQL

import matplotlib.pyplot as plt
import numpy as np
import calendar
import locale
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Exibir_Grafico():
    def __init__(self, destino_layout, lbl_warning):
        self.destino_layout = destino_layout
        self.lbl_warning = lbl_warning
        self.lbl_warning.setVisible(False)
        self.sql = ConsultaSQL()
        self.update_grafico()
        
    def update_grafico(self):
        df = self.sql.consultar("""
        SELECT 
        YEAR(data_realizada) AS ano,
        MONTH(data_realizada) AS mes,
        tipo,
        SUM(valor) AS total
        FROM tb_registro
        GROUP BY ano, mes, tipo
        ORDER BY ano, mes, tipo
        """)

        # Garante que há dados antes de tentar plotar
        if df.empty:
            self.lbl_warning.setVisible(True)
            return
        
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Linux/Mac
        except:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')  # Windows fallback

        # Aplica os nomes dos meses e anos em pt-br abreviados
        df["mes_ano"] = df.apply(lambda row: f"{calendar.month_abbr[row['mes']].capitalize()}/{int(row['ano'])}", axis=1)

        # Lista única dos meses (ordenada)
        meses_unicos = df["mes"].unique()
        mes_labels = [calendar.month_abbr[m].capitalize() for m in meses_unicos]
        x = np.arange(len(meses_unicos))  # [0, 1, 2, ..., n]

        # Separa os dados por tipo
        # Indexa os dataframes por (ano, mes)
        df_pos = df[df["tipo"] == 'entrada'].set_index(["ano", "mes"])
        df_neg = df[df["tipo"] == 'saída'].set_index(["ano", "mes"])

        # Garante a ordem correta dos pontos no eixo x
        chaves_ordenadas = df.drop_duplicates(["ano", "mes"]).sort_values(["ano", "mes"])[["ano", "mes", "mes_ano"]]

        mes_ano_labels = chaves_ordenadas["mes_ano"].tolist()
        x = np.arange(len(mes_ano_labels))

        # Alinha os valores de entrada e saída com as chaves ordenadas
        valores_entrada = []
        valores_saida = []
        for _, row in chaves_ordenadas.iterrows():
            chave = (row["ano"], row["mes"])
            valores_entrada.append(df_pos.loc[chave, "total"] if chave in df_pos.index else 0)
            valores_saida.append(df_neg.loc[chave, "total"] if chave in df_neg.index else 0)

        # Tamanho da barra
        width = 0.35

        fig, ax = plt.subplots()
        
        fig.patch.set_facecolor('#dbdbdb')
        ax.set_facecolor('#dbdbdb')

        # Barras lado a lado
        ax.bar(x - width/2, valores_entrada, width, label='Entradas', color="#057927")
        ax.bar(x + width/2, valores_saida, width, label='Saídas', color='#B40606')

        # Eixos e legenda
        ax.set_xticks(x)
        ax.set_xticklabels(mes_ano_labels, rotation=45)
        ax.set_title("Receita Mensal", fontsize=14)
        ax.set_xlabel("Mês/Ano")
        ax.set_ylabel("Total R$")
        ax.legend()
        fig.tight_layout()
        
        
        self.limpar_grafico()
                
        canvas = FigureCanvas(fig)
        canvas.updateGeometry()

        #Redimensiona gráfico
        self.destino_layout.addWidget(canvas, stretch=1)

    def limpar_grafico(self):
        for i in reversed(range(self.destino_layout.count())):
            widget = self.destino_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)