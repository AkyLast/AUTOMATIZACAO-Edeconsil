import os
import time
import pandas as pd

from dotenv import load_dotenv
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.support import expected_conditions as EC

def formatar_RastreOnline(arquivo):
    df = pd.read_csv(arquivo, encoding="ISO-8859-1", header = 5, sep = ";")

    df = df.drop(df.index[-1])
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

    df = df[["DATA", "HORA", "TAG", "MOTORISTA", "LOCALIZAÇÃO", "LATITUDE", "LONGITUDE", "VELOCIDADE", "STATUS"]]
    
    nome_teste = "RastreOnline"
    diretorio_arquivo = os.path.dirname(arquivo)
    
    # Define o caminho completo para o arquivo Excel (mesmo diretório)
    caminho_excel = os.path.join(diretorio_arquivo, f"Relatorio_Formatado - {nome_teste}.xlsx")
    
    # Salva o DataFrame no Excel
    df.to_excel(caminho_excel, index=False)

    print(f"Arquivo formatado e salvo como '{caminho_excel}'")

def formatar_Ociosidade(arquivo):
    df = pd.read_csv(arquivo, encoding="ISO-8859-1", header = 5, sep = ";")
    if "Dados Adicionais" in df.columns:
        df = df.drop(["Dados Adicionais"], axis = 1)
    df = df.dropna(axis = 0)
    
    def format_df(row):
        def format_time(duracao):
            try:
                hh, mm, ss = duracao.split(':')
                segundos = ((int(hh) * 60 + int(mm)) * 60) + int(ss)
                return int(segundos // 60)
            except:
                return duracao


        row["Veículo"] = row["Veículo"].replace(" ", "").replace("-", "")
        #row["Data Final"] = pd.to_datetime(row["Data Final"], dayfirst=True)
        #row["Data Final"] = row["Data Final"].strftime("%d/%m/%Y %H:%M:%S")
        row["Duração Minutos"] = format_time(row["Duração"])
        #row["Duração"] = pd.to_datetime(row["Duração"])

        #row["Duração"] = row["Duração"].strftime("%H:%M:%S") 
        return row

    df = df.apply(format_df, axis = 1)

    df = df.rename(columns = {
        "Veículo": "TAG",
        "Endereço": "Localização",
        "Duração": "Tempo Ocioso",
        "Data Final": "DATA FINAL",
    })
    
    df = df[["DATA FINAL", "TAG", "Localização", "Tempo Ocioso", "Duração Minutos"]]
    
    volts = "12v" if "12v" in arquivo else "24v"
    nome_teste = f"Ociosidade {volts}"
    diretorio_arquivo = os.path.dirname(arquivo)
    
    # Define o caminho completo para o arquivo Excel (mesmo diretório)
    caminho_excel = os.path.join(diretorio_arquivo, f"Relatorio_Formatado - {nome_teste}.xlsx")
    
    # Salva o DataFrame no Excel
    df.to_excel(caminho_excel, index=False)

    print(f"Arquivo formatado e salvo como '{caminho_excel}'")
  
def formatar_ForaHorario(arquivo):
    df = pd.read_csv(arquivo, encoding = "ISO-8859-1", header = 4, sep = ";")
    df = df.drop(df.index[-1])

    df["DATA"] = pd.to_datetime(df["Data Inicial"], dayfirst=True)
    df["HORA"] = df["DATA"].dt.strftime("%H:%M:%S")
    df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")
    df = df.drop("Data Inicial", axis = 1)

    df["Placa"] = df["Placa"].apply(lambda x: x.upper().strip().replace("-", ""))
    df["Veículo"] = df["Veículo"].apply(lambda x: x.upper().strip().replace(" ", ""))

    df.rename(columns={
        "Placa": "PLACA",
        "Veículo": "TAG",
        "Endereço": "LOCALIZAÇÃO",
        "Km Percorrida": "KM PERCORRIDO",
    }, inplace=True)

    hoje = datetime.today().date()

    # Definir a data limite como um objeto datetime
    data_limite = datetime(2025, 6, 30).date()

    # Fazer a comparação de datas
    if hoje >= data_limite:
        df = df[~df["TAG"].isin(["CB258", "CB170", "CE22"])]
        
    print("Ordenando as Colunas")
    df = df[["DATA", "HORA", "TAG", "LOCALIZAÇÃO", "PLACA"]]

    diretorio_arquivo = os.path.dirname(arquivo)
    
    # Define o caminho completo para o arquivo Excel (mesmo diretório)
    caminho_excel = os.path.join(diretorio_arquivo, "Relatorio_Formatado - Fora de Horário.xlsx")
    
    # Salva o DataFrame no Excel
    df.to_excel(caminho_excel, index=False)

    print(f"Arquivo formatado e salvo como '{caminho_excel}'")

def selecionar_formatacao(download_path, arquivo):
    print("selecionando arquivo")
    if "Tempo_Ocioso_veiculos_de_12v" in arquivo or "Tempo_Ocioso_veiculos_de_24v" in arquivo:
        formatar_Ociosidade(os.path.join(download_path, arquivo))

    elif "Velocidade_(Relatorio_para_robo)" in arquivo:
        formatar_RastreOnline(os.path.join(download_path, arquivo))

    elif "FORA_DO_HORARIO_GERAL" in arquivo:
        formatar_ForaHorario(os.path.join(download_path, arquivo))

load_dotenv()

USERNAME = os.getenv("USUARIO")
PASSWORD = os.getenv("SENHA")

DOWNLOAD_PATH = r"C:\Users\edeconsil\Downloads"  
BASES = [
    ("Velocidade_(Relatorio_para_robo)", "/relatorios/print?alias=CUSTOMIZADO&id=384"), 
    ("Tempo_Ocioso_veiculos_de_12v", "/relatorios/print?alias=CUSTOMIZADO&id=218"),
    ("Tempo_Ocioso_veiculos_de_24v", "/relatorios/print?alias=CUSTOMIZADO&id=389"),
    ("FORA_DO_HORARIO_GERAL", "/relatorios/print?alias=CUSTOMIZADO&id=375")
    ]
TIMEOUT = 120  

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def iniciar_navegador():
    # Inicializa o navegador com o caminho correto para o chromedriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Acessa o site de login
    print("indo por login")
    driver.get("https://rastreioonline.seeflex.com.br/users/login")
    time.sleep(2)

    return driver


def login(download_path, nome_base, nome_caminho):
    def baixar_arquivo(download_path, nome_base, nome_caminho):
        if "FORA_DO_HORARIO_GERA" in nome_base:
            hoje = datetime.today()
            hoje_formatado = hoje.strftime("%d/%m/%Y")
            #ontem = hoje - timedelta(days=1)
            ontem = hoje - timedelta(days=1) #apagar
            data_ontem_formatada = ontem.strftime('%d/%m/%Y')

            hora_ontem = "20:00"
            hora_hoje = "05:30"

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="date"]'))
            )
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="time"]'))
            )

            print("Encontra os campos de data") 
            inputs_date = driver.find_elements(By.CSS_SELECTOR, 'input[type="date"]')
            print(f"Campos de data encontrados: {len(inputs_date)}")

            #hora
            print("Encontra os campos de hora") 
            inputs_hora = driver.find_elements(By.CSS_SELECTOR, 'input[type="time"]')
            print(f"Campos de hora encontrados: {len(inputs_hora)}")


            # Preenche o primeiro input (Data Inicial) com a data de ontem
            inputs_date[0].clear()
            inputs_date[0].send_keys(data_ontem_formatada)
            inputs_hora[0].clear()
            inputs_hora[0].send_keys(hora_ontem)

            # Preenche o segundo input (Data Final) com a data de hoje
            inputs_date[1].clear()
            inputs_date[1].send_keys(hoje_formatado)
            inputs_hora[1].clear()
            inputs_hora[1].send_keys(hora_hoje)

            print(f"Datas preenchidas: {data_ontem_formatada} a {hoje_formatado} entre {hora_ontem} à {hora_hoje}")
            time.sleep(3)

            print("Procurando Excel/CSV")
            select_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '(//select[@class="form-control"])[2]'))
            )

            select = Select(select_element)
            select.select_by_visible_text("Excel/CSV")

            print("Opção 'Excel/CSV' selecionada com sucesso.")

            botao_pesquisa = driver.find_element(By.XPATH, '//button[contains(@class, "btn-pesquisa")]')
            botao_pesquisa.click()

        else: 
            hoje = datetime.today()
            #ontem = hoje - timedelta(days=1)

            inicio = hoje - timedelta(days=1) #apagar
            fim = hoje - timedelta(days=1)

            data_inicio_formatada = inicio.strftime('%d/%m/%Y')
            data_fim_formatada = fim.strftime('%d/%m/%Y')

            inicio = data_inicio_formatada
            final = data_fim_formatada
            time.sleep(2)

            print("Encontra os campos de data") 
            inputs_date = driver.find_elements(By.CSS_SELECTOR, 'input[type="date"]')
            inputs_date[0].clear()
            inputs_date[0].send_keys(inicio)
            inputs_date[1].clear()
            inputs_date[1].send_keys(final)
            print(f"Datas preenchidas: {inicio} a {final}")

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
        timeout = TIMEOUT
        for _ in range(timeout):
            arquivo = arquivo_baixado()
            if arquivo:
                print(f"Download concluído: {arquivo}")
                selecionar_formatacao(download_path, arquivo)
                break
            time.sleep(1)
        else:
            print("⚠️ Tempo esgotado. Arquivo não encontrado.")

    driver = iniciar_navegador()
    
    usuario = USERNAME
    senha = PASSWORD

    print("Fazendo Login")
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "user_username"))
    )
    driver.find_element(By.ID, "user_username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(senha)
    driver.find_element(By.XPATH, '//input[@type="submit"]').click()
    print("Login Feito")
    time.sleep(5)

    print("Indo por Relatórios")
    driver.get("https://rastreioonline.seeflex.com.br/relatorios")
    time.sleep(5)
    print("Selecionando a opção 100...")
    select_element = driver.find_element(By.NAME, "DataTables_Table_0_length")
    select = Select(select_element)
    select.select_by_value("100")
    print("opção 100... Selecionada")
    time.sleep(2)

    print("Clicando no botão de relatório...")
    botao_relatorio = driver.find_element(By.XPATH, f'//a[contains(@href, "{nome_caminho}")]')
    print(f"\n{botao_relatorio}\n")
    botao_relatorio.click()
    print("Botão clicado")
    time.sleep(5)

    baixar_arquivo(download_path, nome_base, nome_caminho)

    driver.quit()


for nome_base, nome_caminho in BASES:
    print(f"\n{nome_caminho}\n")
    try:
        download_path = DOWNLOAD_PATH
        login(download_path, nome_base, nome_caminho)
    except:
        print(f"Erro ao baixar o arquivo - {nome_base}")