import sys
from PyQt6.QtWidgets import QApplication
from src.windows.auth_login_view import Login

def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()