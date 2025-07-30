import os
import sys
from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

if DEBUG_MODE:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
else:
    BASE_DIR = Path(sys.executable).parent
    
TRANSLATE_PATH = BASE_DIR  / "data"

class LanguageManager:
    def trocar_linguagem(app: QApplication, translator: QTranslator, idioma: str):
        app.removeTranslator(translator)
    
        path_qm = f"{str(TRANSLATE_PATH)}/translations_{idioma}.qm"
        if translator.load(path_qm):
            app.installTranslator(translator)
            #print(f"Idioma trocado para {idioma}") #DEBUG
        else:
            print(f"Não foi possível carregar o arquivo {path_qm}")