# src/gui/styles/card_passo_styles

class CardPassoStyles:
    """Declaração dos estilos CSS para o Card Passo"""

    CARD_BASE = """
        CardPassoTeste { 
            background-color: #1e1e1e; 
            border: 1px solid #3d3d3d; 
            border-radius: 10px; 
        }
        QLabel { color: #f5f5f5; font-weight: bold; }
        QLineEdit, QComboBox { 
            background-color: #2d2d2d; 
            color: white; 
            border: 1px solid #3d3d3d; 
            padding: 4px; 
            border-radius: 4px;
        }
    """

    BTN_EDITAR = """
        QPushButton {
            background-color: #2980b9; 
            color: white;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        QPushButton:disabled {
            background-color: #555555; 
            color: #888888;
        }
    """
    
    BTN_SALVAR = """
        QPushButton {
            background-color: #27ae60; 
            color: white; 
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2ecc71;
        }
        QPushButton:disabled {
            background-color: #555555; 
            color: #888888;
        }
    """

    BTN_CANCELAR = """
        QPushButton {
            background-color: #7f8c8d;
            color: white;
        }
        QPushButton:hover {
            background-color: #95a5a6;
        }
        QPushButton:disabled {
            background-color: #555555; 
            color: #888888;
        }
    """

    BTN_EXCLUIR = """
        QPushButton {
            background-color: #c0392b;
            color: white;
        }
        QPushButton:hover {
            background-color: #e74c3c;
        }
        QPushButton:disabled {
            background-color: #555555; 
            color: #888888;
        }
    """

class TabPassosStyles:
    """Declaração dos estilos CSS para a Aba Passos"""

    BTN_NOVO = """
        QPushButton {
            background-color: #27ae60; 
            font-weight: bold; 
            color: white;
        }
        QPushButton:hover {
            background-color: #2ecc71;
        }
        QPushButton:disabled {
            background-color: #555555; 
            color: #888888;
        }
    """

    SCROLL_AREA = """
        QScrollArea {
            border: none;
            background-color: transparent;
        }
    """
