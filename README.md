# 🏭 Avaliador Automático de CLP

Uma ferramenta de automação e interface gráfica (GUI) desenvolvida em Python para avaliar, testar e validar a lógica de Controladores Lógicos Programáveis (CLPs). Projetado com foco em ambientes educacionais e de laboratório, o software permite a criação de roteiros de testes dinâmicos sem necessidade de programação por parte do usuário final.

## ✨ Principais Funcionalidades

* **Comunicação Multi-Protocolo:** Suporte nativo para conexão com CLPs via **OPC UA** e **Modbus TCP**.
* **Motor de Testes Assíncrono:** Execução fluida de roteiros de validação utilizando `qasync`, garantindo que a interface permaneça responsiva durante a comunicação industrial.
* **Criação Visual de Roteiros:** Interface baseada em "Cartões de Passo" dinâmicos (Model-View-Controller) para montagem de sequências lógicas.
* **Ações de Teste Industriais:** Suporte a comandos robustos como `WRITE`, `READ_EQUAL`, `COMPARISON` (>, <, ==, !=), `PRESS_PUSH_BUTTON` (pulsos simulados), `WAIT_CHANGE` e `SLEEP`.
* **Dicionário e Mapeamento OPC:** Tabela de configuração (CRUD) inteligente para mapear Tags lógicas, endereços físicos e sinônimos, com tratativas específicas para variáveis discretas (BOOL) e analógicas (INT/FLOAT).
* **Geração de Relatórios:** Log de execução detalhado em tempo real com zoom acessível, exportável para `.txt` com cabeçalho de *timestamp* automático.

## 🛠️ Stack Tecnológica e Arquitetura

* **Linguagem Base:** Python 3
* **Interface Gráfica:** PySide6 (Qt for Python)
* **Assincronicidade:** `asyncio` e `qasync`
* **Arquitetura UI:** Padrão MVC e Separação de Responsabilidades (SoC). Os componentes visuais complexos (como o `CardPassoTeste`) são divididos em:
  * `*_ui.py`: Construtores visuais (Views).
  * `*_rules.py`: Motor de regras de negócio estáticas (Business Logic/Fallbacks).
  * `*.py`: Orquestradores (Controllers) que gerenciam estado e I/O.

## 📁 Estrutura de Diretórios

O projeto segue um padrão modular organizado:

```text
CORRETOR_AUTOMATICO_CLP/
├── db/                   # Roteiros padrão e banco de dados JSON salvos
├── src/                  # Código-fonte principal
│   ├── clp/              # Módulos de comunicação (OpcClpClient, ModbusClpClient, Protocolos)
│   ├── gui/              # Interface gráfica e componentes (PySide6)
│   │   ├── components/   # Tabs, Cards isolados e Widgets customizados
│   │   ├── custom_widgets# Componentes Qt sobrescritos (ex: NoScrollComboBox)
│   │   └── main_window.py# Janela e orquestrador principal
│   └── test/             # Classes de domínio (TestEngine, TestScript, TestStep, Actions)
├── main.py               # Ponto de entrada do aplicativo (Entrypoint)
├── pyproject.toml        # Configurações de dependências
└── README.md             # Documentação do projeto