from connection import *
import pandas as pd

#motorista_XTAG = {row["name"]: row["TAG"] for row in lista_motoristas()}
#print(motorista_XTAG)

df_new = pd.read_excel(r"C:\Users\edeconsil\Downloads\veiculos_e_equipamento - atualizar.xlsx")

df_new.rename(columns={col: col.strip().upper() for col in df_new.columns}, inplace=True)

#print(df_new)

rows = lista_tags()

for row in rows:
    row