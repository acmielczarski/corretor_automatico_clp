# main.py (na raiz do projeto)
import sys
import asyncio
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# O Python entra em src/, vê que é um pacote, entra em gui/ e acha a Main Window
from src.gui.main_window import AvaliadorCLPGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    gui = AvaliadorCLPGUI()
    gui.show()
    
    with loop:
        loop.run_forever()