# main.py

import sys
import asyncio
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLibraryInfo
from qasync import QEventLoop

# O Python entra em src/, vê que é um pacote, entra em gui/ e acha a Main Window
from src.gui.main_window import AvaliadorCLPGUI

#TODO implementar um arquivo de configuração (*json) para armazenar as preferências do usuário.
# podendo salvar ao sair do programa. salvar caminho para os roteiros salvos, qual o último roteiro utilizado
# para carregar automaticamente ao abrir o programa de novo.

if __name__ == "__main__":
    app = QApplication(sys.argv)

    tradutor = QTranslator()
    translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if tradutor.load("qtbase_pt_BR", translations_path) or tradutor.load("qt_pt_BR", translations_path):
        app.installTranslator(tradutor)
    else:
        print("[main] Aviso: Arquivos de tradução PT_BR não encontrados.")

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    gui = AvaliadorCLPGUI()
    gui.show()
    
    with loop:
        loop.run_forever()