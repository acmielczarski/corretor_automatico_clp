class MainWindowStyles:
    BTN_INICIAR_TESTE = """
        QPushButton {
            background-color: #2980b9; 
            font-weight: bold; 
            color: white;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        QPushButton:disabled {
            background-color: #555555; 
            color: #888888;
        }
    """

    LABEL_STATUS_ARQUIVO_BASE = """
        color: #27ae60;
        font-style: italic;
        padding-left: 5px;
    """

    LABEL_STATUS_ARQUIVO_OK = """
        color: #3498db;
        font-style: italic;
        padding-left: 5px;
    """

    LABEL_CABECALHO_LOG = """
        font-weight: bold;
        font-size: 14px;
    """

    TXT_LOG = """
        background-color: #1e1e1e;
        color: #d4d4d4;
    """