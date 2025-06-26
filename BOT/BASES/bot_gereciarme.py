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

def mesclar_arquivos(download_path, arquivo_baixado=None, name = None, data = None):
    base = r"C:\Users\edeconsil\Documents"
    
    # Lista para armazenar os DataFrames
    dfs = []
    
    # Data atual (usado para a coluna 'DATA')
    data_atual = datetime.now().strftime('%Y-%m-%d')
    
    # Se um arquivo específico foi baixado, vamos adicionar ele com as novas colunas
    if arquivo_baixado:
        caminho_arquivo = os.path.join(download_path, arquivo_baixado)
        df = pd.read_csv(caminho_arquivo, sep = ";")

        # Adiciona a coluna 'DATA' com a data de hoje
        df['DATA'] = data
        # Adiciona a coluna 'CR' com o nome do arquivo (CR)
        df['CR'] = name
        dfs.append(df)
    
    # Concatena todos os DataFrames em um único DataFrame
    df_completo = pd.concat(dfs, ignore_index=True)
    
    # Caminho para o arquivo base
    arquivo_base_path = os.path.join(base, "Base Gerenciarme.xlsx")
    
    # Se o arquivo base já existir, vamos adicionar as novas linhas a ele
    if os.path.exists(arquivo_base_path):
        # Lê o arquivo existente
        df_base = pd.read_excel(arquivo_base_path)
        # Concatena o DataFrame base com o novo
        df_completo = pd.concat([df_base, df_completo], ignore_index=True)
    
    # Salva o DataFrame completo em 'arquivo_base.csv'
    df_completo.to_excel(arquivo_base_path, index=False)
    print(f"Arquivos mesclados com sucesso em '{arquivo_base_path}'.")

class Downloader:
    def __init__(self, name, data):
        self.download_path = r"C:\Users\edeconsil\Downloads"
        self.name = name
        self.file = None
        self.data = data
    
    def download_file(self, timeout=20):
        start_time = time.time()
        while time.time() - start_time < timeout:
            arquivo = self.search_file()
            if arquivo:
                print(f"Download concluído: {arquivo}")
                self.file = arquivo
                # Chama a função para mesclar os arquivos
                mesclar_arquivos(self.download_path, arquivo_baixado=arquivo, name = self.name, data = self.data)
                break
            time.sleep(1)
        else:
            print("⚠️ Tempo esgotado. Arquivo não encontrado.")
    
    def search_file(self):
        # Lista arquivos no diretório e filtra de forma otimizada
        for filename in os.listdir(self.download_path):
            if self.name in filename and not filename.endswith('.crdownload') and "relatorio" in filename:
                return filename
        return None



options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def iniciar_navegador():
    # Inicializa o navegador com o caminho correto para o chromedriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Acessa o site de login
    print("indo por login")
    driver.get("http://v5.gerenciar.me/#/")
    time.sleep(2)

    return driver


def navegar(days_start: int, days_end: int = None):
    driver = iniciar_navegador()
    
    usuario = os.getenv("USERNAME_GERENCIARME")
    password = os.getenv("PASSWORD_GERENCIARME")

    print("Fazendo login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-29"))
    ).send_keys(usuario)
    driver.find_element(By.ID, "input-33").send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    print("Login Feito")

    time.sleep(1.5)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//button[@type="button"]'))
    ).click()

    time.sleep(1.5)
    driver.find_element(By.CLASS_NAME, "v-list-group__header").click()
    time.sleep(1.5)
    wait = WebDriverWait(driver, 10)
    elements = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".v-list-group__items > .v-list-item"))
    )

    # Acessando o segundo item (índice 1)
    segundo_item = elements[1]

    try:
        # Encontrando o link <a> dentro do segundo item
        href = segundo_item.get_attribute('href')
        print("Href do segundo item:", href)
        driver.get(href)
    except Exception as e:
        print("Erro ao encontrar o link no segundo item:", e)

    entradas = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input"))
    )
    entradas[0].click()
    entradas[0].click()

    time.sleep(1.5)
    items = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".v-menu__content>.v-list>.v-list-item"))
    )
    
    def baixar(item, entrada, name_file):
        data_atual = datetime.now().strftime('%d/%m/%Y')
        global data 
        data = data_atual
        dd, mm, yy = data_atual.split("/")
        dd = days_start
        data = f"{dd}/{mm}/{yy}"


        obj_downloader = Downloader(name = name_file, data = data)

        days_start_select = None
        days_end_select = None
        click_on_twos = 0
        valor_atual = item
        valor_atual.click()
        time.sleep(1)
        if days_start_select == None or days_end_select == None:
            driver.find_element(By.CSS_SELECTOR, ".v-text-field__slot>input").click()
            time.sleep(0.2)
            caixa = driver.find_elements(By.CSS_SELECTOR, "div.v-date-picker-header>button")
            if days_start > int(dd):
                data = f"{dd}/{int(mm) - 1}/{yy}"
                caixa[0].click()

            time.sleep(1)
            dias = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.v-btn__content"))                
            )
                
            
            for dia in dias:
                print(f"{dia.text.strip()} = {str(days_start)}  == {dia.text.strip() == str(days_start)}")
                if dia.text.strip() == str(days_start):
                    days_start_select = dia
                    if days_end == None:
                        break
                    if days_end != None and dia.text.strip() == str(days_end):
                        days_end_select = dia
                        click_on_twos = 1
                    
            if click_on_twos:
                days_start_select.click()
                days_end_select.click()
            else:
                days_start_select.click()
                time.sleep(0.5)
                days_start_select.click()

            ok_ = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.v-btn__content"))
            )

                #for i in range(days_start, 30)
        
            select_ok = None
            for analisar_ok in ok_:
                if analisar_ok.text.strip() == "OK":
                    select_ok = analisar_ok
                    break
                time.sleep(0.2)
            select_ok.click()

        time.sleep(1.5)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".row>.text-end>.v-btn"))
        ).click()

        time.sleep(1)
        obj_downloader.download_file()
     
   
    valor_atual = None
    dict = {}
    for i, item in enumerate(items):
        entradas = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input"))
        )
        entradas[0].click()
        entradas[0].click()
        items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".v-menu__content>.v-list>.v-list-item"))
        )
        # print(items[i].text)
        baixar(items[i], entradas, items[i].text)
        driver.refresh()
        time.sleep(1)

navegar(days_start = 20)