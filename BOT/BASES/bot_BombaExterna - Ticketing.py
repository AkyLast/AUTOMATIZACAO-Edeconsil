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

options = webdriver.ChromeOptions()

#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializa o navegador com o caminho correto para o chromedriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Acessa o site de login
print("indo por login")
driver.get("https://plataforma.ticketlog.com.br/")
time.sleep(2)

# Preencher login e senha
usuario = os.getenv("USUARIO_T")
senha = os.getenv("PASSWORD_T")


print("por aqui")
driver.find_element(By.ID, "Username").send_keys(usuario)
driver.find_element(By.ID, "Password").send_keys(senha)
driver.find_element(By.XPATH, '//button[@type="submit"]').click()

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