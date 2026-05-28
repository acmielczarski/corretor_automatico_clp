# src/gui/components/tab_passos.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                               QPushButton, QFrame, QMessageBox)
from PySide6.QtCore import Qt, Slot, QTimer
from src.test import TestStep, Action, TestScript
from .card_passo import CardPassoTeste

#--------------------------------------------------------------------------------#
#                        ABA DE PASSOS (ORQUESTRADOR)                            #
#--------------------------------------------------------------------------------#
class TabPassos(QWidget):
    def __init__(self, roteiro : TestScript, parent=None):
        super().__init__(parent)
        self.roteiro = roteiro
        self._setup_ui()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        
        # Botão Superior para Adicionar
        frame_botao = QFrame()
        layout_botao = QHBoxLayout(frame_botao)
        self.btn_add_novo = QPushButton("➕ NOVO PASSO")
        self.btn_add_novo.setFixedHeight(35)
        self.btn_add_novo.setStyleSheet("background-color: #27ae60; font-weight: bold; color: white;")
        self.btn_add_novo.clicked.connect(self._adicionar_passo_vazio)
        layout_botao.addStretch()
        layout_botao.addWidget(self.btn_add_novo)
        layout_principal.addWidget(frame_botao)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.container_passos = QWidget()
        self.layout_passos = QVBoxLayout(self.container_passos)
        self.layout_passos.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.container_passos)
        layout_principal.addWidget(self.scroll_area)

        self.atualizar_tabela()    

    def atualizar_tabela(self, rolar_para_o_final : bool = False):
        """Reconstrói todos os cards com base na lista 'self.roteiro.passos'."""
        # Limpa layout
        while self.layout_passos.count():
            child = self.layout_passos.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        tags_opc = self.roteiro.dicionario_opc

        for i, passo in enumerate(self.roteiro.passos):
            # Verifica se o índice coincide com o passo criado anteriormente
            deve_iniciar_em_edicao = (hasattr(self, 'index_passo_novo') and i == self.index_passo_novo)

            card = CardPassoTeste(passo, i, tags_opc, iniciar_em_edicao=deve_iniciar_em_edicao, parent=self)
            
            # Conecta sinais de comando
            card.pedir_exclusao.connect(self._excluir_passo)
            card.pedir_subida.connect(self._subir_passo)
            card.pedir_descida.connect(self._descer_passo)
            card.pedir_atualizacao.connect(self.atualizar_tabela)          
            self.layout_passos.addWidget(card)

        # Limpa o indicador da memória após finalizar o redesenho, 
        # garantindo que ações futuras (como reordenações) não reativem a edição sozinhos
        self.index_passo_novo = None

        if rolar_para_o_final:
            QTimer.singleShot(80, self._rolar_para_o_final)

    def _adicionar_passo_vazio(self):
        novo = TestStep(Action.WRITE, description="Novo passo")
        self.roteiro.passos.append(novo)

        # Guarda o índice do elemento que acabou de ser criado
        self.index_passo_novo = len(self.roteiro.passos) - 1
        # Atualiza a lista com o passo novo
        self.atualizar_tabela(True)

    def _rolar_para_o_final(self):
        """Joga a barra de rolagem para o final do Scroll Area"""
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    @Slot(int)
    def _excluir_passo(self, index):
        if QMessageBox.question(self, "Excluir", f"Remover o passo #{index+1}?") == QMessageBox.StandardButton.Yes:
            self.roteiro.passos.pop(index)
            self.atualizar_tabela()

    @Slot(int)
    def _subir_passo(self, index):
        if index > 0:
            # Swap na lista
            self.roteiro.passos[index], self.roteiro.passos[index-1] = \
                self.roteiro.passos[index-1], self.roteiro.passos[index]
            self.atualizar_tabela()

    @Slot(int)
    def _descer_passo(self, index):
        if index < len(self.roteiro.passos) - 1:
            # Swap na lista
            self.roteiro.passos[index], self.roteiro.passos[index+1] = \
                self.roteiro.passos[index+1], self.roteiro.passos[index]
            self.atualizar_tabela()

    def limpar_aba(self):
        if QMessageBox.question(self, "Limpar", "Remover TODOS os passos?") == QMessageBox.StandardButton.Yes:
            self.roteiro.passos.clear()
            self.atualizar_tabela()