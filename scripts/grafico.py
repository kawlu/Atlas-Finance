from database import ConsultaSQL
import matplotlib.pyplot as plt
import numpy as np
import calendar
import locale
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Exibir_Grafico():
    def __init__(self, destino_layout):
        self.destino_layout = destino_layout
        self.sql = ConsultaSQL()

    def update_grafico(self, mes_selecionado=0):
        if mes_selecionado == 0:
            try:
                locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            except:
                locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
            #Agrupamento por mês e ano
            df = self.sql.pd_consultar("""
                SELECT 
                    YEAR(data_realizada) AS ano,
                    MONTH(data_realizada) AS mes,
                    tipo,
                    SUM(valor) AS total
                FROM tb_registro
                GROUP BY ano, mes, tipo
                ORDER BY ano, mes, tipo
            """)

            if df.empty:
                self.limpar_grafico()
                return
                
            
            df["mes_ano"] = df.apply(
                lambda row: f"{calendar.month_abbr[row['mes']].capitalize()}/{int(row['ano'])}", axis=1
            )

            df_pos = df[df["tipo"] == 'entrada'].set_index(["ano", "mes"])
            df_neg = df[df["tipo"] == 'saída'].set_index(["ano", "mes"])

            chaves_ordenadas = df.drop_duplicates(["ano", "mes"]).sort_values(["ano", "mes"])[["ano", "mes", "mes_ano"]]
            mes_ano_labels = chaves_ordenadas["mes_ano"].tolist()
            x = np.arange(len(mes_ano_labels))

            valores_entrada = []
            valores_saida = []
            for _, row in chaves_ordenadas.iterrows():
                chave = (row["ano"], row["mes"])
                valores_entrada.append(df_pos.loc[chave, "total"] if chave in df_pos.index else 0)
                valores_saida.append(df_neg.loc[chave, "total"] if chave in df_neg.index else 0)
            
            self._plotar_grafico(
                x, mes_ano_labels, valores_entrada, valores_saida,
                titulo="Receita Mensal", eixo_x="Mês/Ano"
            )
        else:
            # Mostrar evolução do mês específico por ano
            df = self.sql.pd_consultar(f"""
                SELECT 
                    YEAR(data_realizada) AS ano,
                    tipo,
                    SUM(valor) AS total
                FROM tb_registro
                WHERE MONTH(data_realizada) = {mes_selecionado}
                GROUP BY ano, tipo
                ORDER BY ano
            """)

            if df.empty:
                self.limpar_grafico()
                return
            
            anos = sorted(df["ano"].unique())
            x = np.arange(len(anos))

            df_pos = df[df["tipo"] == 'entrada'].set_index("ano")
            df_neg = df[df["tipo"] == 'saída'].set_index("ano")

            valores_entrada = [df_pos.loc[a, "total"] if a in df_pos.index else 0 for a in anos]
            valores_saida = [df_neg.loc[a, "total"] if a in df_neg.index else 0 for a in anos]

            MESES_PT = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho","Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

            nome_mes = MESES_PT[mes_selecionado]
            
            self._plotar_grafico(
                x, [str(a) for a in anos], valores_entrada, valores_saida,
                titulo=f"{nome_mes} - Comparativo Anual", eixo_x="Ano"
            )

    def _plotar_grafico(self, x, labels, valores_entrada, valores_saida, titulo, eixo_x):
        self.limpar_grafico()

        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#dbdbdb')
        ax.set_facecolor('#dbdbdb')

        width = 0.35
        ax.bar(x - width/2, valores_entrada, width, label='Entradas', color="#057927")
        ax.bar(x + width/2, valores_saida, width, label='Saídas', color='#B40606')

        for i in range(len(x)):
            ax.text(x[i] - width/2, valores_entrada[i], f"R${valores_entrada[i]:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), 
                    ha='center', va='bottom', fontsize=8, color='black')
            ax.text(x[i] + width/2, valores_saida[i], f"R${valores_saida[i]:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."), 
                    ha='center', va='bottom', fontsize=8, color='black')
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.set_title(titulo, fontsize=14)
        ax.set_xlabel(eixo_x)
        ax.set_ylabel("Total R$")
        ax.legend()
        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.updateGeometry()
        self.destino_layout.addWidget(canvas, stretch=1)

    def limpar_grafico(self):
        for i in reversed(range(self.destino_layout.count())):
            widget = self.destino_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)