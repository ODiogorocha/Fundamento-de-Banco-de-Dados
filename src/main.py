# main.py

import sys
import os
import pandas as pd
import mysql.connector

# Importa as classes e funções dos outros arquivos
from webscraper_pd import WikipediaScraper, DataTransformer
from data_analysis import DatabaseConnector, build_transaction_dataset, run_apriori_analysis, plot_release_timeline, plot_frequent_itemsets, plot_rules
from data_visualization import run_query, plot_bar_chart, generate_visualizations as generate_sql_visualizations
from database import connect as db_connect # Renomeado para evitar conflito

def setup_database(config):
    """
    Tenta conectar ao servidor MySQL e criar o banco de dados se ele não existir.
    Isso é uma etapa de segurança, mas o script SQL é o principal para a criação.
    """
    try:
        # Conecta sem especificar o banco de dados inicialmente
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']};")
        print(f"Banco de dados '{config['database']}' verificado/criado com sucesso.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Erro ao configurar o banco de dados: {err}")
        sys.exit(1)

def insert_company_data(connector, company_df):
    """Insere dados da empresa no banco de dados."""
    cursor = connector.connection.cursor()
    
    # Inserir atividade (se não existir)
    try:
        cursor.execute("INSERT IGNORE INTO atividEmp (atividade) VALUES (%s)", (company_df['Atividade'].iloc[0],))
        connector.connection.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir atividade: {err}")

    # Inserir tipo (se não existir)
    try:
        cursor.execute("INSERT IGNORE INTO tipoEmp (tipo) VALUES (%s)", (company_df['Tipo'].iloc[0],))
        connector.connection.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir tipo: {err}")

    # Inserir empresa
    try:
        query = """
        INSERT INTO empresa (nome, fundacao, sede, head, atividade, tipo, numEmpregados)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        fundacao=VALUES(fundacao), sede=VALUES(sede), head=VALUES(head), 
        atividade=VALUES(atividade), tipo=VALUES(tipo), numEmpregados=VALUES(numEmpregados)
        """
        data = (
            company_df['Nome'].iloc[0],
            company_df['Fundação'].iloc[0] if 'Fundação' in company_df.columns and pd.notna(company_df['Fundação'].iloc[0]) else None,
            company_df['Sede'].iloc[0] if 'Sede' in company_df.columns and pd.notna(company_df['Sede'].iloc[0]) else None,
            company_df['Head'].iloc[0] if 'Head' in company_df.columns and pd.notna(company_df['Head'].iloc[0]) else None,
            company_df['Atividade'].iloc[0] if 'Atividade' in company_df.columns and pd.notna(company_df['Atividade'].iloc[0]) else None,
            company_df['Tipo'].iloc[0] if 'Tipo' in company_df.columns and pd.notna(company_df['Tipo'].iloc[0]) else None,
            int(company_df['NumEmpregados'].iloc[0]) if 'NumEmpregados' in company_df.columns and pd.notna(company_df['NumEmpregados'].iloc[0]) and str(company_df['NumEmpregados'].iloc[0]).isdigit() else None
        )
        cursor.execute(query, data)
        connector.connection.commit()
        print(f"Dados da empresa '{company_df['Nome'].iloc[0]}' inseridos/atualizados.")
        return cursor.lastrowid if cursor.lastrowid else get_company_id(connector, company_df['Nome'].iloc[0])
    except mysql.connector.Error as err:
        print(f"Erro ao inserir empresa: {err}")
    finally:
        cursor.close()
    return None

