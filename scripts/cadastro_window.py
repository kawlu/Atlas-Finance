from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QMainWindow
import sys
import pymysql

from database import ConsultaSQL

class CadastroWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("ui/CadastroWindow.ui", self)
        self.sql = ConsultaSQL()
        
        
    def limpar_campos(self):
        for campo in ["lineEdit", "lineEdit_2", "lineEdit_3", "lineEdit_4", "lineEdit_5", "lineEdit_6", "lineEdit_7", "lineEdit_9", "lineEdit_10"]:
            janela_principal.findChild(QtWidgets.QLineEdit, campo).clear()
        janela_principal.findChild(QtWidgets.QCheckBox, "checkBox").setChecked(False)
        
    def cadastrar_usuario(self):
        nome = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit").text()
        senha = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_2").text()
        celular = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_3").text()
        ocupacao = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_4").text()
        objetivo = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_5").text()
        email = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_6").text()
        senha_confirma = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_7").text()
        nascimento = janela_principal.findChild(QtWidgets.QDateEdit, "dateEdit").date().toString("yyyy-MM-dd")
        salario = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_9").text()
        pais = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_10").text()
        termos = janela_principal.findChild(QtWidgets.QCheckBox, "checkBox").isChecked()

        if not termos:
            QMessageBox.warning(janela_principal, "Erro", "Você precisa aceitar os termos.")
            return

        if senha != senha_confirma:
            QMessageBox.warning(janela_principal, "Erro", "As senhas não coincidem.")
            return

        if not all([nome, senha, celular, ocupacao, email, nascimento, salario, pais]):
            QMessageBox.warning(janela_principal, "Erro", "Preencha todos os campos.")
            return

        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="root",
                database="db_finance"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tb_usuario (nome, email, senha, celular, ocupacao, salario, pais, nascimento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, email, senha, celular, ocupacao, float(salario), pais, nascimento))
            conn.commit()
            conn.close()

            QMessageBox.information(janela_principal, "Sucesso", "Cadastro realizado com sucesso!")
            self.limpar_campos()
        except pymysql.MySQLError as e:
            QMessageBox.critical(janela_principal, "Erro de banco", str(e))
