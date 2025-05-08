import os
import mysql.connector
import logging

from dotenv import load_dotenv
from mysql.connector import Error
from mysql.connector import errorcode

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler("app_logs.log")
    ]
)

logger = logging.getLogger()
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
        logger.info("Tentando conectar com o banco de dados.")
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("Conexão com o banco de dados feita com SUCESSO!")
        return conn
    except Error as e:
        logger.error(f"[ERRO] Não foi possível conectar: {e}")
        raise

def execute_query(query: str, params: tuple = None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        logger.info("Dados inseridos com SUCESSO!")
    except Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            logger.error(f"[AVISO] Registro já existente: {e.msg}")
            return False
        conn.rollback()
        logger.error(f"[ERRO] Falha na query: {e.msg}")
        raise
    finally:
        cursor.close()
        conn.close()
    return True

def execute_many(query: str, params: list):
    conn = get_connection() 
    cursor = conn.cursor()
    try:
        cursor.executemany(query, params)
        conn.commit()
        logger.info("Dados inseridos com sucesso!")
        logger.info(f"{len(params)} registros inseridos com sucesso.")

    except Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            logger.error(f"[AVISO] Registro já existente: {e.msg}. Operação RECUSADA.")
            return False
        conn.rollback()
        logger.error(f"[ERRO] Falha na query: {e.msg}")
        raise
    finally:
        cursor.close()
        conn.close()
    return True

def fetch_all(query: str, params: tuple = None):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)
    try:
        logger.info("Buscando dados no DB.")
        cursor.execute(query, params or ())
        logger.info("Dados obtidos com SUCESSO!")
        return cursor.fetchall()
    except Error as e:
        logger.error(f"[ERRO] Falha no SELECT: {e}")
        raise
    finally:
        cursor.close()
        conn.close()