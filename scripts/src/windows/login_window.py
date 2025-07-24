from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic


import os

from src.util.database import ConsultaSQL
from src.util.crypto import criptografar, descriptografar
from src.util import icons_rc

from src.windows.cadastro_window import CadastroWindow
from src.windows.home_window import HomeWindow
from src.util.qt_util import MessageBox

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/LoginWindow.ui", self)
        self.sql = ConsultaSQL()
        
        self.cliente_id = 0
        self.login_status = False

        self.btn_login.clicked.connect(self.login)
        self.btn_cadastro.clicked.connect(self.cadastro)
        
        self.checkBox.stateChanged.connect(self.salvar_lembrete)
        self.carregar_lembrete()

    def carregar_lembrete(self):
        if os.path.exists("lembrete_login.bin"):
            try:
                with open("lembrete_login.bin", "rb") as f:
                    dados_criptografados = f.read()
                    dados = descriptografar(dados_criptografados).splitlines()
                if len(dados) >= 2:
                    self.lineEdit.setText(dados[0])
                    self.lineEdit_2.setText(dados[1])
                    self.checkBox.setChecked(True)
            except Exception as e:
                print(f"Erro ao abrir lembrete criptografado: {e}")

    def salvar_lembrete(self):
        if self.checkBox.isChecked():
            dados = f"{self.lineEdit.text()}\n{self.lineEdit_2.text()}"
            try:
                with open("lembrete_login.bin", "wb") as f:
                    f.write(criptografar(dados))
            except Exception as e:
                print(f"Erro ao salvar lembrete criptografado: {e}")
        else:
            if os.path.exists("lembrete_login.bin"):
                os.remove("lembrete_login.bin")

    def login(self):
        email = self.lineEdit.text()
        senha = self.lineEdit_2.text()
        
        login_status = False

        if not email or not senha:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "Preencha o email e a senha.")
            return
            
        client_id, login_status = self.consulta_login(email, senha)    
            
        if login_status:
            self.abrir_homewindow()
            
        return client_id
            
    def cadastro(self):
        self.hide()
        self.home = CadastroWindow()
        self.home.show()
    
    def consulta_login(self, email, senha):
        query = "SELECT * FROM tb_usuario WHERE email = %s AND senha = %s"
        df = self.sql.pd_consultar(query, (email, senha))
        
        if not df.empty:
            if df['situacao'].iloc[0] != 'ativa':
                MessageBox.show_custom_messagebox(self, "error", "Erro", "Conta desativada!")
                return 0, False
            MessageBox.show_custom_messagebox(self, "information", "Login", "Login bem-sucedido!")

            self.cliente_id = df['pk_usuario_id'].iloc[0]
            self.login_status = True
            
            self.salvar_lembrete()
        
        else:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "Email ou senha incorretos!")
        
        return self.cliente_id, self.login_status
    
    def abrir_homewindow(self):
        self.hide()
        self.home = HomeWindow(self.cliente_id, self.login_status)
        self.home.showMaximized()