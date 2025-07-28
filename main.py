import sys
import locale
from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from src.windows.auth_login_view import Login
from pathlib import Path

TRANSLATE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "translations_pt.qm"
default_locale = locale.getlocale()  # Retorna tupla: ('pt_BR', 'xxxxxx')

def main():
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load(str(TRANSLATE_PATH))
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