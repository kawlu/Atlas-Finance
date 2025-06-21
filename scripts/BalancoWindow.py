from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDialog
import sys

"""
Tela que mostra os registros (entradas e saídas) e linka a outra tela para adicionar mais registros
"""

#botões presentes: btn_add_registro e btn_excluir_registro
class BalancoWindow(QDialog):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("ui/BalancoWindow.ui", self)    # type: ignore
        
        self.novo_registro_window = None
        
        self.btn_add_registro.clicked.connect(self.btn_new_registro) # type: ignore
        
    def btn_new_registro(self):
        if not self.novo_registro_window:
            self.novo_registro_window = NovoRegistroWindow()
        self.novo_registro_window.show()
        
    
class NovoRegistroWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/NovoRegistroWindow.ui", self)     # type: ignore