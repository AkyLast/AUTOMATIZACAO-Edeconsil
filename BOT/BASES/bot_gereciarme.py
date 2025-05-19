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


options = webdriver.ChromeOptions()
#options.add_argument('--headless')
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
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".v-list-item>.v-list-item__content>.v-list-item__title"))
    )

    valor_atual = None
    for i, item in enumerate(items):
        if item.text.strip() == "CR REDUÇÃO":
            valor_atual = item
            break
    valor_atual.click()

    driver.find_element(By.CSS_SELECTOR, ".v-text-field__slot>input").click()
    dias = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.v-btn__content"))
    )
    
    days_start_select = None
    days_end_select = None
    click_on_twos = 0

    for dia in dias:
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
    
    select_ok.click()

    time.sleep(600)

navegar(days_start = 5)