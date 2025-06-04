# Documentação do Projeto FromSoftware

Este projeto coleta dados da Wikipedia sobre a empresa FromSoftware, armazena no banco MySQL, realiza análise de associação com o algoritmo Apriori e apresenta os resultados em um dashboard web com Streamlit.

---

## 1. `wikipedia_scraper_selenium.py`

### Objetivo
Coletar dados da infobox da página Wikipedia da FromSoftware utilizando Selenium para navegação dinâmica, e armazenar esses dados em um banco de dados MySQL.

### Descrição Geral das Classes e Funções

- **Classe WikipediaScraperSelenium**  
  - `__init__(self, driver_path: str, url: str)`: Inicializa o scraper com o caminho do driver Selenium e a URL da página a ser coletada.  
  - `load_page(self)`: Abre a página da Wikipedia usando Selenium em modo headless e carrega o conteúdo HTML na propriedade `soup`.  
  - `extract_infobox(self) -> dict`: Extrai os dados da tabela infobox, retornando um dicionário com os pares atributo-valor.

- **Classe MySQLManager**  
  - `__init__(self, host, user, password, database)`: Estabelece conexão com o banco MySQL e chama a criação da tabela `fromsoftware_info`.  
  - `create_table(self)`: Cria a tabela `fromsoftware_info` caso não exista, com colunas para atributo e valor.  
  - `insert_data(self, data_dict: dict)`: Limpa a tabela e insere os dados extraídos da infobox.  
  - `fetch_data(self) -> list`: Retorna todos os registros da tabela para exibição.

- **Classe FromSoftwareApp**  
  - `__init__(self, url, db_config, driver_path)`: Inicializa o scraper e gerenciador do banco.  
  - `run(self)`: Executa o fluxo: carrega a página, extrai dados, salva no banco e imprime os dados salvos.

### Pontos importantes
- Utiliza Selenium para garantir que o conteúdo dinâmico da página seja carregado.
- Banco de dados MySQL armazena os dados em uma tabela simples (atributo, valor).
- Código configurável via parâmetros de conexão e caminho do WebDriver.

---

## 2. `data_analysis_apriori.py`

### Objetivo
Realizar uma análise de associação dos dados dos jogos e expansões usando o algoritmo Apriori e gerar gráficos para facilitar a visualização.

### Descrição das Funções

- `connect_to_database() -> mysql.connector.connection.MySQLConnection`  
  Conecta ao banco MySQL e retorna o objeto de conexão.

- `load_dataframes(conn) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`  
  Carrega os dados das tabelas `produto`, `expansao` e um dataframe combinado com ano de lançamento e tipo (jogo base ou expansão).

- `prepare_transaction_data(products: pd.DataFrame, expansions: pd.DataFrame) -> pd.DataFrame`  
  Prepara os dados em formato transacional para o Apriori, combinando jogos e suas expansões em listas e codificando em binário.

- `run_apriori(transactions_df: pd.DataFrame, min_support: float, min_lift: float) -> tuple[pd.DataFrame, pd.DataFrame]`  
  Executa o algoritmo Apriori para encontrar itemsets frequentes e regras de associação, filtrando por suporte e lift mínimos.

- `generate_plots(rules: pd.DataFrame, itemsets: pd.DataFrame, release_df: pd.DataFrame)`  
  Gera gráficos de suporte vs confiança e linha do tempo de lançamentos usando matplotlib e seaborn.

- `main()`  
  Orquestra a execução: conecta ao banco, carrega dados, executa Apriori, imprime regras e exibe gráficos.

### Pontos importantes
- Utiliza as bibliotecas `pandas`, `matplotlib`, `seaborn` e `mlxtend`.
- Regras de associação auxiliam a encontrar relações frequentes entre jogos e expansões.
- Visualização clara para análise temporal e relevância das regras.

---

## 3. `streamlit_dashboard.py`

### Objetivo
Criar uma interface web interativa para explorar os dados, as regras de associação e visualizações geradas pelo Apriori, usando Streamlit.

### Descrição das Funções

- `connect_and_load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`  
  Conecta ao banco MySQL e carrega os dados necessários para a análise. Usa cache do Streamlit para otimizar a performance.

- `prepare_transaction_data(products: pd.DataFrame, expansions: pd.DataFrame) -> pd.DataFrame`  
  Prepara os dados combinando jogos e expansões em formato binário para o Apriori.

