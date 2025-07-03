import sys
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from balanco_window import tratar_valor_para_exibir
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

import cliente_window, balanco_window, relatorio_window
from database import ConsultaSQL
from atualizar_dados import Grafico

class HomeWindow(QMainWindow):
    def __init__(self, cliente_id, login_status):
        super().__init__()

        uic.loadUi("ui/HomeWindow.ui", self)

        # Janela secundária
        self.balanco_window = None
        self.perfil_window = None
        
        self.cliente_id = cliente_id
        self.login_status = login_status

        # Gráfico
        self.grafico = Grafico(self.frame_grafico.layout(), self.cliente_id)
        self.cmb_mes.currentIndexChanged.connect(self.atualizar_grafico_global)

        # Carrega inicialmente
        self.atualizar_grafico_global()
        self.carregar_ultimas_transacoes()
        self.carregar_totais()
        
        # Botões
        self.btn_relatorio.clicked.connect(self.btn_gerar_relatorio)
        self.btn_logoff.clicked.connect(self.logoff)
        self.btn_editar.clicked.connect(self.btn_balanco)
        self.btn_perfil.clicked.connect(self.btn_cliente)


    # === MÉTODOS DOS BOTÕES ===
    def btn_gerar_relatorio(self):
        popup = relatorio_window.RelatorioWindow(self.cliente_id)
        popup.exec()
        
    def btn_balanco(self):
        if not self.balanco_window:
            self.balanco_window = balanco_window.BalancoWindow(self.cliente_id)

            # Conexões com os sinais
            self.balanco_window.grafico_atualizado.connect(self.atualizar_grafico_global)
            self.balanco_window.transacoes_atualizadas.connect(self.carregar_ultimas_transacoes)
            self.balanco_window.totais_atualizados.connect(self.carregar_totais)
            
        self.balanco_window.exec()

    def btn_cliente(self):
        if not self.perfil_window:
            self.perfil_window = cliente_window.ClienteWindow(self.cliente_id, self.login_status, self)
        self.perfil_window.set_labels()
        self.hide()
        self.perfil_window.showMaximized()
        #self.unhide()

    def logoff(self):
        from login_window import LoginWindow #importação tardia pra evitar importação circular
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def atualizar_grafico_global(self):
        mes = self.cmb_mes.currentIndex()
        self.grafico.update_grafico(mes)

    # === ATUALIZAR TRANSACOES ===
    def carregar_ultimas_transacoes(self):
        try:
            db = ConsultaSQL()

            query = """
                SELECT nome, valor, tipo
                FROM tb_registro WHERE fk_usuario_id = %s
                ORDER BY transacao_id DESC
                LIMIT 3
            """
            registros = db.consultar(query, self.cliente_id)

            labels_nome = [self.lbl_produto1, self.lbl_produto2, self.lbl_produto3]
            labels_valor = [self.lbl_valor1, self.lbl_valor2, self.lbl_valor3]

            # Limpa os labels
            for label_nome, label_valor in zip(labels_nome, labels_valor):
                label_nome.setText("Sem registro")
                label_nome.setStyleSheet("font-size: 12pt; font-weight: bold;")
                
                label_valor.setText("")
                label_valor.setStyleSheet("color: black; font-size: 12pt; font-weight: bold;")

            # Preenche os dados
            for i, (nome, valor, tipo) in enumerate(registros):
                nome_formatado = str(nome).title()

                if tipo.lower() == 'saída':
                    valor_formatado = f"- {tratar_valor_para_exibir(float(valor))}"
                    cor = "#8D0A0A"
                else:
                    valor_formatado = tratar_valor_para_exibir(float(valor))
                    cor = "#147117"
                
                labels_nome[i].setText(nome_formatado)
                labels_nome[i].setStyleSheet(f"color: {cor}; font-size: 12pt; font-weight: bold;")
                labels_valor[i].setText(valor_formatado)
                labels_valor[i].setStyleSheet(f"color: {cor}; font-size: 12pt; font-weight: bold;")

        except Exception as e:
            print(f"Erro ao carregar últimas transações: {e}")

    # === ATUALIZAR TOTAIS DE RECEITA, DESPESA E SALDO ===
    def carregar_totais(self):
        try:
            db = ConsultaSQL()

            query = "SELECT tipo, valor FROM tb_registro WHERE fk_usuario_id = %s"
            dados = db.pd_consultar(query, self.cliente_id)

            if dados.empty:
                receita = 0
                despesa = 0
            else:
                receita = dados[dados['tipo'] == 'entrada']['valor'].sum()
                despesa = dados[dados['tipo'] == 'saída']['valor'].sum()

            saldo = receita - despesa

            receita_formatada = tratar_valor_para_exibir(receita)
            despesa_formatada = tratar_valor_para_exibir(despesa)
            saldo_formatada = tratar_valor_para_exibir(saldo)

            # Aplica nos labels
            self.lbl_value_receita.setText(receita_formatada)
            self.lbl_value_receita.setStyleSheet("color: #147117; font-size: 12pt; font-weight: bold;")

            self.lbl_value_despesa.setText(despesa_formatada)
            self.lbl_value_despesa.setStyleSheet("color: #8D0A0A; font-size: 12pt; font-weight: bold;")  # Vermelho

            if saldo >= 0:
                cor_saldo = "#147117"
            else:
                cor_saldo = "#8D0A0A"

            self.lbl_saldo_atual_value.setText(saldo_formatada)
            self.lbl_saldo_atual_value.setStyleSheet(f"color: {cor_saldo}; font-size: 12pt; font-weight: bold;")

        except Exception as e:
            print(f"Erro ao carregar totais: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.showMaximized()
    sys.exit(app.exec())