import re
import os
import sys
import json
from pathlib import Path
from datetime import datetime

from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt, QTranslator
from PyQt6.QtWidgets import QApplication, QMainWindow
from psycopg2 import IntegrityError, DatabaseError
import re

from src.util.db_manager import ConsultaSQL
from src.util.qt_util import MessageBox
from src.util.language_manager import LanguageManager as lm
from src.util import icons_rc

from src.windows.dashboard_view import HomeWindow

from dotenv import load_dotenv

load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

if DEBUG_MODE:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
else:
    BASE_DIR = Path(sys.executable).parent

DATA_PATH = BASE_DIR / "src" / "util" / "data_util.json"
UI_PATH = BASE_DIR / "ui" / "signup.ui"
BIN_PATH = BASE_DIR / "data" / "lembrete_login.bin"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data_util = json.load(f)
    translate = data_util['traducao']['mensage_box']


class SignUp(QMainWindow):
    def __init__(self, linguagem_atual):
        super().__init__()

        self.linguagem_atual = linguagem_atual
        translator = QTranslator()
        lm.trocar_linguagem(QApplication.instance(), translator, linguagem_atual)

        uic.loadUi(UI_PATH, self)

        self.sql = ConsultaSQL()
        self.foto_bytes = None

        self.cmb_ocupacao.addItems(data_util['list']['lista_ocupacoes'])
        self.cmb_pais.addItems(data_util['list']['lista_paises'])
        self.faixa = self.cmb_faixa.currentText()

        self.btn_cadastro.clicked.connect(self.cadastrar_usuario)
        self.btn_login.clicked.connect(self.voltar_login)
        self.edit_foto.clicked.connect(self.buscar_foto)

    def voltar_login(self):
        from src.windows.auth_login_view import Login
        self.login_window = Login(self.linguagem_atual)
        self.login_window.show()
        self.close()

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

    def buscar_foto(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilters(["Imagens (*.png *.jpg *.jpeg)", "Todos os arquivos (*)"])
        file_dialog.selectNameFilter("Imagens (*.png *.jpg *.jpeg)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['invalid_image_format'])
                return

            with open(file_path, 'rb') as f:
                self.foto_bytes = f.read()
            self.set_foto(self.foto_bytes)

    def set_foto(self, foto_bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(foto_bytes)
        pixmap = pixmap.scaled(215, 215, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)

        pixmap_redondo = QPixmap(215, 215)
        pixmap_redondo.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap_redondo)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addEllipse(0, 0, 215, 215)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.lbl_foto.setPixmap(pixmap_redondo)

    def cadastrar_usuario(self):
        nome = self.input_nome.text()
        email = self.input_email.text()
        senha = self.input_senha.text()
        confirmar_senha = self.input_confirmar_senha.text()
        celular = re.sub(r'\D', '', self.input_celular.text().strip())
        ocupacao = self.cmb_ocupacao.currentText()
        objetivo = self.cmb_objetivo.currentText()
        faixa = self.cmb_faixa.currentText()
        pais = self.cmb_pais.currentText()
        nascimento = self.date_nascimento.date().toString("yyyy-MM-dd")
        termos = self.checkBox.isChecked()

        if not termos:
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['terms_required'])
            return

        if not self.checar_campos(nome, email, senha, confirmar_senha, celular, ocupacao, objetivo, faixa, pais, nascimento):
            return

        if len(celular) != 13:
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['phone_length'])
            return

        if not self.sql.pd_consultar("SELECT 1 FROM tb_usuario WHERE email = %s LIMIT 1", (email,)).empty:
            MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['email_exists'])
            return

        if not self.sql.pd_consultar("SELECT 1 FROM tb_usuario WHERE celular = %s LIMIT 1", (celular,)).empty:
            MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['phone_exists'])
            return

        celular_formatado = f"+{celular[0:2]} ({celular[2:4]}) {celular[4:-4]}-{celular[-4:]}"

        try:
            self.sql.editar("""
                INSERT INTO tb_usuario (
                    nome, email, senha, celular, ocupacao, salario, pais, nascimento, foto, situacao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ativa')
            """, (nome, email, senha, celular_formatado, ocupacao, faixa, pais, nascimento, self.foto_bytes))

            MessageBox.show_custom_messagebox(self, tipo="information", title=translate[self.linguagem_atual]['success'], message=translate[self.linguagem_atual]['registration_success'])
            self.limpar_campos()
            
            self.logar(email, senha)
            self.hide()

        except IntegrityError as e:
            MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['db_error'])
            print(f"Erro de integridade: {e}")
        except DatabaseError as e:
            MessageBox.show_custom_messagebox(self, tipo="error", title=translate[self.linguagem_atual]['error'], message=translate[self.linguagem_atual]['db_error'])

    def checar_campos(self, nome, email, senha, confirmar_senha, celular, ocupacao, objetivo, faixa, pais, nascimento):
        if (
            not all([nome, email, senha, confirmar_senha, celular]) or
            ocupacao.startswith("Selecione") or
            objetivo.startswith("Selecione") or
            faixa.startswith("Selecione") or
            pais.startswith("Selecione")
        ):
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['fill_fields'])
            return False

        return (
            self.checar_nome(nome) and
            self.checar_email(email) and
            self.checar_senha(senha) and
            self.checar_confirmar_senha(senha, confirmar_senha) and
            self.checar_nascimento(nascimento)
        )

    def checar_nome(self, nome):
        nome_sem_espacos = nome.replace(' ', '')
        if not nome_sem_espacos.isalpha() or len(nome_sem_espacos) < 3 or nome.count(' ') < 1:
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['invalid_name'])
            return False
        return True

    def checar_senha(self, senha):
        if ' ' in senha or len(senha) < 6:
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['invalid_password'])
            return False
        return True

    def checar_confirmar_senha(self, senha, confirmar_senha):
        if senha != confirmar_senha:
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['password_mismatch'])
            return False
        return True

    def checar_email(self, email):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['invalid_email'])
            return False
        return True

    def checar_nascimento(self, nascimento):
        try:
            data = datetime.strptime(nascimento, "%Y-%m-%d")
            idade = (datetime.today() - data).days // 365
            if idade < 8:
                MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['minimum_age'])
                return False
        except ValueError:
            MessageBox.show_custom_messagebox(self, tipo="warning", title=translate[self.linguagem_atual]['warning'], message=translate[self.linguagem_atual]['invalid_birthdate'])
            return False
        return True

    def logar(self, email, senha):
        query = "SELECT * FROM tb_usuario WHERE email = %s AND senha = %s"
        df = self.sql.pd_consultar(query, (email, senha))
        client_id = df['pk_usuario_id'].iloc[0]
        if BIN_PATH.exists():
            BIN_PATH.unlink()
        self.home = HomeWindow(client_id, True, self.linguagem_atual)
        self.home.showMaximized()