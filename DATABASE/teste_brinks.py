from connection import *
import pandas as pd
from datetime import datetime


df_motoristas = pd.read_excel(r"C:\Users\edeconsil\Downloads\LISTA DE MOTORISTAS POR CR - DB.xlsx", header = 3)
df_motoristas.rename(columns={col: col.strip().upper() for col in df_motoristas.columns}, inplace=True)

def formatar_base(df):
    df = df[["MOTORISTA", "TAG"]]
    df = df.dropna(axis = 0)
    return df

df = formatar_base(df_motoristas)

data = df.iloc[3].tolist()

atualizar_motoristas(data[0], data[1])