- `run_apriori(transactions_df: pd.DataFrame, min_support: float, min_lift: float) -> tuple[pd.DataFrame, pd.DataFrame]`  
  Executa Apriori para obter itemsets frequentes e regras de associação, filtrando conforme parâmetros.

### Descrição da Interface

- Barra lateral com sliders para ajustar suporte mínimo e lift mínimo.
- Exibição dinâmica da tabela de regras de associação.
- Gráfico de dispersão mostrando suporte versus confiança, com tamanho e cor pelo lift.
- Gráfico de linha do tempo com contagem de lançamentos por ano, separando jogos base e expansões.
- Tabela dos conjuntos frequentes mais relevantes.

### Pontos importantes
- Utiliza cache do Streamlit para evitar recarregamentos desnecessários.
- Interface intuitiva para explorar configurações e resultados da análise.
- Visualizações dinâmicas e atualizadas conforme o usuário ajusta parâmetros.

---

## 4. `webscraper_pd.py`
Claro! Aqui está a documentação reformulada no mesmo estilo solicitado:

---

## `wikipedia_scraper.py`

### Objetivo

Extrair, normalizar e estruturar dados de estúdios de jogos a partir de páginas da Wikipedia, utilizando tabelas HTML e pandas.

### Descrição das Classes e Funções

---

### Classe: `DataTransformer`

* `get_studios(url: str) -> str`
  Retorna o nome do estúdio com base na URL da Wikipedia.

* `separate_rows(data: pd.DataFrame, url: str, isGamesTable: bool = True) -> pd.DataFrame`
  Separa múltiplos valores nas colunas `International publisher` e `System/Platform(s)`, gerando uma linha por valor.

* `get_fromsoftware_expansion_platforms(expansions: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame`
  Associa expansões de jogos da FromSoftware às plataformas dos jogos principais.

* `create_company_dataframe(data: pd.DataFrame, studio: str) -> pd.DataFrame`
  Extrai e estrutura informações institucionais da empresa a partir da infobox.

* `format_company_data(data: pd.DataFrame) -> pd.DataFrame`
  Limpa e formata os dados da empresa (removendo parênteses, símbolos, separadores, etc.).

---

### Classe: `WikipediaScraper`

* `__init__(url: str)`
  Inicializa o scraper com a URL e define flags de controle baseadas no estúdio.

* `read_tables_from_wikipedia()`
  Lê todas as tabelas HTML da página e define atributos internos com as tabelas lidas.

* `extract_infobox() -> pd.DataFrame | None`
  Extrai a infobox da empresa (primeira tabela da página).

* `extract_products() -> pd.DataFrame | None`
  Extrai a tabela de jogos desenvolvidos (segunda tabela da página).

* `extract_expansions() -> pd.DataFrame | None`
  Extrai a tabela de expansões, se disponível.

* `formated_products_table() -> pd.DataFrame | None`
  Aplica transformação e limpeza à tabela de jogos, separando colunas compostas.

* `formated_expansions_table() -> pd.DataFrame | None`
  Aplica transformação à tabela de expansões e associa plataformas com base nos jogos principais.

* `formated_company_info() -> pd.DataFrame | None`
  Formata e estrutura os dados institucionais da empresa a partir da infobox.

---

### Pontos importantes

* Utiliza a biblioteca `pandas` para leitura e transformação de dados.
* Compatível com as páginas da Wikipedia dos estúdios *FromSoftware* e *Bethesda Game Studios*.
* Normaliza entradas compostas para facilitar análises posteriores e integração com bancos de dados.

---

## Instalação das Dependências

Execute:

```bash
pip install selenium mysql-connector-python pandas matplotlib seaborn mlxtend streamlit
````

---

## Organização dos Arquivos

```
projeto_fromsoftware/
│
├── wikipedia_scraper_selenium.py     # Scraper Selenium + MySQL
├── data_analysis_apriori.py          # Análise Apriori + gráficos
├── streamlit_dashboard.py            # Dashboard interativo com Streamlit
├── requirements.txt                  # (Opcional) lista de pacotes Python
```

---

## Executando o Projeto

1. **Rodar o scraper** para coletar e armazenar dados:

```bash
python wikipedia_scraper_selenium.py
```

2. **Executar análise local** para visualizar resultados e gráficos:

```bash
python data_analysis_apriori.py
```

3. **Iniciar o dashboard web** para explorar visualmente:

```bash
streamlit run streamlit_dashboard.py
```
