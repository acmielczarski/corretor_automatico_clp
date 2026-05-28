# src/gui/dialog_config.py
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                               QDialog, QMessageBox, QTabWidget, QFileDialog)
from src.test import TestScript

# Importando as tabs
from src.gui.components import TabOPC, TabModbus, TabPassos
# from src.gui.components.tests import TabPassos

class JanelaConfigurarTeste(QDialog):
    """Janela secundária com Abas para gerenciar passos, regras OPC e mapas Modbus."""  

    def __init__(self, roteiro_atual: TestScript = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurador Avançado de Testes")
        self.setMinimumSize(750, 550)
        
        self.roteiro = roteiro_atual if roteiro_atual is not None else TestScript([])
        
        layout_principal = QVBoxLayout(self)
        
        # --- INSTANCIANDO AS ABAS ---
        self.tabs = QTabWidget()
        layout_principal.addWidget(self.tabs)  
        self.tabs.currentChanged.connect(self._notificar_abas)     
        
        # Injeta a referência do 'roteiro' em cada componente isolado
        self.tab_opc = TabOPC(self.roteiro, self)
        self.tab_modbus = TabModbus(self.roteiro, self)
        self.tab_passos = TabPassos(self.roteiro, self)

        self.tabs.addTab(self.tab_opc, "🔗 Dicionário OPC")
        self.tabs.addTab(self.tab_modbus, "⚙️ Mapeamento Modbus")
        self.tabs.addTab(self.tab_passos, "📍 Passos do Roteiro")             
        
        # --- BOTÕES DE AÇÃO GLOBAIS ---
        layout_botoes = QHBoxLayout()

        self.btn_novo = QPushButton("Novo")
        self.btn_novo.clicked.connect(self._novo_roteiro)
        layout_botoes.addWidget(self.btn_novo)

        self.btn_limpar = QPushButton("Limpar Aba Atual")
        self.btn_limpar.clicked.connect(self._limpar_aba_atual)
        layout_botoes.addWidget(self.btn_limpar)

        self.btn_carregar = QPushButton("Carregar")
        self.btn_carregar.clicked.connect(self._carregar_roteiro_json)
        layout_botoes.addWidget(self.btn_carregar)       
        
        layout_botoes.addStretch()

        self.btn_concluir = QPushButton("Salvar e Sair")
        self.btn_concluir.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_concluir.clicked.connect(self.accept_custom)
        layout_botoes.addWidget(self.btn_concluir)
        
        layout_principal.addLayout(layout_botoes)

    def _notificar_abas(self):
        """Ao mudar de aba, avisa os componentes para puxarem as tags novas do OPC"""
        aba_atual = self.tabs.currentIndex()
        if aba_atual == 1:
            self.tab_modbus.roteiro = self.roteiro
            self.tab_modbus.atualizar_tabela()
        elif aba_atual == 2:
            self.tab_passos.roteiro = self.roteiro
            self.tab_passos.atualizar_tabela()

    def _limpar_aba_atual(self):
        """Manda limar a aba atual de acordo com a aba aberta"""
        aba = self.tabs.currentIndex()
        # Delegação: o Orquestrador manda a aba se limpar
        if aba == 0 and QMessageBox.question(self, "Confirma", "Limpar OPC?") == QMessageBox.StandardButton.Yes:
            self.tab_opc.limpar_aba()
        elif aba == 1 and QMessageBox.question(self, "Confirma", "Limpar Modbus?") == QMessageBox.StandardButton.Yes:
            self.tab_modbus.limpar_aba()
        elif aba == 2 and QMessageBox.question(self, "Confirma", "Limpar Passos?") == QMessageBox.StandardButton.Yes:
            self.tab_passos.limpar_aba()

    def _novo_roteiro(self):
        """Cria um novo roteiro em branco, perguntando se deseja salvar ou não"""
        # Método para limpar o roteiro
        def __reseta_roteiro():
            self.roteiro.dicionario_opc.clear()
            self.roteiro.mapa_modbus.clear()
            self.roteiro.passos.clear()
            # Manda todo mundo se atualizar visualmente
            self.tab_opc.atualizar_tabela()
            self.tab_modbus.atualizar_tabela()
            self.tab_passos.atualizar_tabela()

        resposta = QMessageBox.question(self, "Criar novo roteiro", "Deseja realmente apagar o roteiro?\nTodos os dados de Tags OPC, Mapeamento Modbus e Passos serão perdidos.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Save)        
        
        if resposta == QMessageBox.StandardButton.Yes:
            __reseta_roteiro()
        elif resposta == QMessageBox.StandardButton.Save:
            self._salvar_roteiro_json()
            __reseta_roteiro()            

    def _carregar_roteiro_json(self):
        """Carrega roteiro e configuração de variáveis a partir de um JSON"""
        caminho, _ = QFileDialog.getOpenFileName(self, "Carregar Roteiro", "", "Arquivos JSON (*.json)")

        if caminho:
            resposta = QMessageBox.question(self, "Carregar Roteiro", "Deseja sobrescrever o roteiro atual?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Save)
            
            if resposta == QMessageBox.StandardButton.No:
                return
            elif resposta == QMessageBox.StandardButton.Save:
                self._salvar_roteiro_json()

            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                self.roteiro = TestScript.from_json(conteudo)                
                self.tab_opc.roteiro = self.roteiro
                self.tab_opc.atualizar_tabela()
                self.tab_modbus.roteiro = self.roteiro
                self.tab_modbus.atualizar_tabela()
                self.tab_passos.roteiro = self.roteiro
                self.tab_passos.atualizar_tabela()
                QMessageBox.information(self, "Sucesso", "Roteiro carregado com sucesso")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao processar JSON:\n{e}")

    def _salvar_roteiro_json(self):
        """Salva o roteiro JSON"""
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Roteiro", "", "Arquivos JSON (*.json)")
        if caminho:
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(self.roteiro.to_json())
                QMessageBox.information(self, "Sucesso", "Roteiro e Mapeamentos salvos com sucesso!")                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")

    def accept_custom(self):
        """Fecha a janela de Configuração de Teste"""
        resposta = QMessageBox.question(self, "Salvar", "Deseja carregar o roteiro configurado para o teste ativo?\nOs passos serão ordenados automaticamente de acordo com a tabela.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resposta == QMessageBox.StandardButton.Yes:
            self.accept()