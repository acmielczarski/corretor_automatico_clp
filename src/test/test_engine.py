# src/test_engine.py
import asyncio
from typing import Any, Callable
import operator
import time
from src.clp.opc_client import CLPClient, Protocol
from src.test.test_strucuture import TestScript, TestStep, Action

class TestEngine:
    """
    Motor executor que recebe um roteiro de testes (lista de TestSteps),
    traduz os nomes das tags usando o mapeamento e executa as ações no CLP.

    :param clp_client: Objeto de :class:`CLPClient`
    :type clp_client: CLPClient    
    :param roteiro: Roteiro do teste da classe :class:`TestScript`, contendo passos do teste, dicionário OPC e mapeamento Modbus.
    :type roteiro: TestScript
    :param log_callback: Destino dos logs dos testes realizados. Por padrão utiliza o `print`, escrevendo no terminal.
    :type log_callback: Callable[[str], None]
    """
    def __init__(self,
                 clp_client: CLPClient,
                 roteiro : TestScript,
                 log_callback: Callable[[str], None] = None):
        
        self.clp = clp_client
        self.tags_mapeadas = {}
        self.log = log_callback if log_callback is not None else print
        self.__mapa_operadores = {
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            ">" : operator.gt,
            "<" : operator.lt
        }        
        self.roteiro = self._ordenar_teste(roteiro) if not roteiro.ordenado else roteiro

    #TODO melhorar a identificação de variáveis com nomes parecidos (tipo liga e desliga), caso procure por LIGA, pode encontrar qualquer uma das duas
    def mapear_tags_locais(self) -> bool:
        """Faz o casamento de sinônimos com as variáveis escaneadas do CLP."""
        self.tags_mapeadas = {}
        for nome_real_clp, no_objeto in self.clp.tags.items():
            nome_clp_lower = nome_real_clp.lower()
            
            for tag_padrao, values in self.roteiro.dicionario_opc.items():
                sinonimos = values.get('alias')
                if any(sinonimo in nome_clp_lower for sinonimo in sinonimos):
                    if tag_padrao not in self.tags_mapeadas:
                        self.tags_mapeadas[tag_padrao] = no_objeto
                        break
                        
        tags_faltantes = set(self.roteiro.dicionario_opc.keys()) - set(self.tags_mapeadas.keys())
        if tags_faltantes:
            self.log(f"[TestEngine] ❌ Erro de Mapeamento. Tags críticas ausentes: {tags_faltantes}")
            return False
        self.log(f"[TestEngine] Mapeamento concluído com sucesso ({len(self.tags_mapeadas)} tags).")
        return True           

    async def executar_roteiro(self) -> bool:
        """
        Percorre e executa sequencialmente cada passo do roteiro.
        
        :returns: Resultado do teste. ``True`` se concluido, ``False`` caso falhe em algum passo.
        :rtype: bool
        """
        if not self.tags_mapeadas:
            if not self.mapear_tags_locais():
                return False        
        
        self._zera_retries() # Certifica que todos os retries começam em 0 para o teste

        ponteiro = 0 # Controle de execução dos passos
        total_passos = len(self.roteiro) # Quantidade total de passos no teste

        self.log("\n" + "="*60)
        self.log("INICIANDO EXECUÇÃO DO ROTEIRO DE TESTE")
        self.log(f"Total de passos: {total_passos}")
        self.log("="*60)

        while ponteiro < total_passos:

            # Inicialização do passo a ser executado
            passo = self.roteiro.passos[ponteiro]           

            desc = passo.description or f" {passo.action.name} em {passo.tag_name}"
            if passo.action == Action.SLEEP and not passo.description:
                desc = f"{passo.action.name} de {passo.timeout}s"

            
            # Indica se é o início do teste ou já é um retry
            if passo._current_retry == 0:
                self.log(f"\n▶️ Executando Passo {passo.order}: {desc}")
            else:
                self.log(f"\n🔄 [Tentativa {passo._current_retry + 1}/{passo.retries}] Executando Passo {passo.order}: {desc}")

            sucesso = await self._do_executa_passo(passo)            

            # Caso o teste seja bem-sucedido, segue par ao próximo passo
            if sucesso:
                self.log("    ✅ Passo concluído com sucesso.")
                ponteiro += 1
            else:
                passo._current_retry += 1

                if passo._current_retry < passo.retries:
                    await asyncio.sleep(0.2) # Pequeno tempo entre retries          

                    # Verifica para qual passo o teste deve voltar
                    if passo.step_to_retry is not None:
                        novo_ponteiro = None                      
                        # Busca no roteiro pelo passo alvo indicado pelo passo atual para reexecução
                        for i, p in enumerate(self.roteiro):
                            if p.order == passo.step_to_retry:
                                novo_ponteiro = i
                                break
                        # Coloca a execução para o passo encontrado
                        if novo_ponteiro is not None:
                            self.log(f"    ⚠️ Falha detectada. Executando o passo: {passo.step_to_retry}...")
                            ponteiro = novo_ponteiro
                            continue

                else:
                    self.log(f"\n❌ ROTEIRO FALHOU NO PASSO {passo.order}: {desc}")
                    self.log("="*60)
                    return False           

        self.log("\n" + "="*60)
        self.log(" 🎉 PARABÉNS! Todo o roteiro foi executado com SUCESSO!")
        self.log("="*60)
        return True
    
    # --- Métodos Auxiliares de Ação ---

    async def _wait_for_value(self, node_obj, target_value: Any, timeout: float) -> bool:
        """Loop interno de polling para aguardar uma tag atingir o valor esperado."""
        intervalo = 0.1
        passos_totais = int(timeout / intervalo)
        
        for _ in range(passos_totais):
            await asyncio.sleep(intervalo)
            if await self.clp.read_node(node_obj) == target_value:
                return True
        self.log(f"    [Timeout] A variável não atingiu o valor {target_value} em {timeout}s.")
        return False
    
    async def _do_write(self, tag : str, val : Any) -> bool:
        """Escreve em alguma Tag"""
        no = self.tags_mapeadas[tag]
        if self.clp._protocol == Protocol.OPC_UA:
            tipo = self.roteiro.dicionario_opc.get('type')
        elif self.clp._protocol == Protocol.MODBUS_TCP:
            tipo = self.roteiro.mapa_modbus.get('type')    
        await self.clp.write_node(no, val, tipo_dado=tipo)
        return True

    async def _do_read_equal(self, tag : str, expected : Any) -> bool:
        """Verifica o valor de uma variável"""
        no = self.tags_mapeadas[tag]
        atual = await self.clp.read_node(no)
        if atual == expected:
            return True
        
        self.log(f"    [Erro] Esperado: {expected} | Lido: {atual}")
        return False

    async def _do_wait(self, tag : str, val : Any, timeout : float) -> bool:
        """Aguarda o valor de uma variável boolena"""
        no = self.tags_mapeadas[tag]        
        tempo_limite = time.monotonic() + timeout
        while time.monotonic() <= tempo_limite:
            await asyncio.sleep(0.1)
            if await self.clp.read_node(no) == val:
                return True
        self.log(f"    [Timeout] A variável não atingiu a condição '{val}' em {timeout}s.")
        return False

    async def _do_press_button(self, tag : str, pulse_time : float, value : bool = True) -> bool:
        """Executa a sequência Acionar -> Esperar -> Desacionar."""
        no = self.tags_mapeadas[tag]
        self.log(f"    [Pulso] Acionando {tag}...")
        tempo_limite = time.monotonic() + pulse_time
        while time.monotonic() <= tempo_limite:
            await self.clp.write_node(no, value, tipo_dado="BOOL")
            await asyncio.sleep(0.1)       
        self.log(f"    [Pulso] Desacionando {tag}...")
        await self.clp.write_node(no, not value, tipo_dado="BOOL")
        return True
    
    async def _do_comparison(self, tag : str, exp : str) -> bool:
        """Verifica o valor de uma tag de acordo com a expressão informada"""
        val_str, op_func = self.__verifica_operador(exp)
        if not val_str:
            return
        try:
            val = float(val_str) if "." in val_str else int(val_str)
        except Exception as e:
            self.log(f"[TestEngine] ❌ Erro de Parsing de valor:\n{e}")
            return False
        no = self.tags_mapeadas[tag]
        atual = await self.clp.read_node(no)

        if op_func(atual, val):
            return True

        self.log(f"    [Erro] Esperado: {exp} | Valor atual: {atual}")
        return False
    
    async def _do_wait_until(self, tag : str, exp : str, timeout : float) -> bool:
        """Aguarda que o valor de uma variável chegue na expressão informada"""
        val_str, op_func = self.__verifica_operador(exp)
        try:            
            val = float(val_str) if "." in val_str else int(val_str)            
        except Exception as e:
            self.log(f"[TestEngine] ❌ Erro de Parsing de valor:\n{e}")
            return False
        else:
            if self.clp._protocol == Protocol.OPC_UA:
                pass
            elif self.clp._protocol == Protocol.MODBUS_TCP:
                val = int(val*10)

        # Executa o teste
        no = self.tags_mapeadas[tag]
        intervalo = 0.1
        tempo_limite = time.monotonic() + timeout
        while time.monotonic() <= tempo_limite:
            await asyncio.sleep(intervalo)
            leitura = await self.clp.read_node(no)
            if op_func(leitura, val):
                return True            
        self.log(f"    [Timeout] A variável não atingiu a condição '{exp}' em {timeout}s.")
        return False
    
    def __verifica_operador(self, exp : str) -> list[str, Any] | list[bool, None]:
        # Trata a string de expressão eliminando espaços caso possua
        if " " in exp:
            exp = exp.replace(" ", "")

        # Identifica a operação solicitada        
        op_str = None # String da operação
        op_func = None # Objeto de operator de acordo com a string da operação

        # Procura pela comparação dentro do mapa de operadores e atribui o operador caso encontre
        # Levanta um erro caso não encontre o operador enviado em exp
        for op_chave, funcao in self.__mapa_operadores.items():
            if op_chave in exp:
                op_str = op_chave
                op_func = funcao
                break
        if not op_str:    
            self.log("    [Erro] Operador de comparação não identificado")
            return [False, None]        
        # Separa e trata o valor informado em exp
        _, val_str = exp.split(op_str, 1)

        return [val_str, op_func]
        
    
    async def _do_executa_passo(self, passo : TestStep) -> bool:
        """Executa a ação do passo"""
        try:
            if passo.action == Action.WRITE:
                return await self._do_write(passo.tag_name, passo.value, passo.data_type)
                       
            elif passo.action == Action.READ_EQUAL:
                return await self._do_read_equal(passo.tag_name, passo.value)
                        
            elif passo.action == Action.WAIT_CHANGE:
                return await self._do_wait(passo.tag_name, passo.value, passo.timeout)
                        
            elif passo.action == Action.SLEEP:
                await asyncio.sleep(passo.timeout)
                return True
            
            elif passo.action == Action.PRESS_PUSH_BUTTON:
                return await self._do_press_button(passo.tag_name, passo.pulse_time)            
            
            elif passo.action == Action.NO_ACTION:
                return True            
            
            elif passo.action == Action.WAIT_UNTIL:
                return await self._do_wait_until(passo.tag_name, passo.value, passo.timeout)            
            
            elif passo.action == Action.COMPARISON:
                return await self._do_comparison(passo.tag_name, passo.value)
            
            else:
                self.log(f"    ❌ Ação desconhecida: {passo.action}")
                return False
            
        except Exception as e:
            self.log(f"    ❌ Erro de execução na tentativa {passo.order}: {e}")


    def _ordenar_teste(self, roteiro : TestScript) -> TestScript:
        """
        Ordena os passos de acordo com o roteiro passado.
        """        
        for idx, passo in enumerate(roteiro.passos,1):
            passo.order = idx
            passo._current_retry = 0

        roteiro.ordenado = True

        return roteiro
    
    def _zera_retries(self):
        """Função para zerar os valores do atributo ``TestStep._current_retry``"""
        for _, passo in enumerate(self.roteiro):
            passo._current_retry = 0