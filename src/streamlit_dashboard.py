import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules


@st.cache_data
def connect_and_load_data():
    """
    Conecta ao banco de dados MySQL e carrega os dados das tabelas 'jogo', 'expansao' e 'publicacoes'.
    Usa st.cache_data para cachear o resultado e evitar recarregamentos desnecessários.
    """
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '06112004 Wh', # Certifique-se de que a senha está correta
        'database': 'fromsoftware_db'
    }
    conn = None # Inicializa conn como None
    try:
        conn = mysql.connector.connect(**config)

        # Buscar dados de jogos e expansões
        product_df = pd.read_sql("SELECT id, nome FROM jogo", conn)
        expansion_df = pd.read_sql("SELECT idJogo, nome FROM expansao", conn)

        # Obter o ano de lançamento de jogos e expansões da tabela 'publicacoes'
        # Assumindo que 'publicacoes' tem 'idJogo' e 'idExpansao' ou que
        # 'expansao' tem uma coluna 'ano_lancamento'
        # Se 'expansao' não tiver 'ano_lancamento', esta query pode precisar de ajuste
        # para fazer JOIN com 'publicacoes' para expansões.
        # Exemplo de ajuste (se publicacoes tem idExpansao):
        # SELECT e.nome, p.ano AS ano_lancamento, 'Expansao' AS tipo
        # FROM expansao e JOIN publicacoes p ON e.id = p.idExpansao
        release_df = pd.read_sql("""
            SELECT j.nome, p.ano AS ano_lancamento, 'Jogo Base' AS tipo
            FROM jogo j
            JOIN publicacoes p ON j.id = p.idJogo
            UNION ALL
            SELECT nome, ano_lancamento, 'Expansao' AS tipo FROM expansao;
        """, conn)
        return product_df, expansion_df, release_df
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados ou carregar dados: {err}")
        # Retorna DataFrames vazios para evitar erros subsequentes no aplicativo
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        if conn:
            conn.close()


def prepare_transaction_data(products, expansions):
    """
    Prepara os dados de transação para o algoritmo Apriori.
    Combina jogos base com suas expansões e cria um DataFrame one-hot encoded.
    """
    # Verifica se os DataFrames de entrada não estão vazios
    if products.empty or expansions.empty:
        return pd.DataFrame()

    # 'nome_x' refere-se ao nome do jogo base (da coluna 'nome' de 'jogo')
    # 'nome_y' refere-se ao nome da expansão (da coluna 'nome' de 'expansao')
    merged = products.merge(expansions, left_on="id", right_on="idJogo", how="left")
    
    # Agrupa por jogo base e coleta todas as expansões relacionadas
    # dropna() é usado para remover valores NaN (jogos que não possuem expansões)
    grouped = merged.groupby('nome_x')['nome_y'].apply(lambda x: list(x.dropna())).reset_index()
    
    # Cria uma nova coluna 'items' que inclui o jogo base e suas expansões
    grouped['items'] = grouped.apply(lambda row: [row['nome_x']] + row['nome_y'], axis=1)

    transactions = grouped['items'].tolist()
    
    # Coleta todos os itens únicos (jogos e expansões) para codificação one-hot
    all_items = sorted(set(item for sublist in transactions for item in sublist))
    
    # Cria um DataFrame one-hot encoded, onde cada coluna representa um item e os valores são 0 ou 1
    encoded_df = pd.DataFrame([{item: int(item in t) for item in all_items} for t in transactions])
    return encoded_df


def run_apriori(transactions_df, min_support, min_lift):
    """
    Aplica o algoritmo Apriori e gera regras de associação.
    Inclui uma verificação para `itemsets` vazios.
    """
    if transactions_df.empty:
        st.warning("Nenhum dado de transação para analisar. Verifique a conexão com o banco ou os dados.")
        return pd.DataFrame(), pd.DataFrame() # Retorna DataFrames vazios

    # Aplica o algoritmo Apriori para encontrar conjuntos de itens frequentes
    itemsets = apriori(transactions_df, min_support=min_support, use_colnames=True)
    
    # VERIFICAÇÃO ADICIONADA AQUI: Se itemsets estiver vazio, não tente gerar regras.
    if itemsets.empty:
        st.warning("Nenhum conjunto de itens frequente encontrado com o suporte mínimo atual. Tente diminuir o valor do 'Suporte mínimo'.")
        return pd.DataFrame(), pd.DataFrame() # Retorna DataFrames vazios para evitar o erro

    # Gera regras de associação a partir dos conjuntos de itens frequentes
    rules = association_rules(itemsets, metric="lift", min_threshold=min_lift)
    return itemsets, rules


st.title("Painel Analítico FromSoftware")

# Carrega e prepara os dados do banco de dados
product_df, expansion_df, release_df = connect_and_load_data()

# Verifica se os DataFrames carregados do banco de dados não estão vazios antes de prosseguir
if product_df.empty or expansion_df.empty or release_df.empty:
    st.error("Não foi possível carregar os dados do banco de dados. Verifique a conexão e as tabelas.")
    st.stop() # Interrompe a execução do Streamlit se os dados não foram carregados

transaction_df = prepare_transaction_data(product_df, expansion_df)

# Configurações do Apriori na barra lateral do Streamlit
st.sidebar.header("Configurações do Apriori")
# Valores iniciais ajustados para permitir mais resultados se os dados forem esparsos
support = st.sidebar.slider("Suporte mínimo", 0.01, 1.0, 0.05, 0.01) # Min. default 0.05
lift = st.sidebar.slider("Lift mínimo", 1.0, 5.0, 1.0, 0.1)

# Executa o Apriori com as configurações escolhidas
itemsets, rules = run_apriori(transaction_df, support, lift)

# Exibe as regras de associação
st.subheader("Regras de Associação")
if not rules.empty:
    st.dataframe(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
else:
    st.info("Nenhuma regra de associação encontrada com as configurações atuais.")

# Exibe o gráfico de Suporte vs Confiança
st.subheader("Gráfico de Suporte vs Confiança")
if not rules.empty:
    fig1, ax1 = plt.subplots()
    sns.scatterplot(data=rules, x="support", y="confidence", size="lift", hue="lift", sizes=(20, 200), ax=ax1)
    st.pyplot(fig1)
else:
    st.info("Não há regras para gerar o gráfico de Suporte vs Confiança.")

# Exibe a linha do tempo de lançamentos
st.subheader("Linha do Tempo de Lançamentos")
if not release_df.empty:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.countplot(data=release_df, x="ano_lancamento", hue="tipo", palette="Set2", ax=ax2)
    plt.xticks(rotation=45)
    st.pyplot(fig2)
else:
    st.info("Dados de lançamento não disponíveis para a linha do tempo.")

# Exibe os conjuntos frequentes
st.subheader("Conjuntos Frequentes")
if not itemsets.empty:
    st.dataframe(itemsets.sort_values(by="support", ascending=False).head(10))
else:
    st.info("Nenhum conjunto frequente encontrado com as configurações atuais.")

