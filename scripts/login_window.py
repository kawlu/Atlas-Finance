from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6 import uic
import sys
import os
import atexit
from database import ConsultaSQL
from home_window import HomeWindow  # Só importa a classe, não executa nada ainda

# Função para apagar o arquivo ActiveUser.txt ao sair do programa
def limpar_arquivo_active_user():
    if os.path.exists("ActiveUser.txt"):
        os.remove("ActiveUser.txt")

# Registra a função para ser executada ao final
atexit.register(limpar_arquivo_active_user)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/LoginWindow.ui", self)
        self.sql = ConsultaSQL()

        self.pushButton_2.clicked.connect(self.login)
        self.checkBox.stateChanged.connect(self.salvar_lembrete)
        self.carregar_lembrete()

    def carregar_lembrete(self):
        if os.path.exists("lembrete_login.txt"):
            with open("lembrete_login.txt", "r", encoding="utf-8") as f:
                dados = f.read().splitlines()
                if len(dados) >= 2:
                    self.lineEdit.setText(dados[0])
                    self.lineEdit_2.setText(dados[1])
                    self.checkBox.setChecked(True)

    def salvar_lembrete(self):
        if self.checkBox.isChecked():
            with open("lembrete_login.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.lineEdit.text()}\n{self.lineEdit_2.text()}")
        else:
            if os.path.exists("lembrete_login.txt"):
                os.remove("lembrete_login.txt")

    def login(self):
        email = self.lineEdit.text()
        senha = self.lineEdit_2.text()

        if not email or not senha:
            QMessageBox.warning(self, "Erro", "Preencha o email e a senha.")
            return

        # Consulta segura (evitando SQL Injection)
        query = "SELECT * FROM tb_usuario WHERE email = %s AND senha = %s"
        df = self.sql.pd_consultar(query, (email, senha))

        if not df.empty:
            QMessageBox.information(self, "Login", "Login bem-sucedido!")

            # Salvar o lembrete se necessário
            self.salvar_lembrete()

            # Salvar os dados do usuário logado no arquivo ActiveUser.txt
            usuario = df.iloc[0]  # Pega a primeira linha

            with open("ActiveUser.txt", "w", encoding="utf-8") as f:
                f.write(f"ID: {usuario['pk_usuario_id']}\n")
                f.write(f"Nome: {usuario['nome']}\n")
                f.write(f"Email: {usuario['email']}\n")
                f.write(f"Senha: {usuario['senha']}\n")
                f.write(f"Celular: {usuario['celular']}\n")
                f.write(f"Ocupacao: {usuario['ocupacao']}\n")
                f.write(f"Salario: {usuario['salario']}\n")
                f.write(f"Nascimento: {usuario['nascimento']}\n")

            # Abrir a tela Home
            self.hide()
            self.home = HomeWindow()
            self.home.showMaximized()

        else:
            QMessageBox.critical(self, "Erro", "Email ou senha incorretos!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.showMaximized()
    sys.exit(app.exec())
