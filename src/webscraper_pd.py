import pandas as pd

class DataTransformer:
    def __init__(self):
        pass


    def __separate_internacional_publisher__(self, row): 
        content = row[3]
        regions = ['NA:', 'EU:', 'JP:', 'PAL:']
        parts = []
        
        for i in range(len(content)): # Pega o índice de cada caractere
            for region in regions:
                if content[i:i+len(region)] == region: # Testa se a substring é igual a uma das regiões
                    begin = i
                    i += len(region)
                    
                    # Aumenta o índice até encontrar o próximo marcador de região ou o final do conteúdo
                    while i < len(content) and not any(content[i:i+len(r)] == r for r in regions):
                        i += 1
                    
                    # Adiciona as partes antes e depois do marcador de região à lista 'partes' 
                    parts.append(content[begin:i].strip())
                    break # Quebra e continua com o próximo caractere
                
        new_lines = []
        for part in parts:
            new = pd.Series([row[0], row[1], row[2], row[3]],
                              index=['Year', 'Title', 'System', 'International publisher'])
            new.iloc[3] = part
            new_lines.append(new)

        if parts == []:
            new = pd.Series([row[0], row[1], row[2], row[3]],
                              index=['Year', 'Title', 'System', 'International publisher'])
            new_lines.append(new)  # Se não houver partes, mantém a linha original 
        
        return pd.DataFrame(new_lines)


    def __separate_system__(self, row, studio, isGamesTable=True):
        separator = ', '
        series_index = []
        index = 2
        series = []

        # Define o index correto para a coluna de sistema/plataforma dependendo do estúdio
        if studio == 'FromSoftware':
            series_index = ['Year', 'Title', 'System', 'International publisher']
        elif studio == 'Bethesda Game Studios':
            if isGamesTable:        
                series_index = ['Year', 'Title', 'Platform(s)']
            else:
                series_index = ['Year', 'Title', 'Game', 'Platform(s)']

        content = row[index]

        parts = []
        new_lines = []

        separated = content.split(separator)

        # Faz esse processamento só se tem mais de um sistema/plataforma na linha
        if separated != [content]:
            for i in range(len(separated)):
                parts.append(separated[i])

            for i in range(0, index+2):
                series.append(row[i]) # Cria uma lista com os valores das colunas

            for part in parts: # Separa os sistemas/plataformas
                new = pd.Series(series, index=series_index)
                new.iloc[index] = part
                new_lines.append(new)
        else:
            new = pd.Series(row, index=series_index)
            new_lines.append(new)
        
        return pd.DataFrame(new_lines)
    

    def __atomize_rows__(self, row, studio, isGamesTable=True):
        if studio == 'FromSoftware':
            intermediate_rows = self.__separate_internacional_publisher__(row)
            final_rows = []

            # Concatena as linhas separadas de 'International publisher' com as 
            # linhas separadas de 'System'/'Platform(s)'
            for row in intermediate_rows.itertuples(index=False):
                separated = self.__separate_system__(row, studio, isGamesTable=isGamesTable)
                final_rows.append(separated)

            return pd.concat(final_rows, ignore_index=True)
        elif studio == 'Bethesda Game Studios':
            new_rows = self.__separate_system__(new_rows, studio, isGamesTable=isGamesTable)

        return new_rows    

 
    def __get_index_from_itertuple__(self, itertuple, data):
        for row in data.itertuples(index=True):
            for i in range(len(itertuple)):
                if row[i + 1] != itertuple[i]:
                    continue
            
                return row.Index
            
        return None


    def __get_studios__(self, url):
        if url == "https://en.wikipedia.org/wiki/Bethesda_Game_Studios":
            return 'Bethesda Game Studios'
        elif url == "https://en.wikipedia.org/wiki/FromSoftware":
            return 'FromSoftware'
        else:
            raise ValueError("URL inválida. Deve ser de uma das duas empresas.")

    # separa as linhas que possuem mais de um valor nas colunas International publisher e System
    def separate_rows(self, data, url, isGamesTable=True):
        for row in data.itertuples(index=False):
            if len(row) == 4:
                studio = self.__get_studios__(url)
                new_rows = self.__atomize_rows__(row, studio, isGamesTable=isGamesTable)
                if new_rows is not None:
                    index = self.__get_index_from_itertuple__(row, data)
                    if index is not None:
                        data = data.drop(index=index, axis=0)  # remove a linha original
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
    transformer.separate_rows(data, urlFS)