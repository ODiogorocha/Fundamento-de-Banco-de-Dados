import mysql.connector
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import matplotlib.pyplot as plt
import seaborn as sns


class DatabaseConnector:
    def __init__(self, config):
        self.connection = mysql.connector.connect(**config)

    def get_product_expansion_data(self):
        query = """
        SELECT 
            p.id AS id_jogo, 
            p.nome AS jogo, 
            e.nome AS expansao
        FROM produto p
        LEFT JOIN expansao e ON p.id = e.idJogo
        ORDER BY p.nome;
        """
        return pd.read_sql(query, self.connection)

    def get_release_year_data(self):
        query = """
        SELECT nome, ano_lancamento, 'Jogo Base' AS tipo FROM produto
        UNION ALL
        SELECT nome, ano_lancamento, 'Expansao' AS tipo FROM expansao;
        """
        return pd.read_sql(query, self.connection)


def build_transaction_dataset(df):
    grouped = df.groupby('jogo')['expansao'].apply(lambda x: list(x.dropna())).reset_index()
    grouped['items'] = grouped.apply(lambda row: [row['jogo']] + row['expansao'], axis=1)
    transactions = grouped['items'].tolist()

    all_items = sorted(set(item for sublist in transactions for item in sublist))
    encoded_df = pd.DataFrame([{item: int(item in transaction) for item in all_items} for transaction in transactions])
    return encoded_df


def run_apriori_analysis(transactions_df, min_support=0.2, min_lift=1.0):
    itemsets = apriori(transactions_df, min_support=min_support, use_colnames=True)
    rules = association_rules(itemsets, metric="lift", min_threshold=min_lift)
    return itemsets, rules


def plot_release_timeline(df):
    plt.figure(figsize=(10, 5))
    sns.countplot(data=df, x="ano_lancamento", hue="tipo", palette="Set2")
    plt.title("Lançamentos por Ano")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("release_timeline.png")


def plot_frequent_itemsets(itemsets):
    top_itemsets = itemsets.sort_values(by="support", ascending=False).head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(x="support", y=top_itemsets['itemsets'].astype(str), data=top_itemsets)
    plt.title("Top 10 Conjuntos Frequentes")
    plt.tight_layout()
    plt.savefig("frequent_itemsets.png")


def plot_rules(rules):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rules, x="support", y="confidence", size="lift", hue="lift", sizes=(20, 200))
    plt.title("Regras de Associação (Apriori)")
    plt.tight_layout()
    plt.savefig("association_rules.png")


def main():
    db_config = {
        'host': 'localhost',
        'user': 'seu_usuario',
        'password': 'sua_senha',
        'database': 'fromsoftware_db'
    }

    print("Conectando ao banco de dados...")
    connector = DatabaseConnector(db_config)

    print("Carregando dados de jogos e expansões...")
    expansion_data = connector.get_product_expansion_data()
    transaction_df = build_transaction_dataset(expansion_data)

    print("Executando Apriori...")
    itemsets, rules = run_apriori_analysis(transaction_df)

    print("Gerando gráficos...")
    plot_frequent_itemsets(itemsets)
    plot_rules(rules)

    print("Gerando linha do tempo de lançamentos...")
    release_df = connector.get_release_year_data()
    plot_release_timeline(release_df)

    print("Análises e gráficos salvos com sucesso.")


if __name__ == "__main__":
    main()
