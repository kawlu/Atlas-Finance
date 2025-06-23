from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6 import uic
import sys
import os
from database import ConsultaSQL
from home_window import HomeWindow  # Só importa a classe, não executa nada ainda

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
            with open("lembrete_login.txt", "r") as f:
                dados = f.read().splitlines()
                if len(dados) >= 2:
                    self.lineEdit.setText(dados[0])
                    self.lineEdit_2.setText(dados[1])
                    self.checkBox.setChecked(True)

    def salvar_lembrete(self):
        if self.checkBox.isChecked():
            with open("lembrete_login.txt", "w") as f:
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

        query = f"""
            SELECT * FROM tb_usuario
            WHERE email = '{email}' AND senha = '{senha}'
        """
        df = self.sql.pd_consultar(query)

        if not df.empty:
            QMessageBox.information(self, "Login", "Login bem-sucedido!")

            self.salvar_lembrete()

            # Agora abre a tela Home
            self.hide()
            self.home = HomeWindow()
            self.home.show()

        else:
            QMessageBox.critical(self, "Erro", "Email ou senha incorretos!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
