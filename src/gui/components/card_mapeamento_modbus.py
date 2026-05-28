from PySide6.QtWidgets import (QHBoxLayout, QLabel, 
                               QLineEdit, QFrame)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from src.clp import ModbusType
from src.gui.custom_widgets import NoScrollComboBox

#--------------------------------------------------------------------------------#
#        WIDGET CUSTOMIZADO: UMA LINHA DINÂMICA DE MAPEAMENTO MODBUS             #
#--------------------------------------------------------------------------------#
class LinhaMapeamentoModbus(QFrame):
    """
    Widget contendo um QHLayout dentro de um QFrame que representa uma única Tag.
    Dispara um sinal customizado sempre que o endereço ou tipo for alterado.
    """
    # Define o Sinal: (nome_da_tag, tipo_modbus, endereco_int)
    mapeamento_alterado = Signal(str, str, int)

    def __init__(self, tag_name: str, tipo_inicial: str = "COIL", endereco_inicial: int = 0, parent=None):
        super().__init__(parent)
        self.tag_name = tag_name
        
        # Estilização básica de bloco/linha comercial
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 6px; padding: 2px; }")
        
        layout = QHBoxLayout(self)
        
        # 1. Nome da Tag Logística (Fixo, vindo do OPC)
        self.lbl_tag = QLabel(self.tag_name)
        self.lbl_tag.setStyleSheet("font-weight: bold; color: #f5f5f5;")
        self.lbl_tag.setMinimumWidth(150)
        layout.addWidget(self.lbl_tag)
        
        layout.addStretch()

        # 2. ComboBox para Seleção do Tipo Modbus
        layout.addWidget(QLabel("Tipo:"))
        self.combo_tipo = NoScrollComboBox()
        self.combo_tipo.addItems([t.name for t in ModbusType])        
        self.combo_tipo.setCurrentText(tipo_inicial)
        self._ajustar_operacao_por_tipo(tipo_inicial)
        self.combo_tipo.setFixedWidth(200)
        self.combo_tipo.currentTextChanged.connect(self._notificar_alteracao)
        layout.addWidget(self.combo_tipo)

        # 3. LineEdit para o Endereço Físico
        layout.addWidget(QLabel("Endereço:"))
        self.txt_endereco = QLineEdit()
        self.txt_endereco.setFixedWidth(80)
        self.txt_endereco.setValidator(QIntValidator(bottom=0))  # Apenas inteiros positivos
        self.txt_endereco.setText(str(endereco_inicial))
        self.txt_endereco.textChanged.connect(self._notificar_alteracao)
        layout.addWidget(self.txt_endereco)

    def _notificar_alteracao(self):
        """Captura os dados atuais do componente e emite o sinal para o parent."""
        tipo = self.combo_tipo.currentText()
        addr_str = self.txt_endereco.text().strip()
        
        # Se o campo de endereço estiver temporariamente vazio enquanto o usuário digita, assume 0
        addr = int(addr_str) if addr_str else 0
        
        # Dispara o sinal enviando os dados encapsulados para quem estiver escutando
        self.mapeamento_alterado.emit(self.tag_name, tipo, addr)

    def _ajustar_operacao_por_tipo(self, tipo_inicial : str):
        modelo = self.combo_tipo.model()

        for i in range(modelo.rowCount()):
            modelo.item(i).setEnabled(True)
        
        if tipo_inicial == ModbusType.COIL.name or tipo_inicial == ModbusType.INPUT_STATUS.name: 
            itens_to_disable = [ModbusType.HOLDING_REGISTER.name, ModbusType.INPUT_REGISTER.name]
        else:            
            itens_to_disable = [ModbusType.COIL.name, ModbusType.INPUT_STATUS.name]           

        for i in range(modelo.rowCount()):
            if modelo.item(i).text() in itens_to_disable:
                modelo.item(i).setEnabled(False)
            
