from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtGui import QPixmap, QPainter, QRegion, QBitmap
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtCore import Qt
import pymysql
import re

from database import ConsultaSQL
from utilitarios import MessageBox

import lista
class CadastroWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/CadastroWindow.ui", self)

        self.sql = ConsultaSQL()
        self.foto_bytes = None

        
        lista_ocupacoes = lista.lista_ocupacoes
        lista_paises = lista.lista_paises
        # Preenche os comboboxes
        self.cmb_ocupacao.addItems(lista_ocupacoes)
        self.cmb_pais.addItems(lista_paises)

        # Conectar botões
        self.btn_cadastro.clicked.connect(self.cadastrar_usuario)
        self.btn_login.clicked.connect(self.voltar_login)  # <- botão que retorna para a tela de login
        self.edit_foto.clicked.connect(self.buscar_foto)

    def voltar_login(self):
        from login_window import LoginWindow  # <- Importa aqui para evitar importações circulares
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

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

        self.checar_campos(nome=nome, email=email, senha=senha, confirmar_senha=confirmar_senha, celular=celular,ocupacao=ocupacao,objetivo=objetivo,pais=pais, nascimento=nascimento)

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
                    nome, email, senha, celular, ocupacao, salario, pais, nascimento, foto situacao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nome, email, senha, celular, ocupacao, salario, pais, nascimento, self.foto_bytes, 'ativa'
            ))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Cadastro realizado com sucesso!")
            self.limpar_campos()

        except pymysql.err.IntegrityError as e:
            QMessageBox.critical(self, "Erro", f"Erro de integridade: {e}")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Erro de banco", str(e))

    def checar_campos(self, nome, email, senha, confirmar_senha, celular, ocupacao, objetivo, faixa, pais, nascimento):
        
        combobox_false = ocupacao.startswith("Selecione") or objetivo.startswith("Selecione") or faixa.startswith("Selecione") or pais.startswith("Selecione") or nascimento.startswith("Selecione")
        
        if not all([nome, email, senha, confirmar_senha, celular]) or combobox_false:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
            return 
        
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
        
    def checar_nome(self, nome):
        if not nome.isalpha() or len(nome) < 4:
            QMessageBox.warning(self, "Erro", "Nome inválido.")
            return False
        return True
    def checar_senha(self, senha):
        if ' ' in senha or len(senha) < 6:
            QMessageBox.warning(self, "Erro", "Senha inválida, evite espaços e insira pelo menos 6 carácteres.")
            return False
        return True
    def checar_confirmar_senha(self, senha, confirmar_senha):
        if senha != confirmar_senha:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return False
        return True
        
    def checar_email(self, email):
        regex_email = r"^[^@]+@[^@]+.[^@]+$"
        if not re.match(regex_email, email):
            MessageBox.show_custom_messagebox(self, "warning", "Aviso", "Email inválido.")
            return
        pass
    
    def checar_nascimento(self, nascimento):
        from datetime import datetime
        try:
            data_nascimento = datetime.strptime(nascimento, "%d/%m/%Y")
            idade = (datetime.today() - data_nascimento).days // 365
            if idade < 8:
                QMessageBox.warning(self, "Erro", "Idade mínima é de 8 anos.")
                return False
        except ValueError:
            QMessageBox.warning(self, "Erro", "Data de nascimento inválida.")
            return False
        return True