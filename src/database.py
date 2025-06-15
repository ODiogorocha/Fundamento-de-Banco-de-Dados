import mysql.connector

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="06112004 Wh",         # substitua se necessário
        database="fromsoftware_db"    # nome correto do banco
    )

# Teste de conexão (opcional)
if __name__ == "__main__":
    try:
        conn = connect()
        print("Conexão bem-sucedida!")
        conn.close()
    except Exception as e:
        print("Erro ao conectar:", e)