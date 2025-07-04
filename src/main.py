import sys
import os
import pandas as pd
import mysql.connector

# Importa as classes e funções dos outros arquivos
from webscraper_pd import WikipediaScraper, DataTransformer
from data_analysis import DatabaseConnector, build_transaction_dataset, plot_release_timeline
from database import connect as db_connect # Renomeado para evitar conflito
from plotter import * 

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
    cursor = connector.connection.cursor(buffered=True)
    company_id = None
    try:
        cursor.execute("INSERT IGNORE INTO atividEmp (atividade) VALUES (%s)", (company_df['Atividade'].iloc[0],))
        connector.connection.commit()

        cursor.execute("INSERT IGNORE INTO tipoEmp (tipo) VALUES (%s)", (company_df['Tipo'].iloc[0],))
        connector.connection.commit()

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

        print(f"DEBUG_INSERT: Dados da empresa para INSERT: {data}")

        cursor.execute(query, data)
        connector.connection.commit()
        print(f"Dados da empresa '{company_df['Nome'].iloc[0]}' inseridos/atualizados.")
        company_id = cursor.lastrowid if cursor.lastrowid else get_company_id(cursor, company_df['Nome'].iloc[0])
    except mysql.connector.Error as err:
        print(f"Erro ao inserir empresa: {err}")
        company_id = None
    finally:
        cursor.close()
    return company_id

