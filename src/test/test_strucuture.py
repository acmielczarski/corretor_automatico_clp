from typing import Any, List, Callable
from dataclasses import dataclass
from enum import Enum, auto
import json

class Action(Enum):
    '''
    Constantes para o roteiro de testes
    '''
    WRITE = auto() # Any
    READ_EQUAL = auto() # Bool
    COMPARISON = auto() # Number
    WAIT_CHANGE = auto() # Bool
    WAIT_UNTIL = auto() # Number
    PRESS_PUSH_BUTTON = auto() # Bool
    SLEEP = auto() # Any
    NO_ACTION = auto() # Placeholder

@dataclass
class TestStep:
    """
    Define a estrutura de um único passo dentro de um roteiro de testes.
    
    :param action: comando aplicado na etapa. see: ``Action``
    :type action: Action
    :param order: ordem de execução do teste. Criada automaticamente ao configurar ``TestEngine``.
    :type order: int
    :param tag_name: Nome lógico da TAG configurada para o teste.
    :type tag_name: str
    :param value: Valor que será escrito ou esperado em ``tag_name``.
    :type value: Any
    :param data_type: *(Opcional)* Tipo de dado para escrita.
        A função identifica automaticamente entre ``BOOL``, ``INT16`` e ``FLOAT``.
        Se o valor INT for maior que 32767, tenta mandar ``INT32``.
        *Default: None*
    :type data_type: str
    :param timeout: Tempo máximo de espera para ações de monitoramento. *Default: 5.0*
    :type timeout: float
    :param retries: Quantidade de tentativas para o passo. *Default: 1*
    :type retries: int
    :param step_to_retry: Passo que deve ser repetido caso o passo atual falhe. Se o valor for ``None`` e ``retries > 1``, executa novamente o mesmo passo.
    :type step_to_retry: int
    :param pulse_time: Tempo para voltar o botão para o estado original. Usado somente se ``action = PRESS_PUSH_BUTTON``. *Default: 0.3*
    :type pulse_time: float
    :param description: *(Opcional)* Descrição do passo para log.
    :type description: str
    """
    action: Action    
    tag_name: str = ""
    order: int = None
    value: Any = None
    data_type: str | None = None
    timeout: float = 5.0
    retries: int = 1
    step_to_retry: int = None
    pulse_time: float = 0.3
    description: str = ""
    _current_retry: int = 0

