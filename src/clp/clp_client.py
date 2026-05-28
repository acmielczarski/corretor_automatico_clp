# src/clp_clien.py

from typing import Any
from enum import Enum, auto

class Protocol(Enum):
    OPC_UA = auto()
    MODBUS_TCP = auto()

class VarDataType(Enum):
    """Tipos de dados para as variáveis. Divididos em `Basic` e `Extended`"""
    class Basic(Enum):
        """Tipos de variáveis básicas"""
        BOOL = auto()
        INT16 = auto()
        UINT16 = auto()
        INT32 = auto()
        UINT32 = auto()
        FLOAT = auto()

    class Extended(Enum): 
        """Tipos especializados e variáveis"""   
        INT64 = auto()
        UINT64 = auto()    
        DOUBLE = auto()
        STRING = auto()
        DATE_TIME = auto()
        EXTENSION_OBJECT = auto()

class CLPClient:
    """
    Classe abstrata que define a comunicação entre o Script e o CLP
    Todos os protocolos de comunicação devem herdar esta classe.
    """
    def __init__(self, url : str, port : int, protocol : Protocol):
        self.url = url
        self.port = port
        self._protocol = protocol
        self.tags = {}       

    async def connect(self):
        raise NotImplementedError(f"O método connect() não foi implementado para protocolo {self._protocol.name}.")
    
    async def disconnect(self):
        raise NotImplementedError(f"O método disconnect() não foi implementado para protocolo {self._protocol.name}.")
    
    async def escanear_variaveis_disponiveis(self, *args, **kwargs):
        raise NotImplementedError("O método escanear_variaveis_disponiveis() não foi implementado para protocolo {self._protocol.name}.")
    
    async def read_node(self, node_obj: Any) -> Any:
        raise NotImplementedError("O método read_node() não foi implementado para protocolo {self._protocol.name}.")

    async def write_node(self, node_obj: Any, valor: Any, tipo_dado: str = None) -> bool:
        raise NotImplementedError("O método write_node() não foi implementado para protocolo {self._protocol.name}.")

    def get_protocol(self) -> str:
        return self._protocol.name