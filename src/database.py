import mysql.connector
from database import connect

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sua_senha",         # substitua se necessário
        database="fromsoftware_db"    # nome correto do banco
    )


try:
    conn = connect()
    print("Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print("Erro ao conectar:", e)