def get_company_id(connector, company_name):
    """Obtém o ID de uma empresa pelo nome."""
    cursor = connector.connection.cursor(buffered=True)
    cursor.execute("SELECT id FROM empresa WHERE nome = %s", (company_name,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def insert_game_data(connector, games_df, id_empresa):
    """Insere dados de jogos no banco de dados."""
    cursor = connector.connection.cursor()
    for _, row in games_df.iterrows():
        try:
            query = """
            INSERT INTO jogo (nome, idEmpDev)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE idEmpDev=VALUES(idEmpDev)
            """
            cursor.execute(query, (row['Title'], id_empresa))
            connector.connection.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir jogo '{row['Title']}': {err}")
    cursor.close()

def get_game_id(connector, game_name):
    """Obtém o ID de um jogo pelo nome."""
    cursor = connector.connection.cursor(buffered=True)
    cursor.execute("SELECT id FROM jogo WHERE nome = %s", (game_name,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def insert_publisher_data(connector, games_df):
    """Insere dados de publishers e publicações."""
    cursor = connector.connection.cursor()
    for _, row in games_df.iterrows():
        publisher_name = row['International publisher'] if 'International publisher' in games_df.columns and pd.notna(row['International publisher']) else None
        game_id = get_game_id(connector, row['Title'])
        year = int(row['Year']) if 'Year' in games_df.columns and pd.notna(row['Year']) else None

        if publisher_name and game_id:
            try:
                # Inserir publisher (se não existir)
                cursor.execute("INSERT IGNORE INTO publisher (nome) VALUES (%s)", (publisher_name,))
                connector.connection.commit()

                # Obter idPublisher
                cursor.execute("SELECT idPublisher FROM publisher WHERE nome = %s", (publisher_name,))
                pub_id = cursor.fetchone()[0]

                # Inserir publicações
                if year:
                    query = """
                    INSERT INTO publicacoes (idJogo, idPublisher, ano)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE ano=VALUES(ano)
                    """
                    cursor.execute(query, (game_id, pub_id, year))
                    connector.connection.commit()
            except mysql.connector.Error as err:
                print(f"Erro ao inserir publisher/publicação para '{row['Title']}': {err}")
    cursor.close()

def insert_platform_data(connector, games_df):
    """Insere dados de plataformas e compatibilidade."""
    cursor = connector.connection.cursor()
    for _, row in games_df.iterrows():
        platform_name = row['System'] if 'System' in games_df.columns and 'System' in games_df.columns and pd.notna(row['System']) else \
                        row['Platform(s)'] if 'Platform(s)' in games_df.columns and pd.notna(row['Platform(s)']) else None
        game_id = get_game_id(connector, row['Title'])

        if platform_name and game_id:
            try:
                # Inserir plataforma (se não existir)
                cursor.execute("INSERT IGNORE INTO plataforma (nome) VALUES (%s)", (platform_name,))
                connector.connection.commit()

                # Obter idPlataforma
                cursor.execute("SELECT idPlataforma FROM plataforma WHERE nome = %s", (platform_name,))
                plat_id = cursor.fetchone()[0]

                # Inserir compatibilidade
                query = """
                INSERT INTO compatibilidade (idJogo, idPlataforma)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE idJogo=VALUES(idJogo)
                """
                cursor.execute(query, (game_id, plat_id))
                connector.connection.commit()
            except mysql.connector.Error as err:
                print(f"Erro ao inserir plataforma/compatibilidade para '{row['Title']}': {err}")
    cursor.close()

def insert_expansion_data(connector, expansions_df):
    """Insere dados de expansões."""
    cursor = connector.connection.cursor()
    for _, row in expansions_df.iterrows():
        game_id = get_game_id(connector, row['Game'])
        
        if game_id:
            try:
                query = """
                INSERT INTO expansao (idJogo, nome, ano_lancamento)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE ano_lancamento=VALUES(ano_lancamento)
                """
                year = int(row['Year']) if 'Year' in expansions_df.columns and pd.notna(row['Year']) else None
                cursor.execute(query, (game_id, row['Title'], year))
                connector.connection.commit()
            except mysql.connector.Error as err:
                print(f"Erro ao inserir expansão '{row['Title']}': {err}")
    cursor.close()


def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',          # Verifique e ajuste conforme seu 'database.py' e MySQL
        'password': 'sua_senha', # Verifique e ajuste conforme seu 'database.py' e MySQL
        'database': 'fromsoftware_db'
    }

    # Etapa 2 (Parte): Criação do esquema - Assumimos que 'fromsoftware_db.sql' já foi executado.
    # O setup_database abaixo é um check/criação do DB, mas não das tabelas.
    print("Verificando e configurando o banco de dados...")
    setup_database(db_config)
    
    print("Conectando ao banco de dados para operações de carga...")
    db_connector_loader = DatabaseConnector(db_config) # Conector para operações de carga

    # URLs das páginas da Wikipédia
    fromsoftware_url = "https://en.wikipedia.org/wiki/FromSoftware"
    bethesda_url = "https://en.wikipedia.org/wiki/Bethesda_Game_Studios"
    
    urls_to_scrape = [fromsoftware_url, bethesda_url]

    # Etapa 3: Carga dos dados (Scraping e Inserção no DB)
    print("\n--- Etapa 3: Carga dos Dados ---")
    for url in urls_to_scrape:
        print(f"\nRaspando e processando dados de: {url}")
        scraper = WikipediaScraper(url)
        
        # Obter informações da empresa
        company_info_df = scraper.formated_company_info()
        if company_info_df is not None and not company_info_df.empty:
            company_name = company_info_df['Nome'].iloc[0]
            print(f"Inserindo/Atualizando dados da empresa: {company_name}")
            id_empresa = insert_company_data(db_connector_loader, company_info_df)
            
            # Obter e inserir dados de jogos
            games_df = scraper.formated_products_table()
            if games_df is not None and not games_df.empty and id_empresa:
                print(f"Inserindo jogos para {company_name}...")
                insert_game_data(db_connector_loader, games_df, id_empresa)
                insert_publisher_data(db_connector_loader, games_df) # Publishers e Publicações
                insert_platform_data(db_connector_loader, games_df) # Plataformas e Compatibilidade
            else:
                print(f"Nenhum dado de jogo encontrado para {company_name} ou ID da empresa inválido.")

            # Obter e inserir dados de expansões (se existirem)
            expansions_df = scraper.formated_expansions_table()
            if expansions_df is not None and not expansions_df.empty:
                print(f"Inserindo expansões para {company_name}...")
                insert_expansion_data(db_connector_loader, expansions_df)
            else:
                print(f"Nenhuma expansão encontrada para {company_name}.")
        else:
            print(f"Não foi possível obter informações da empresa para {url}.")

    db_connector_loader.connection.close()
    print("Carga de dados concluída.")

    # Etapa 4: Visualização dos Dados (Análises e Gráficos)
    print("\n--- Etapa 4: Visualização dos Dados ---")
    
    # Conector para as análises e visualizações
    db_connector_analysis = DatabaseConnector(db_config) 

    # Análise de Associação (Apriori)
    print("Carregando dados para análise de associação...")
    expansion_data = db_connector_analysis.get_game_expansion_data()
    if not expansion_data.empty:
        transaction_df = build_transaction_dataset(expansion_data)
        if not transaction_df.empty:
            print("Executando Apriori e gerando gráficos de regras de associação...")
            itemsets, rules = run_apriori_analysis(transaction_df)
            plot_frequent_itemsets(itemsets)
            plot_rules(rules)
            print("Gráficos de Apriori salvos: frequent_itemsets.png, association_rules.png")
        else:
            print("Nenhum dado de transação para Apriori.")
    else:
        print("Nenhum dado de jogo/expansão para análise de associação.")

    # Linha do tempo de lançamentos
    print("Gerando linha do tempo de lançamentos...")
    release_df = db_connector_analysis.get_release_year_data()
    if not release_df.empty:
        plot_release_timeline(release_df)
        print("Gráfico da linha do tempo de lançamentos salvo: release_timeline.png")
    else:
        print("Nenhum dado de lançamento para a linha do tempo.")
    
    db_connector_analysis.connection.close()

    # Visualizações baseadas em SQL (do data_visualization.py)
    print("\nGerando visualizações adicionais baseadas em SQL...")
    generate_sql_visualizations()
    print("Visualizações adicionais geradas.")

    print("\nTodas as etapas concluídas com sucesso!")

if __name__ == "__main__":
    main()