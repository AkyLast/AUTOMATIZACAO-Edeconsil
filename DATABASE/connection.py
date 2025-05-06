from db import execute_query, fetch_all, execute_many

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

def inserir_motorista_EmMassa(data):
    sql = """
        INSERT INTO motoristas (name, TAG)
        VALUES (%s, %s)
    """
    sucess = execute_many(sql, data)
    return sucess

def inserir_motorista(nome: str, tag: str):
    sql = """
        INSERT INTO motoristas (name, TAG)
        VALUES (%s, %s)
    """
    sucess = execute_query(sql, (nome, tag))
    if not sucess:
        print(f"Motorista: '{nome}' já existe - Pulando inserção")

def inserir_tagsEmMassa(data):
    sql = """
        INSERT INTO dim_tags (tag, cr, marca, modelo, ano, placa, descricao)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    sucess = execute_many(sql, data)
    return sucess

def atualizar_motoristas(nome: str, new_tag: str):
    sql = """
        UPDATE motoristas SET TAG = %s WHERE name = %s  
    """
    sucess = execute_query(sql, (new_tag, nome))
    return sucess

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