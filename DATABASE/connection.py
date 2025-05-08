import logging
from db import execute_query, fetch_all, execute_many

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler("app_logs.log")
    ]
)

logger = logging.getLogger()


# BUSCAR

def procurar_XName(nome: str):
    sql = """
        SELECT * FROM motoristas WHERE name = %s    
    """
    rows = fetch_all(sql, (nome, ))
    return rows

def procurar_XTAG(tag: str):
    sql = """
        SELECT name FROM motoristas WHERE TAG = %s
    """
    valor = fetch_all(sql,(tag, ))
    return valor

def lista_motoristas():
    sql = """
        SELECT * FROM motoristas
    """
    rows = fetch_all(sql)
    return rows

def lista_tags():
    sql = """
        SELECT * FROM dim_tags
    """
    rows = fetch_all(sql)
    return rows


# INSERIR

def inserir_motorista_EmMassa(data):
    sql = """
        INSERT INTO motoristas (name, TAG)
        VALUES (%s, %s)
    """
    logger.info("Inserindo motoristas.")
    sucess = execute_many(sql, data)
    if sucess:
        logger.info("Motoristas inseridos com SUCESSO!")

    return sucess

def inserir_motorista(nome: str, tag: str):
    sql = """
        INSERT INTO motoristas (name, TAG)
        VALUES (%s, %s)
    """
    logger.info("Inserindo dados no DB.")
    sucess = execute_query(sql, (nome, tag))
    if sucess:
        logger.info(f"Motorista: {nome} e TAG: {tag} inseridos com SUCESSO!")
    else:
        logger.error(f"Motorista: '{nome}' já existe - Pulando inserção")

def inserir_tagsEmMassa(data):
    sql = """
        INSERT INTO dim_tags (tag, cr, marca, modelo, ano, placa, descricao)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    sucess = execute_many(sql, data)
    return sucess

def inserir_ralatorioVelocidade(data):
    sql = """
        INSERT INTO relatorio_velocidade (data, hora, tag, motorista, localizacao, longitude, latitude, velocidade, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    logger.info("Inserindo dados na tabela")
    sucess = execute_many(sql, data)
    logger.info("Dados de Relatório de Velocidade inseridos com SUCESSO!")
    return sucess


# UPDATE
def atualizar_motoristas(nome: str, new_tag: str):
    sql = """
        UPDATE motoristas SET TAG = %s WHERE name = %s  
    """
    sucess = execute_query(sql, (new_tag, nome))
    return sucess

def update_dimTags(tag: str, new_value: str, column: str):
    param = column
    sql = f"""
        UPDATE dim_tags SET {param} = %s WHERE tag = %s
    """
    sucess = execute_query(sql, (new_value, tag))
    return sucess