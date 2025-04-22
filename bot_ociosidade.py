import os
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

def formatar_RastreOnline(arquivo):
    df = pd.read_csv(arquivo, encoding="ISO-8859-1", header = 5, sep = ";")

    df = df.dropna(axis=0)
    df = df[df["Data Inicial"] != '""']

    df["Data Inicial"] = pd.to_datetime(df['Data Inicial'], dayfirst=True)
    df["Dados Adicionais"] = df["Dados Adicionais"].astype(int)

    def format_tag(valor):
        formatado = valor.replace(" ", "")
        return formatado

    def format_LatLong(lat_long):
        lat_long = lat_long.split(",")
        return pd.Series([lat_long[0], lat_long[1]])

    def formatacao_time(data):
        tempo = data.strftime("%d/%m/%Y")
        horas = data.strftime("%H:%M:%S")
        return pd.Series([tempo, horas])

    df["Dados Adicionais"] = pd.to_numeric(df["Dados Adicionais"])
    df.loc[:, "Veículo"] = df["Veículo"].apply(format_tag)
    df.loc[:, "Data Inicial"] = pd.to_datetime(df['Data Inicial'])

    df[["DATA", "HORA"]] = df["Data Inicial"].apply(formatacao_time)
    df = df.drop("Data Inicial", axis = 1)

    df[["LATITUDE", "LONGITUDE"]] = df["Lat./Long."].apply(format_LatLong)
    df = df.drop("Lat./Long.", axis = 1)

    def status(row):
        if row["Dados Adicionais"] > 110 and row["Veículo"][0:2] == "CA":
            valor = "ALTA"
        elif row["Dados Adicionais"] > 85 and row["Veículo"][0:2] != "CA":
            valor = "ALTA"
        else:
            valor = "MODERADA"
        return valor

    df["STATUS"] = df.apply(status, axis = 1)
    df = df.rename(columns={
        "Veículo": "TAG",
        "Endereço": "LOCALIZAÇÃO",
        "Dados Adicionais": "VELOCIDADE",
        "Motorista": "MOTORISTA"
    })

    diretorio_arquivo = os.path.dirname(arquivo)
    
    # Define o caminho completo para o arquivo Excel (mesmo diretório)
    caminho_excel = os.path.join(diretorio_arquivo, "Relatorio_Formatado.xlsx")
    
    # Salva o DataFrame no Excel
    df.to_excel(caminho_excel, index=False)

    print(f"Arquivo formatado e salvo como '{caminho_excel}'")


def formatar_Ociosidade(arquivo):
    print("transformar em df")
    df = pd.read_csv(arquivo, encoding="ISO-8859-1", header = 5, sep = ";")
    df = df.dropna(axis=0)
    print("transformado em df")
    def format_df(row):
        def format_placa(placa):
            placa = placa.replace("-", "")
            try:
                param = placa.split(" ")
                for indice in param:
                    if len(indice) == 7:
                        placa = indice
            except:
                placa = placa
            return placa.upper()

        row["Veículo"] = row["Veículo"].replace(" ", "").replace("-", "")
        
        row["Data Inicial"] = pd.to_datetime(row["Data Inicial"], dayfirst=True)
        row["Data Final"] = pd.to_datetime(row["Data Final"], dayfirst=True)
        row["Duração"] = pd.to_datetime(row["Duração"])

        if pd.api.types.is_timedelta64_dtype(row["Duração"]):
                row["Duração"] = row["Duração"].astype("timedelta64[s]").dt.total_seconds()
                row["Duração"] = pd.to_datetime(row["Duração"], unit="s").strftime("%H:%M:%S")
        else:
                row["Duração"] = row["Duração"].strftime("%H:%M:%S") 
        row["Placa"] = format_placa(row["Placa"])
        return row

    df = df.apply(format_df, axis = 1)

    df = df.rename(columns = {
        "Veículo": "TAG",
        "Endereço": "Localização",
        "Placa": "PLACA",
        "Duração": "DURAÇÃO",
        "Data Inicial": "DATA INICIAL",
        "Data Final": "DATA FINAL",
    })

    nome_teste = "Ociosidade"
    diretorio_arquivo = os.path.dirname(arquivo)
    
    # Define o caminho completo para o arquivo Excel (mesmo diretório)
    caminho_excel = os.path.join(diretorio_arquivo, f"Relatorio_Formatado - {nome_teste}.xlsx")
    
    # Salva o DataFrame no Excel
    df.to_excel(caminho_excel, index=False)

    print(f"Arquivo formatado e salvo como '{caminho_excel}'")
  

