from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import QMessageBox
from pathlib import Path
import sys
current_script_path = Path(__file__).resolve()
parent_directory = current_script_path.parent.parent
sys.path.append(str(parent_directory / 'assets/png'))
sys.path.append(str(parent_directory))
from listas.dados_combo import lista_paises
import home_window
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
        
        #self.set_labels()

        self.btn_editar_email.clicked.connect(self.habilitar_edit_email) # type: ignore[attr-defined]
        self.btn_editar_senha.clicked.connect(self.habilitar_edit_senha) # type: ignore[attr-defined]
        self.btn_editar_ocupacao.clicked.connect(self.habilitar_edit_ocupacao) # type: ignore[attr-defined]
        self.btn_editar_celular.clicked.connect(self.habilitar_edit_celular) # type: ignore[attr-defined]
        self.btn_salvar.clicked.connect(self.salvar) # type: ignore[attr-defined]
        self.btn_desativar_conta.clicked.connect(self.desativar_conta) # type: ignore[attr-defined]
        

    def habilitar_edit_email(self):
        self.edit_email.setEnabled(not self.edit_email.isEnabled()) # type: ignore[attr-defined]
        self.edit_email.setFocus() # type: ignore[attr-defined]
    def habilitar_edit_senha(self):
        self.edit_senha.setEnabled(not self.edit_senha.isEnabled()) # type: ignore[attr-defined]
        self.edit_senha.setFocus() # type: ignore[attr-defined]
    def habilitar_edit_ocupacao(self):
        self.edit_ocupacao.setEnabled(not self.edit_ocupacao.isEnabled()) # type: ignore[attr-defined]
        self.edit_ocupacao.setFocus() # type: ignore[attr-defined]
    def habilitar_edit_celular(self):
        self.edit_celular.setEnabled(not self.edit_celular.isEnabled()) # type: ignore[attr-defined]
        self.edit_celular.setFocus() # type: ignore[attr-defined]
    
    def set_labels(self):
        usuario = self.get_usuario()

        nome = usuario["nome"]
        email = usuario["email"]
        senha = usuario["senha"]
        ocupacao = usuario["ocupacao"]
        celular = usuario["celular"]
        pais = usuario["pais"]
        salario = str(usuario["salario"])[:-3]

        self.lbl_nome.setText(nome)
        self.edit_email.setText(email)
        self.edit_senha.setText(senha)
        self.edit_ocupacao.setText(ocupacao)
        self.edit_celular.setText(celular)
        self.cmbox_pais.addItems(lista_paises) # type: ignore[attr-defined]
        index_pais = self.cmbox_pais.findText(pais, QtCore.Qt.MatchFlag.MatchContains)
        self.cmbox_pais.setCurrentIndex(index_pais)
        self.edit_salario.setText("R$" + salario + ".00")

    def get_usuario(self):
        id_usuario = ""

        with open("ActiveUser.txt", "r", encoding="utf-8") as f:
            id_usuario = f.readline().strip().replace("ID: ", "")

        query = "SELECT * FROM tb_usuario WHERE pk_usuario_id = %s"
        df = self.sql.pd_consultar(query, (id_usuario))

        usuario = df.iloc[0]  # Pega a primeira linha
        return usuario

    def salvar(self):
        email_temp = self.edit_email.text() # type: ignore[attr-defined]
        senha_temp = self.edit_senha.text() # type: ignore[attr-defined]
        ocupacao_temp = self.edit_ocupacao.text()
        celular_temp = re.sub(r'\D', '', self.edit_celular.text().strip()) # type: ignore[attr-defined]
        salario_temp = self.edit_salario.text().strip()

        regex_email = r"^[^@]+@[^@]+\.[^@]+$"
        regex_salario = r'^(R\$)?\d+(?:[.,]\d{1,2})?$'
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
            QtWidgets.QMessageBox.warning(self, "Erro", "O número de celular deve conter 13 dígitos numéricos.")
            return
        if not re.match(regex_salario, salario_temp):
            QtWidgets.QMessageBox.warning(self, "Erro", "Salário inválido.")
            return
        ddi = celular_temp[0:2]
        ddd = celular_temp[2:4]
        digitos_1 = celular_temp[4:-4]
        digitos_2 = celular_temp[-4:]
        celular_temp = f"+{ddi} ({ddd}) {digitos_1}-{digitos_2}"

        email = email_temp
        senha = senha_temp
        ocupacao = ocupacao_temp
        celular = celular_temp
        salario = self.edit_salario.text().replace("R$", "").replace(",", ".").strip()
        if '.' not in salario:
            salario += '.00'
        else:
            parte_decimal = salario.split('.')[-1]
            if len(parte_decimal) == 1:
                salario += '0'
        pais = self.cmbox_pais.currentText()

        try:
            # Atualiza o banco de dados
            query = "UPDATE tb_usuario SET email = %s, senha = %s, ocupacao = %s, celular = %s, salario = %s, pais = %s WHERE pk_usuario_id = %s"
            params = (email, senha, ocupacao, celular, salario, pais, self.get_usuario()["pk_usuario_id"])
            print(params)
            df = self.sql.editar(query, params)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erro", "Não foi possível alterar os dados de usuário.")
            print(e)
            return
        # Atualiza o lembrete_login.txt
        if os.path.exists("lembrete_login.txt"):
            with open("lembrete_login.txt", "w", encoding="utf-8") as f:
                f.write(f"{email}\n{senha}")

        QMessageBox.information(self, "Alterar dados", "Dados de perfil atualizados com sucesso.")

        print("\nEmail: " + email, "\nSenha: " + senha, "\nOcupação: " + ocupacao,
              "\nCelular: " + celular, "\nSalário: " + salario, "\nPaís: " + pais, "\n")
        
    def desativar_conta(self):
        try:
            query = "DELETE FROM tb_usuario WHERE pk_usuario_id = %s"
            df = self.sql.editar(query, (self.get_usuario()["pk_usuario_id"]))

            if os.path.exists("lembrete_login.txt"):
                os.remove("lembrete_login.txt")
            
            QMessageBox.information(self, "Conta desativada", "Conta desativada com sucesso.")

            #TODO: ir corretamente à tela de login após desativar a conta
            #self.hide()
            #self.home = home_window.HomeWindow()
            #self.home.showMaximized()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erro", "Não foi possível desativar a conta.")
            print(e)
            return