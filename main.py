import sys
from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from src.windows.auth_login_view import Login
from pathlib import Path

TRANSLATE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "translations_pt.qm"

def main():
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load(str(TRANSLATE_PATH))
    app.installTranslator(translator)
    window = Login()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()