from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDialog
import sys

"""
Tela para gerenciar perfil do cliente
"""

class ClienteWindow(QWidget):
    def __init__(self):
        super().__init__()
        #TODO Inserir aqui o nome do .ui corretamente
        uic.loadUi("", self)    # type: ignore