import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules


@st.cache_data

def connect_and_load_data():
    config = {
        'host': 'localhost',
        'user': 'seu_usuario',
        'password': 'sua_senha',
        'database': 'fromsoftware_db'
    }
    conn = mysql.connector.connect(**config)

    product_df = pd.read_sql("SELECT id, nome FROM produto", conn)
    expansion_df = pd.read_sql("SELECT idJogo, nome FROM expansao", conn)
    release_df = pd.read_sql("""
        SELECT nome, ano_lancamento, 'Jogo Base' AS tipo FROM produto
        UNION ALL
        SELECT nome, ano_lancamento, 'Expansao' AS tipo FROM expansao;
    """, conn)

    return product_df, expansion_df, release_df


def prepare_transaction_data(products, expansions):
    merged = products.merge(expansions, left_on="id", right_on="idJogo", how="left")
    grouped = merged.groupby('nome_x')['nome_y'].apply(lambda x: list(x.dropna())).reset_index()
    grouped['items'] = grouped.apply(lambda row: [row['nome_x']] + row['nome_y'], axis=1)

    transactions = grouped['items'].tolist()
    all_items = sorted(set(item for sublist in transactions for item in sublist))
    encoded_df = pd.DataFrame([{item: int(item in t) for item in all_items} for t in transactions])
    return encoded_df


def run_apriori(transactions_df, min_support, min_lift):
    itemsets = apriori(transactions_df, min_support=min_support, use_colnames=True)
    rules = association_rules(itemsets, metric="lift", min_threshold=min_lift)
    return itemsets, rules


st.title("Painel Analítico FromSoftware")

product_df, expansion_df, release_df = connect_and_load_data()
transaction_df = prepare_transaction_data(product_df, expansion_df)

st.sidebar.header("Configurações do Apriori")
support = st.sidebar.slider("Suporte mínimo", 0.1, 1.0, 0.2, 0.05)
lift = st.sidebar.slider("Lift mínimo", 1.0, 5.0, 1.0, 0.1)

itemsets, rules = run_apriori(transaction_df, support, lift)

st.subheader("Regras de Associação")
st.dataframe(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

st.subheader("Gráfico de Suporte vs Confiança")
fig1, ax1 = plt.subplots()
sns.scatterplot(data=rules, x="support", y="confidence", size="lift", hue="lift", sizes=(20, 200), ax=ax1)
st.pyplot(fig1)

st.subheader("Linha do Tempo de Lançamentos")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.countplot(data=release_df, x="ano_lancamento", hue="tipo", palette="Set2", ax=ax2)
plt.xticks(rotation=45)
st.pyplot(fig2)

st.subheader("Conjuntos Frequentes")
st.dataframe(itemsets.sort_values(by="support", ascending=False).head(10))
