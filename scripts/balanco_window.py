from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem
import sys
from database import ConsultaSQL


# Conexão com o banco
db = ConsultaSQL()


class NovoRegistroWindow(QDialog):
    def __init__(self, balanco_window):
        super().__init__()
        uic.loadUi("ui/NovoRegistroWindow.ui", self)  # type: ignore
        self.balanco_window = balanco_window

        # Botão confirmar
        self.btn_Confirmar.clicked.connect(self.adicionar_registro)  # type: ignore

    def adicionar_registro(self):
        nome = self.input_Nome.text()
        tipo = self.cbox_Tipo.currentText()
        categoria = self.cbox_Categoria.currentText()
        data_realizada = self.input_Data.text()
        valor = self.input_Valor.text()

        if nome and tipo and categoria and data_realizada and valor:
            try:
                query = """
                    INSERT INTO tb_registro (nome, valor, moeda, tipo, categoria, data_realizada, fk_usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                valores = (nome, valor, 'BRL', tipo, categoria, data_realizada, 1)

                db.editar(query, valores)

                # Buscar o ID recém-inserido
                transacao_id = db.consultar("SELECT LAST_INSERT_ID()")[0][0]

                # Atualizar a tabela na interface principal
                self.balanco_window.adicionar_na_tabela(
                    (transacao_id, nome, tipo, categoria, data_realizada, valor)
                )

                self.close()

            except Exception as e:
                print("Erro ao inserir registro:", e)
        else:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha todos os campos corretamente.")


class BalancoWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/BalancoWindow.ui", self)  # type: ignore

        self.novo_registro_window = None

        self.btn_add_registro.clicked.connect(self.abrir_novo_registro)  # type: ignore
        self.btn_excluir_registro.clicked.connect(self.excluir_registro)  # type: ignore

        self.carregar_registros()

        # Opcional: esconder a coluna do ID visualmente
        self.tabela_Registros.setColumnHidden(0, True)

    def abrir_novo_registro(self):
        if not self.novo_registro_window:
            self.novo_registro_window = NovoRegistroWindow(self)
        self.novo_registro_window.show()

    def carregar_registros(self):
        try:
            query = """
                SELECT transacao_id, nome, tipo, categoria, data_realizada, valor
                FROM tb_registro
            """
            registros = db.consultar(query)

            self.tabela_Registros.setRowCount(0)

            for row_data in registros:
                self.adicionar_na_tabela(row_data)

        except Exception as e:
            print("Erro ao carregar registros:", e)

    def adicionar_na_tabela(self, dados):
        row_number = self.tabela_Registros.rowCount()
        self.tabela_Registros.insertRow(row_number)

        for column_number, data in enumerate(dados):
            self.tabela_Registros.setItem(
                row_number, column_number, QTableWidgetItem(str(data))
            )

    def excluir_registro(self):
        linha_selecionada = self.tabela_Registros.currentRow()

        if linha_selecionada < 0:
            QtWidgets.QMessageBox.warning(
                self, "Aviso", "Selecione um registro para excluir."
            )
            return

        # Pegando o ID (na coluna 0, que está escondida)
        transacao_id = self.tabela_Registros.item(linha_selecionada, 0).text()

        resposta = QtWidgets.QMessageBox.question(
            self,
            "Confirmação",
            f"Tem certeza que deseja excluir o registro ID {transacao_id}?",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )

        if resposta == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                sql = "DELETE FROM tb_registro WHERE transacao_id = %s"
                db.editar(sql, (transacao_id,))

                # Remove da interface
                self.tabela_Registros.removeRow(linha_selecionada)

                QtWidgets.QMessageBox.information(
                    self, "Sucesso", "Registro excluído com sucesso."
                )
            except Exception as erro:
                QtWidgets.QMessageBox.critical(
                    self, "Erro", f"Erro ao excluir registro:\n{erro}"
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BalancoWindow()
    window.show()
    sys.exit(app.exec())
