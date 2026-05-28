# src/modbus_client.py

from .clp_client import CLPClient, Protocol
from pymodbus.client import AsyncModbusTcpClient
from enum import Enum, auto

class ModbusType(Enum):
    COIL = auto()
    INPUT_STATUS = auto()
    INPUT_REGISTER = auto()
    HOLDING_REGISTER = auto()


class ModbusClpClient(CLPClient):
    """
    Cliente genérico para comunicação Modbus TCP com CLPs.

    Realiza leitura, escrita e varredura de variáveis do escopo FactoryIO.
    O Construtor vazio tenta conectar-se ao `localhost`.
    Herda :class:`CLPClient`

    :param url: Endereço do servidor Modbus TCP.
    :type url: str
    :param port: porta do servidor Modbus TCP.
    :type port: int
    """

    def __init__(self, url : str = '127.0.0.1', port : int = 502):
        super().__init__(url, port, Protocol.MODBUS_TCP)        
        self.client = AsyncModbusTcpClient(host=self.url, port=self.port)        

    async def connect(self):
        """
        Estabelece conexão com o servidor Modbus TCP.
        
        Utiliza :func:`pymodbus.client.AsyncModbusTcpClient.connect`.
        """       
        await self.client.connect()
        print(f"Conectado ao servidor Modbus em {self.url}:{self.port}")

    def disconnect(self):
        """
        Fecha a conexão com o servidor.
        
        Utiliza :func:`pymodbus.client.AsyncModbusTcpClient.close`.
        """
        self.client.close()   
        print(f"Conexão encerrada com servidor em {self.url}:{self.port}")

    def is_connected(self):
        """
        Verifica o status da conexão com o Servidor Modbus.

        :returns: `True` se a conexão está ativa com o servidor Modbus.
        :rtype: bool
        """
        return self.client.connected

    async def escanear_variaveis_disponiveis(self, mapa_modbus : dict = None):
        """
        Armazena os nomes, tipos e valores das variáveis Modbus contidas em `mapa_modbus`

        :param mapa_modbus: Objeto ``dict`` contendo o mapeamento das variáveis no servidor Modbus
        :type mapa_modbus: dict
        """
        self.tags = mapa_modbus if mapa_modbus is not None else {}
        print(f"[ModbusCLient] Mapa de IOs carregado. {len(self.tags)} variáveis configuradas.")

    async def read_node(self, node_obj : dict) -> bool | int:
        """
        Lê o valor real de um endereço Modbus.

        :param node_obj: ``dict`` contendo tipo e endereço para leitura.
        :type node_obj: dict

        :returns: valor lido no endereço
        :rtype: bool | int
        """
        tipo = node_obj['type']
        addr = node_obj['addr']

        try:
            if tipo == ModbusType.COIL:
                rr = await self.client.read_coils(addr)
                return rr.bits[0]
            elif tipo == ModbusType.INPUT_STATUS:
                rr = await self.client.read_discrete_inputs(addr)
                return rr.bits[0]
            elif tipo == ModbusType.INPUT_REGISTER:
                rr = await self.client.read_input_registers(addr)
                return rr.registers[0]
            elif tipo == ModbusType.HOLDING_REGISTER:
                rr = await self.client.read_holding_registers(addr)
                return rr.registers[0]
            else:
                print(f"[ModbusClient] Erro na operação de leitura Modbus, operação {tipo} não reconhecida")
                return False
        except Exception as e:
            print(f"[Modbus Client] Erro ao ler do servidor Modbus. {e}")

    async def write_node(self, node_obj : dict, valor : bool | int, tipo_dado = None):
        """
        Escreve ``valor`` em ``node_obj``.

        Escreve `bool` se ``type = ModbusType.COIL``. Escreve `int` se ``type = ModbusType.HOLDING_REGISTER``
        
        :param node_obj: ``dict`` contendo tipo e endereço para escrita.
        :type node_obj: dict
        :param valor: valor que será escrito no endereço.
        :type valor: bool | int
        :returns: `True` se a operação de escrita for bem sucedida. Retorna `False` caso `type` seja `INPUT_STATUS` ou `HOLDING_REGISTER`.
        :rtype: bool
        :raises Exception: caso algum erro ocorra no processo de escrita.
        """
        tipo = node_obj['type']
        addr = node_obj['addr']

        try:
            if tipo == ModbusType.COIL:
                await self.client.write_coil(addr, bool(valor))
            elif tipo == ModbusType.HOLDING_REGISTER:
                await self.client.write_register(addr, int(valor))
            else:
                print(f"[ModbusClient] Tipo {tipo.name} não suporta operação de escrita.")
                return False
            return True        
        except Exception as e:
            print(f"[ModbusClient] Erro ao escrever em {tipo.name} {addr}. {e}")
