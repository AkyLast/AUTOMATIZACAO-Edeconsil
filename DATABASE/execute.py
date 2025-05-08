import logging
import pandas as pd
from connection import *

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler("app_logs.log")
    ]
)

logger = logging.getLogger()

#df = pd.read_excel(r"C:\Users\edeconsil\Downloads\veiculos_e_equipamento - bagunçar.xlsx")
#df_new = pd.read_excel(r"C:\Users\edeconsil\Downloads\veiculos_e_equipamento - atualizar.xlsx")
#df_velocidade = pd.read_excel(r"C:\Users\edeconsil\Downloads\Relatorio_Formatado - RastreOnline.xlsx")
df_motoristas = pd.read_excel(r"C:\Users\edeconsil\Downloads\LISTA DE MOTORISTAS POR CR - DB.xlsx", header = 3)

#df.rename(columns={col: col.strip().upper() for col in df.columns}, inplace=True)
#df_new.rename(columns={col: col.strip().upper() for col in df_new.columns}, inplace=True)
df_motoristas.rename(columns={col: col.strip().upper() for col in df_motoristas.columns}, inplace=True)

def formatar_base(df):
    df = df[["MOTORISTA", "TAG"]]
    df = df.dropna(axis = 0)
    return df

df = formatar_base(df_motoristas)
print(len(df))

def adicionar_motoristas(df):
    motoristas = df["MOTORISTA"].tolist()
    tags = df["TAG"].tolist()

    motoristas_existentes = {row["name"]: row["TAG"] for row in lista_motoristas()}
    novos_motoristas = []

    for motorista, tag in zip(motoristas, tags):
        motorista = motorista.strip().upper()
        if motorista not in motoristas_existentes.keys():
            novos_motoristas.append((motorista, tag))
            motoristas_existentes[motorista] = tag
        else:
            logger.info(f"Motorista: {motorista} já existe.")

    try:
        if novos_motoristas:
            for data in novos_motoristas:
                inserir_motorista(data) # não aceita assim "data"
        else:
            logger.info("Nenhum motorista novo")
    except Exception as e:
        logger.error(f"Erro ao inserir motoristas: {str(e)}")

def atualizar_tag_XMotoristas(df):
    motorista_XTAG = {row["name"]: row["TAG"] for row in lista_motoristas()}
    motoristas, tags = df["MOTORISTA"].tolist(), df["TAG"].tolist()

    try:
        for motorista, tag in zip(motoristas, tags):
            tag = str(tag.strip())
            if motorista_XTAG[motorista] != tag:
                atualizar_motoristas(motorista, tag)
            
            if motorista not in motorista_XTAG:
                inserir_motorista(motorista, tag)
                motorista_XTAG[motorista] = tag

    except Exception as e:
        logger.error(f"Erro ao atualizar motoristas: {str(e)}")
        print(e)

adicionar_motoristas(df)

def adicionar_tags(df):
    tag, cr, marca, modelo, ano, placa, descricao = df["TAG"].tolist(), df["CR"].tolist(), df["MARCA"].tolist(), df["MODELO"].tolist(), df["ANO"].tolist(), df["PLACA"], df["DESCRIÇÃO"]
    data = list(zip(tag, cr, marca, modelo, ano, placa, descricao))
    try:
        inserir_tagsEmMassa(data)
    except Exception as e:
        print(f"Erro ao inserir as tags: {e}")

def atualizar_tags(df):
    tags_XVeiculos = {row["tag"]: row["cr"] for row in lista_tags()}
    tags = df["TAG"].tolist()
    CRs = df["CR"].tolist()
    
    for tag, cr in zip(tags, CRs):
        if tag not in tags_XVeiculos:
            df = df[df["TAG"] == tag]
            adicionar_tags(df)

        elif tags_XVeiculos.get(tag) != cr:
            update_dimTags(tag, cr, "cr")


# FORMATAR 
def formatando_relatorioVelocidade(df):
    df['DATA'] = pd.to_datetime(df_velocidade['DATA'], dayfirst = True).dt.strftime("%Y-%m-%d")
    df = df[df["STATUS"] == "ALTA"]
    df = df.dropna(axis = 0)
    data = df.values.tolist()
    inserir_ralatorioVelocidade(data)


#formatando_relatorioVelocidade(df_velocidade)