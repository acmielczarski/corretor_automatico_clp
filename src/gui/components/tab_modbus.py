# src/gui/components/tab_modbus.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QLabel, QScrollArea)
from PySide6.QtCore import Qt, Slot, Signal
from collections import defaultdict
from .card_mapeamento_modbus import LinhaMapeamentoModbus
from src.test import TestScript

#--------------------------------------------------------------------------------#
#                    A COMPONENTIZAÇÃO DA ABA MODBUS PRINCIPAL                   #
#--------------------------------------------------------------------------------#
class TabModbus(QWidget):

    # Sinal para ajustar o estilo do card se existir erro
    validacao_modbus = Signal(bool)
    def __init__(self, roteiro : TestScript, parent=None):
        super().__init__(parent)
        self.roteiro = roteiro
        self.widget_linhas = {} # Dicionário de acesso aos widgets filhos
        self._setup_ui()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        
        lbl_info = QLabel("Mapeamento de Endereços Físicos Modbus TCP")
        lbl_info.setStyleSheet("font-size: 18px; font-weight: bold; margin: 5px;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_principal.addWidget(lbl_info)
        
        lbl_sub = QLabel("As variáveis abaixo são carregadas automaticamente a partir do Dicionário OPC UA.")
        lbl_sub.setStyleSheet("color: gray; font-style: italic; margin-bottom: 10px;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_principal.addWidget(lbl_sub)

        # --- ÁREA DE ROLAGEM (ScrollArea) ---
        # Garante suporte caso existam muitas tags no laboratório
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Container interno que receberá as linhas dinâmicas
        self.container_linhas = QWidget()
        self.layout_linhas = QVBoxLayout(self.container_linhas)
        self.layout_linhas.setAlignment(Qt.AlignmentFlag.AlignTop)  # Alinha os itens no topo do scroll
        self.layout_linhas.setSpacing(8) # Espaçamento elegante entre os frames
        
        self.scroll_area.setWidget(self.container_linhas)
        layout_principal.addWidget(self.scroll_area)

    def atualizar_tabela(self):
        """
        Método acionado pelo orquestrador (dialog_config) sempre que o usuário 
        entra na aba Modbus. Reconstrói a lista com base nas tags ativas do OPC UA.
        """
        # 1. Limpa todas as linhas antigas da tela para evitar duplicação visual
        while self.layout_linhas.count():
            item = self.layout_linhas.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.widget_linhas.clear() # Limpa a referência aos widgets filho

        # 2. Se não houver tags cadastradas no OPC UA ainda, avisa o usuário
        if not self.roteiro.dicionario_opc:
            lbl_vazio = QLabel("Nenhuma Tag cadastrada no Dicionário OPC UA.\nCadastre tags na aba anterior para configurar o Modbus.")
            lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_vazio.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 50px;")
            self.layout_linhas.addWidget(lbl_vazio)
            return

        # 3. Monta dinamicamente uma linha para cada Tag logística do Dicionário OPC
        for tag_name, values in self.roteiro.dicionario_opc.items():
            # Verifica se essa tag já possuía alguma configuração prévia salva no mapa
            config_existente = self.roteiro.mapa_modbus.get(tag_name, {"type": "COIL", "addr": 0})
            
            # Se a tag for nova e não estava no mapa_modbus, já adicionamos o padrão ao modelo de dados
            if tag_name not in self.roteiro.mapa_modbus:
                if values.get('type') == "BOOL":
                    tipo_inicial = "COIL"
                else:
                    tipo_inicial = "HOLDING_REGISTER"
                self.roteiro.mapa_modbus[tag_name] = {"type": tipo_inicial, "addr": self._ultimo_endereco_por_tipo(tag_name, tipo_inicial)}
                config_existente = self.roteiro.mapa_modbus[tag_name]

            # Instancia o widget filho customizado
            linha_widget = LinhaMapeamentoModbus(
                tag_name=tag_name,
                tipo_inicial=config_existente["type"],
                endereco_inicial=config_existente["addr"],                
                parent=self
            )

            self.widget_linhas[tag_name] = linha_widget # Referência para a configuração do widget filho
            
            # CONEXÃO DO SINAL: Conecta o sinal do filho ao slot (método) receptor no pai
            linha_widget.mapeamento_alterado.connect(self._salvar_alteracao_dados)
            
            # Adiciona o frame ao layout vertical interno do scroll
            self.layout_linhas.addWidget(linha_widget)

        self._validar_todos_enderecos()

    @Slot(str, str, int)
    def _salvar_alteracao_dados(self, tag_name: str, tipo_modbus: str, endereco_int: int):
        """
        SLOT RECEPTOR: Executado automaticamente toda vez que qualquer uma 
        das linhas disparar uma alteração de valor e verifica se há conflito de endereços.
        """        
        # Atualiza diretamente o dicionário de dados do roteiro em tempo real
        self.roteiro.mapa_modbus[tag_name] = {
            "type": tipo_modbus,
            "addr": endereco_int
        }
        self._validar_todos_enderecos()

    def _validar_todos_enderecos(self):
        """Verifica as colisões de endereçamento"""
        tem_erro = False

        # Mapeia os endereços, verificando o que está sendo usado {(Tipo, Endereço): [tag1, tag2]}
        mapa_verificacao = defaultdict(list)        
        
        for tag, dados in self.roteiro.mapa_modbus.items():
            chave = (dados['type'], dados['addr'])
            mapa_verificacao[chave].append(tag)

        # Atualiza o visual dos widgets na tela
        for tag, widget in self.widget_linhas.items():
            dados = self.roteiro.mapa_modbus.get(tag)
            if not dados:                
                continue

            chave = (dados['type'], dados['addr'])

            if len(mapa_verificacao[chave]) > 1:
                widget._set_estado_erro(True)
                tem_erro = True
            else:
                widget._set_estado_erro(False)

        self.validacao_modbus.emit(tem_erro)

    def _ultimo_endereco_por_tipo(self, tag_atual : str, tipo : str) -> int:
        """Verifica o último endereço adicionado de acordo com o tipo da variável e retorna o próximo disponível. Começando sempre em 0"""
        ultimo_endereco = None

        for tag, dados in self.roteiro.mapa_modbus.items():
            if tipo == dados.get('type') and tag != tag_atual:
                ultimo_endereco = dados.get('addr')

        if ultimo_endereco is None:
            return 0
        else:
            return ultimo_endereco + 1



    def limpar_aba(self):
        """Zera as configurações do modelo de dados e força a reatualização visual."""
        self.roteiro.mapa_modbus.clear()
        self.atualizar_tabela()