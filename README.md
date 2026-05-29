# 🏭 Avaliador Automático de CLP

Uma ferramenta de automação e interface gráfica (GUI) desenvolvida em Python para avaliar, testar e validar a lógica de Controladores Lógicos Programáveis (CLPs). Projetado com foco em ambientes educacionais e de laboratório, o software permite a criação de roteiros de testes dinâmicos sem necessidade de programação por parte do usuário final.  
Este software foi desenvolvida utilizando `Codesys` comunicando com o software de simulação `Factory I/O`, visando a correção automática de tarefas de estudantes do Curso Técnico em Automação Industrial. Simulações no `Factory I/O` que utilizam um escopo de funcionamento bem estruturada em passos, podem ser facilmente avaliadas automaticamente com este código.  
Embora este software tenha sido desenvolvido e testado no ambiente `Codesys`, qualquer CLP que possua comunicação OPC UA ou Modbus TCP ajustando os valores de configuração dos passos e mapeamento de endereços.

Me mande um [e-mail](mailto:andrew.mielczarki@senairs.org.br) caso queira contrinuir ou dar sugestões.  
Andrew Mielczarski:
<andrew.mielczarski@senairs.org.br>

* **INFO:** também foram realizados testes utilizando o CLP da família M221 (M221CE40T) da `Schneider Eletric` utilizando comunicação Modbus TCP*

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
├── db/                    # Roteiros JSON padrão
├── src/                   # Código-fonte principal
│   ├── clp/               # Módulos de comunicação (OpcClpClient, ModbusClpClient, Protocolos)
│   ├── gui/               # Interface gráfica e componentes (PySide6)
│   │   ├── components/    # Tabs, Cards isolados e Widgets customizados
│   │   ├── custom_widgets # Componentes Qt sobrescritos (ex: NoScrollComboBox)
│   │   └── main_window.py # Janela e orquestrador principal
│   └── test/              # Classes de domínio (TestEngine, TestScript, TestStep, Actions)
├── main.py                # Ponto de entrada do aplicativo (Entrypoint)
├── pyproject.toml         # Configurações de dependências
└── README.md              # Documentação do projeto
```

## 🚀 Instalação e Uso Local
Pré-requisitos
  * Python 3.12 ou superior instalado na máquina.
  * Gerenciador de pacotes `pip`.

### Passos de Instalação
  1. Clone o repositório:

```powershell
  git clone https://github.com/acmielczarski/corretor_automatico_clp.git
  cd corretor_automatico_clp
```

  2. Crie e ative um ambiente virtual (Recomendado):

```powershell
  python -m venv .venv
  # No Windows:
  .venv\Scripts\activate
  # No Linux/Mac:
  source .venv/bin/activate
```
  3. Instale as dependências:

```powershell
  python -m uv sync --no-dev
 ```

  4. Execute a aplicação:

```powershell
  python main.py
```
## 🧠 Como Funciona o Fluxo de Teste
* **Conexão:** Na tela principal, o usuário define o IP e a porta (ex: 4840 para OPC ou 502 para Modbus) e escolhe o protocolo.

* **Configuração OPC/Modbus:** Através do botão "Configurar Roteiro", o usuário cadastra as Tags do CLP na aba correspondente, definindo seus tipos e sinônimos lógicos.

* **Criação do Roteiro:** Na aba de "Passos de Teste", o usuário adiciona os cartões de ação. O software possui Proteção UX (Fallbacks) que impede a seleção de comandos incompatíveis com o tipo da variável (ex: aplicar COMPARISON em variável booleana).

* **Execução e Avaliação:** O JSON do roteiro é injetado no TestEngine, que se comunica com o equipamento físico/simulado e retorna o diagnóstico (Pass/Fail) no painel de Logs.

## 📄 Licença
Este projeto é para uso educacional/privado, sob licença GNU General Public License v3.0.