def selecionar_formatacao(arquivo):
    print("selecionando arquivo")
    if "Tempo_Ocioso_2" in arquivo:
        formatar_Ociosidade(os.path.join(download_path, arquivo))
    elif "Velocidade_(Relatorio_para_robo)" in arquivo:
        formatar_RastreOnline(os.path.join(download_path, arquivo))

download_path = r"C:\Users\edeconsil\Downloads"  
nome_base = "Velocidade_(Relatorio_para_robo)"
# nome_caminho = "/relatorios/print?alias=CUSTOMIZADO&id=218" # O
nome_caminho = "/relatorios/print?alias=CUSTOMIZADO&id=384"
timeout = 120  

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializa o navegador com o caminho correto para o chromedriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Acessa o site de login
print("indo por login")
driver.get("https://rastreioonline.seeflex.com.br/users/login")
time.sleep(2)

# Preencher login e senha
usuario = ""
senha = ""
print("por aqui")
driver.find_element(By.ID, "user_username").send_keys(usuario)
driver.find_element(By.ID, "password").send_keys(senha)
driver.find_element(By.XPATH, '//input[@type="submit"]').click()

print("passou")
# Espera a próxima página carregar
time.sleep(5)

# Verifica se logou com sucesso
print("Página atual:", driver.title)

print("indo pra página de relatórios...")

driver.get("https://rastreioonline.seeflex.com.br/relatorios")

# Espera a página carregar
time.sleep(5)

# Verifica se acessou corretamente
print("Título da página de relatórios:", driver.title)

print("Selecionando a opção 100...")
select_element = driver.find_element(By.NAME, "DataTables_Table_0_length")
select = Select(select_element)
select.select_by_value("100")

print("opção 100... Selecionada")
time.sleep(2)

print("Clicando no botão de relatório...")
botao_relatorio = driver.find_element(By.XPATH, f'//a[contains(@href, "{nome_caminho}")]')
botao_relatorio.click()
print("Botão clicado")
time.sleep(5)

# Calcula as datas
hoje = datetime.today()
ontem = hoje - timedelta(days=1)
data_ontem_formatada = ontem.strftime('%d/%m/%Y')
time.sleep(2)

print("Encontra os campos de data") 
inputs_date = driver.find_elements(By.CSS_SELECTOR, 'input[type="date"]')
inputs_date[0].clear()
inputs_date[0].send_keys(data_ontem_formatada)
inputs_date[1].clear()
inputs_date[1].send_keys(data_ontem_formatada)
print(f"Datas preenchidas: {data_ontem_formatada}")

select_element = driver.find_element(By.XPATH, '//select[@class="form-control"]')
select = Select(select_element)
select.select_by_value("CSV")
print("opção CSV... Selecionada")
time.sleep(1)

botao_pesquisa = driver.find_element(By.XPATH, '//button[contains(@class, "btn-pesquisa")]')
botao_pesquisa.click()

print("Butão de Pesquisa selecionado")

time.sleep(4)

def arquivo_baixado():
    for filename in os.listdir(download_path):
        if nome_base in filename and not filename.endswith('.crdownload'):
            return filename
    return None

print("Esperando o download do relatório...")

# C:\Users\edeconsil\Downloads\Velocidade_(Relatorio_para_robo)_NzJXWlJ0.csv

for _ in range(timeout):
    arquivo = arquivo_baixado()
    if arquivo:
        print(f"Download concluído: {arquivo}")
        selecionar_formatacao(arquivo)
        break
    time.sleep(1)
else:
    print("⚠️ Tempo esgotado. Arquivo não encontrado.")