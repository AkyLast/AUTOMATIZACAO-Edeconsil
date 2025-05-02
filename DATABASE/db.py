import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERRO] Não foi possível conectar: {e}")
        raise

def execute_query(query: str, params: tuple = None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
    except Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            print(f"[AVISO] Registro já existente: {e.msg}")
            # aqui, em vez de raise, você pode optar por:
            # - ignorar e seguir em frente
            # - retornar um valor específico (False, None…) para quem chamou
            # - lançar uma exceção customizada
            return False
        # Para outros erros, desfaz e relança
        conn.rollback()
        print(f"[ERRO] Falha na query: {e.msg}")
        raise
    finally:
        cursor.close()
        conn.close()
    return True

def fetch_all(query: str, params: tuple = None):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Error as e:
        print(f"[ERRO] Falha no SELECT: {e}")
        raise
    finally:
        cursor.close()
        conn.close()