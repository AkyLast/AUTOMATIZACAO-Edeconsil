from db import execute_query, fetch_all

def procurar(nome: str):
    sql = """
        SELECT * FROM motoristas WHERE name = %s    
    """
    rows = fetch_all(sql, (nome, ))
    return rows

def inserir_motorista(nome: str, tag: str):
    sql = """
        INSERT INTO motoristas (name, TAG)
        VALUES (%s, %s)
    """
    sucess = execute_query(sql, (nome, tag))
    if not sucess:
        print(f"Motorista: '{nome}' já existe - Pulando inserção")

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
    for row in rows:
        print(row)

