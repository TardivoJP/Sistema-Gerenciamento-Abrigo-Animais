# Sistema de Gestão de ONG de Abrigo de Animais

Este é um sistema desenvolvido em **Python** (utilizando **PyQt6** e **SQLite**) para auxiliar ONGs que oferecem abrigo, adoção de animais e recebem doações. O sistema permite gerenciar informações sobre animais, adotantes, voluntários, adoções, doações, além de oferecer análises visuais e um módulo de relatórios.

## Funcionalidades

### 1. **Home**
- Tela inicial com uma visão geral simples do sistema.

### 2. **Cadastros**
- **Animais**: Gerenciamento completo, com possibilidade de adicionar, editar, remover e filtrar por nome, tipo, raça e status.  
  Validações incorporadas (ex: nome, tipo e raça obrigatórios).
- **Adotantes**: Cadastro detalhado, com validações em campos como telefone (formatação dinâmica), CPF (11 dígitos), endereço obrigatório e renda numérica.
- **Voluntários**: Cadastro com campos como telefone, CPF validados e formatados, endereço obrigatório, e outros campos opcionais (disponibilidade, habilidades, experiência, motivação).

### 3. **Processos**
- **Adoções**: Registro e acompanhamento das adoções, associando animais a adotantes. Possibilidade de filtrar por ID, adotante, animal, status e data. Também há validações (não adotar animal já adotado).
- **Doações**: Registro de doações associadas a voluntários, com filtragens por período e validações no valor das doações.

### 4. **Análise e Insights**
- Gráficos e estatísticas interativas sobre:
  - Adoções ao longo do tempo (com filtragem por ano).
  - Distribuição de raças de animais não adotados no abrigo.
  - Doações ao longo do tempo (com filtragem por ano).
  - Participação de voluntários (porcentagem ativos/inativos, média de doações por voluntário ativo).
  
### 5. **Relatórios**
- Geração de relatórios resumidos sobre o estado atual da ONG em um intervalo de datas.
- Exibição em tela e opção de exportar para PDF (usando `reportlab` caso disponível).
- Inclui informações como:
  - Número de animais disponíveis.
  - Adoções realizadas no período.
  - Total de doações no período.
  - (E outras estatísticas dependendo dos dados disponíveis.)

## Pré-requisitos

- **Python 3.8+**
- **Bibliotecas**:
  - PyQt6: `pip install PyQt6`
  - Matplotlib (para gráficos): `pip install matplotlib`
  - (Opcional) reportlab para exportar relatório em PDF: `pip install reportlab`

Abaixo está uma versão atualizada do README, sem imagens e refletindo as melhorias realizadas recentemente, incluindo validações, filtragens, novos módulos e a seção de relatório:

# Sistema de Gestão de ONG de Abrigo de Animais

Este é um sistema desenvolvido em **Python** (utilizando **PyQt6** e **SQLite**) para auxiliar ONGs que oferecem abrigo, adoção de animais e recebem doações. O sistema permite gerenciar informações sobre animais, adotantes, voluntários, adoções, doações, além de oferecer análises visuais e um módulo de relatórios.

## Funcionalidades

### 1. **Home**
- Tela inicial com uma visão geral simples do sistema.

### 2. **Cadastros**
- **Animais**: Gerenciamento completo, com possibilidade de adicionar, editar, remover e filtrar por nome, tipo, raça e status.  
  Validações incorporadas (ex: nome, tipo e raça obrigatórios).
- **Adotantes**: Cadastro detalhado, com validações em campos como telefone (formatação dinâmica), CPF (11 dígitos), endereço obrigatório e renda numérica.
- **Voluntários**: Cadastro com campos como telefone, CPF validados e formatados, endereço obrigatório, e outros campos opcionais (disponibilidade, habilidades, experiência, motivação).

### 3. **Processos**
- **Adoções**: Registro e acompanhamento das adoções, associando animais a adotantes. Possibilidade de filtrar por ID, adotante, animal, status e data. Também há validações (não adotar animal já adotado).
- **Doações**: Registro de doações associadas a voluntários, com filtragens por período e validações no valor das doações.

### 4. **Análise e Insights**
- Gráficos e estatísticas interativas sobre:
  - Adoções ao longo do tempo (com filtragem por ano).
  - Distribuição de raças de animais não adotados no abrigo.
  - Doações ao longo do tempo (com filtragem por ano).
  - Participação de voluntários (porcentagem ativos/inativos, média de doações por voluntário ativo).
  
### 5. **Relatórios**
- Geração de relatórios resumidos sobre o estado atual da ONG em um intervalo de datas.
- Exibição em tela e opção de exportar para PDF.
- Inclui informações como:
  - Número de animais disponíveis.
  - Adoções realizadas no período.
  - Total de doações no período.
  - (E outras estatísticas dependendo dos dados disponíveis.)

## Pré-requisitos

- **Python 3.8+**
- **Bibliotecas**:
  - PyQt6: `pip install PyQt6`
  - Matplotlib (para gráficos): `pip install matplotlib`
  - reportlab para exportar relatório em PDF: `pip install reportlab`