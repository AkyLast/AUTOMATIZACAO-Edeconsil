import pandas as pd
from connection import *

#param = atualizar_motoristas("CArlso", "CE10")
#print(param)

#lista_motoristas()

df = pd.read_excel(r"C:\Users\edeconsil\Downloads\veiculos_e_equipamento - bagunçar.xlsx")
df_new = pd.read_excel(r"C:\Users\edeconsil\Downloads\veiculos_e_equipamento - atualizar.xlsx")
df.rename(columns={col: col.strip().upper() for col in df.columns}, inplace=True)
df_new.rename(columns={col: col.strip().upper() for col in df_new.columns}, inplace=True)


def adicionar_motoristas(df):
    sucess = 0
    fails = []

    motoristas = df["MOTORISTA"].tolist()
    tags = df["TAG"].tolist()

    motoristas_existentes = [procurar_XName(name)[0]["name"] for name in motoristas if procurar_XName(name)]
    novos_motoristas = []

    for motorista, tag in zip(motoristas, tags):
        if motorista not in motoristas_existentes:
            novos_motoristas.append((motorista, tag))
        else:
            fails.append(f"Motorista: {motorista} já existe.")

    try:
        if novos_motoristas:
            inserir_motorista_EmMassa(novos_motoristas)
            sucess = len(novos_motoristas)
        else:
            print("Nenhum motorista novo")
    except Exception as e:
        fails.append("Erro ao inserir motoristas: {str(e)}")

    return sucess, fails

def atualizar_tag_XMotoristas(df):
    sucess = 0
    fails = []

    motorista_XTAG = {row["name"]: row["TAG"] for row in lista_motoristas()}
    motoristas, tags = df["MOTORISTA"].tolist(), df["TAG"].tolist()

    try:
        for motorista, tag in zip(motoristas, tags):
            tag = str(tag.strip())
            if motorista_XTAG[motorista] != tag:
                atualizar_motoristas(motorista, tag)
                sucess += 1
            
            if motorista not in motorista_XTAG:
                inserir_motorista(motorista, tag)
                sucess += 1

    except Exception as e:
        fails.append("Erro ao atualizar motoristas: {str(e)}")
    
    return sucess, fails

df_new["CR"] = "ALUMAR OPERAÇÃO REDUÇÃO"

def adicionar_tags(df):
    tag, cr, marca, modelo, ano, placa, descricao = df["TAG"].tolist(), df["CR"].tolist(), df["MARCA"].tolist(), df["MODELO"].tolist(), df["ANO"].tolist(), df["PLACA"], df["DESCRIÇÃO"]
    data = list(zip(tag, cr, marca, modelo, ano, placa, descricao))
    try:
        inserir_tagsEmMassa(data)
    except Exception as e:
        print(f"Erro ao inserir as tags: {e}")

adicionar_tags(df_new)