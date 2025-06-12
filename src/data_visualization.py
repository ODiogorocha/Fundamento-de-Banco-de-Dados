import matplotlib.pyplot as plt
from database import connect

def run_query(sql):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return columns, results

def plot_bar_chart(x, y, title, xlabel, ylabel):
    plt.figure(figsize=(10, 6))
    plt.bar(x, y, color='cornflowerblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def generate_visualizations():
    # Query 1: Países com mais empresas
    query1 = """
    SELECT pais_origem, COUNT(*) AS quantidade_empresas
    FROM empresa
    GROUP BY pais_origem
    ORDER BY quantidade_empresas DESC
    LIMIT 10;
    """
    _, results1 = run_query(query1)
    plot_bar_chart(
        [row[0] for row in results1],
        [row[1] for row in results1],
        "Top 10 Países com Mais Empresas",
        "País",
        "Quantidade de Empresas"
    )

    # Query 2: Número de jogos por empresa
    query2 = """
    SELECT e.nome, COUNT(j.id) AS quantidade_jogos
    FROM jogo j
    JOIN empresa e ON j.idEmpresa = e.id
    GROUP BY e.nome
    ORDER BY quantidade_jogos DESC
    LIMIT 10;
    """
    _, results2 = run_query(query2)
    plot_bar_chart(
        [row[0] for row in results2],
        [row[1] for row in results2],
        "Top 10 Empresas com Mais Jogos",
        "Empresa",
        "Quantidade de Jogos"
    )

    # Query 3: Lançamentos por ano (considerando só expansões)
    query3 = """
    SELECT ano_lancamento, COUNT(*) AS quantidade_lancamentos
    FROM expansao
    WHERE ano_lancamento IS NOT NULL
    GROUP BY ano_lancamento
    ORDER BY ano_lancamento;
    """
    _, results3 = run_query(query3)
    plot_bar_chart(
        [str(row[0]) for row in results3],
        [row[1] for row in results3],
        "Quantidade de Expansões Lançadas por Ano",
        "Ano",
        "Lançamentos"
    )

if __name__ == "__main__":
    generate_visualizations()
