from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtCore import Qt
import pymysql
import re

from src.util.db_manager import ConsultaSQL
from src.util.qt_util import MessageBox
from src.util import icons_rc

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "util" / "data_util.json"

class CadastroWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/CadastroWindow.ui", self)

        self.foto_bytes = None
        self.sql = ConsultaSQL()
        
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data_util = json.load(f)
        
        lista_ocupacoes = data_util.lista_ocupacoes
        lista_paises = data_util.lista_paises
        
        # Preenche os comboboxes
        self.cmb_ocupacao.addItems(lista_ocupacoes)
        self.cmb_pais.addItems(lista_paises)
        self.faixa = self.cmb_faixa.currentText()

        # Conectar botões
        self.btn_cadastro.clicked.connect(self.cadastrar_usuario)
        self.btn_login.clicked.connect(self.voltar_login)  # <- botão que retorna para a tela de login
        self.edit_foto.clicked.connect(self.buscar_foto)

    def voltar_login(self):
        from src.windows.login_window import LoginWindow  # <- Importa aqui para evitar importações circulares
        self.login_window = LoginWindow()
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
        nascimento_qdate = self.date_nascimento.date()
        nascimento = nascimento_qdate.toString("yyyy-MM-dd")
        termos = self.checkBox.isChecked()

        if not termos:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Você precisa aceitar os termos.")
            return

        # Validação de campos obrigatórios
        if not self.checar_campos(nome, email, senha, confirmar_senha, celular, ocupacao, objetivo, faixa, pais, nascimento):
            return
        
        if not len(celular) == 13:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "O número de celular deve conter 13 dígitos numéricos.")
            return

        # Verifica duplicidade de e-mail
        email_query = "SELECT 1 FROM tb_usuario WHERE email = %s LIMIT 1"
        if not self.sql.pd_consultar(email_query, (email,)).empty:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "E-mail já cadastrado.")
            return

        # Verifica duplicidade de celular
        celular_query = "SELECT 1 FROM tb_usuario WHERE celular = %s LIMIT 1"
        if not self.sql.pd_consultar(celular_query, (celular,)).empty:
            MessageBox.show_custom_messagebox(self, "error", "Erro", "Celular já cadastrado.")
            return
        
        ddi = celular[0:2]
        ddd = celular[2:4]
        digitos_1 = celular[4:-4]
        digitos_2 = celular[-4:]
        celular = f"+{ddi} ({ddd}) {digitos_1}-{digitos_2}"

        try:
            insert_query = """
                INSERT INTO tb_usuario (
                    nome, email, senha, celular, ocupacao, salario, pais, nascimento, foto, situacao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ativa')
            """
            valores = (
                nome, email, senha, celular, ocupacao,
                faixa, pais, nascimento, self.foto_bytes
            )

            self.sql.editar(insert_query, valores)

            QMessageBox.information(self, "Sucesso", "Cadastro realizado com sucesso!")
            self.limpar_campos()
            
            self.voltar_login()

        except pymysql.err.IntegrityError as e:
            MessageBox.show_custom_messagebox(self, "error", "Erro", f"Erro de integridade: {e}")
        except pymysql.MySQLError as e:
            MessageBox.show_custom_messagebox(self, "error", "Erro no banco de dados", str(e))



    def checar_campos(self, nome, email, senha, confirmar_senha, celular, ocupacao, objetivo, faixa, pais, nascimento):
        combobox_false = (
            ocupacao.startswith("Selecione") or
            objetivo.startswith("Selecione") or
            faixa.startswith("Selecione") or
            pais.startswith("Selecione")
        )

        if not all([nome, email, senha, confirmar_senha, celular]) or combobox_false:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Todos os campos devem ser preenchidos.")
            return False

        if not self.checar_nome(nome):
            return False
        if not self.checar_senha(senha):
            return False
        if not self.checar_confirmar_senha(senha, confirmar_senha):
            return False
        if not self.checar_email(email):
            return False
        if not self.checar_nascimento(nascimento):
            return False

        return True


    def checar_nome(self, nome):
        if not nome.isalpha() or len(nome) < 4:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Nome inválido.")
            return False
        return True

    def checar_senha(self, senha):
        if ' ' in senha or len(senha) < 6:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Senha inválida, evite espaços e insira pelo menos 6 caracteres.")
            return False
        return True

    def checar_confirmar_senha(self, senha, confirmar_senha):
        if senha != confirmar_senha:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "As senhas não coincidem.")
            return False
        return True

    def checar_email(self, email):
        regex_email = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(regex_email, email):
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Email inválido.")
            return False
        return True

    def checar_nascimento(self, nascimento):
        from datetime import datetime
        try:
            data_nascimento = datetime.strptime(nascimento, "%Y-%m-%d")
            idade = (datetime.today() - data_nascimento).days // 365
            if idade < 8:
                MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Idade mínima é de 8 anos.")
                return False
        except ValueError:
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Data de nascimento inválida.")
            return False
        return True
