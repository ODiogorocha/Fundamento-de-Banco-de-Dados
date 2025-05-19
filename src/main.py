import requests
import mysql.connector
from bs4 import BeautifulSoup


class ColetorWikipedia:
    def __init__(self):
        self.sopa = None


    def buscar_pagina(self, url):
        resposta = requests.get(url)
        if resposta.status_code == 200:
            self.sopa = BeautifulSoup(resposta.content, 'html.parser')
        else:
            raise Exception(f"Erro ao acessar a página: {resposta.status_code}")

    def extrair_infobox(self):
        dados = {}
        tabela = self.sopa.find("table", {"class": "infobox"})

        if not tabela:
            raise Exception("Tabela infobox não encontrada na página.")

        for linha in tabela.find_all("tr"):
            cabecalho = linha.find("th")
            conteudo = linha.find("td")

            if cabecalho and conteudo:
                chave = cabecalho.text.strip()
                valor = conteudo.text.strip().replace('\n', ' ')
                dados[chave] = valor

        return dados


class GerenciadorBancoMySQL:
    def __init__(self, host, usuario, senha, banco):
        self.conexao = mysql.connector.connect(
            host=host,
            user=usuario,
            password=senha,
            database=banco
        )
        self.criar_tabela()

    def criar_tabela(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fromsoftware_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                atributo VARCHAR(255),
                valor TEXT
            );
        """)
        self.conexao.commit()

    def inserir_dados(self, dicionario_dados):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM fromsoftware_info;")
        for chave, valor in dicionario_dados.items():
            cursor.execute("""
                INSERT INTO fromsoftware_info (atributo, valor)
                VALUES (%s, %s);
            """, (chave, valor))
        self.conexao.commit()

    def listar_dados(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT atributo, valor FROM fromsoftware_info;")
        return cursor.fetchall()


class AplicativoFromSoftware:
    def __init__(self, url, configuracao_banco):
        self.coletor = ColetorWikipedia(url)
        self.banco = GerenciadorBancoMySQL(**configuracao_banco)

    def executar(self):
        print("Buscando dados da Wikipedia...")
        self.coletor.buscar_pagina()

        print("Extraindo informações da tabela infobox...")
        dados_extraidos = self.coletor.extrair_infobox()

        print("Salvando no banco de dados MySQL...")
        self.banco.inserir_dados(dados_extraidos)

        print("Dados armazenados no banco:")
        for atributo, valor in self.banco.listar_dados():
            print(f"{atributo}: {valor}")


if __name__ == "__main__":
    configuracao_banco = {
        'host': 'localhost',
        'usuario': 'seu_usuario',     # substitua aqui
        'senha': 'sua_senha',         # substitua aqui
        'banco': 'fromsoftware_db'
    }

    app = AplicativoFromSoftware("https://en.wikipedia.org/wiki/FromSoftware", configuracao_banco)
    app.executar()
