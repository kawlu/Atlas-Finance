import json
from pathlib import Path
from src.util.db_manager import ConsultaSQL

# Bibliotecas para plotagem e manipulação de arrays numéricos
import matplotlib.pyplot as plt
import numpy as np

# Backend que integra matplotlib com interfaces Qt (PyQt5/PyQt6)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)
            translate_graph = data_util['traducao']['graph']
            translate_month = data_util['traducao']['meses']

# Classe responsável por exibir gráficos em um layout Qt
class Grafico():
    def __init__(self, destino_layout, cliente_id, linguagem_atual):
        self.destino_layout = destino_layout 
        self.sql = ConsultaSQL()       
        self.cliente_id = cliente_id       
        self.linguagem_atual = linguagem_atual

    # Atualiza o gráfico com base no mês selecionado
    def update_grafico(self, mes_selecionado=0):
        self.sql = ConsultaSQL()
        
        # Caso não seja selecionado mês específico, exibe gráfico por mês/ano agrupado
        if mes_selecionado == 0:
            query = """
            SELECT
                EXTRACT(YEAR FROM data_realizada) AS ano,
                EXTRACT(MONTH FROM data_realizada) AS mes,
                tipo,
                SUM(valor) AS total
            FROM tb_registro
            WHERE fk_usuario_id = %s
            GROUP BY ano, mes, tipo
            ORDER BY ano, mes, tipo;
            """
            df = self.sql.pd_consultar(query, int(self.cliente_id))
            
            if df.empty:
                self._plotar_grafico_vazio(translate_graph[self.linguagem_atual]['empty_graph'])
                return
            
            # Cria coluna com rótulo "Mês/Ano" para o eixo X do gráfico
            df["mes_ano"] = df.apply(
                lambda row: f"{translate_month[self.linguagem_atual][str(row['mes'])][:3]}/{int(row['ano'])}",
                axis=1
            )

            # Separa os dados em dois DataFrames: entradas e saídas
            df_pos = df[df["tipo"] == 'entrada'].set_index(["ano", "mes"])
            df_neg = df[df["tipo"] == 'saida'].set_index(["ano", "mes"])

            # Obtém os meses únicos ordenados para construir o eixo X
            chaves_ordenadas = df.drop_duplicates(["ano", "mes"]).sort_values(["ano", "mes"])[["ano", "mes", "mes_ano"]]
            mes_ano_labels = chaves_ordenadas["mes_ano"].tolist()
            x = np.arange(len(mes_ano_labels))  # Posições no eixo X

            valores_entrada = []
            valores_saida = []
            # Para cada mês/ano, adiciona o total de entrada e saída (0 se não existir)
            for _, row in chaves_ordenadas.iterrows():
                chave = (row["ano"], row["mes"])
                valores_entrada.append(df_pos.loc[chave, "total"] if chave in df_pos.index else 0)
                valores_saida.append(df_neg.loc[chave, "total"] if chave in df_neg.index else 0)
            
            # Chama função para plotar o gráfico com os dados gerados
            self._plotar_grafico(
                x, mes_ano_labels, valores_entrada, valores_saida,
                titulo=translate_graph[self.linguagem_atual]['monthly'], eixo_x=translate_graph[self.linguagem_atual]['mounth_year']
            )
        else:
            # Caso um mês específico seja selecionado, exibe gráfico comparando diferentes anos
            query = """
                SELECT 
                    EXTRACT(YEAR FROM data_realizada) AS ano,
                    tipo,
                    SUM(valor) AS total
                FROM tb_registro
                WHERE EXTRACT(MONTH FROM data_realizada) = %s AND fk_usuario_id = %s
                GROUP BY ano, tipo
                ORDER BY ano
            """
            df = self.sql.pd_consultar(query, (mes_selecionado, int(self.cliente_id)))

            if df.empty:
                self._plotar_grafico_vazio(translate_graph[self.linguagem_atual]['empty_graph'])
                return
            
            anos = sorted(df["ano"].unique())      # Lista dos anos existentes no filtro
            x = np.arange(len(anos))              # Posições no eixo X

            # Separa os dados por tipo
            df_pos = df[df["tipo"] == 'entrada'].set_index('ano')
            df_neg = df[df["tipo"] == 'saida'].set_index('ano')

            # Lista com os valores de entrada e saída por ano
            valores_entrada = [df_pos.loc[a, 'total'] if a in df_pos.index else 0 for a in anos]
            valores_saida = [df_neg.loc[a, 'total'] if a in df_neg.index else 0 for a in anos]

            # Nomes dos meses em português (manual, evita problemas com locale)
            meses_traduzidos = data_util["traducao"]["meses"][self.linguagem_atual]
            nome_mes = meses_traduzidos[str(mes_selecionado)]  # Nome do mês escolhido
            
            # Plota gráfico comparativo por ano
            self._plotar_grafico(
                x, [str(a) for a in anos], valores_entrada, valores_saida,
                titulo=f"{nome_mes} - {translate_graph[self.linguagem_atual]['year_comparison']}", eixo_x=translate_graph[self.linguagem_atual]['year']
            )

    # Função interna para plotar o gráfico com matplotlib
    def _plotar_grafico(self, x, labels, valores_entrada, valores_saida, titulo, eixo_x):
        self.limpar_grafico()  # Remove qualquer gráfico anterior

        fig, ax = plt.subplots()  # Cria a figura e o eixo
        fig.patch.set_facecolor('#dbdbdb')  # Cor de fundo da figura
        ax.set_facecolor('#dbdbdb')         # Cor de fundo do gráfico

        width = 0.35  # Largura das barras
        # Plota barras de entrada (esquerda)
        ax.bar(x - width/2, valores_entrada, width, label=translate_graph[self.linguagem_atual]['entries'], color="#057927")
        # Plota barras de saída (direita)
        ax.bar(x + width/2, valores_saida, width, label=translate_graph[self.linguagem_atual]['outcome'], color='#B40606')

        # Adiciona valores no topo de cada barra
        for i in range(len(x)):
            ax.text(x[i] - width/2, valores_entrada[i],
                    f"R${valores_entrada[i]:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
                    ha='center', va='bottom', fontsize=8, color="#057927")
            ax.text(x[i] + width/2, valores_saida[i],
                    f"R${valores_saida[i]:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
                    ha='center', va='bottom', fontsize=8, color='#B40606')
        
        # Configurações dos eixos
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.set_title(titulo, fontsize=14)
        ax.set_xlabel(eixo_x)
        #TODO Pegar a moeda do usuário se tiver essa opção
        ax.set_ylabel(f"{translate_graph[self.linguagem_atual]['total']} R$")
        ax.legend()  # Legenda do gráfico
        fig.tight_layout()  # Ajusta o layout da figura

        # Cria o canvas com o gráfico e adiciona ao layout Qt
        canvas = FigureCanvas(fig)
        canvas.updateGeometry()
        self.destino_layout.addWidget(canvas, stretch=1)

    def _plotar_grafico_vazio(self, mensagem):
        self.limpar_grafico()
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#dbdbdb')
        ax.set_facecolor('#dbdbdb')

        ax.text(0.5, 0.5, mensagem, fontsize=14, ha='center', va='center', transform=ax.transAxes, color='gray')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(translate_graph[self.linguagem_atual]['graph_title'], fontsize=14)

        canvas = FigureCanvas(fig)
        canvas.updateGeometry()
        self.destino_layout.addWidget(canvas, stretch=1)

    # Remove todos os widgets do layout (usado ao atualizar o gráfico)
    def limpar_grafico(self):
        for i in reversed(range(self.destino_layout.count())):
            widget = self.destino_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)