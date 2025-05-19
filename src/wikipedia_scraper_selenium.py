from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import mysql.connector


class WikipediaScraperSelenium:
    def __init__(self, driver_path: str):
        self.driver_path = driver_path
        self.driver = None

    def _init_browser(self) -> None:
        options = Options()
        options.add_argument("--headless")  # Executa sem abrir janela
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=options)

    def fetch_infobox(self, url: str) -> dict:
        """Acessa a página da Wikipedia e extrai os dados da infobox"""
        self._init_browser()
        self.driver.get(url)
        time.sleep(2)  # Aguarda carregar a página

        try:
            table = self.driver.find_element(By.CLASS_NAME, "infobox")
            rows = table.find_elements(By.TAG_NAME, "tr")

            data = {}
            for row in rows:
                try:
                    header = row.find_element(By.TAG_NAME, "th").text.strip()
                    cell = row.find_element(By.TAG_NAME, "td").text.strip().replace('\n', ' ')
                    data[header] = cell
                except:
                    continue

            return data

        except Exception as e:
            raise Exception(f"Erro ao encontrar a tabela infobox: {e}")

        finally:
            self.driver.quit()


class MySQLManager:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self._create_table()

    def _create_table(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fromsoftware_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                atributo VARCHAR(255),
                valor TEXT
            );
        """)
        self.connection.commit()

    def insert_data(self, info_dict: dict) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM fromsoftware_info;")

        for key, value in info_dict.items():
            cursor.execute("""
                INSERT INTO fromsoftware_info (atributo, valor)
                VALUES (%s, %s);
            """, (key, value))

        self.connection.commit()

    def fetch_data(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute("SELECT atributo, valor FROM fromsoftware_info;")
        return cursor.fetchall()


class FromSoftwareApp:
    def __init__(self, url: str, db_config: dict, driver_path: str):
        self.scraper = WikipediaScraperSelenium(driver_path)
        self.database = MySQLManager(**db_config)
        self.url = url

    def run(self) -> None:
        print("Buscando dados da Wikipedia com Selenium...")
        extracted_data = self.scraper.fetch_infobox(self.url)

        print("Salvando no banco de dados MySQL...")
        self.database.insert_data(extracted_data)

        print("Dados armazenados no banco:")
        for attribute, value in self.database.fetch_data():
            print(f"{attribute}: {value}")


if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'seu_usuario',   # substitua aqui
        'password': 'sua_senha', # substitua aqui
        'database': 'fromsoftware_db'
    }

    DRIVER_PATH = "/caminho/para/seu/chromedriver"  # substitua aqui

    app = FromSoftwareApp(
        url="https://en.wikipedia.org/wiki/FromSoftware",
        db_config=db_config,
        driver_path=DRIVER_PATH
    )
    app.run()
