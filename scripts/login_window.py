from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6 import uic
import sys
import os
import atexit
from database import ConsultaSQL
from home_window import HomeWindow  # Só importa a classe, não executa nada ainda
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/LoginWindow.ui", self)
        self.sql = ConsultaSQL()
        
        self.cliente_id = 0
        self.login_status = False

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
        
        login_status = False

        if not email or not senha:
            QMessageBox.warning(self, "Erro", "Preencha o email e a senha.")
            return
            
        client_id, login_status = self.consulta_login(email, senha)    
            
        if login_status:
            self.abrir_homewindow()
            
        return client_id
            
    def consulta_login(self, email, senha):
        # Consulta segura (evitando SQL Injection)
        query = "SELECT * FROM tb_usuario WHERE email = %s AND senha = %s"
        df = self.sql.pd_consultar(query, (email, senha))
        
        if not df.empty:
            QMessageBox.information(self, "Login", "Login bem-sucedido!")

            self.cliente_id = df['pk_usuario_id'].iloc[0]
            self.login_status = True
            
            # Salvar o lembrete se necessário
            self.salvar_lembrete()
        
        else:
            QMessageBox.critical(self, "Erro", "Email ou senha incorretos!")
        
        return self.cliente_id, self.login_status
    
    def abrir_homewindow(self):
        self.hide()
        self.home = HomeWindow(self.cliente_id, self.login_status)
        self.home.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())