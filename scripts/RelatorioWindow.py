from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDialog
import sys

"""
POPUP que vai confirmar e gerar o pdf
"""

class RelatorioWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("", self)  # type: ignore