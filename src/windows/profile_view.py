from PyQt6.QtGui import QPixmap, QPainter, QRegion, QBitmap
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from pathlib import Path

import sys
import re
import os

from src.util import icons_rc

from src.util.db_manager import ConsultaSQL

from src.util.qt_util import MessageBox
from src.util.crypto import CryptoManager

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"
UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui" / "profile.ui"

current_script_path = Path(__file__).resolve()
parent_directory = current_script_path.parent.parent
sys.path.append(str(parent_directory / 'assets/png'))
sys.path.append(str(parent_directory))

class ClienteWindow(QtWidgets.QMainWindow):
    btn_home_pressed = pyqtSignal()
    
    def __init__(self, cliente_id, login_status, home_window):
        super().__init__()

        uic.loadUi(UI_PATH, self)

        self.sql = ConsultaSQL()
        
        self.cliente_id = cliente_id
        self.login_status = login_status
        self.home_window = home_window
        self.foto_bytes = None

        self.btn_editar_email.clicked.connect(self.habilitar_edit_email)
        self.btn_editar_senha.clicked.connect(self.habilitar_edit_senha)
        self.btn_editar_celular.clicked.connect(self.habilitar_edit_celular)
        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_editar_foto.clicked.connect(self.buscar_foto)
        self.btn_logoff.clicked.connect(self.logoff)
        self.btn_desativar_conta.clicked.connect(self.desativar_conta)
        self.btn_home.clicked.connect(self.reopen_home)

    def habilitar_edit_email(self):
        self.edit_email.setEnabled(not self.edit_email.isEnabled())
        self.edit_email.setFocus()
    def habilitar_edit_senha(self):
        self.edit_senha.setEnabled(not self.edit_senha.isEnabled())
        self.edit_senha.setFocus()
    def habilitar_edit_celular(self):
        self.edit_celular.setEnabled(not self.edit_celular.isEnabled())
        self.edit_celular.setFocus()
    
    def set_labels(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)

        
        lista_paises = data_util['lista_paises']
        lista_ocupacoes = data_util['lista_ocupacoes']

        usuario = self.get_usuario()

        nome = usuario["nome"].iloc[0]
        email = usuario["email"].iloc[0]
        senha = usuario["senha"].iloc[0]
        ocupacao = usuario["ocupacao"].iloc[0]
        celular = usuario["celular"].iloc[0]
        pais = usuario["pais"].iloc[0]
        salario = usuario["salario"].iloc[0]
        foto = usuario["foto"].iloc[0]

        self.lbl_nome.setText(nome)
        self.edit_email.setText(email)
        self.edit_senha.setText(senha)
        self.edit_celular.setText(celular)

        self.cmbox_pais.addItems(lista_paises)
        index_pais = self.cmbox_pais.findText(pais, QtCore.Qt.MatchFlag.MatchContains)
        self.cmbox_pais.setCurrentIndex(index_pais)

        self.cmbox_ocupacao.addItems(lista_ocupacoes)
        index_ocupacao = self.cmbox_ocupacao.findText(ocupacao, QtCore.Qt.MatchFlag.MatchContains)
        self.cmbox_ocupacao.setCurrentIndex(index_ocupacao)

        index_salario = self.cmbox_salario.findText(salario, QtCore.Qt.MatchFlag.MatchContains)
        self.cmbox_salario.setCurrentIndex(index_salario)

        if foto:
            self.set_foto(foto)
        else:
            with open(str(parent_directory / 'assets/png/user.png'), 'rb') as f:
                self.foto_bytes = f.read()
            self.set_foto(self.foto_bytes)

    def get_usuario(self):
        query = "SELECT * FROM tb_usuario WHERE pk_usuario_id = %s"
        df = self.sql.pd_consultar(query, (self.cliente_id))

        return df

    def buscar_foto(self):
        # Abre janela para selecionar arquivo de imagem
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilters(["Imagens (*.png *.jpg *.jpeg)", "Todos os arquivos (*)"])
        file_dialog.selectNameFilter("Imagens (*.png *.jpg *.jpeg)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            # Verifica se é imagem válida
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                MessageBox.show_custom_messagebox(self, "error", "Erro", "Selecione uma imagem válida (.png, .jpg, .jpeg).")
                return
            
            with open(file_path, 'rb') as f:
                self.foto_bytes = f.read()
            self.set_foto(self.foto_bytes)

    def set_foto(self, foto_bytes):
        # Atualiza label da foto
        pixmap = QPixmap()
        pixmap.loadFromData(foto_bytes)
        pixmap = pixmap.scaled(375, 375, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        
        pixmap_redondo = QPixmap(375, 375)
        pixmap_redondo.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap_redondo)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QtGui.QPainterPath()
        path.addEllipse(0, 0, 375, 375)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.lbl_foto.setPixmap(pixmap_redondo)

    def salvar(self):
        email_temp = self.edit_email.text()
        senha_temp = self.edit_senha.text()
        celular_temp = re.sub(r'\D', '', self.edit_celular.text().strip())

        regex_email = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(regex_email, email_temp):
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Email inválido.")
            return
        if len(senha_temp) < 6:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "A senha deve ter ao menos 6 caracteres.")
            return
        elif ' ' in senha_temp:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "A senha não pode conter espaços.")
            return
        if not len(celular_temp) == 13:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "O número de celular deve conter 13 dígitos numéricos.")
            return
        ddi = celular_temp[0:2]
        ddd = celular_temp[2:4]
        digitos_1 = celular_temp[4:-4]
        digitos_2 = celular_temp[-4:]
        celular_temp = f"+{ddi} ({ddd}) {digitos_1}-{digitos_2}"

        email = email_temp
        senha = senha_temp
        celular = celular_temp
        
        pais = self.cmbox_pais.currentText()
        ocupacao = self.cmbox_ocupacao.currentText()
        salario = self.cmbox_salario.currentText()

        try:
            # Atualiza o banco de dados
            if self.foto_bytes:
                query = "UPDATE tb_usuario SET email = %s, senha = %s, ocupacao = %s, celular = %s, salario = %s, pais = %s, foto = %s WHERE pk_usuario_id = %s"
                params = (email, senha, ocupacao, celular, salario, pais, self.foto_bytes, self.get_usuario()["pk_usuario_id"].iloc[0])
            else:
                query = "UPDATE tb_usuario SET email = %s, senha = %s, ocupacao = %s, celular = %s, salario = %s, pais = %sWHERE pk_usuario_id = %s"
                params = (email, senha, ocupacao, celular, salario, pais, self.get_usuario()["pk_usuario_id"].iloc[0])
            df = self.sql.editar(query, params)
        except Exception as e:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "Não foi possível alterar os dados de usuário.")
            print(e)
            return
        
        # Atualiza o lembrete_login.bin
        if os.path.exists("lembrete_login.bin"):
            dados = f"{email}\n{senha}"
            with open("lembrete_login.bin", "wb") as f:
                f.write(CryptoManager.criptografar(dados))

        MessageBox.show_custom_messagebox(self, "information", "Alterar dados", "Dados de perfil atualizados com sucesso.")
        
        #DEBUG
        # print("\nEmail: " + email, "\nSenha: " + senha, "\nOcupação: " + ocupacao,
        #       "\nCelular: " + celular, "\nSalário: " + salario, "\nPaís: " + pais, "\n")
        
    def logoff(self):
        from src.windows.auth_login_view import LoginWindow #importação tardia pra evitar importação circular
        self.close()
        self.home_window.close()
        self.login_window = LoginWindow()
        self.login_window.show()
        
    def reopen_home(self):
        self.btn_home_pressed.emit()
        self.hide()
    
    def desativar_conta(self):
        confirmado = MessageBox.ask_confirmation(self, "Confirmação", "Tem certeza que deseja desativar a conta?")
        if confirmado:
            try:
                query = "UPDATE tb_usuario SET situacao = 'desativada' WHERE pk_usuario_id = %s"
                self.sql.editar(query, (self.get_usuario()["pk_usuario_id"].iloc[0]))

                if os.path.exists("lembrete_login.bin"):
                    os.remove("lembrete_login.bin")
                
                MessageBox.show_custom_messagebox(self, "information", "Conta desativada", "Conta desativada com sucesso.")

                from src.windows.auth_login_view import LoginWindow #importação tardia pra evitar importação circular
                self.close()
                self.home_window.close()
                self.login_window = LoginWindow()
                self.login_window.show()
            except Exception as e:
                MessageBox.show_custom_messagebox(self, "error", "Erro", "Não foi possível desativar a conta.")
                print(e)
                return