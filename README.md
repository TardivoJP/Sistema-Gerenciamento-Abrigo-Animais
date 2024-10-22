# Sistema de Gestão de ONG de Abrigo de Animais

Este é um sistema desenvolvido para auxiliar na gestão de ONGs que oferecem abrigo e adoção de animais. A aplicação oferece uma interface gráfica desenvolvida em **Python** usando **PyQt6** e armazena dados utilizando **SQLite**.

O sistema permite gerenciar informações sobre os animais, adotantes, voluntários, adoções, doações, além de oferecer uma seção de análise com gráficos e estatísticas sobre as operações da ONG.

## Funcionalidades

### 1. **Home**

-   Tela inicial com uma visão geral do sistema.
 ![Home](https://i.imgur.com/FFBi00x.png)

### 2. **Cadastros**

-   **Animais**: Gerenciamento de animais disponíveis para adoção, com possibilidade de adicionar, editar e remover registros.
-   **Adotantes**: Cadastro de adotantes, com informações detalhadas como nome, endereço, telefone, CPF, entre outros.
-   **Voluntários**: Cadastro de voluntários que participam das atividades da ONG, com registro de habilidades, disponibilidade, etc.
![Cadastros](https://i.imgur.com/g9SMGPt.png)
### 3. **Processos**

-   **Adoções**: Registro e acompanhamento das adoções, associando animais a adotantes, com controle de status.
-   **Doações**: Gerenciamento de doações realizadas, associadas a voluntários.

### 4. **Análise e Insights**

-   Gráficos e estatísticas sobre o desempenho da ONG, como:
    -   Adoções ao longo do tempo.
    -   Quantidade de animais no abrigo.
    -   Participação de voluntários.
    -   Resumo de doações recebidas.
![Analise](https://i.imgur.com/QUlgqwa.png)
## Pré-requisitos

-   **Python 3.8+**
-   **Bibliotecas**:
    -   PyQt6: `pip install PyQt6`
    -   SQLite (já incluído no Python por padrão)
    -   Matplotlib (para gráficos): `pip install matplotlib`

## Instalação

1.  Clone o repositório:
    

```Bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

2. Navegue até o diretório do projeto:

```Bash
cd seu-repositorio
```

3. Instale as dependências:

```Bash
pip install -r requirements.txt
```

4. Execute o arquivo principal:

```Bash
python main.py
```

## Como Usar

1.  **Navegação**: Utilize a barra lateral para acessar diferentes seções do sistema, como Cadastros, Processos e Análises.
2.  **Gerenciamento de Animais e Pessoas**: Adicione, edite ou remova registros de animais, adotantes e voluntários através das tabelas de cada módulo.
3.  **Registros de Adoções e Doações**: Associe adoções e doações a voluntários e adotantes de forma fácil.
4.  **Estatísticas**: Visualize gráficos e estatísticas na seção "Análise e Insights" para monitorar o desempenho da ONG.

## Estrutura do Projeto

```Bash
├── analytics_module.py      # Módulo responsável pelos gráficos e estatísticas
├── animal_module.py         # Módulo de gerenciamento de animais
├── adoption_module.py       # Módulo de gerenciamento de adoções
├── adopter_module.py        # Módulo de gerenciamento de adotantes
├── volunteer_module.py      # Módulo de gerenciamento de voluntários
├── donation_module.py       # Módulo de gerenciamento de doações
├── database.py              # Configuração do banco de dados SQLite
├── main.py                  # Arquivo principal que integra todos os módulos
└── README.md                # Arquivo de documentação do projeto
```