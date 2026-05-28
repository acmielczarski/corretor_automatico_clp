# src/gui/components/card_passo_rules.py
from src.test import Action

class CardRulesEngine:
    
    @staticmethod
    def configurar_acao_por_tipo(card):
        """Avalia a tag selecionada e bloqueia ações incompatíveis no ComboBox."""
        tag = card.combo_tag.currentText()
        modelo = card.combo_acao.model()

        # Habilita todos os campos por padrão
        for i in range(modelo.rowCount()):
            modelo.item(i).setEnabled(True)

        if tag == "-" or not tag:
            return
        
        boolean_actions = [Action.READ_EQUAL.name, Action.WAIT_CHANGE.name, Action.PRESS_PUSH_BUTTON.name]
        number_actions = [Action.COMPARISON.name, Action.WAIT_UNTIL.name]        

        if card.dict_tags[tag].get('type') == "BOOL":
            itens_to_disable = number_actions
        else:
            itens_to_disable = boolean_actions

        for i in range(modelo.rowCount()):
            item = modelo.item(i)
            if item.text() in itens_to_disable:
                item.setEnabled(False)

        indice_atual = card.combo_acao.currentIndex()
        if not modelo.item(indice_atual).isEnabled():
            card.combo_acao.setCurrentText(Action.WRITE.name)

    @staticmethod
    def ajustar_inputs_por_acao(card):
        """Ajusta os campos visuais habilitados com base na ação atual do card."""
        if not card.em_edicao:
            CardRulesEngine.set_desabilitado_e_padrao(card, set_default=False)

        actual_action = card.combo_acao.currentText()

        if card.em_edicao:
            card.combo_acao.setEnabled(True)
            card.txt_desc.setEnabled(True)

        if actual_action == Action.WRITE.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_write(card)

        elif actual_action == Action.READ_EQUAL.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_read_equal(card)

        elif actual_action == Action.COMPARISON.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_comparison(card)
            CardRulesEngine._set_use_expression_strings(card)

        elif actual_action == Action.WAIT_CHANGE.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_wait_change(card)

        elif actual_action == Action.WAIT_UNTIL.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_wait_until(card)           
            CardRulesEngine._set_use_expression_strings(card)

        elif actual_action == Action.PRESS_PUSH_BUTTON.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_push_button(card)

        elif actual_action == Action.SLEEP.name:
            if card.em_edicao:
                CardRulesEngine._configura_parametros_sleep(card)

    @staticmethod
    def set_desabilitado_e_padrao(card, set_default: bool):
        """Bloqueia todos os inputs. Opcionalmente, redefine-os para seus valores de placeholder."""
        card.combo_tag.setDisabled(True)
        card.combo_acao.setDisabled(True)
        card.txt_valor.setDisabled(True)        
        card.txt_retries.setDisabled(True)        
        card.txt_tempo.setDisabled(True)        
        card.txt_retry_step.setDisabled(True)
        card.txt_desc.setDisabled(True)
        
        if set_default:
            card.txt_valor.setText("")
            card.txt_retries.setText("1")
            card.txt_tempo.setText("5.0")
            card.txt_retry_step.setText("")

            if "pulso" in card.label_timeout_pulse.text().lower():
                card.label_timeout_pulse.setText("Timeout (s):")

            _item_to_delete = card.combo_tag.findText("-")
            if _item_to_delete != -1:
                card.combo_tag.removeItem(_item_to_delete)

            if card.label_valor_passo.text() != card.valor_padrao_label_valor_passo:
                card.label_valor_passo.setText(card.valor_padrao_label_valor_passo)
                card.txt_valor.setPlaceholderText(card.placeholer_padrao_txt_valor_passo)
                card.txt_valor.setToolTip(card.tooltip_padrao_txt_valor_passo)

    # --- REGRAS ESPECÍFICAS DE AÇÃO ---
    @staticmethod
    def _configura_parametros_write(card):
        card.combo_tag.setEnabled(True)
        card.txt_valor.setEnabled(True)

    @staticmethod
    def _configura_parametros_read_equal(card):
        card.combo_tag.setEnabled(True)
        card.txt_valor.setEnabled(True)
        card.txt_tempo.setEnabled(True)
        card.txt_retries.setEnabled(True)
        card.txt_retry_step.setEnabled(True)

    @staticmethod
    def _configura_parametros_comparison(card):
        card.combo_tag.setEnabled(True)
        card.txt_valor.setEnabled(True)
        card.txt_retries.setEnabled(True)
        card.txt_tempo.setEnabled(True)           
        card.txt_retry_step.setEnabled(True)       

    @staticmethod
    def _configura_parametros_wait_change(card):
        card.combo_tag.setEnabled(True)       
        card.txt_valor.setEnabled(True)
        card.txt_retries.setEnabled(True)
        card.txt_tempo.setEnabled(True)           
        card.txt_retry_step.setEnabled(True)
        card.txt_retry_step.setText("")

    @staticmethod
    def _configura_parametros_wait_until(card):
        card.combo_tag.setEnabled(True)
        card.txt_valor.setEnabled(True)
        card.txt_retries.setEnabled(True)            
        card.txt_retry_step.setEnabled(True)            
        card.txt_tempo.setEnabled(True)
    
    @staticmethod
    def _configura_parametros_push_button(card):
        card.combo_tag.setEnabled(True)
        card.txt_valor.setEnabled(True)           
        card.txt_tempo.setEnabled(True)
        card.label_timeout_pulse.setText("Pulso (s):")

    @staticmethod
    def _configura_parametros_sleep(card):
        if card.combo_tag.findText("-") == -1:
            card.combo_tag.addItem("-")
        card.combo_tag.setCurrentText("-")
        card.txt_tempo.setEnabled(True)

    @staticmethod
    def _set_use_expression_strings(card):
        card.label_valor_passo.setText("Expr:")
        card.txt_valor.setPlaceholderText("<, >, ==, !=, etc.")
        card.txt_valor.setToolTip("Insira uma expressão de comparação.\nExemplo: >80, <=1, !=0, etc.")