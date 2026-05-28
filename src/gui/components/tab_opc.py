# src/gui/components/tab_opc.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame, QTableWidget, 
                               QTableWidgetItem, QMessageBox, QCheckBox,
                               QAbstractItemView)
from PySide6.QtCore import Qt
from src.clp import VarDataType
from src.gui.custom_widgets import NoScrollComboBox
from src.test import TestScript

class TabOPC(QWidget):
    def __init__(self, roteiro : TestScript, parent=None):
        super().__init__(parent)
        self.roteiro = roteiro  # Recebe a referência do roteiro principal
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        lbl_info = QLabel("Configuração do mapeamento de Tags e Sinônimos do Roteiro")
        lbl_info.setStyleSheet("font-size: 18px; font-weight: bold; margin: 5px")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(lbl_info)

        frame_form = QFrame()
        frame_form.setFrameShape(QFrame.Shape.StyledPanel)
        layout_form = QHBoxLayout(frame_form)

        layout_form.addWidget(QLabel("TAG:"))
        self.txt_nome_opc = QLineEdit()
        self.txt_nome_opc.setFixedWidth(120)
        self.txt_nome_opc.setPlaceholderText("Ex: btLiga, motor")
        layout_form.addWidget(self.txt_nome_opc)
        layout_form.addStretch()

        layout_form.addWidget(QLabel("Tipo:"))
        self.combo_data_type = NoScrollComboBox()
        self.combo_data_type.setFixedWidth(140)
        self.combo_data_type.addItems(t.name for t in VarDataType.Basic)
        layout_form.addWidget(self.combo_data_type)

        self.checkbox_extended_type = QCheckBox("Extended")
        self.checkbox_extended_type.checkStateChanged.connect(self._atualiza_lista_tipos)
        layout_form.addWidget(self.checkbox_extended_type)

        layout_form.addStretch()

        layout_form.addWidget(QLabel("Sinônimos:"))
        self.txt_sinonimos_opc = QLineEdit()
        self.txt_sinonimos_opc.setPlaceholderText("Nomes das variáveis separados por vírgula")
        self.txt_sinonimos_opc.setFixedWidth(210)
        layout_form.addWidget(self.txt_sinonimos_opc)

        self.btn_adicionar_sinonimo_opc = QPushButton("➕ Add")
        self.btn_adicionar_sinonimo_opc.clicked.connect(self._adicionar_sinonimo_opc)
        layout_form.addWidget(self.btn_adicionar_sinonimo_opc)

        layout.addWidget(frame_form)

        self.table_dicionario_opc = QTableWidget(0, 3)
        self.table_dicionario_opc.setHorizontalHeaderLabels(["Tag Logística", "Tipo", "Sinônimos"])
        self.table_dicionario_opc.setColumnWidth(0, 200)
        self.table_dicionario_opc.setColumnWidth(1, 140)
        self.table_dicionario_opc.horizontalHeader().setStretchLastSection(True)
        self.table_dicionario_opc.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_dicionario_opc.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table_dicionario_opc)

        frame_botoes = QFrame()
        frame_botoes.setFrameShape(QFrame.Shape.NoFrame)
        layout_botoes = QHBoxLayout(frame_botoes)

        self.btn_editar_selecionado_opc = QPushButton("Editar Selecionado")        
        self.btn_editar_selecionado_opc.clicked.connect(self._editar_linha_selecionada_opc)

        self.btn_excluir_selecionado_opc = QPushButton("Excluir Selecionado")        
        self.btn_excluir_selecionado_opc.clicked.connect(self._excluir_linha_selecionada_opc)

        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_editar_selecionado_opc)
        layout_botoes.addWidget(self.btn_excluir_selecionado_opc)
        layout.addWidget(frame_botoes)

        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.table_dicionario_opc.setRowCount(0)
        for key, values in self.roteiro.dicionario_opc.items():
            row = self.table_dicionario_opc.rowCount()
            self.table_dicionario_opc.insertRow(row)
            self.table_dicionario_opc.setItem(row, 0, QTableWidgetItem(f"{key}"))
            type_text = QTableWidgetItem(values.get('type'))
            type_text.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_dicionario_opc.setItem(row, 1, type_text)
            self.table_dicionario_opc.setItem(row, 2, QTableWidgetItem(", ".join(values.get('alias'))))

    def _adicionar_sinonimo_opc(self):
        tag = self.txt_nome_opc.text().strip()
        tipo = self.combo_data_type.currentText()
        sinonimos_str = self.txt_sinonimos_opc.text().strip()      

        if not tag:
            QMessageBox.warning(self, "Aviso", "Insira o nome da Tag Logística.")
            return 
        if not sinonimos_str or "," not in sinonimos_str:
            QMessageBox.warning(self, "Aviso", "Insira os sinônimos separados por vírgula.")
            return
                
        sinonimos = sinonimos_str.replace(" ", "").split(",")                   
        self.roteiro.dicionario_opc[tag] = {'type' : tipo, 'alias' : sinonimos}
        
        self.txt_nome_opc.clear()
        self.txt_sinonimos_opc.clear()
        self.atualizar_tabela()

    def limpar_aba(self):
        self.roteiro.dicionario_opc.clear()
        self.atualizar_tabela()

    def _atualiza_lista_tipos(self):
        estado_atual = self.checkbox_extended_type.checkState()
        if estado_atual == Qt.CheckState.Checked:            
            self.combo_data_type.addItems(t.name for t in VarDataType.Extended)
        elif estado_atual == Qt.CheckState.Unchecked:
            self.combo_data_type.clear()
            self.combo_data_type.addItems(t.name for t in VarDataType.Basic)

    def _editar_linha_selecionada_opc(self):
        linha_selecionada = self.table_dicionario_opc.currentRow()

        # Verifica se o usuário selecionou alguma linha
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha na tabela para editar")
            return
        
        # Extrai os dados da linha selecionada na tabela
        tag = self.table_dicionario_opc.item(linha_selecionada, 0).text()
        tipo = self.table_dicionario_opc.item(linha_selecionada, 1).text()
        sinonimos = self.table_dicionario_opc.item(linha_selecionada, 2).text()

        # Tratamento do tipo de dado
        indice_tipo = self.combo_data_type.findText(tipo)

        # Se não achar na lista Basic, procura na lista Extended
        if indice_tipo == -1:
            self.checkbox_extended_type.setChecked(True)
            indice_tipo = self.combo_data_type.findText(tipo)

        if indice_tipo != -1:
            self.combo_data_type.setCurrentIndex(indice_tipo)
        else:
            QMessageBox.critical(self, "Erro", "Erro ao definir o tipo da variável.\nTente excluir a configuração e criar uma nova.")
            return
                
        # Preenche os campos com o dados extraídos
        self.txt_nome_opc.setText(tag)
        self.txt_sinonimos_opc.setText(sinonimos)

        # Remove a tag do roteiro para evitar duplicação
        if tag in self.roteiro.dicionario_opc:
            del self.roteiro.dicionario_opc[tag]

        self.atualizar_tabela()
    
    def _excluir_linha_selecionada_opc(self):
        linha_selecionada = self.table_dicionario_opc.currentRow()

        # Verifica se o usuário selecionou alguma linha
        if linha_selecionada < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha na tabela para editar")
            return
        
        tag = self.table_dicionario_opc.item(linha_selecionada, 0).text()
        
        # Confirma a exclusão
        resposta = QMessageBox.question(self, "Confirmar Exclusão",
                                        f"Deseja realmente exlcuir a configuração da tag \"{tag}\"?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Caso SIM seja selecionado, exclui a configuração do dicionário
        if resposta == QMessageBox.StandardButton.Yes:
            if tag in self.roteiro.dicionario_opc:
                del self.roteiro.dicionario_opc[tag]
        
        self.atualizar_tabela()