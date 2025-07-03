from PyQt6.QtGui import QPixmap, QPainter, QRegion, QBitmap
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from PyQt6.QtWidgets import QMessageBox
from database import ConsultaSQL
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from pathlib import Path
from shutil import copy2
import icons_rc
import sys
import re
import os

current_script_path = Path(__file__).resolve()
parent_directory = current_script_path.parent.parent
sys.path.append(str(parent_directory / 'assets/png'))
sys.path.append(str(parent_directory))

class ClienteWindow(QtWidgets.QMainWindow):
    btn_home_pressed = pyqtSignal()
    
    def __init__(self, cliente_id, login_status, home_window):
        super().__init__()

        # Carrega tela principal
        uic.loadUi(parent_directory / 'ui/ClienteWindow.ui', self)
        
        #appIcon = QtGui.QIcon("")
        #self.setWindowIcon(appIcon)
        
        self.sql = ConsultaSQL()
        
        self.cliente_id = cliente_id
        self.login_status = login_status
        self.home_window = home_window
        self.foto_bytes = None

        self.btn_editar_email.clicked.connect(self.habilitar_edit_email)
        self.btn_editar_senha.clicked.connect(self.habilitar_edit_senha)
        self.btn_editar_ocupacao.clicked.connect(self.habilitar_edit_ocupacao)
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
    def habilitar_edit_ocupacao(self):
        self.edit_ocupacao.setEnabled(not self.edit_ocupacao.isEnabled())
        self.edit_ocupacao.setFocus()
    def habilitar_edit_celular(self):
        self.edit_celular.setEnabled(not self.edit_celular.isEnabled())
        self.edit_celular.setFocus()
    
    def set_labels(self):
        lista_paises = [
            "Afeganistão", "África do Sul", "Albânia", "Alemanha", "Andorra", "Angola", "Antígua e Barbuda",
            "Arábia Saudita", "Argélia", "Argentina", "Armênia", "Austrália", "Áustria", "Azerbaijão",
            "Bahamas", "Bangladesh", "Barbados", "Bareine", "Bélgica", "Belize", "Benin", "Bielorrússia",
            "Bolívia", "Bósnia e Herzegovina", "Botsuana", "Brasil", "Brunei", "Bulgária", "Burquina Faso",
            "Burundi", "Butão", "Cabo Verde", "Camarões", "Camboja", "Canadá", "Catar", "Cazaquistão",
            "Chade", "Chile", "China", "Chipre", "Colômbia", "Comores", "Congo-Brazzaville", "Congo-Kinshasa",
            "Coreia do Norte", "Coreia do Sul", "Costa do Marfim", "Costa Rica", "Croácia", "Cuba", "Dinamarca",
            "Dominica", "Egito", "El Salvador", "Emirados Árabes Unidos", "Equador", "Eritreia", "Eslováquia",
            "Eslovênia", "Espanha", "Estados Unidos", "Estônia", "Eswatini", "Etiópia", "Fiji", "Filipinas",
            "Finlândia", "França", "Gabão", "Gâmbia", "Gana", "Geórgia", "Granada", "Grécia", "Guatemala",
            "Guiana", "Guiné", "Guiné-Bissau", "Guiné Equatorial", "Haiti", "Holanda", "Honduras", "Hungria",
            "Iémen", "Ilhas Marshall", "Ilhas Salomão", "Índia", "Indonésia", "Irã", "Iraque", "Irlanda",
            "Islândia", "Israel", "Itália", "Jamaica", "Japão", "Jordânia", "Kosovo", "Kuwait", "Laos",
            "Lesoto", "Letônia", "Líbano", "Libéria", "Líbia", "Liechtenstein", "Lituânia", "Luxemburgo",
            "Macedônia do Norte", "Madagáscar", "Malásia", "Malaui", "Maldivas", "Mali", "Malta", "Marrocos",
            "Maurício", "Mauritânia", "México", "Mianmar", "Micronésia", "Moçambique", "Moldávia", "Mônaco",
            "Mongólia", "Montenegro", "Namíbia", "Nauru", "Nepal", "Nicarágua", "Níger", "Nigéria", "Noruega",
            "Nova Zelândia", "Omã", "Palau", "Palestina", "Panamá", "Papua-Nova Guiné", "Paquistão", "Paraguai", "Peru",
            "Polônia", "Portugal", "Quênia", "Quirguistão", "Reino Unido", "República Centro-Africana",
            "República Dominicana", "República Tcheca", "Romênia", "Ruanda", "Rússia", "São Cristóvão e Névis",
            "São Marino", "São Tomé e Príncipe", "São Vicente e Granadinas", "Seicheles", "Senegal", "Serra Leoa",
            "Sérvia", "Singapura", "Síria", "Somália", "Sri Lanka", "Suazilândia", "Sudão", "Sudão do Sul",
            "Suécia", "Suíça", "Suriname", "Tailândia", "Taiwan", "Tajiquistão", "Tanzânia", "Timor-Leste",
            "Togo", "Tonga", "Trindade e Tobago", "Tunísia", "Turcomenistão", "Turquia", "Tuvalu", "Ucrânia",
            "Uganda", "Uruguai", "Uzbequistão", "Vanuatu", "Vaticano", "Venezuela", "Vietnã", "Zâmbia", "Zimbábue"
        ]
        usuario = self.get_usuario()

        nome = usuario["nome"].iloc[0]
        email = usuario["email"].iloc[0]
        senha = usuario["senha"].iloc[0]
        ocupacao = usuario["ocupacao"].iloc[0]
        celular = usuario["celular"].iloc[0]
        pais = usuario["pais"].iloc[0]
        #TODO: olhar isso daqui ó
        salario = str(usuario["salario"].iloc[0])[:-3]
        #salario = str(usuario["salario"].iloc[0]).split(".")[0]
        foto = usuario["foto"].iloc[0]

        self.lbl_nome.setText(nome)
        self.edit_email.setText(email)
        self.edit_senha.setText(senha)
        self.edit_ocupacao.setText(ocupacao)
        self.edit_celular.setText(celular)
        self.cmbox_pais.addItems(lista_paises)
        index_pais = self.cmbox_pais.findText(pais, QtCore.Qt.MatchFlag.MatchContains)
        self.cmbox_pais.setCurrentIndex(index_pais)
        self.edit_salario.setText("R$" + salario + ".00")
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
                QMessageBox.warning(self, "Erro", "Selecione uma imagem válida (.png, .jpg, .jpeg).")
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
        ocupacao_temp = self.edit_ocupacao.text()
        celular_temp = re.sub(r'\D', '', self.edit_celular.text().strip())
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
            if self.foto_bytes:
                query = "UPDATE tb_usuario SET email = %s, senha = %s, ocupacao = %s, celular = %s, salario = %s, pais = %s, foto = %s WHERE pk_usuario_id = %s"
                params = (email, senha, ocupacao, celular, salario, pais, self.foto_bytes, self.get_usuario()["pk_usuario_id"].iloc[0])
            else:
                query = "UPDATE tb_usuario SET email = %s, senha = %s, ocupacao = %s, celular = %s, salario = %s, pais = %sWHERE pk_usuario_id = %s"
                params = (email, senha, ocupacao, celular, salario, pais, self.get_usuario()["pk_usuario_id"].iloc[0])
            #print(params)
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
        
    def logoff(self):
        from login_window import LoginWindow #importação tardia pra evitar importação circular
        self.close()
        self.home_window.close()
        self.login_window = LoginWindow()
        self.login_window.show()
        
    def reopen_home(self):
        self.btn_home_pressed.emit()
        self.hide()
    
    def desativar_conta(self):
        try:
            query = "DELETE FROM tb_usuario WHERE pk_usuario_id = %s"
            df = self.sql.editar(query, (self.get_usuario()["pk_usuario_id"].iloc[0]))

            if os.path.exists("lembrete_login.txt"):
                os.remove("lembrete_login.txt")
            
            QMessageBox.information(self, "Conta desativada", "Conta desativada com sucesso.")

            from login_window import LoginWindow #importação tardia pra evitar importação circular
            self.close()
            self.home_window.close()
            self.login_window = LoginWindow()
            self.login_window.showMaximized()
        except Exception as e:
            QMessageBox.warning(self, "Erro", "Não foi possível desativar a conta.")
            print(e)
            return