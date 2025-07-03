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
        
        #TODO colocar na função que vai usar
        ocupacao = [
            "Administração",
            "Recursos Humanos",
            "Financeiro",
            "Contabilidade",
            "Marketing",
            "Comercial",
            "Vendas",
            "Atendimento ao Cliente",
            "Logística",
            "Transporte",
            "Tecnologia da Informação",
            "Desenvolvimento de Software",
            "Suporte Técnico",
            "Engenharia",
            "Jurídico",
            "Compras",
            "Produção",
            "Manutenção",
            "Qualidade",
            "Pesquisa e Desenvolvimento",
            "Educação",
            "Saúde",
            "Segurança do Trabalho",
            "Serviços Gerais",
            "Limpeza",
            "Almoxarifado",
            "Operações",
            "Planejamento",
            "Design",
            "Arquitetura",
            "Construção Civil",
            "Agropecuária",
            "Meio Ambiente",
            "Comunicação",
            "Eventos",
            "Moda",
            "Hotelaria",
            "Turismo",
            "Outros"
        ]
        #TODO mesmo que o acima
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
        
    # def limpar_campos(self):
    #     for campo in ["lineEdit", "lineEdit_2", "lineEdit_3", "lineEdit_4", "lineEdit_5", "lineEdit_6", "lineEdit_7", "lineEdit_9", "lineEdit_10"]:
    #         janela_principal.findChild(QtWidgets.QLineEdit, campo).clear()
    #     janela_principal.findChild(QtWidgets.QCheckBox, "checkBox").setChecked(False)
        
    # def cadastrar_usuario(self):
    #     nome = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit").text()
    #     senha = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_2").text()
    #     celular = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_3").text()
    #     ocupacao = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_4").text()
    #     objetivo = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_5").text()
    #     email = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_6").text()
    #     senha_confirma = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_7").text()
    #     nascimento = janela_principal.findChild(QtWidgets.QDateEdit, "dateEdit").date().toString("yyyy-MM-dd")
    #     salario = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_9").text()
    #     pais = janela_principal.findChild(QtWidgets.QLineEdit, "lineEdit_10").text()
    #     termos = janela_principal.findChild(QtWidgets.QCheckBox, "checkBox").isChecked()

    #     if not termos:
    #         QMessageBox.warning(janela_principal, "Erro", "Você precisa aceitar os termos.")
    #         return

    #     if senha != senha_confirma:
    #         QMessageBox.warning(janela_principal, "Erro", "As senhas não coincidem.")
    #         return

    #     if not all([nome, senha, celular, ocupacao, email, nascimento, salario, pais]):
    #         QMessageBox.warning(janela_principal, "Erro", "Preencha todos os campos.")
    #         return

    #     try:
    #         conn = pymysql.connect(
    #             host="localhost",
    #             user="root",
    #             password="root",
    #             database="db_finance"
    #         )
    #         cursor = conn.cursor()
    #         cursor.execute("""
    #             INSERT INTO tb_usuario (nome, email, senha, celular, ocupacao, salario, pais, nascimento)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #         """, (nome, email, senha, celular, ocupacao, float(salario), pais, nascimento))
    #         conn.commit()
    #         conn.close()

    #         QMessageBox.information(janela_principal, "Sucesso", "Cadastro realizado com sucesso!")
    #         self.limpar_campos()
    #     except pymysql.MySQLError as e:
    #         QMessageBox.critical(janela_principal, "Erro de banco", str(e))
