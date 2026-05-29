# 🤝 Como Contribuir para o Avaliador de CLP

Ficamos felizes com o seu interesse em contribuir! Este documento serve como guia para garantir que o projeto cresça mantendo a qualidade e a organização.

## 🛠️ Processo de Contribuição (O Básico)

1. Faça um **Fork** deste repositório.
2. Crie uma branch para a sua feature ou correção: `git checkout -b feature/minha-nova-feature` ou `fix/correcao-bug`.
3. Faça suas alterações e *commits*.
4. Envie para o seu Fork: `git push origin feature/minha-nova-feature`.
5. Abra um **Pull Request (PR)** detalhando as suas mudanças.

## 🏛️ Padrões de Arquitetura e Código

Para manter o código limpo e escalável, seguimos algumas regras de ouro neste projeto:

* **Padrão MVC na Interface (PySide6):** Evite os monólitos de código. Se for criar um componente visual complexo, divida-o em:
  * `_ui.py` (Apenas layouts, estilos e instâncias de widgets).
  * `_rules.py` (Regras de negócio e travas de interface como `@staticmethod`).
  * `arquivo_principal.py` (Apenas eventos, sinais e orquestração).
* **Tipagem:** Utilize *Type Hints* do Python sempre que possível (ex: `def calcular_tempo(valor: float) -> bool:`).
* **Nomenclatura:** Variáveis e métodos em `snake_case`. Classes em `PascalCase`. Métodos internos/protegidos devem iniciar com um `_` (underscore).

## 🧪 Testes e Validações

Antes de abrir o seu PR, certifique-se de que:
- O código roda localmente sem erros no terminal.
- Nenhuma funcionalidade de leitura/escrita OPC UA ou Modbus foi quebrada com as suas alterações.
- A interface se adapta corretamente ao redimensionamento da janela.

Obrigado por ajudar a melhorar a automação industrial de código aberto!