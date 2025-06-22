from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
import cliente_window, balanco_window, relatorio_window
import sys

from database import ConsultaSQL

"""
Tela HOME (se estiver logado), linka a todas as outras.. por enquanto ao menos
"""

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("ui/HomeWindow.ui", self)
        
        #Variável para verificar se as respectivas telas estão abertas
        self.balanco_window = None
        self.perfil_window = None
        
        #TODO Gerar o PDF contendo um relatório - a decidir estrutura
        # É UM POPUP de confirmação
        self.btn_relatorio.clicked.connect(self.btn_gerar_relatorio)
        self.btn_logoff.clicked.connect(self.btn_desconectar)
        self.btn_editar.clicked.connect(self.btn_balanco)
        self.btn_perfil.clicked.connect(self.btn_cliente)
        
     
    #MÉTODOS DOS BOTÕES   
    def btn_gerar_relatorio(self):
        popup = relatorio_window.RelatorioWindow()
        popup.exec() 
        
    def btn_balanco(self):
        if not self.balanco_window:
            self.balanco_window = balanco_window.BalancoWindow()
        self.balanco_window.show()
        
    def btn_cliente(self):
        if not self.perfil_window:
            self.perfil_window = cliente_window.ClienteWindow()
        self.perfil_window.showMaximized()
    
    #TODO
    def btn_desconectar(self):
        ...
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.showMaximized()
    sys.exit(app.exec())