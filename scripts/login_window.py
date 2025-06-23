from PyQt6 import QtWidgets, uic
import sys

app = QtWidgets.QApplication(sys.argv)

# Carrega tela principal
janela_principal = uic.loadUi("ui/login_window.ui")

# Exibe a janela principal
janela_principal.show()

sys.exit(app.exec())