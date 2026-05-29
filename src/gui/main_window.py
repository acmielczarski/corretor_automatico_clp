# src/gui/main_window
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QComboBox, QLineEdit,
                               QPushButton, QTextEdit, QFrame, QDialog, 
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont
from qasync import asyncSlot

# Import da janela Popup
from .dialog_config import JanelaConfigurarTeste

# Importações dos módulos de comunicação e teste
from src.clp import Protocol, OpcClpClient, ModbusClpClient, ModbusType
from src.test import TestEngine, TestScript

class AvaliadorCLPGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avaliador Automático de CLP v1.0")
        self.setBaseSize(800, 600)
        
        self.clp = None

        # Carregamento do roteiro padrão do programa
        roteiro_padrao = "roteiro_nivel.json"
        caminho_padrao = os.path.join("db", roteiro_padrao)
        if os.path.exists(caminho_padrao):
            # Tenta carregar o arquivo padrão JSON para a janela inicial
            try:
                with open(caminho_padrao, 'r', encoding='utf-8') as f:
                    conteudo_json = f.read()
                self.roteiro_atual = TestScript.from_json(conteudo_json)
                self.status_inicial = f"Roteiro \"{roteiro_padrao}\" carregado automaticamente. ({len(self.roteiro_atual.passos)} passos)."
            except Exception as e:
                print(f"Erro ao carregar o roteiro padrão: {e}")
                self.roteiro_atual = TestScript([])
                self.status_inicial = "Roteiro padrão não encontrado. Iniciado com roteiro vazio"
        else: 
            self.status_inicial = "Roteiro padrão não encontrado."
        centro = QWidget()
        self.setCentralWidget(centro)
        self.layout_principal = QVBoxLayout(centro)

        self._ajustar_resolucao_e_centralizar()
        self._criar_widgets()

    def _ajustar_resolucao_e_centralizar(self):
        """Calcula o tamanho da tela e ajusta a janela de acordo com a resolução do monitor"""
        # Referência da tela principal onde a aplicação está rodando
        # tela = self.screen()

        # Pega os valores de largura e altura da tela
        geometria_tela = self.screen().availableGeometry()
        # largura_da_tela = geometria_tela.width()
        # altura_da_tela = geometria_tela.height()

        # Calcula o valor da janela
        largura_janela = int(geometria_tela.width() * 0.75)
        altura_janela = int(geometria_tela.height() * 0.8)

        # Define o tamanho da janela
        self.resize(largura_janela, altura_janela)

        # Centralização da janela na tela
        geometria_janela = self.frameGeometry()
        centro_da_tela = geometria_tela.center()
        geometria_janela.moveCenter(centro_da_tela)
        self.move(geometria_janela.topLeft())


    def _criar_widgets(self):
        lbl_titulo = QLabel("Configuração do Roteiro de Testes")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin: 5px;")
        self.layout_principal.addWidget(lbl_titulo)

        # Frame da configuração da conexão com clp
        frame_conexao = QFrame()
        frame_conexao.setFrameShape(QFrame.Shape.StyledPanel)
        layout_conexao = QHBoxLayout(frame_conexao)

        layout_conexao.addStretch()

        layout_conexao.addWidget(QLabel("Protocolo:"))
        self.combo_protocolo = QComboBox()
        self.combo_protocolo.addItems(["OPC UA", "Modbus TCP"])
        self.combo_protocolo.setFixedWidth(180)
        self.combo_protocolo.currentTextChanged.connect(self._atualizar_porta_padrao)
        layout_conexao.addWidget(self.combo_protocolo)

        layout_conexao.addStretch()

        layout_conexao.addWidget(QLabel("Endereço/IP:"))
        self.txt_url = QLineEdit("127.0.0.1")
        self.txt_url.setFixedWidth(110)
        layout_conexao.addWidget(self.txt_url)

        layout_conexao.addStretch()

        layout_conexao.addWidget(QLabel("Porta:"))
        self.txt_porta = QLineEdit("4840")
        self.txt_porta.setFixedWidth(60)
        layout_conexao.addWidget(self.txt_porta)

        layout_conexao.addStretch()

        #TODO adicionar um campo para escolher o nome da GVL para encontrar as tags OPC

        self.layout_principal.addWidget(frame_conexao)

        # Frame da configuração do roteiro
        frame_arquivos = QFrame()
        frame_arquivos.setFrameShape(QFrame.Shape.StyledPanel)
        layout_arquivos = QHBoxLayout(frame_arquivos)
        
        self.btn_configurar = QPushButton("🛠️ Configurar Roteiro e Cenas")
        self.btn_configurar.clicked.connect(self.abrir_configurador_roteiro)
        layout_arquivos.addWidget(self.btn_configurar)
        
        self.btn_salvar = QPushButton("💾 Salvar Roteiro (.json)")
        self.btn_salvar.clicked.connect(self.salvar_teste_json)
        layout_arquivos.addWidget(self.btn_salvar)
        
        self.btn_carregar = QPushButton("📂 Carregar Roteiro (.json)")
        self.btn_carregar.clicked.connect(self.carregar_teste_json)
        layout_arquivos.addWidget(self.btn_carregar)

        self.btn_descrever = QPushButton("📝 Descrever Roteiro")
        self.btn_descrever.clicked.connect(self.descrever_teste)
        layout_arquivos.addWidget(self.btn_descrever)
        
        self.layout_principal.addWidget(frame_arquivos)
        
        self.lbl_status_arquivo = QLabel(self.status_inicial)
        self.lbl_status_arquivo.setStyleSheet("color: #27ae60; font-style: italic; padding-left: 5px;")
        self.layout_principal.addWidget(self.lbl_status_arquivo)

        layout_cabecalho_log = QHBoxLayout()
        lbl_log = QLabel("Console de Saída (Logs):")
        lbl_log.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_cabecalho_log.addWidget(lbl_log)

        layout_cabecalho_log.addStretch()

        self.btn_aumentar_fonte = QPushButton("A+")
        self.btn_aumentar_fonte.setToolTip("Aumentar tamanho da fonte")
        self.btn_aumentar_fonte.setFixedWidth(35)
        self.btn_aumentar_fonte.clicked.connect(lambda: self.txt_log.zoomIn(1))       

        self.btn_diminuir_fonte = QPushButton("A-")
        self.btn_diminuir_fonte.setToolTip("Diminuir tamanho da fonte")
        self.btn_diminuir_fonte.setFixedWidth(35)
        self.btn_diminuir_fonte.clicked.connect(lambda: self.txt_log.zoomOut(1))

        self.btn_limpar_log = QPushButton("Limpar")
        self.btn_limpar_log.setToolTip("Limpa todo o log")
        self.btn_limpar_log.clicked.connect(lambda: self.txt_log.clear())

        self.btn_salvar_log = QPushButton("Salvar log atual")
        self.btn_salvar_log.setToolTip("Salva o log atual em um arquivo TXT")
        self.btn_salvar_log.clicked.connect(self.salvar_log_atual)

        layout_cabecalho_log.addWidget(self.btn_limpar_log)
        layout_cabecalho_log.addWidget(self.btn_salvar_log)
        layout_cabecalho_log.addSpacing(30)
        layout_cabecalho_log.addWidget(self.btn_aumentar_fonte)
        layout_cabecalho_log.addWidget(self.btn_diminuir_fonte)
        
        self.layout_principal.addLayout(layout_cabecalho_log)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        fonte_log = QFont("Courier New", 11)
        self.txt_log.setFont(fonte_log)
        self.txt_log.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.layout_principal.addWidget(self.txt_log)        

        self.btn_executar = QPushButton("INICIAR PROCESSO DE AVALIAÇÃO")
        self.btn_executar.setFixedHeight(45)
        self.btn_executar.setStyleSheet("font-weight: bold; font-size: 13px; background-color: #007acc; color: white;")
        self.btn_executar.clicked.connect(self.processar_teste_gui)
        self.layout_principal.addWidget(self.btn_executar)

    def _atualizar_porta_padrao(self, escolha):
        self.txt_porta.setText("4840" if "OPC UA" in escolha else "502")

    def log(self, mensagem: str):
        self.txt_log.append(mensagem)
        self.txt_log.ensureCursorVisible()

    def abrir_configurador_roteiro(self):
        janela = JanelaConfigurarTeste(self.roteiro_atual, self)
        if janela.exec() == QDialog.Accepted:
            self.roteiro_atual = janela.roteiro
            self.lbl_status_arquivo.setText(f"Roteiro atualizado ({len(self.roteiro_atual.passos)} passos).")
            self.lbl_status_arquivo.setStyleSheet("color: #3498db; font-style: italic; padding-left: 5px;")

    def salvar_teste_json(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Roteiro e Cenas", "", "Arquivos JSON (*.json)")
        if caminho:
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(self.roteiro_atual.to_json())
                QMessageBox.information(self, "Sucesso", "Roteiro e Mapeamentos salvos com sucesso!")
                self.lbl_status_arquivo.setText(f"Salvo em: {os.path.basename(caminho)}")
                self.lbl_status_arquivo.setStyleSheet("color: #3498db; font-style: italic; padding-left: 5px;")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")

    def carregar_teste_json(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Carregar Roteiro e Cenas", "", "Arquivos JSON (*.json)")
        if caminho:
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                self.roteiro_atual = TestScript.from_json(conteudo)
                QMessageBox.information(self, "Sucesso", "Roteiro carregado com sucesso!")
                self.lbl_status_arquivo.setText(f"Carregado: {os.path.basename(caminho)} ({len(self.roteiro_atual.passos)} passos)")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao processar JSON:\n{e}")

    def descrever_teste(self):
        self.txt_log.clear()
        self.roteiro_atual.log = self.log
        self.roteiro_atual.describe()

    #TODO implementar o método para salvar o log atual em um arquivo txt
    def salvar_log_atual(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar log", "", "Arquivos de texto (*.txt)")
        if caminho:
            try:
                data_hora  = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
                header_txt = "=" * 90
                header_txt += f"\n {self.windowTitle()}"
                header_txt += f"\n Data de geração do relatório: {data_hora}\n"
                header_txt += "=" * 90
                header_txt += "\n\n"
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(header_txt + self.txt_log.toPlainText())
                QMessageBox.information(self, "Sucesso", "Log salvo com sucesso.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar o arquivo:\n{e}")
        # QMessageBox.warning(self, "Aviso", "Método não implementado ainda.")

    @asyncSlot()
    async def processar_teste_gui(self):
        protocolo = self.combo_protocolo.currentText()
        ip = self.txt_url.text()
        porta = int(self.txt_porta.text())
        
        self.txt_log.clear()
        self.log(f"🔄 Inicializando ferramenta via {protocolo}...")
        
        if len(self.roteiro_atual.passos) == 0:
            self.log("❌ Erro: O roteiro de testes atual está vazio.")
            return
            
        if "OPC UA" in protocolo:
            self.clp = OpcClpClient(url=ip, port=porta)
        else:
            self.clp = ModbusClpClient(url=ip, port=porta)

        try:
            await self.clp.connect()
            self.log(f"✅ Conexão estabelecida com sucesso no endereço {self.clp.url}:{self.clp.port}.")
            
            if "OPC UA" in protocolo:
                await self.clp.escanear_variaveis_disponiveis(gvl_name="FactoryIO")
            else:
                # Conversão dinâmica das strings (salvas no JSON) para os Enums nativos do seu ModbusClpClient
                mapa_modbus_parsed = {}
                for tag, cfg in self.roteiro_atual.mapa_modbus.items():
                    tipo_enum = ModbusType[cfg['type']] if isinstance(cfg['type'], str) else cfg['type']
                    mapa_modbus_parsed[tag] = {'type': tipo_enum, 'addr': cfg['addr']}
                
                await self.clp.escanear_variaveis_disponiveis(mapa_modbus=mapa_modbus_parsed)
            
            self.log(f"📋 {len(self.clp.tags)} variáveis mapeadas/encontradas.")

            # Passamos as regras dinâmicas extraídas do Roteiro
            engine = TestEngine(self.clp, self.roteiro_atual, log_callback=self.log)
            
            self.log("🚀 Executando passos do roteiro...")
            sucesso_total = await engine.executar_roteiro()
            
            if sucesso_total:
                self.log("\n🏆 AVALIAÇÃO CONCLUÍDA: Todos os testes passaram!")
            else:
                self.log("\n❌ AVALIAÇÃO CONCLUÍDA: Erros encontrados.")

        except Exception as e:
            self.log(f"❌ Erro crítico: {e}")
        finally:
            if self.clp._protocol == Protocol.MODBUS_TCP:
                self.clp.disconnect()
            else:
                await self.clp.disconnect()
            self.log("🔒 Porta de comunicação encerrada.")