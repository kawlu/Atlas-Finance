from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

class MessageBox():
    def show_custom_messagebox(parent, tipo, title, message):
            box = QMessageBox(parent)
            box.setWindowTitle(title)
            box.setText(message)
            if tipo == "warning":
                box.setIcon(QMessageBox.Icon.Warning)
            elif tipo == "information":
                box.setIcon(QMessageBox.Icon.Information)
            elif tipo == "error":
                box.setIcon(QMessageBox.Icon.Critical)

            box.setStyleSheet("""
                QMessageBox {
                    background-color: #DBDBDB;
                }

                QLabel {
                    color: #0D192B;
                    font-size: 14px;
                    background-color: transparent;
                }
                            
                QPushButton {
                    background-color: #0D192B;
                    color: #DBDBDB;
                    padding: 6px 14px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    qproperty-cursor: PointingHandCursor;
                }

                QPushButton:hover {
                    background-color: #1A2A46;
                    padding-top: 7px;
                }
                              
                QPushButton:pressed {
                    background-color: #1A2A46;
                    padding-top: 8px;
                }
            """)

            ok_button = box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            ok_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            box.exec()
    
    def ask_confirmation(parent, title, message):
        box = QMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(QMessageBox.Icon.Question)

        btn_sim = box.addButton("SIM", QMessageBox.ButtonRole.YesRole)
        btn_nao = box.addButton("NÃO", QMessageBox.ButtonRole.NoRole)

        btn_sim.setObjectName("btn_sim")
        btn_nao.setObjectName("btn_nao")

        btn_sim.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_nao.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        box.setStyleSheet("""
            QMessageBox {
                background-color: #DBDBDB;
            }

            QLabel {
                color: #0D192B;
                font-size: 14px;
                background-color: transparent;
            }
                                    
            QPushButton#btn_sim {
                background-color: #147117;
                color: #DBDBDB;
                padding: 6px 14px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
                          
            QPushButton#btn_nao{
                background-color: #8D0A0A;
                color: #DBDBDB;
                padding: 6px 14px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
                          
            QPushButton#btn_sim:hover {
                padding-top: 7px;
                background-color: #116514;
            }
                          
            QPushButton#btn_sim:pressed {
                padding-top: 9px;
                background-color: #0D570F;
            }
                          
            QPushButton#btn_nao:hover {
                padding-top: 7px;
                background-color: #790A0A;
            }
                          
            QPushButton#btn_nao:pressed {
                padding-top: 9px;
                background-color: #770909;
            }
        """)

        box.exec()

        return box.clickedButton() == btn_sim