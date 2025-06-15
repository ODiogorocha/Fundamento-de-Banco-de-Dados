import mysql.connector
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import matplotlib.pyplot as plt
import seaborn as sns


class DatabaseConnector:
    def __init__(self, config):
        self.connection = mysql.connector.connect(**config)

    def get_game_expansion_data(self):
        query = """
        SELECT 
            j.id AS id_jogo, 
            j.nome AS jogo, 
            e.nome AS expansao
        FROM jogo j
        LEFT JOIN expansao e ON j.id = e.idJogo
        ORDER BY j.nome;
        """
        return pd.read_sql(query, self.connection)

    def get_release_year_data(self):
        query = """
        SELECT nome, NULL AS ano_lancamento, 'Jogo Base' AS tipo FROM jogo
        UNION ALL
        SELECT nome, ano_lancamento, 'Expansao' AS tipo FROM expansao;
        """
        return pd.read_sql(query, self.connection)


def build_transaction_dataset(df):
    grouped = df.groupby('jogo')['expansao'].apply(lambda x: list(x.dropna())).reset_index()
    grouped['items'] = grouped.apply(lambda row: [row['jogo']] + row['expansao'], axis=1)
    transactions = grouped['items'].tolist()

    all_items = sorted(set(item for sublist in transactions for item in sublist))
    
    # Altere esta linha:
    encoded_df = pd.DataFrame([{item: int(item in transaction) for item in all_items} for transaction in transactions])
    
    # Adicione esta linha para converter para booleano:
    encoded_df = encoded_df.astype(bool)
    
    return encoded_df

def run_apriori_analysis(transactions_df, min_support=0.01, min_lift=1.0): # Altere aqui
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
        'user': 'root',          # Verifique e ajuste conforme seu 'database.py' e MySQL
        'password': '06112004 Wh',    # Substitua aqui
        'database': 'fromsoftware_db'
    }

    print("Conectando ao banco de dados...")
    connector = DatabaseConnector(db_config)

    print("Carregando dados de jogos e expansões...")
    expansion_data = connector.get_game_expansion_data()
    transaction_df = build_transaction_dataset(expansion_data)

    # --- Adicione essas linhas para depuração ---
    print("\n--- Conteúdo de transaction_df (primeiras 5 linhas) ---")
    print(transaction_df.head())
    print(f"\n--- Dimensões de transaction_df: {transaction_df.shape} ---")
    print(f"--- Colunas de transaction_df: {transaction_df.columns.tolist()} ---")
    print(f"--- Soma de True por coluna (exemplos): ---")
    # Mostra a soma de 'True' para as primeiras 10 colunas, se houver
    if not transaction_df.empty:
        print(transaction_df.iloc[:, :10].sum())
    # --- Fim das linhas de depuração ---

    print("\nExecutando Apriori...")
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
