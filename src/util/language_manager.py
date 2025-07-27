from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from pathlib import Path

TRANSLATE_PATH = Path(__file__).resolve().parent.parent.parent / "data"


class LanguageManager:
    def trocar_linguagem(app: QApplication, translator: QTranslator, idioma: str):
        app.removeTranslator(translator)
    
        path_qm = f"{str(TRANSLATE_PATH)}/translations_{idioma}.qm"
        if translator.load(path_qm):
            app.installTranslator(translator)
            print(f"Idioma trocado para {idioma}")
        else:
            print(f"Não foi possível carregar o arquivo {path_qm}")