import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

csv_folder_path = "/home/diogo/Documents/Aulas/Fundamento-de-Banco-de-Dados/arq"

def load_csv_files(path):
    dataframes = {}
    for file in os.listdir(path):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(path, file)).drop_duplicates().dropna(how='all')
            dataframes[file] = df
    return dataframes

def plot_bar(data, title, xlabel, ylabel, rotation=0, wide=False, figsize=None):
    if figsize:
        plt.figure(figsize=figsize)
    elif wide:
        plt.figure(figsize=(14, 6))
    else:
        plt.figure(figsize=(11, 6))
    
    data_int = data.astype(int)
    
    ax = sns.barplot(x=data_int.index, y=data_int.values, palette='viridis')
    ax.set_title(title, fontsize=14, weight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=rotation, ha='right')
    
    for i, v in enumerate(data_int.values):
        ax.text(i, v + max(data_int.values)*0.01, str(v), ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()

dfs = load_csv_files(csv_folder_path)

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (11, 6)

jogos = dfs["jogos.csv"]
expansoes = dfs["expanção.csv"]
publicacoes = dfs["publicaçoes.csv"]
empresa = dfs["empresa.csv"]
compat = dfs["compatibilidade.csv"]
plataformas = dfs["plataforma.csv"].drop_duplicates(subset=["idPlataforma"])

publicacoes_por_ano = publicacoes["ano"].value_counts().sort_index()
publicacoes_por_ano.index = publicacoes_por_ano.index.astype(str)

plot_bar(publicacoes_por_ano, "Quantidade de Jogos Publicados por Ano", "Ano de Publicação", "Número de Jogos", rotation=45, wide=True)

jogo_nomes = jogos.set_index("id")["nome"].to_dict()
expansoes_count = expansoes["idJogo"].value_counts()
expansoes_count.index = [jogo_nomes.get(i, f"Jogo ID {i}") for i in expansoes_count.index]
plot_bar(expansoes_count.head(10), "Top 10 Jogos com Mais Expansões", "Nome do Jogo", "Número de Expansões", rotation=30)

plat_nomes = plataformas.set_index("idPlataforma")["nome"].to_dict()
jogos_por_plat = compat["idPlataforma"].value_counts()
jogos_por_plat.index = [plat_nomes.get(i, f"Plataforma ID {i}") for i in jogos_por_plat.index]

plot_bar(jogos_por_plat, "Quantidade de Jogos por Plataforma", "Nome da Plataforma", "Número de Jogos", rotation=45, figsize=(16,8))

plot_bar(empresa["tipo"].value_counts(), "Classificação das Empresas por Tipo", "Tipo de Empresa", "Quantidade")

plot_bar(jogos["idEmpDev"].value_counts(), "Quantidade de Jogos por Empresa Desenvolvedora", "ID da Empresa Desenvolvedora", "Número de Jogos")

if "sede" in empresa.columns:
    plot_bar(empresa["sede"].value_counts(), "Localização das Sedes das Empresas", "Cidade/País da Sede", "Número de Empresas", rotation=30)

