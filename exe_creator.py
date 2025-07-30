import subprocess
import shutil
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env e configurações
load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Ajuste conforme seus diretórios do projeto
PROJECT_ROOT = Path(__file__).resolve().parent
if DEBUG_MODE:
    BASE_DIR = PROJECT_ROOT
else:
    # Para build, assume que os dados serão colocados relativamentes
    BASE_DIR = PROJECT_ROOT

# Configuração principal
MAIN_SCRIPT = BASE_DIR / "main.py"
ICON_PATH = BASE_DIR / "assets" / "icon.ico"        # ícone (.ico)
DIST_DIR = BASE_DIR / "build" / "executavel"        # pasta de saída
DATA_TRANSLATION = BASE_DIR / "data" / "translations_pt_BR.qm"
DATA_JSON = BASE_DIR / "src" / "util" / "data_util.json"
UI_DIR = BASE_DIR / "ui"
DATA_PATH = BASE_DIR / "data"

DATA_DIR = BASE_DIR / "data"

DATA_TRANSLATIONS = [
    f"{str(arquivo)};data"
    for arquivo in DATA_DIR.glob("*.qm")
]


add_data_args = DATA_TRANSLATIONS + [
    f"{DATA_JSON};src/util",
    f"{UI_DIR};ui"
]

# Função principal de build
def build():
    # Limpa pasta de saída anterior
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    add_data_args = [
        f"{DATA_TRANSLATION};data",
        f"{DATA_JSON};src/util",
        f"{UI_DIR};ui"
    ]

    cmd = [
        "pyinstaller",
        str(MAIN_SCRIPT),
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--exclude-module", "PySide6",
        "--icon", str(ICON_PATH),
        "--distpath", str(DIST_DIR)
    ]

    for entry in add_data_args:
        cmd.extend(["--add-data", entry])

    print("Executando:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Build finalizado. Executável está em: {DIST_DIR}")

if __name__ == "__main__":
    build()