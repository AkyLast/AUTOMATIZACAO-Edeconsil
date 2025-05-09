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



load_dotenv()

USERNAME = os.getenv("USERNAME_ITURAN")
PASSWORD = os.getenv("PASWORD_ITURAN")

DOWNLOAD_PATH = r"C:\Users\edeconsil\Downloads"  
BASES = [
    ("Velocidade_(Relatorio_para_robo)", "/relatorios/print?alias=CUSTOMIZADO&id=384"), 
    #("Tempo_Ocioso_veiculos_de_12v", "/relatorios/print?alias=CUSTOMIZADO&id=218"),
    #("Tempo_Ocioso_veiculos_de_24v", "/relatorios/print?alias=CUSTOMIZADO&id=389"),
    ("FORA_DO_HORARIO_GERAL", "/relatorios/print?alias=CUSTOMIZADO&id=375")
    ]
TIMEOUT = 120  

options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def iniciar_navegador():
    # Inicializa o navegador com o caminho correto para o chromedriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Acessa o site de login
    print("indo por login")
    driver.get("https://iweb.ituran.com.br/iweb2/login.aspx")
    time.sleep(2)
    return driver


def login():
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
        EC.presence_of_element_located((By.ID, "txt_username"))
    )
    driver.find_element(By.ID, "txt_username").send_keys(usuario)
    driver.find_element(By.ID, "txt_password").send_keys(senha)
    driver.find_element(By.XPATH, '//input[@type="submit"]').click()
    print("Login Feito")
    time.sleep(5)

    print("Indo por Relatórios")

    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "Main_ReportsandPlaybackImg"))
    )
    driver.get("https://iweb.ituran.com.br/iweb2/PeleReports/Pelereports.aspx")
    time.sleep(2)

    select_element = driver.find_element(By.NAME, "SelectReportType")
    select = Select(select_element)
    select.select_by_value("4")

    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.NAME, "SelectReportParameter"))
    )

    select_element = driver.find_element(By.NAME, "SelectReportParameter")
    select = Select(select_element)
    select.select_by_value("85")

    driver.find_element(By.ID, "span_Yesterday").click()
    time.sleep(2)
    
    driver.find_element(By.XPATH, "//a[@href='#tab-3']").click()
    time.sleep(2)

    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "fancytree-checkbox"))
    ).click()
    time.sleep(2)                     

    driver.find_element(By.XPATH, "//a[@href='#tab-9']").click()

    """
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "(//span[@class='dynatree-expander'])[1]"))
    )
    
    # Clica no segundo elemento
    element.click()
    

    WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@title='Latitude / Longitude']/preceding-sibling::span[@class='dynatree-checkbox']"))
    ).click()
    """
    driver.find_element(By.ID, "reportButton").click()

    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Ok' and not(contains(@class, 'hidden'))]"))
    )
    element.click()
    time.sleep(30)

    print("Clicando em exportar")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@id='exportButton' and text()='Export']"))
    ).click
    print("btn clicador")


    
    time.sleep(TIMEOUT)  

login()
