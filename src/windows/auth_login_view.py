import json
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator
from PyQt6 import uic


import os

from src.util.db_manager import ConsultaSQL
from src.util.crypto import CryptoManager as cm
from src.util.language_manager import LanguageManager as lm
from src.util import icons_rc

from src.windows.auth_register_view import SignUp
from src.windows.dashboard_view import HomeWindow
from src.util.qt_util import MessageBox

from pathlib import Path

BIN_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "lembrete_login.bin"
UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "login.ui"
DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)
            translate = data_util['traducao']['mensage_box']

class Login(QMainWindow):
    def __init__(self, linguagem_atual):
        super().__init__()

        self.linguagem_atual = linguagem_atual

        translator = QTranslator()
        lm.trocar_linguagem(QApplication.instance(), translator, linguagem_atual)

        uic.loadUi(UI_PATH, self)
        self.sql = ConsultaSQL()
        
        self.cliente_id = 0
        self.login_status = False

        self.conectar_sinais()
        self.carregar_lembrete()
        self.carregar_lembrete()

    def carregar_lembrete(self):
        if BIN_PATH:
            try:
                with open(BIN_PATH, "rb") as f:
                    dados_criptografados = f.read()
                    dados = cm.descriptografar(dados_criptografados).splitlines()
                if len(dados) >= 2:
                    self.lineEdit.setText(dados[0])
                    self.lineEdit_2.setText(dados[1])
                    self.checkBox.setChecked(True)
            except FileNotFoundError:
                ...
                    
            except Exception as e:
                print(f"Erro ao tentar ler lembrete criptografado: {e}")

    def salvar_lembrete(self):
        if self.checkBox.isChecked():
            dados = f"{self.lineEdit.text()}\n{self.lineEdit_2.text()}"
            try:
                with open(BIN_PATH, "wb") as f:
                    f.write(cm.criptografar(dados))
            except Exception  as e:
                print(f"Erro ao salvar lembrete criptografado: {e}")
        else:
            if os.path.exists(BIN_PATH):
                os.remove(BIN_PATH)

    def fazer_login(self):
        email = self.lineEdit.text()
        senha = self.lineEdit_2.text()
        
        login_status = False

        if not email or not senha:
            MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['fill_email_password'])
            return
            
        client_id, login_status = self.consulta_login(email, senha)    
            
        if login_status:
            self.abrir_homewindow()
            
        return client_id
            
    def cadastro(self):
        self.hide()
        self.cadastro = SignUp(self.linguagem_atual)
        self.cadastro.show()
    
    def consulta_login(self, email, senha):
        query = "SELECT * FROM tb_usuario WHERE email = %s AND senha = %s"
        df = self.sql.pd_consultar(query, (email, senha))
        
        if not df.empty:
            if df['situacao'].iloc[0] != 'ativa':
                MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['error_account_deactivated'])
                return 0, False
            
            MessageBox.show_custom_messagebox(self, tipo="information", title=translate[self.linguagem_atual]['information'], message=translate[self.linguagem_atual]['login_success'])

            self.cliente_id = df['pk_usuario_id'].iloc[0]
            self.login_status = True
            
            self.salvar_lembrete()
        else:
            MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['wrong_email_password'])
        
        return self.cliente_id, self.login_status
    
    def abrir_homewindow(self):
        self.hide()
        self.home = HomeWindow(self.cliente_id, self.login_status, self.linguagem_atual)
        self.home.showMaximized()

    def trocar_linguagem(self, linguagem):
        self.linguagem_atual = linguagem
        translator = QTranslator()
        lm.trocar_linguagem(QApplication.instance(), translator, linguagem)

        email_temp = self.lineEdit.text()
        senha_temp = self.lineEdit_2.text()
        lembrete_temp = self.checkBox.isChecked()

        uic.loadUi(UI_PATH, self)
        self.conectar_sinais()

        self.lineEdit.setText(email_temp)
        self.lineEdit_2.setText(senha_temp)
        self.checkBox.setChecked(lembrete_temp)

        #self.retranslateUi()  só existe quando o .ui é convertido para .py

    def conectar_sinais(self):
        self.btn_login.clicked.connect(self.fazer_login)
        self.btn_cadastro.clicked.connect(self.cadastro)
        self.switchPtBr.triggered.connect(lambda: self.trocar_linguagem('pt_BR'))
        self.switchEnUs.triggered.connect(lambda: self.trocar_linguagem('en_US'))
        self.checkBox.stateChanged.connect(self.salvar_lembrete)