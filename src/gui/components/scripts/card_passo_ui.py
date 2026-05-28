from PySide6.QtWidgets import (QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame)
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtCore import QLocale
from src.gui.custom_widgets import NoScrollComboBox
from src.test import Action

class CardUIBuilder:

    @staticmethod
    def build(card : QFrame):
        """Contrói o layout com os Widgets vazios"""
        # --- LINHA DE CABEÇALHO (Ordem e Botões de Controle) ---
        layout_header = QHBoxLayout()
        card.lbl_ordem = QLabel(f"PASSO #{card.index + 1}")
        card.lbl_ordem.setStyleSheet("color: #deff9a; font-size: 14px;")
        layout_header.addWidget(card.lbl_ordem)        
        layout_header.addStretch()
        
        # Botões do modo EDIÇÃO
        card.btn_salvar = QPushButton("💾 Salvar")
        card.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        # card.btn_salvar.clicked.connect(card._validar_edicao)
        
        card.btn_cancelar = QPushButton("🚫 Cancelar")
        card.btn_cancelar.setStyleSheet("background-color: #7f8c8d; color: white;")
        # card.btn_cancelar.clicked.connect(card._cancelar_edicao)
        
        card.btn_del = QPushButton("🗑️ Excluir")
        card.btn_del.setStyleSheet("background-color: #c0392b; color: white;")
        # card.btn_del.clicked.connect(lambda: card.pedir_exclusao.emit(card.index))

        # Botões do modo LEITURA
        card.btn_up = QPushButton("▲")
        card.btn_up.setFixedWidth(30)
        card.btn_up.setToolTip("Mover para cima")
        # card.btn_up.clicked.connect(lambda: card.pedir_subida.emit(card.index))
        
        card.btn_down = QPushButton("▼")
        card.btn_down.setFixedWidth(30)
        card.btn_down.setToolTip("Mover para baixo")
        # card.btn_down.clicked.connect(lambda: card.pedir_descida.emit(card.index))
        
        card.btn_editar = QPushButton("✏️ Editar")
        card.btn_editar.setStyleSheet("background-color: #2980b9; color: white;")
        # card.btn_editar.clicked.connect(card._entrar_modo_edicao)
        
        layout_header.addWidget(card.btn_salvar)
        layout_header.addWidget(card.btn_cancelar)
        layout_header.addWidget(card.btn_del)        
        layout_header.addWidget(card.btn_up)
        layout_header.addWidget(card.btn_down)
        layout_header.addWidget(card.btn_editar)
        card.main_layout.addLayout(layout_header)

        # --- LINHA 1: Parâmetros Primários ---
        layout_linha1 = QHBoxLayout()
        
        layout_linha1.addWidget(QLabel("Tag:"))
        card.combo_tag = NoScrollComboBox()
        card.combo_tag.addItems(card.dict_tags.keys()) 
        # card.combo_tag.currentTextChanged.connect(card.__configura_acao_por_tipo)  
        layout_linha1.addWidget(card.combo_tag)

        layout_linha1.addWidget(QLabel("Ação:"))
        card.combo_acao = NoScrollComboBox()
        card.combo_acao.addItems([a.name for a in Action if a != Action.NO_ACTION])  
        # card.combo_acao.currentTextChanged.connect(card._ao_mudar_acao)
        card.combo_acao.setDuplicatesEnabled(False)
        layout_linha1.addWidget(card.combo_acao)

        card.valor_padrao_label_valor_passo = "Valor:"
        card.placeholer_padrao_txt_valor_passo = "True/10/0.5"
        card.tooltip_padrao_txt_valor_passo = "Valor a ser lido ou escrito na tag selecionada."
        card.label_valor_passo = QLabel(card.valor_padrao_label_valor_passo)
        layout_linha1.addWidget(card.label_valor_passo)

        card.txt_valor = QLineEdit()
        card.txt_valor.setPlaceholderText(card.placeholer_padrao_txt_valor_passo)
        card.txt_valor.setToolTip(card.tooltip_padrao_txt_valor_passo)        
        layout_linha1.addWidget(card.txt_valor)
        
        card.main_layout.addLayout(layout_linha1)

        # --- LINHA 2: Parâmetros Secundários ---
        layout_linha2 = QHBoxLayout()
        
        layout_linha2.addWidget(QLabel("Retries:"))
        card.txt_retries = QLineEdit()
        card.txt_retries.setValidator(QIntValidator(bottom=1))
        card.txt_retries.setFixedWidth(40)        
        layout_linha2.addWidget(card.txt_retries)

        card.label_timeout_pulse = QLabel("Timeout (s):")
        layout_linha2.addWidget(card.label_timeout_pulse)
        # Verifica se é pulso ou timeout para exibição inicial        
        card.txt_tempo = QLineEdit()
        validator_tempo = QDoubleValidator(bottom=0.0, top=60.0, decimals=1, notation=QDoubleValidator.Notation.StandardNotation)
        validator_tempo.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        card.txt_tempo.setValidator(validator_tempo)
        card.txt_tempo.setFixedWidth(60)        
        layout_linha2.addWidget(card.txt_tempo)

        layout_linha2.addWidget(QLabel("Retry Step (#):"))
        card.txt_retry_step = QLineEdit()
        card.txt_retry_step.setValidator(QIntValidator(bottom=1))
        card.txt_retry_step.setFixedWidth(40)        
        layout_linha2.addWidget(card.txt_retry_step)

        layout_linha2.addWidget(QLabel("Descrição:"))
        card.txt_desc = QLineEdit()
        layout_linha2.addWidget(card.txt_desc)
        
        card.main_layout.addLayout(layout_linha2)