# src/opc_clp_client.py
from asyncua import Client, ua
from .clp_client import CLPClient, Protocol

class OpcClpClient(CLPClient):
    """
    Cliente genérico para comunicação OPC UA com CLPs (focado em CODESYS).

    Realiza leitura, escrita e varredura de variáveis do escopo FactoryIO.
    O Construtor vazio tenta conectar-se ao `localhost`.
    Herda :class:`CLPClient`

    :param url: Endereço do servidor OPC UA.
    :type url: str
    :param port: porta do servidor OPC UA.
    :type port: int
    """
    def __init__(self, url: str = '127.0.0.1', port: int = 4840):
        super().__init__(url, port, Protocol.OPC_UA)
        self.opc_url = f"opc.tcp://{url}:{port}"
        self.client = Client(url=self.opc_url)
        self.tags = {}  # Guarda { 'Nome_Do_Node': Objeto_Do_No }

    async def connect(self):
        """
        Estabelece conexão com o servidor OPC UA.
        
        Utiliza :func:`asyncua.Client.connect`.
        """
        await self.client.connect()
        print(f"[CLPClient] Conectado ao servidor OPC UA em {self.opc_url}")

    async def disconnect(self):
        """
        Fecha a conexão com o servidor.
        
        Utiliza :func:`asyncua.Client.disconnect`.
        """
        await self.client.disconnect()
        print("[CLPClient] Desconectado do servidor.")

    async def is_connected(self) -> bool:
        """
        Verifica o status da conexão com o Servidor OPC.

        :returns: `True` se a conexão está ativa com o servidor OPC.
        :rtype: bool
        :raises ConnectionError, UaError: Descrição do erro de conexão com o `CLPClient`
        """
        try:
            await self.client.check_connection()
            return True
        except (ConnectionError, ua.UaError) as e:
            print(f"[CLPClient] Sem com o servidor OPC UA. {e}")

    async def escanear_variaveis_disponiveis(self, gvl_name : str = 'FactoryIO', verbose : bool = True):
        """
        Varre o servidor e mapeia todas as variáveis do escopo informado.
        Armazena os nomes dos nodes e o endereço em `CLPClient.tags`.

        :param gvl_name: Nome da GVL para procurar no servidor OPC UA. *Default: FactoryIO*
        :type gvl_name: str
        :param verbose: Se `True` mostra os nomes dos nodes e os nodeIds encontrados. *Default: True*
        :type verbose: bool
        """
        objects = self.client.nodes.objects
        self.tags = {} 
        
        async def _buscar(no_atual):
            try:
                node_id_str = str(no_atual.nodeid)
                if gvl_name.lower() in node_id_str.lower():
                    tipo_no = await no_atual.read_node_class()
                    if tipo_no == ua.NodeClass.Variable:
                        browse_name = await no_atual.read_browse_name()
                        self.tags[browse_name.Name] = no_atual
                
                for filho in await no_atual.get_children():
                    if filho.nodeid.NamespaceIndex not in [0, 1]:
                        await _buscar(filho)
            except Exception:
                pass

        await _buscar(objects)
        print(f"[CLPClient] Varredura concluída. {len(self.tags)} variáveis encontradas.")

        if verbose:
            print("Nodes encontrados:")
            for k, v in self.tags.items():
                print(f"Nome: {k} | Node ID: {v}")

    async def read_node(self, node_obj):
        """
        Lê o valor real de um nó do OPC UA.

        :param node_obj: nodeId que será lido.
        :type node_obj: str

        :returns: valor lido em `node_obj`
        :rtype: Any
        """
        return await node_obj.read_value()

    async def write_node(self, node_obj, valor, tipo_dado: str = None):
        """
        Escreve ``valor`` em ``node_obj``.
        
        :param node_obj: nodeId que será escrito.
        :type node_obj: str
        :param valor: valor que será escrito no node.
        :type valor: Any
        :param tipo_dado: Tipo de dado que será escrito.
        :type tipo_dado: str
        """
        try:
            if tipo_dado == "BOOL":
                await node_obj.write_value(ua.DataValue(ua.Variant(bool(valor), ua.VariantType.Boolean)))
            elif tipo_dado == "INT16":
                await node_obj.write_value(ua.DataValue(ua.Variant(int(valor), ua.VariantType.Int16)))
            elif tipo_dado == "INT32":
                await node_obj.write_value(ua.DataValue(ua.Variant(int(valor), ua.VariantType.Int32)))
            elif tipo_dado == "INT64":
                await node_obj.write_value(ua.DataValue(ua.Variant(int(valor), ua.VariantType.Int64)))
            elif tipo_dado == "FLOAT":
                await node_obj.write_value(ua.DataValue(ua.Variant(float(valor), ua.VariantType.Float)))
            else:
                await node_obj.write_value(valor)
        except Exception as e:
            print(f"Erro ao escrever valor.\nNode:{node_obj}\nErro: {e}")