def get_company_id(cursor, company_name):
    """Obtém o ID de uma empresa pelo nome."""
    cursor.execute("SELECT id FROM empresa WHERE nome = %s", (company_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_game_data(connector, games_df, id_empresa):
    """Insere dados de jogos no banco de dados."""
    cursor = connector.connection.cursor(buffered=True)
    try:
        for _, row in games_df.iterrows():
            query = """
            INSERT INTO jogo (nome, idEmpDev)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE idEmpDev=VALUES(idEmpDev)
            """
            cursor.execute(query, (row['Title'], id_empresa))
            connector.connection.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao inserir jogo: {err}")
    finally:
        cursor.close()

def get_game_id(cursor, game_name):
    """Obtém o ID de um jogo pelo nome."""
    cursor.execute("SELECT id FROM jogo WHERE nome = %s", (game_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_publisher_data(connector, games_df):
    """Insere dados de publishers e publicações."""
    cursor = connector.connection.cursor(buffered=True)
    try:
        for _, row in games_df.iterrows():
            publisher_name = row['International publisher'] if 'International publisher' in games_df.columns and pd.notna(row['International publisher']) else None
            game_id = get_game_id(cursor, row['Title'])

            year = None
            if 'Release Date' in row and pd.notna(row['Release Date']):
                try:
                    date_str = str(row['Release Date'])
                    if len(date_str) == 4 and date_str.isdigit():
                        year = int(date_str)
                    else:
                        parsed_date = pd.to_datetime(date_str, errors='coerce')
                        if pd.notna(parsed_date):
                            year = parsed_date.year
                except Exception as e:
                    print(f"Aviso: Não foi possível analisar o ano para o jogo '{row['Title']}': {e}")
                    year = None
            elif 'Year' in row and pd.notna(row['Year']):
                try:
                    year = int(row['Year'])
                except ValueError:
                    print(f"Aviso: Não foi possível converter 'Year' para int para o jogo '{row['Title']}': {row['Year']}")
                    year = None

            if publisher_name and game_id:
                try:
                    cursor.execute("INSERT IGNORE INTO publisher (nome) VALUES (%s)", (publisher_name,))
                    connector.connection.commit()

                    cursor.execute("SELECT idPublisher FROM publisher WHERE nome = %s", (publisher_name,))
                    pub_id = cursor.fetchone()[0]

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
    finally:
        cursor.close()

def insert_platform_data(connector, games_df):
    """Insere dados de plataformas e compatibilidade."""
    cursor = connector.connection.cursor(buffered=True)
    try:
        for _, row in games_df.iterrows():
            platform_name = row['System'] if 'System' in games_df.columns and pd.notna(row['System']) else \
                            row['Platform(s)'] if 'Platform(s)' in games_df.columns and pd.notna(row['Platform(s)']) else None
            game_id = get_game_id(cursor, row['Title'])

            if platform_name and game_id:
                try:
                    cursor.execute("INSERT IGNORE INTO plataforma (nome) VALUES (%s)", (platform_name,))
                    connector.connection.commit()

                    cursor.execute("SELECT idPlataforma FROM plataforma WHERE nome = %s", (platform_name,))
                    plat_id = cursor.fetchone()[0]

                    query = """
                    INSERT INTO compatibilidade (idJogo, idPlataforma)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE idJogo=VALUES(idJogo)
                    """
                    cursor.execute(query, (game_id, plat_id))
                    connector.connection.commit()
                except mysql.connector.Error as err:
                    print(f"Erro ao inserir plataforma/compatibilidade para '{row['Title']}': {err}")
    finally:
        cursor.close()

def insert_expansion_data(connector, expansions_df):
    """Insere dados de expansões."""
    cursor = connector.connection.cursor(buffered=True)
    try:
        for _, row in expansions_df.iterrows():
            game_id = get_game_id(cursor, row['Game'])

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
    finally:
        cursor.close()

def main():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '06112004 Wh',
        'database': 'fromsoftware_db'
    }

    print("Verificando e configurando o banco de dados...")
    setup_database(db_config)

    print("Conectando ao banco de dados para operações de carga...")
    db_connector_loader = DatabaseConnector(db_config)

    fromsoftware_url = "https://en.wikipedia.org/wiki/FromSoftware"
    bethesda_url = "https://en.wikipedia.org/wiki/Bethesda_Game_Studios"

    urls_to_scrape = [fromsoftware_url, bethesda_url]

    print("\n--- Etapa 3: Carga dos Dados ---")
    for url in urls_to_scrape:
        print(f"\nRaspando e processando dados de: {url}")
        scraper = WikipediaScraper(url)

        company_info_df = scraper.formated_company_info()

        print("DEBUG_MAIN: DataFrame da empresa retornado por formated_company_info():")
        print(company_info_df)

        if company_info_df is not None and not company_info_df.empty:
            company_name = company_info_df['Nome'].iloc[0]
            print(f"Inserindo/Atualizando dados da empresa: {company_name}")
            id_empresa = insert_company_data(db_connector_loader, company_info_df)

            games_df = scraper.formated_products_table()
            if games_df is not None and not games_df.empty and id_empresa:
                print(f"Inserindo jogos para {company_name}...")
                insert_game_data(db_connector_loader, games_df, id_empresa)
                insert_publisher_data(db_connector_loader, games_df)
                insert_platform_data(db_connector_loader, games_df)
            else:
                print(f"Nenhum dado de jogo encontrado para {company_name} ou ID da empresa inválido.")

            expansions_df = scraper.formated_expansions_table()
            if expansions_df is not None and not expansions_df.empty:
                print(f"Inserindo expansões para {company_name}...")
                insert_expansion_data(db_connector_loader, expansions_df)
            else:
                print(f"Nenhuma expansão encontrada para {company_name}.")
        else:
            print("Nenhum dado da empresa encontrado ou DataFrame vazio.")

    print("\n--- Etapa 4: Análises e Visualizações ---")

    # Conexão para consultas e visualizações
    db_connector_query = DatabaseConnector(db_config)

    # Visualizações SQL genéricas
    plot_bar()
    # Visualização timeline dos lançamentos de jogos (por empresa)
    print("\nVisualizando linha do tempo de lançamentos de jogos:")
    plot_release_timeline(db_connector_query)

    print("\nExecução concluída.")

if __name__ == "__main__":
    main()
