from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox, QMainWindow
import pymysql

from database import ConsultaSQL

class CadastroWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/CadastroWindow.ui", self)

        self.sql = ConsultaSQL()

        # Preenche os comboboxes
        self.cmb_ocupacao.addItems(self.get_ocupacoes())
        self.cmb_pais.addItems(self.get_paises())

        # Conectar botões
        self.btn_cadastro.clicked.connect(self.cadastrar_usuario)
        self.btn_login.clicked.connect(self.voltar_login)  # <- botão que retorna para a tela de login

    def voltar_login(self):
        from login_window import LoginWindow  # <- Importa aqui para evitar importações circulares
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def get_ocupacoes(self):
        return [
            "Administração", "Recursos Humanos", "Financeiro", "Contabilidade",
            "Marketing", "Comercial", "Vendas", "Atendimento ao Cliente",
            "Logística", "Transporte", "Tecnologia da Informação", "Desenvolvimento de Software",
            "Suporte Técnico", "Engenharia", "Jurídico", "Compras", "Produção", "Manutenção",
            "Qualidade", "Pesquisa e Desenvolvimento", "Educação", "Saúde", "Segurança do Trabalho",
            "Serviços Gerais", "Limpeza", "Almoxarifado", "Operações", "Planejamento",
            "Design", "Arquitetura", "Construção Civil", "Agropecuária", "Meio Ambiente",
            "Comunicação", "Eventos", "Moda", "Hotelaria", "Turismo", "Outros"
        ]

    def get_paises(self):
        return [
            "Brasil", "Argentina", "Estados Unidos", "Canadá", "França", "Alemanha",
            "Itália", "Portugal", "Reino Unido", "Japão", "China", "Índia", "Outros"
        ]

    def faixa_para_salario(self, faixa_str):
        faixa_dict = {
            "1500-2500": 2000.00,
            "2500-3500": 3000.00,
            "3500-5000": 4250.00,
            "5000+": 5500.00
        }
        return faixa_dict.get(faixa_str, 0.0)

    def limpar_campos(self):
        self.input_nome.clear()
        self.input_email.clear()
        self.input_senha.clear()
        self.input_confirmar_senha.clear()
        self.input_celular.clear()
        self.cmb_ocupacao.setCurrentIndex(0)
        self.cmb_objetivo.setCurrentIndex(0)
        self.cmb_faixa.setCurrentIndex(0)
        self.cmb_pais.setCurrentIndex(0)
        self.date_nascimento.setDate(self.date_nascimento.minimumDate())
        self.checkBox.setChecked(False)

    def cadastrar_usuario(self):
        nome = self.input_nome.text()
        email = self.input_email.text()
        senha = self.input_senha.text()
        confirmar = self.input_confirmar_senha.text()
        celular = self.input_celular.text()
        ocupacao = self.cmb_ocupacao.currentText()
        objetivo = self.cmb_objetivo.currentText()
        faixa = self.cmb_faixa.currentText()
        pais = self.cmb_pais.currentText()
        nascimento = self.date_nascimento.date().toString("yyyy-MM-dd")
        termos = self.checkBox.isChecked()

        if not termos:
            QMessageBox.warning(self, "Erro", "Você precisa aceitar os termos.")
            return

        if senha != confirmar:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return

        if not all([nome, email, senha, celular]) or ocupacao.startswith("Selecione") or objetivo.startswith("Selecione") or faixa.startswith("Selecione") or pais.startswith("Selecione"):
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos corretamente.")
            return

        try:
            salario = self.faixa_para_salario(faixa)

            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="root",
                database="db_finance"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tb_usuario (
                    nome, email, senha, celular, ocupacao, salario, pais, nascimento, situacao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nome, email, senha, celular, ocupacao, salario, pais, nascimento, 'ativa'
            ))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Cadastro realizado com sucesso!")
            self.limpar_campos()

        except pymysql.err.IntegrityError as e:
            QMessageBox.critical(self, "Erro", f"Erro de integridade: {e}")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erro de banco", str(e))
