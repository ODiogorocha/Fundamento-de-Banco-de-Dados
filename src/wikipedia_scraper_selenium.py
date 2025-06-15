from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service # Importa a classe Service
import time
import mysql.connector


class WikipediaScraperSelenium:
    def __init__(self, driver_path: str):
        self.driver_path = driver_path
        self.driver = None

    def _init_browser(self) -> None:
        """
        Inicializa o navegador Chrome.
        Atualizado para usar a classe Service para especificar o caminho do driver,
        pois 'executable_path' foi descontinuado.
        """
        options = Options()
        options.add_argument("--headless")  # Executa sem abrir janela do navegador
        options.add_argument("--disable-gpu") # Desabilita a aceleração de hardware da GPU
        options.add_argument("--no-sandbox") # Essencial para ambientes como Docker ou CI/CD
        options.add_argument("--disable-dev-shm-usage") # Evita problemas de memória compartilhada em alguns ambientes Linux

        # Cria um objeto Service com o caminho do chromedriver
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

    def fetch_infobox(self, url: str) -> dict:
        """
        Acessa a página da Wikipedia e extrai os dados da infobox.
        Args:
            url (str): A URL da página da Wikipedia a ser raspada.
        Returns:
            dict: Um dicionário contendo os dados da infobox (cabeçalho: valor).
        Raises:
            Exception: Se a tabela infobox não for encontrada ou ocorrer outro erro.
        """
        self._init_browser()
        self.driver.get(url)
        time.sleep(2)  # Aguarda a página carregar completamente

        try:
            # Tenta encontrar a tabela da infobox pela classe 'infobox'
            table = self.driver.find_element(By.CLASS_NAME, "infobox")
            rows = table.find_elements(By.TAG_NAME, "tr")

            data = {}
            for row in rows:
                try:
                    # Tenta extrair o cabeçalho (th) e o valor (td) de cada linha
                    header = row.find_element(By.TAG_NAME, "th").text.strip()
                    # Substitui quebras de linha por espaços para um valor mais limpo
                    cell = row.find_element(By.TAG_NAME, "td").text.strip().replace('\n', ' ')
                    data[header] = cell
                except Exception as e:
                    # Ignora linhas que não têm um par th/td (ex: linhas de imagem, cabeçalhos de seção)
                    # print(f"Aviso: Não foi possível extrair dados da linha: {row.text}. Erro: {e}") # Para depuração
                    continue

            return data

        except Exception as e:
            # Captura qualquer erro na busca da infobox e levanta uma exceção mais descritiva
            raise Exception(f"Erro ao encontrar ou processar a tabela infobox: {e}. Verifique se a classe 'infobox' ainda é válida ou se a estrutura da página mudou.")

        finally:
            # Garante que o driver seja fechado, mesmo se ocorrer um erro
            if self.driver:
                self.driver.quit()


class MySQLManager:
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Gerencia a conexão e operações com o banco de dados MySQL.
        Args:
            host (str): Host do banco de dados MySQL.
            user (str): Usuário do banco de dados MySQL.
            password (str): Senha do usuário do banco de dados MySQL.
            database (str): Nome do banco de dados MySQL.
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self._create_table()
        except mysql.connector.Error as err:
            raise Exception(f"Erro ao conectar ao MySQL ou criar a tabela: {err}")

    def _create_table(self) -> None:
        """Cria a tabela 'fromsoftware_info' se ela ainda não existir."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fromsoftware_info (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    atributo VARCHAR(255) NOT NULL,
                    valor TEXT
                );
            """)
            self.connection.commit()
            print("Tabela 'fromsoftware_info' verificada/criada com sucesso.")
        except mysql.connector.Error as err:
            raise Exception(f"Erro ao criar a tabela: {err}")
        finally:
            cursor.close()

    def insert_data(self, info_dict: dict) -> None:
        """
        Insere os dados extraídos da infobox no banco de dados.
        Limpa a tabela antes de inserir novos dados para evitar duplicatas.
        Args:
            info_dict (dict): Dicionário de atributos e valores a serem inseridos.
        """
        cursor = self.connection.cursor()
        try:
            # Limpa os dados existentes na tabela antes de inserir novos
            cursor.execute("DELETE FROM fromsoftware_info;")
            print("Dados antigos excluídos da tabela 'fromsoftware_info'.")

            for key, value in info_dict.items():
                cursor.execute("""
                    INSERT INTO fromsoftware_info (atributo, valor)
                    VALUES (%s, %s);
                """, (key, value))

            self.connection.commit()
            print(f"{len(info_dict)} registros inseridos com sucesso.")
        except mysql.connector.Error as err:
            raise Exception(f"Erro ao inserir dados: {err}")
        finally:
            cursor.close()

    def fetch_data(self) -> list:
        """
        Busca todos os dados armazenados na tabela 'fromsoftware_info'.
        Returns:
            list: Uma lista de tuplas, onde cada tupla contém (atributo, valor).
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT atributo, valor FROM fromsoftware_info;")
            data = cursor.fetchall()
            return data
        except mysql.connector.Error as err:
            raise Exception(f"Erro ao buscar dados: {err}")
        finally:
            cursor.close()

    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão com o MySQL fechada.")


class FromSoftwareApp:
    def __init__(self, url: str, db_config: dict, driver_path: str):
        """
        Inicializa a aplicação principal, configurando o scraper e o gerenciador de banco de dados.
        Args:
            url (str): URL da Wikipedia a ser raspada.
            db_config (dict): Dicionário de configuração do banco de dados MySQL.
            driver_path (str): Caminho para o executável do Chromedriver.
        """
        self.scraper = WikipediaScraperSelenium(driver_path)
        self.database = MySQLManager(**db_config)
        self.url = url

    def run(self) -> None:
        """Executa o fluxo completo: raspa dados, salva no DB e os exibe."""
        try:
            print("Buscando dados da Wikipedia com Selenium...")
            extracted_data = self.scraper.fetch_infobox(self.url)
            print("Dados extraídos com sucesso.")

            if extracted_data:
                print("Salvando no banco de dados MySQL...")
                self.database.insert_data(extracted_data)

                print("\nDados armazenados no banco:")
                fetched_data = self.database.fetch_data()
                if fetched_data:
                    for attribute, value in fetched_data:
                        print(f"{attribute}: {value}")
                else:
                    print("Nenhum dado encontrado no banco após a inserção.")
            else:
                print("Nenhum dado da infobox foi extraído. Verifique a URL ou a estrutura da página.")

        except Exception as e:
            print(f"\nOcorreu um erro na aplicação: {e}")
        finally:
            # Garante que a conexão com o banco de dados seja fechada no final
            self.database.close()


if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '06112004 Wh', # Por favor, lembre-se de que hardcodar senhas não é recomendado para produção.
        'database': 'fromsoftware_db'
    }

    # ATENÇÃO: SUBSTITUA COM O CAMINHO CORRETO DO SEU CHROMEDRIVER!
    # Exemplo: DRIVER_PATH = "/usr/local/bin/chromedriver" (Linux/macOS) ou "C:\\path\\to\\chromedriver.exe" (Windows)
    DRIVER_PATH = "/home/weslley/Documentos/chromedriver"  # Caminho de exemplo (você deve ajustar este)

    app = FromSoftwareApp(
        url="https://en.wikipedia.org/wiki/FromSoftware",
        db_config=db_config,
        driver_path=DRIVER_PATH
    )
    app.run()
