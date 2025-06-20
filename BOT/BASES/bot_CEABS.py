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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

class Downloader:
    def __init__(self, name):
        self.download_path = r"C:\Users\edeconsil\Downloads"
        self.name = name
        self.file = None
    
    def download_file(self, timeout=20):
        start_time = time.time()
        while time.time() - start_time < timeout:
            arquivo = self.search_file()
            if arquivo:
                print(f"Download concluído: {arquivo}")
                self.file = arquivo
                print(arquivo)
                # Chama a função para mesclar os arquivos
                # mesclar_arquivos(self.download_path, arquivo_baixado=arquivo, name = self.name)
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
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def iniciar_navegador():
    # Inicializa o navegador com o caminho correto para o chromedriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Acessa o site de login
    print("indo por login")
    driver.get("https://cps.ceabs.com.br/Login/")
    time.sleep(2)

    return driver


def navegar():
    driver = iniciar_navegador()
    
    usuario = os.getenv("USERNAME_CEABS")
    password = os.getenv("PASSWORD_CEABS")
    print(usuario, password)

    print("Fazendo login")
    try:
        # Espera até 10 segundos para o botão 'btn-accept' ser visível
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btn-accept"))
        )
        btn_accept = driver.find_element(By.ID, "btn-accept")
        
        # Se o botão existir, clique nele
        if btn_accept.is_displayed():
            print("Botão de aceitação encontrado. Clicando nele...")
            btn_accept.click()
            time.sleep(2)  # Aguarda a resposta do clique
        else:
            print("Botão de aceitação não está visível. Prosseguindo com o login.")
    except:
        print("Botão de aceitação não encontrado ou não visível.")

    print("Fazendo login...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "Login"))
    ).send_keys(usuario)
    driver.find_element(By.ID, "Senha").send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    print("Login feito")

    time.sleep(3)
    driver.get("https://cps.ceabs.com.br/AlertaViolacoes/Index")

    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='form-group']//div[@class='chosen-group']"))
    )
    print(f"Encontrei {len(elements)} elementos com o XPath especificado.\n")
    """
    for i, element in enumerate(elements):
        print(f"--- Detalhes do Elemento {i+1} ---")
        print(f"Tag: {element.tag_name}")
        print(f"Texto Visível: {element.text}")
        print(f"HTML Interno: {element.get_attribute('innerHTML')}")
        print(f"HTML Completo: {element.get_attribute('outerHTML')}")
        print(f"É Exibível? {element.is_displayed()}")
        print(f"Localização (x, y): {element.location}")
        print(f"Tamanho (largura, altura): {element.size}")
        print("-" * 30)
    """

    try:
        # --- Interagindo com o Chosen.js (parte importante para a interface) ---
        # Encontre o contêiner do Chosen.js para o 'AlertaId'.
        # O ID do contêiner do Chosen é geralmente o ID do select original + '_chosen'
        chosen_container_id = "AlertaId_chosen"
        
        # 1. Espera até que o contêiner do Chosen esteja visível e clicável
        chosen_container = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, chosen_container_id))
        )
        print(f"Contêiner do Chosen.js com id='{chosen_container_id}' encontrado e clicável.")

        # 2. Clique no contêiner para abrir o dropdown
        chosen_container.click()
        print("Dropdown do Chosen.js clicado.")

        # 3. Espera que a opção específica seja visível e clicável dentro do dropdown do Chosen.
        # O texto visível é "Movimentação Fora do Horário Permitido" para o valor "382379"
        # O Chosen geralmente coloca as opções dentro de uma <ul> com a classe "chosen-results"
        # e cada opção é um <li>.
        
        # Construa um XPath para encontrar o <li> com o texto desejado dentro do dropdown aberto.

        # option_text = "Movimentação Fora do Horário Permitido"
        # option_text = "Velocidade"
        option_text = "Ociosidade "
        
        # XPath mais específico para garantir que estamos buscando dentro do dropdown ativo
        # Isso procura por um <li> que esteja dentro de um div.chosen-drop que seja filho do chosen_container
        chosen_option_xpath = f"//div[@id='{chosen_container_id}']//div[@class='chosen-drop']//ul[@class='chosen-results']/li[text()='{option_text}']"

        chosen_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, chosen_option_xpath))
        )
        print(f"Opção '{option_text}' no dropdown do Chosen.js encontrada e clicável.")

        # 4. Clique na opção gerada pelo Chosen.js
        chosen_option.click()
        print(f"Opção '{option_text}' clicada no Chosen.js.")
        
        # Opcional: Pequeno atraso para garantir que a interface seja atualizada
        time.sleep(1) 

        print("\nSeleção e interação com Chosen.js concluídas com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        # Você pode querer capturar uma screenshot aqui para depurar
        # driver.save_screenshot("erro_selecao_alerta.png")

    btn_days = driver.find_element(By.ID, "dtr-periodo")
    btn_days.click()

    try:
        # Usamos WebDriverWait para esperar que os elementos estejam presentes no DOM
        # antes de tentar encontrá-los. Isso torna o código mais robusto.
        teste = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ranges > ul > li"))
        )

        print(f"Encontrados {len(teste)} elementos que correspondem ao seletor CSS.")

        # Você pode iterar sobre 'teste' para acessar cada elemento encontrado:
        for i, elemento in enumerate(teste):
            print(f"Elemento {i+1} - Tag: {elemento.tag_name}, Texto: '{elemento.text}'")

        teste[3].click()

    except Exception as e:
        print(f"Ocorreu um erro ao tentar encontrar os elementos: {e}")

    time.sleep(1)

    btn_exportar = driver.find_element(By.CSS_SELECTOR, ".btn.btn-info.dropdown-toggle")
    btn_exportar.click()

    btn_baixar = driver.find_element(By.ID, "btn-exportar-excel")
    print(btn_baixar.text)
    btn_baixar.click()



    time.sleep(360)


navegar()