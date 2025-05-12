import os
import time
import pandas as pd

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

load_dotenv()

def formatar_ForaHorario(arquivo):
    df = pd.read_csv(arquivo, encoding = "ISO-8859-1", header = 4, sep = ";")
    df = df.dropna(axis=0)

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

    df = df[["DATA", "HORA", "TAG", "KM PERCORRIDO", "LOCALIZAÇÃO", "PLACA"]]

    diretorio_arquivo = os.path.dirname(arquivo)
    
    # Define o caminho completo para o arquivo Excel (mesmo diretório)
    caminho_excel = os.path.join(diretorio_arquivo, "Relatorio_Formatado - Fora de Horário.xlsx")
    
    # Salva o DataFrame no Excel
    df.to_excel(caminho_excel, index=False)

    print(f"Arquivo formatado e salvo como '{caminho_excel}'")



# Configurações do Chrome para rodar no modo headless
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
usuario = os.getenv("USUARIO")
senha = os.getenv("SENHA")

print(usuario, senha)

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

botao_relatorio = driver.find_element(By.XPATH, '//a[contains(@href, "/relatorios/print?alias=CUSTOMIZADO&id=375")]')
botao_relatorio.click()
print("Botão clicado")

# Espera a nova página ou o download iniciar
time.sleep(5)


# Calcula as datas
hoje = datetime.today()
hoje_formatado = hoje.strftime("%d/%m/%Y")
ontem = hoje - timedelta(days=3)
data_ontem_formatada = ontem.strftime('%d/%m/%Y')

hora_ontem = "20:30"
hora_hoje = "05:30"

# Espera a página carregar e garante que os campos de data estão visíveis
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

print("Butão de Pesquisa selecionado")

time.sleep(4)

download_path = r"C:\Users\edeconsil\Downloads"  
nome_base = "FORA_DO_HORARIO_GERAL"
timeout = 120  

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
        formatar_ForaHorario(os.path.join(download_path, arquivo))
        break
    time.sleep(1)
else:
    print("⚠️ Tempo esgotado. Arquivo não encontrado.")