class TestScript:
    """
    Classe para organização do roteiro de testes do CLP.

    Funciona como um container para a lista de ``TestStep``.
    Criada para implementação de métodos específicos e controle de Script de testes para ``TestEngine``.

    :param passos: Lista com os passos do teste.
    :type passos: List[TestStep]
    :param ordenado: Indica se o teste está ordenado (possui atributo `order` nos objetos `TestStep` de forma crescente), se `False`, ordena os passos de acordo com o index de `List`. _Default: False_
    :type ordenado: bool
    :param dicionario_opc: Lista de sinônimos para as tags configuradas. Tenta encontrar dentro o servidor OPC UA os sinônimos para casar com as variáveis configuradas, evitando retrabalho para encontrar nomes de variáveis distintos para cada projeto.
    :type dicionario_opc: dict[str, dict[str, Any]]
    :param mapa_modbus: Mapa dos endereços Modbus contendo nome da variável, tipo de variável (utiliza os nomes de :class:`ModbusType`) e endereço.
    :type mapa_modbus: dict[str, dict[str, Any]]
    """
    def __init__(self,
                 passos: List[TestStep]=None,
                 ordenado : bool = False,
                 dicionario_opc : dict = None,
                 mapa_modbus : dict = None,
                 log_callback: Callable[[str], None] = None):
        self.passos = passos if passos is not None else[]
        self.ordenado = ordenado
        self.dicionario_opc = dicionario_opc        
        self.mapa_modbus = mapa_modbus
        self.log = log_callback if log_callback is not None else print

    def adicionar_passo(self, passo: TestStep):
        """
        Adicona um passo ao roteiro.

        :param passo: objeto contendo um passo de teste.
        :type passo: :class:`TestStep`
        """
        self.passos.append(passo)

    def __iter__(self):
        """Permite a iteração da classe em laços (Ex: for passo in roteiro)"""
        return iter(self.passos)
    
    def __len__(self):
        """Permite usar len(roteiro) na classe"""
        return len(self.passos)
    
    def __getitem__(self, index):
        """Permite acessar passos específicos pelo índice"""
        return self.passos[index]
    
    #TODO melhorar a descrição do roteiro
    def describe(self):
        """
        Gera uma visualização tabular para os passos configurados no teste.
        Visão geral do processo. Para uma visão completa de algum passo específico, utilize :func:`describe_step`
        """
        if not self.passos:
            self.log("\n📋 Roteiro de Teste Vazio.")
            return

        self.log("\n"+"="*90)
        self.log(f"{'ORDEM':<7} | {'AÇÃO':<20} | {'TAG':<18} | {'VALOR':<8} | {'DESCRIÇÃO'}")
        self.log("="*90)

        for passo in self.passos:
            # Tratamento visual para exibir nome da ação do Enum            
            acao_nome = passo.action.name if hasattr(passo.action, 'name') else str(passo.action)
            ordem_str = f"{passo.order}" if passo.order is not None else "-"
            valor_str = str(passo.value) if acao_nome != Action.SLEEP.name else f"{passo.timeout} s"            
            tag_str = passo.tag_name if passo.tag_name else "-"

            # Formatação das colunas
            self.log(f"{ordem_str:<7} | {acao_nome:<20} | {tag_str:<18} | {valor_str:<8} | {passo.description}")
        
        self.log("="*90)

    def describe_step(self, step_order : int | List[int]):
        """
        Visão detalhada de um ou mais passos específicos.

        Para informações de vários passos, usar `List[int]`.
        Sinaliza quando algum passo não e encontrado no roteiro.

        :param step_order: O número de ordem do passo (#) ou uma lista com vários passos.
        :type step_order: int | List[int]
        :raises ValueError: Caso não seja passado um valor ``int`` ou ``List[int]`` em ``step_order``.
        """

        if not self.passos:
            print("\n📋 Roteiro de Teste Vazio.")
            return        

        # Tratamento de dados da entrada
        if isinstance(step_order, int):
            ordens = [step_order]
        elif isinstance(step_order, list):
            ordens = step_order
        else:
            raise ValueError(f"Erro: O parâmetro deve ser int ou List[int]. Recebido: {type(step_order)}")

        for ordem in ordens:
            passo_encontrado = None
            for passo in self.passos:
                if passo.order == ordem:
                    passo_encontrado = passo
                    break

            if passo_encontrado:
                encontrou_algum = True
                acao_nome = passo_encontrado.action.name if hasattr(passo_encontrado.action, 'name') else str(passo_encontrado.action)

                tronco = '├──'
                terminacao = '└──'

                # Impressão em forma de bloco de propriedades
                self.log(f"🔹 Passo #{passo_encontrado.order} - {passo_encontrado.description or 'Sem descrição'}")
                self.log(f"  {tronco} Ação (Action):        {acao_nome}")
                self.log(f"  {tronco} Tag Logística:        {passo_encontrado.tag_name or '-'}")
                self.log(f"  {tronco} Valor Esperado/Envio: {passo_encontrado.value if passo_encontrado.value is not None else '-'}")
                self.log(f"  {tronco} Tipo de Dado:         {passo_encontrado.data_type or 'Automático'}")
                self.log(f"  {tronco} Timeout configurado:  {passo_encontrado.timeout}s")
                self.log(f"  {tronco} Máximo de Tentativas: {passo_encontrado.retries}")
                self.log(f"  {tronco if acao_nome == "PRESS_PUSH_BUTTON" else terminacao} Retornar ao Passo:    {passo_encontrado.step_to_retry or 'Mesmo passo (Padrão)'}")
                if acao_nome == "PRESS_PUSH_BUTTON":
                    self.log(f"  └── Tempo do Pulso:       {passo_encontrado.pulse_time*1000}ms")
                self.log("-" * 80)
            else:
                self.log(f"⚠️ Passo #{ordem} não foi encontrado neste roteiro de teste.")
                self.log("-" * 80)

        if not encontrou_algum:
            self.log("❌ Nenhum dos passos informados existe no roteiro atual.")
            self.log("="*80)

    def to_json(self) -> str:
        """Converte o roteiro para um objeto JSON"""
        dados_passos = []

        for p in self.passos:
            dados_passos.append({
                "action": p.action.name,
                "tag_name": p.tag_name,
                "order": p.order,
                "value": p.value,
                "data_type": p.data_type,
                "timeout": p.timeout,
                "retries": p.retries,
                "step_to_retry": p.step_to_retry,
                "pulse_time": p.pulse_time,
                "description": p.description
            })

        is_ordenado = self.__verifica_ordenacao()    

        export_data = {
            "dicionario_opc" : self.dicionario_opc,
            "mapa_modbus" : self.mapa_modbus,
            "passos" : dados_passos,
            "ordenado" : is_ordenado
        }

        return json.dumps(export_data, indent=4, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TestScript':
        """Cria uma nova instância de TestScript a partir de um JSON"""

        from src.test import TestStep, Action
        dados = json.loads(json_str)

        # Garante compatibilidade com JSONs criados antes da atualização nos objetos
        if isinstance(dados, list):
            lista_passos = dados
            dict_opc = None
            mapa_mb = None
        else:
            lista_passos = dados.get("passos", [])
            dict_opc = dados.get("dicionario_opc")
            mapa_mb = dados.get("mapa_modbus")

        passos = []

        for item in lista_passos:
            action_enum = Action[item['action']]

            passo = TestStep(
                action=action_enum,
                tag_name = item.get('tag_name'),
                order = item.get('order'),
                value = item.get('value'),
                data_type = item.get('data_type'),
                timeout = item.get('timeout'),
                retries = item.get('retries'), 
                step_to_retry = item.get('step_to_retry'), 
                pulse_time = item.get('pulse_time'),
                description = item.get('description')
            )

            passos.append(passo)

        return cls(passos=passos, ordenado=False, dicionario_opc=dict_opc, mapa_modbus=mapa_mb)
    

    def __verifica_ordenacao(self) -> bool:
        """Verifica se o roteiro está ordenado ao salvar"""
        for i, p in enumerate(self.passos, 1):
            if p.order is None:
                return False
            elif p.order != i:
                return False            
        return True