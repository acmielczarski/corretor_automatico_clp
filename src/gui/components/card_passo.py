from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame, QMessageBox)
from PySide6.QtCore import Signal, QLocale
from PySide6.QtGui import QIntValidator, QDoubleValidator
from src.test import TestStep, Action
from src.gui.custom_widgets import NoScrollComboBox
# from src.gui.components.scripts import CardUIBuilder, CardRulesEngine

#--------------------------------------------------------------------------------#
#           WIDGET CUSTOMIZADO: CARD DE PASSO DE TESTE DINÂMICO                  #
#--------------------------------------------------------------------------------#
class CardPassoTeste(QFrame):
    """
    Representação visual de um único passo de teste.
    Permite edição direta e disparar comandos de reordenação/exclusão.
    """
    # Sinais para comunicação com o Parent (TabPassos)
    pedir_exclusao = Signal(int)
    pedir_subida = Signal(int)
    pedir_descida = Signal(int)
    pedir_atualizacao = Signal(bool)

    def __init__(self, passo: TestStep, index: int, dict_tags: dict, iniciar_em_edicao : bool = False, parent=None):
        super().__init__(parent)
        self.passo = passo
        self.index = index # Posição na lista original
        self.dict_tags = dict_tags
        self.em_edicao = False # Controle do estado do card
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            CardPassoTeste { 
                background-color: #1e1e1e; 
                border: 1px solid #3d3d3d; 
                border-radius: 10px; 
            }
            QLabel { color: #f5f5f5; font-weight: bold; }
            QLineEdit, QComboBox { background-color: #2d2d2d; color: white; border: 1px solid #3d3d3d; padding: 4px; border-radius: 4px; }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self._setup_ui()
        # CardUIBuilder.build(self)
        self._carregar_dados_do_objeto()
        if iniciar_em_edicao:
            self._entrar_modo_edicao()
        else:
            self._alternar_modo_leitura() # Bloqueia o card na criação

    def _conectar_sinais(self):
        """Organiza as conexões de eventos do card em um único lugar."""
        self.btn_salvar.clicked.connect(self._salvar_edicao)
        self.btn_cancelar.clicked.connect(self._cancelar_edicao)
        self.btn_editar.clicked.connect(self._entrar_modo_edicao)
        self.combo_tag.currentTextChanged.connect(self.__configura_acao_por_tipo)
        self.combo_acao.currentTextChanged.connect(self._ao_mudar_acao)

    def _setup_ui(self):
        """Contrói o layout com os Widgets vazios"""
        #--- LINHA DE CABEÇALHO (Ordem e Botões de Controle) ---
        layout_header = QHBoxLayout()
        self.lbl_ordem = QLabel(f"PASSO #{self.index + 1}")
        self.lbl_ordem.setStyleSheet("color: #deff9a; font-size: 14px;")
        layout_header.addWidget(self.lbl_ordem)        
        layout_header.addStretch()
        
        #Botões do modo EDIÇÃO
        self.btn_salvar = QPushButton("💾 Salvar")
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_salvar.clicked.connect(self._salvar_edicao)
        
        self.btn_cancelar = QPushButton("🚫 Cancelar")
        self.btn_cancelar.setStyleSheet("background-color: #7f8c8d; color: white;")
        self.btn_cancelar.clicked.connect(self._cancelar_edicao)
        
        self.btn_del = QPushButton("🗑️ Excluir")
        self.btn_del.setStyleSheet("background-color: #c0392b; color: white;")
        self.btn_del.clicked.connect(lambda: self.pedir_exclusao.emit(self.index))

        #Botões do modo LEITURA
        self.btn_up = QPushButton("▲")
        self.btn_up.setFixedWidth(30)
        self.btn_up.setToolTip("Mover para cima")
        self.btn_up.clicked.connect(lambda: self.pedir_subida.emit(self.index))
        
        self.btn_down = QPushButton("▼")
        self.btn_down.setFixedWidth(30)
        self.btn_down.setToolTip("Mover para baixo")
        self.btn_down.clicked.connect(lambda: self.pedir_descida.emit(self.index))
        
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setStyleSheet("background-color: #2980b9; color: white;")
        self.btn_editar.clicked.connect(self._entrar_modo_edicao)
        
        layout_header.addWidget(self.btn_salvar)
        layout_header.addWidget(self.btn_cancelar)
        layout_header.addWidget(self.btn_del)        
        layout_header.addWidget(self.btn_up)
        layout_header.addWidget(self.btn_down)
        layout_header.addWidget(self.btn_editar)
        self.main_layout.addLayout(layout_header)

        #--- LINHA 1: Parâmetros Primários ---
        layout_linha1 = QHBoxLayout()
        
        layout_linha1.addWidget(QLabel("Tag:"))
        self.combo_tag = NoScrollComboBox()
        self.combo_tag.addItems(self.dict_tags.keys()) 
        self.combo_tag.currentTextChanged.connect(self.__configura_acao_por_tipo)  
        layout_linha1.addWidget(self.combo_tag)

        layout_linha1.addWidget(QLabel("Ação:"))
        self.combo_acao = NoScrollComboBox()
        self.combo_acao.addItems([a.name for a in Action if a != Action.NO_ACTION])  
        self.combo_acao.currentTextChanged.connect(self._ao_mudar_acao)
        self.combo_acao.setDuplicatesEnabled(False)
        layout_linha1.addWidget(self.combo_acao)

        self.valor_padrao_label_valor_passo = "Valor:"
        self.placeholer_padrao_txt_valor_passo = "True/10/0.5"
        self.tooltip_padrao_txt_valor_passo = "Valor a ser lido ou escrito na tag selecionada."
        self.label_valor_passo = QLabel(self.valor_padrao_label_valor_passo)
        layout_linha1.addWidget(self.label_valor_passo)

        self.txt_valor = QLineEdit()
        self.txt_valor.setPlaceholderText(self.placeholer_padrao_txt_valor_passo)
        self.txt_valor.setToolTip(self.tooltip_padrao_txt_valor_passo)        
        layout_linha1.addWidget(self.txt_valor)
        
        self.main_layout.addLayout(layout_linha1)

        #--- LINHA 2: Parâmetros Secundários ---
        layout_linha2 = QHBoxLayout()
        
        layout_linha2.addWidget(QLabel("Retries:"))
        self.txt_retries = QLineEdit()
        self.txt_retries.setValidator(QIntValidator(bottom=1))
        self.txt_retries.setFixedWidth(40)        
        layout_linha2.addWidget(self.txt_retries)

        self.label_timeout_pulse = QLabel("Timeout (s):")
        layout_linha2.addWidget(self.label_timeout_pulse)
        #Verifica se é pulso ou timeout para exibição inicial        
        self.txt_tempo = QLineEdit()
        validator_tempo = QDoubleValidator(bottom=0.0, top=60.0, decimals=1, notation=QDoubleValidator.Notation.StandardNotation)
        validator_tempo.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.txt_tempo.setValidator(validator_tempo)
        self.txt_tempo.setFixedWidth(60)        
        layout_linha2.addWidget(self.txt_tempo)

        layout_linha2.addWidget(QLabel("Retry Step (#):"))
        self.txt_retry_step = QLineEdit()
        self.txt_retry_step.setValidator(QIntValidator(bottom=1))
        self.txt_retry_step.setFixedWidth(40)        
        layout_linha2.addWidget(self.txt_retry_step)

        layout_linha2.addWidget(QLabel("Descrição:"))
        self.txt_desc = QLineEdit()
        layout_linha2.addWidget(self.txt_desc)
        
        self.main_layout.addLayout(layout_linha2)        
    
    def _carregar_dados_do_objeto(self):
        """Puxa os dados do self.passo para o card criado"""
        # Desliga os disparos do combobox de ação durante este processo
        self.combo_acao.blockSignals(True)
        self.combo_tag.blockSignals(True)

        # Tratamento do nome da tag para SLEEP
        if self.passo.action == Action.SLEEP:
            if self.combo_tag.findText("-") == -1:         
                self.combo_tag.addItem("-")
        
        # Carrega os dados para o card criado
        self.combo_tag.setCurrentText(self.passo.tag_name if self.passo.tag_name else "-")
        self.__configura_acao_por_tipo()      
        self.combo_acao.setCurrentText(self.passo.action.name)        
        self.txt_valor.setText(str(self.passo.value) if self.passo.value is not None else "")

        self.txt_retries.setText(str(self.passo.retries))
        tempo = self.passo.pulse_time if self.passo.action == Action.PRESS_PUSH_BUTTON else self.passo.timeout
        self.txt_tempo.setText(str(tempo))
        self.txt_retry_step.setText(str(self.passo.step_to_retry) if self.passo.step_to_retry is not None else "")
        self.txt_desc.setText(self.passo.description)        

        # Liga novamente o disparo de eventos do combobox da ação
        self.combo_acao.blockSignals(False)
        self.combo_tag.blockSignals(False)
        self._ajustar_inputs_por_acao()

    #--------------------------------------------------------------------------------#
    #                           MÁQUINA DE ESTADO DA UI                              #
    #--------------------------------------------------------------------------------#

    def _alternar_modo_leitura(self):
        """Trava os campos e mostra os botões do modo leitura"""
        self.em_edicao = False
        self.__set_desabilitado_e_padrao(set_default=False) # Bloqueia os inputs

        # Alterna os botões no card
        self.btn_salvar.hide()
        self.btn_cancelar.hide()
        self.btn_del.hide()

        self.btn_up.show()
        self.btn_down.show()
        self.btn_editar.show()

        # Estilo de leitura suave
        self.setStyleSheet("CardPassoTeste { background-color: #1e1e1e; border: 1px solid #3d3d3d; border-radius: 10px; }")

    def _entrar_modo_edicao(self):
        """Destrava os campos pertinentes para a ação atual e entra no modo de edição"""
        self.em_edicao = True
        self._ajustar_inputs_por_acao()

        # Alterna os botões no card
        self.btn_salvar.show()
        self.btn_cancelar.show()
        self.btn_del.show()

        self.btn_up.hide()
        self.btn_down.hide()
        self.btn_editar.hide()

        # Destaque visual (borda amarela ou azul) para focar a atenção
        self.setStyleSheet("CardPassoTeste { background-color: #1e1e1e; border: 1px solid #3498db; border-radius: 10px; }")
    
    def _validar_cancelar_edicao(self) -> bool:
        """Verifica se os passos mínimos estão preenchidos corretamente e pergunta ser quer arrumar ou excluir"""
        actual_action = Action[self.combo_acao.currentText()]
        requires_value = actual_action != Action.SLEEP
        requires_time = actual_action == Action.WAIT_CHANGE or actual_action == Action.WAIT_UNTIL or actual_action == Action.PRESS_PUSH_BUTTON or actual_action == Action.SLEEP

        missing_field = None
        if requires_value and not self.txt_valor.text():
            if actual_action == Action.WAIT_UNTIL or actual_action == Action.COMPARISON:
                missing_field = "\"expressão\""
            else:
                missing_field = "\"valor\""    
        elif requires_time and not self.txt_tempo.text():
            if actual_action == Action.PRESS_PUSH_BUTTON:
                missing_field = "\"pulso\""
            else:
                missing_field = "\"timeout\""

        if missing_field is not None:
            resposta = QMessageBox.question(self.parent(), "Aviso",
                                            f"O campo {missing_field} deve ser preenchido para a ação {actual_action.name}.\nDeseja corrigir o passo? Caso descartar seja selecionado, o passo é excluído",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Discard)
            
            if resposta == QMessageBox.StandardButton.Yes:
                return False
            elif resposta == QMessageBox.StandardButton.Discard:
                self.pedir_exclusao.emit(self.index)
                return False
        else:
            return True        

    def _cancelar_edicao(self):
        """Cancela a edição e retorna os valores originais do passo"""
        if not self._validar_cancelar_edicao():
            return
        
        self._carregar_dados_do_objeto()
        self._alternar_modo_leitura()
    
    def _validar_edicao(self) -> bool:
        """Verifica se os campos obrigatórios estão preenchidos de acordo com a ação"""
        actual_action = Action[self.combo_acao.currentText()]
        requires_value = actual_action != Action.SLEEP
        requires_time = actual_action == Action.WAIT_CHANGE or actual_action == Action.WAIT_UNTIL or actual_action == Action.PRESS_PUSH_BUTTON or actual_action == Action.SLEEP

        missing_field = None
        if requires_value and not self.txt_valor.text():
            if actual_action == Action.WAIT_UNTIL or actual_action == Action.COMPARISON:
                missing_field = "\"expressão\""
            else:
                missing_field = "\"valor\""    
        elif requires_time and not self.txt_tempo.text():
            if actual_action == Action.PRESS_PUSH_BUTTON:
                missing_field = "\"pulso\""
            else:
                missing_field = "\"timeout\""

        if missing_field is not None:
            QMessageBox.warning(self.parent(), "Aviso", f"O campo {missing_field} deve ser preenchido para a ação {actual_action.name}")
            return False
        
        return True
    
    def _salvar_edicao(self):
        """Salva o objeto editado no Step do passo caso seja validado"""
        # Verifica se está tudo ok com o passo a ser salvo
        if not self._validar_edicao:
            return
        
        self.passo.tag_name = self.combo_tag.currentText() if self.combo_tag.currentText() != "-" else ""
        self.passo.action = Action[self.combo_acao.currentText()]
        self.passo.description = self.txt_desc.text()
        self.passo.retries = int(self.txt_retries.text()) if self.txt_retries.text() else 1
        self.passo.data_type = self.dict_tags[self.passo.tag_name].get('type') if self.passo.action != Action.SLEEP else None

        val_raw = self.txt_valor.text().strip().replace(" ", "")
        if val_raw.lower() == "true" or (self.passo.data_type == "BOOL" and val_raw == "1"):
            self.passo.value = True
        elif val_raw.lower() == "false" or (self.passo.data_type == "BOOL" and val_raw == "0"):
            self.passo.value = False
        else:
            try:
                self.passo.value = float(val_raw) if self.passo.data_type == "FLOAT" or self.passo.data_type == "DOUBLE" else int(val_raw)
            except Exception:
                self.passo.value = val_raw

        # Trata timeout vs pulse_time        
        tempo = float(self.txt_tempo.text().replace(",", ".")) if self.txt_tempo.text() else 0.5        
        if self.passo.action == Action.PRESS_PUSH_BUTTON:
            self.passo.pulse_time = tempo
        else:
            self.passo.timeout = tempo            

        retry_s = self.txt_retry_step.text().strip()
        self.passo.step_to_retry = int(retry_s) if retry_s else None

        self._carregar_dados_do_objeto()
        self._alternar_modo_leitura()                

    #--------------------------------------------------------------------------------#
    #                            LÓGICA DE CAMPOS (UI)                               #
    #--------------------------------------------------------------------------------#

    #TODO ajustar o método para quando a ação sair de SLEEP para que ache a primeira variável válida para a nova ação selecionada. (melhoria de UX)
    def _ao_mudar_acao(self):
        """Ajusta campos quando a ação é modificada no card."""
        # Bloqueia a execução deste método caso não esteja em modo de edição, útil quando estamos preenchendo o card
        if not self.em_edicao:
            return
        
        self.__set_desabilitado_e_padrao(set_default=True)
        self._ajustar_inputs_por_acao()
    
    def _ajustar_inputs_por_acao(self):
        """Ajusta campos conforme a ação carregada no card."""
        # Se não estiver em edição, adequa os labels apenas        
        if not self.em_edicao:
            self.__set_desabilitado_e_padrao(set_default=False)

        actual_action = self.combo_acao.currentText()

        if self.em_edicao:
            self.combo_acao.setDisabled(False)
            self.txt_desc.setDisabled(False)

        if actual_action == Action.WRITE.name:
            if self.em_edicao:
                self.__configura_parametros_write()

        elif actual_action == Action.READ_EQUAL.name:
            if self.em_edicao:
                self.__configura_parametros_read_equal()

        elif actual_action == Action.COMPARISON.name:
            if self.em_edicao:
                self.__configura_parametros_comparison()
            self.__set_use_expression_strings()

        elif actual_action == Action.WAIT_CHANGE.name:
            if self.em_edicao:
                self.__configura_parametros_wait_change()

        elif actual_action == Action.WAIT_UNTIL.name:
            if self.em_edicao:
                self.__configura_parametros_wait_until()           
            self.__set_use_expression_strings()

        elif actual_action == Action.PRESS_PUSH_BUTTON.name:
            self.__configura_parametros_push_button()

        elif actual_action == Action.SLEEP.name:
            self.__configura_parametros_sleep()                  

    #--------------------------------------------------------------------------------#
    #                  Métodos Auxiliares do Widget de passo                         #
    #--------------------------------------------------------------------------------#

    def __set_desabilitado_e_padrao(self, set_default : bool):
        """Desabilita tudo e coloca os valores default caso set_default seja verdadeiro"""
        self.combo_tag.setDisabled(True)
        self.combo_acao.setDisabled(True)
        self.txt_valor.setDisabled(True)        
        self.txt_retries.setDisabled(True)        
        self.txt_tempo.setDisabled(True)        
        self.txt_retry_step.setDisabled(True)
        self.txt_desc.setDisabled(True)
        
        if set_default:
            self.txt_valor.setText("")
            self.txt_retries.setText("1")
            self.txt_tempo.setText("5.0")
            self.txt_retry_step.setText("")

            # Caso a action anterior tenha sido PRESS_PUSH_BUTTON, muda o texto para o original
            if "pulso" in self.label_timeout_pulse.text().lower():
                self.label_timeout_pulse.setText("Timeout (s):")

            # Verifica se o passo anterior foi SLEEP (que adiciona "-" ao combo da tag) e elimina o texto adicionado
            _item_to_delete = self.combo_tag.findText("-")

            # Caso exista a opção "-" na lista de tags, verifica qual o tipo de ação e escolhida e ajusta a tag de acordo com a opção escolhida.
            # Pega o primeiro item válido para a ação e escolhida e coloca na tag.
            if _item_to_delete != -1:
                acao_escolhida = Action[self.combo_acao.currentText()]
                is_number_action = acao_escolhida == Action.COMPARISON or acao_escolhida == Action.WAIT_UNTIL

                # Verifica o tipo da tag e se ação é para uma variável booleana ou numérica
                for name in self.dict_tags:
                    tag_type = self.dict_tags[name].get('type')
                    if is_number_action and tag_type != "BOOL":
                        self.combo_tag.setCurrentText(name)
                        break
                    elif not is_number_action and tag_type == "BOOL":
                        self.combo_tag.setCurrentText(name)
                        break
                # Por fim, exclui a tag "-" da lista
                self.combo_tag.removeItem(_item_to_delete)

            # Verifica se os campos descritivos de 'valor' não foram alterados
            if self.label_valor_passo.text() != self.valor_padrao_label_valor_passo:
                self.label_valor_passo.setText(self.valor_padrao_label_valor_passo)
                self.txt_valor.setPlaceholderText(self.placeholer_padrao_txt_valor_passo)
                self.txt_valor.setToolTip(self.tooltip_padrao_txt_valor_passo)

    def __configura_acao_por_tipo(self):
        tag = self.combo_tag.currentText()
        modelo = self.combo_acao.model()

        # Habilita todos os campos por padrão
        for i in range(modelo.rowCount()):
            modelo.item(i).setEnabled(True)

        # Se a tag for "-", retorna com todos os campos habilitados
        if tag == "-" or not tag:
            return
        
        # Define as ações        
        boolean_actions = [Action.READ_EQUAL.name, Action.WAIT_CHANGE.name, Action.PRESS_PUSH_BUTTON.name]
        number_actions = [Action.COMPARISON.name, Action.WAIT_UNTIL.name]        

        # Verifica se a variável é booleana ou numérica e ajusta os valores para desabilitar
        if self.dict_tags[tag].get('type') == "BOOL":
            itens_to_disable = number_actions
        else:
            itens_to_disable = boolean_actions

        for i in range(modelo.rowCount()):
            item = modelo.item(i)
            if item.text() in itens_to_disable:
                item.setEnabled(False)

        # Caso a ação seja desabilitada pelo tipo da tag, coloca a ação padrão WRITE
        indice_atual = self.combo_acao.currentIndex()
        if not modelo.item(indice_atual).isEnabled():
            self.combo_acao.setCurrentText(Action.WRITE.name)

    def __configura_parametros_write(self):
        self.combo_tag.setDisabled(False)
        self.txt_valor.setDisabled(False)

    def __configura_parametros_read_equal(self):
        self.combo_tag.setDisabled(False)
        self.txt_valor.setDisabled(False)
        self.txt_tempo.setDisabled(False)
        self.txt_retries.setDisabled(False)
        self.txt_retry_step.setDisabled(False)

    def __configura_parametros_comparison(self):
        self.combo_tag.setDisabled(False)
        self.txt_valor.setDisabled(False)
        self.txt_retries.setDisabled(False)
        self.txt_tempo.setDisabled(False)           
        self.txt_retry_step.setDisabled(False)       

    def __configura_parametros_wait_change(self):
        self.combo_tag.setDisabled(False)       
        self.txt_valor.setDisabled(False)
        self.txt_retries.setDisabled(False)
        self.txt_tempo.setDisabled(False)           
        self.txt_retry_step.setDisabled(False)        
        self.txt_tempo.setDisabled(False)

    def __configura_parametros_wait_until(self):
        self.combo_tag.setDisabled(False)
        self.txt_valor.setDisabled(False)
        self.txt_retries.setDisabled(False)            
        self.txt_retry_step.setDisabled(False)            
        self.txt_tempo.setDisabled(False)
        #self.txt_tempo.setText("10.0")        
    
    def __configura_parametros_push_button(self):
        self.combo_tag.setDisabled(False)
        self.txt_valor.setDisabled(False)           
        self.txt_tempo.setDisabled(False)        
        self.label_timeout_pulse.setText("Pulso (s):")

    def __configura_parametros_sleep(self):
        if self.combo_tag.findText("-") == -1:
            self.combo_tag.addItem("-")
        self.combo_tag.setCurrentText("-")
        self.txt_tempo.setDisabled(False)        

    def __set_use_expression_strings(self):
        self.label_valor_passo.setText("Expr:")
        self.txt_valor.setPlaceholderText("<, >, ==, !=, etc.")
        self.txt_valor.setToolTip("Insira uma expressão de comparação.\nExemplo: >80, <=1, !=0, etc.")