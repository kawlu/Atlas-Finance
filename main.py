from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from src.windows.auth_login_view import Login

from pathlib import Path
from dotenv import load_dotenv
import locale
import sys
import os

load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

if DEBUG_MODE:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
else:
    BASE_DIR = Path(sys.executable).parent

default_locale = locale.getlocale()  # Retorna tupla: ('pt_BR', 'xxxxxx')

def main():
    app = QApplication(sys.argv)
    translator = QTranslator()
    app.installTranslator(translator)
    try:
        window = Login(linguagem_atual=default_locale[0])
    except Exception as e:
        print(f"Idioma não reconhecido: {e}")
        window = Login(linguagem_atual='en_US')
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()