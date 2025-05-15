# Projeto de Fundamentos de Banco de Dados

## 📚 Descrição

Este projeto tem como objetivo aplicar os conhecimentos adquiridos na disciplina de **Fundamentos de Banco de Dados** por meio da coleta, tratamento e armazenamento de dados obtidos da [Wikipédia](https://www.wikipedia.org/).

O projeto compreende as seguintes etapas:

1. **Extração de Dados**: Obtenção de dados a partir de páginas específicas da Wikipédia utilizando técnicas de web scraping.
2. **Tratamento de Dados**: Limpeza e estruturação dos dados extraídos para garantir consistência e integridade.
3. **Modelagem e Armazenamento**: Criação de um modelo relacional e inserção dos dados em um banco de dados relacional.
4. **Consultas SQL**: Elaboração de consultas para análise e extração de informações relevantes.

---

## ⚙️ Tecnologias Utilizadas

- Python (bibliotecas: `requests`, `BeautifulSoup`, `pandas`)
- MySQL / PostgreSQL / SQLite (escolha do banco de dados relacional)
- SQL (Structured Query Language)
- Jupyter Notebook / Scripts Python

---

## 📂 Estrutura do Projeto

```

📁 projeto-banco-de-dados
├── scraping/                # Scripts responsáveis pela extração de dados da Wikipédia
│   └── coletar\_dados.py
├── tratamento/             # Scripts para limpeza e padronização dos dados
│   └── tratar\_dados.py
├── banco\_dados/            # Scripts de criação das tabelas e inserção dos dados
│   └── criar\_tabelas.sql
│   └── inserir\_dados.py
├── consultas/              # Consultas SQL para análise dos dados
│   └── consultas.sql
├── requisitos.txt          # Dependências do projeto
└── README.md               # Documentação do projeto

````

---

## 🧠 Tema Escolhido

> *[Insira aqui o tema do projeto, por exemplo: "Lista de Presidentes do Brasil", "Maiores Cidades do Mundo", "Premiados com o Nobel", etc.]*

---

## 🚀 Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio

2. Instale as dependências:

   ```bash
   pip install -r requisitos.txt
   ```

3. Execute o script de coleta:

   ```bash
   python scraping/coletar_dados.py
   ```

4. Execute o script de tratamento:

   ```bash
   python tratamento/tratar_dados.py
   ```

5. Crie o banco de dados e insira os dados:

   ```bash
   python banco_dados/inserir_dados.py
   ```

6. Rode as consultas:

   ```bash
   psql -d nome_do_banco -f consultas/consultas.sql
   ```

---

## 📊 Exemplos de Consultas

* Buscar os registros com maior valor numérico em determinada coluna
* Filtrar por faixa de datas ou categorias
* Contagens e agrupamentos

---

## 👨‍💻 Contribuidores

* [WeslleyHBM](https://github.com/WeslleyHBM)
* [GabrielMarquezan](https://github.com/GabrielMarquezan)
* [ODiogorocha](https://github.com/ODiogorocha)

---
