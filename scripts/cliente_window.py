from PyQt6 import QtCore, QtWidgets, QtGui, uic
from pathlib import Path
import sys
current_script_path = Path(__file__).resolve()
parent_directory = current_script_path.parent.parent
sys.path.append(str(parent_directory / 'assets/png'))
sys.path.append(str(parent_directory))
from listas.dados_combo import lista_paises
from database import ConsultaSQL
import icons_rc
import re
import os

class ClienteWindow(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Carrega tela principal
        uic.loadUi(parent_directory / 'ui/ClienteWindow.ui', self) # type: ignore[attr-defined]
        self.setWindowTitle("Atlas Finance - Usuário")
        appIcon = QtGui.QIcon("")
        self.setWindowIcon(appIcon)
        self.sql = ConsultaSQL()
        usuario = self.get_usuario()

        nome = ""
        email = ""
        senha = ""
        ocupacao = ""
        celular = ""
        pais = ""
        salario = ""

        with open ("ActiveUser.txt", "r", encoding="utf-8") as f:
            dados = f.read().splitlines()
            nome = dados[1]
            email = dados [2]
            senha = dados[3]
            celular = dados[4]
            ocupacao = dados[5]
            salario = dados[6][:-3]
            #TODO: atualizar o sql e o cadastro para incluir o país do usuário
            #TODO: atualizar o arquivo com os dados novos quando salvar

        self.lbl_nome.setText(nome)
        self.edit_email.setText(email)
        self.edit_senha.setText(senha)
        self.edit_ocupacao.setText(ocupacao)
        self.edit_celular.setText(celular)
        index = self.cmbox_salario.findText(salario, QtCore.Qt.MatchFlag.MatchContains)
        self.cmbox_salario.setCurrentIndex(index)

        self.btn_editar_email.clicked.connect(self.habilitar_edit_email) # type: ignore[attr-defined]
        self.btn_editar_senha.clicked.connect(self.habilitar_edit_senha) # type: ignore[attr-defined]
        self.btn_editar_celular.clicked.connect(self.habilitar_edit_celular) # type: ignore[attr-defined]
        self.btn_salvar.clicked.connect(self.salvar) # type: ignore[attr-defined]

        self.cmbox_pais.addItems(lista_paises) # type: ignore[attr-defined]

    def habilitar_edit_email(self):
        self.edit_email.setEnabled(not self.edit_email.isEnabled()) # type: ignore[attr-defined]
        self.edit_email.setFocus() # type: ignore[attr-defined]
    def habilitar_edit_senha(self):
        self.edit_senha.setEnabled(not self.edit_senha.isEnabled()) # type: ignore[attr-defined]
        self.edit_senha.setFocus() # type: ignore[attr-defined]
    def habilitar_edit_celular(self):
        self.edit_celular.setEnabled(not self.edit_celular.isEnabled()) # type: ignore[attr-defined]
        self.edit_celular.setFocus() # type: ignore[attr-defined]

    def get_usuario(self):
        id_usuario = ""

        with open("ActiveUser.txt", "r", encoding="utf-8") as f:
            id_usuario = f.readline().strip().replace("ID: ", "")

        query = "SELECT * FROM tb_usuario WHERE pk_usuario_id = %s"
        df = self.sql.pd_consultar(query, (id_usuario))

        usuario = df.iloc[0]  # Pega a primeira linha
        return usuario

    def salvar(self):
        #TODO: salvar os dados novos no banco de dados
        #TODO: verificar se nada mudou
        email_temp = self.edit_email.text() # type: ignore[attr-defined]
        senha_temp = self.edit_senha.text() # type: ignore[attr-defined]
        ocupacao_temp = self.edit_ocupacao.text()
        celular_temp = re.sub(r'\D', '', self.edit_celular.text().strip()) # type: ignore[attr-defined]

        regex_email = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(regex_email, email_temp):
            QtWidgets.QMessageBox.warning(self, "Erro", "Email inválido.")
            return
        if len(senha_temp) < 6:
            QtWidgets.QMessageBox.warning(self, "Erro", "A senha deve ter ao menos 6 caracteres.")
            return
        elif ' ' in senha_temp:
            QtWidgets.QMessageBox.warning(self, "Erro", "A senha não pode conter espaços.")
            return
        if not len(celular_temp) == 13:
            QtWidgets.QMessageBox.warning(self, "Erro", "O número de celular deve conter 12 dígitos numéricos.")
            return
        ddi = celular_temp[0:2]
        ddd = celular_temp[2:4]
        digitos_1 = celular_temp[4:-4]
        digitos_2 = celular_temp[-4:]
        celular_temp = f"+{ddi} ({ddd}) {digitos_1}-{digitos_2}"

        email = email_temp
        senha = senha_temp
        celular = celular_temp

        print("\nEmail: " + email, "\nSenha: " + senha,"\nCelular: " + celular, "\n")