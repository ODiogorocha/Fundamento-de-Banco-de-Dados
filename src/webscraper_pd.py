import pandas as pd

class DataTransformer:
    def __init__(self):
        pass


    # MELHORAR ESSA FUNÇÃO! O GPT CRIOU E EU FIZ FUNCIONAR, MAS TEM QUE MELHORAR ELA  
    def __separate_internacional_publisher__(self, row):
        col_index = 3 
        content = row[col_index]
    
        delimitadores = ['NA:', 'EU:', 'JP:']
    
        partes = []
        i = 0
        while i < len(content):
            for prefix in delimitadores:
                if content[i:i+len(prefix)] == prefix:
                    inicio = i
                    i += len(prefix)
                    while i < len(content) and not any(content[i:i+len(d)] == d for d in delimitadores):
                        i += 1
                    partes.append(content[inicio:i].strip())
                    break
            else:
                i += 1
    
        novas_linhas = []
        for parte in partes:
            nova = pd.Series([row[0], row[1], row[2], row[3]],
                              index=['Year', 'Title', 'System', 'International publisher'])
            nova.iloc[col_index] = parte
            novas_linhas.append(nova)
    
        return pd.DataFrame(novas_linhas)
    
 
    def __get_index_from_itertuple__(self, itertuple, data):
        for row in data.itertuples(index=True):
            if row[1] == itertuple[0] and row[2] == itertuple[1] and row[3] == itertuple[2]:
                return row.Index


    # separa as linhas que possuem mais de um valor nas colunas International publisher e System
    # SEPARAÇÃO DO SYSTEM AINDA NÃO FOI FEITA
    def separate_rows(self, data):
        for row in data.itertuples(index=False):
            if len(row) == 4:
                new_rows = self.__separate_internacional_publisher__(row)
                if new_rows is not None:
                    index = self.__get_index_from_itertuple__(row, data)
                    data = data.drop(index=index, axis=1) # remove a linha original
                    data = pd.concat([data, new_rows], axis=0) # adiciona as novas linhas formatadas
            
        pd.DataFrame.to_csv(data, "src\\data.csv", index=False)
         

class WikipediaScraper:
    def __init__(self):
        self.tables = None
        self.has_expansions = False
        self.read_only_infobox = True


    def read_tables_from_wikipedia(self, url):
        try:
            self.tables = pd.read_html(url)
            print(f"Número de tabelas lidas: {len(self.tables)}")

            if(url == "https://en.wikipedia.org/wiki/Bethesda_Game_Studios"
               or url == "https://en.wikipedia.org/wiki/FromSoftware"):
                self.has_expansions = True
                self.read_only_infobox = False            
        except Exception as e:
            print(f"Erro ao ler tabelas: {e}")


    def extract_infobox(self):
        data = dict()
        infobox = self.tables[0]
            
        for i in range(1, len(infobox)):
            key = infobox.iloc[i, 0] # Pega a linha i da primeira coluna
            value = infobox.iloc[i, 1] # Pega a linha i da segunda coluna
            data[key] = value
            print(f"{key}: {value}")

        return data
    

    def extract_products(self):
        if not self.read_only_infobox:
            return self.tables[1]
        else:
            print("A tabela de produtos dessa empresa não deve ser lida.")
            return None


    def extract_expansions(self):
        if self.has_expansions:
            return self.tables[2]
        else:
            print("Essa empresa não desenvolveu nenhuma expansão de jogo.")
            return None
        

if __name__ == "__main__":
    urlFS = "https://en.wikipedia.org/wiki/FromSoftware"
    urlBTH = "https://en.wikipedia.org/wiki/Bethesda_Game_Studios"
    scraper = WikipediaScraper()
    scraper.read_tables_from_wikipedia(urlFS)
    data = scraper.extract_products()
    transformer = DataTransformer()
    transformer.separate_rows(data)