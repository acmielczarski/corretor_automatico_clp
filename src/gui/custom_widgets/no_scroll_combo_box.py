from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QStandardItemModel

class NoScrollComboBox(QComboBox):
    """
    Um QComboBox customizado que ignora eventos do Scroll do mouse.
    Isso evita alterações acidentais de valor quando o componente está dentro de um QScrollArea.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._modelo = QStandardItemModel(self)
        self.setModel(self._modelo)

    def wheelEvent(self, e):
        """Override do método do evento do mouse para ignorar o scroll"""
        e.ignore()

    def model(self) -> QStandardItemModel:
        return self._modelo