import pandas as pd

class WikipediaScraper:
    def __init__(self):
        self.tables = None
        self.has_expansions = False
        self.read_only_infobox = True


    def read_tables_from_wikipedia(self, url):
        try:
            self.tables = pd.read_html(url)
            print(f"Número de tabelas lidas: {len(self.tables)}")

            if(url == "https://en.wikipedia.org/wiki/Game_Freak"):
                self.read_only_infobox = False
            elif(url == "https://en.wikipedia.org/wiki/Bethesda_Game_Studios"):
                self.has_expansions = True
                self.read_only_infobox = False
            elif(url == "https://en.wikipedia.org/wiki/FromSoftware"):
                self.has_expansions = True
                self.read_only_infobox = False
            
        except Exception as e:
            raise Exception(f"Erro ao ler tabelas: {e}")


    def extract_infobox(self):
        data = dict()
        infobox = self.tables[0]
            
        for i in range(1, len(infobox)):
            key = infobox.iloc[i, 0]
            value = infobox.iloc[i, 1]
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
    urlGF = "https://en.wikipedia.org/wiki/Game_Freak"
    urlBTH = "https://en.wikipedia.org/wiki/Bethesda_Game_Studios"
    scraper = WikipediaScraper()
    scraper.read_tables_from_wikipedia(urlGF)
    data = scraper.extract_products()

    print(data)