import os
import time
from dotenv import load_dotenv

from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.support import expected_conditions as EC

import logging

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler("app_logs.log")
    ]
)

logger = logging.getLogger()

load_dotenv()

class Motor():
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")

    def inicializar(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        driver.get("https://rastreioonline.seeflex.com.br/users/login")
        time.sleep(2)

        return driver

class Megatron(Motor):
    def __init__(self, name: str, path: str, days: int = 1, TIMEOUT: int = 120):
        super().__init__()
        self.name = name
        self.path = path
        self.days = days
        self.TIMEOUT = TIMEOUT

    def login(self):
        driver = self.inicializar()

        USER = os.getenv("USUARIO")
        PASSWORD = os.getenv("SENHA")
        
        logger.info("Tentando fazer login.")
        WebDriverWait(driver, self.TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "user_username"))
        )

        driver.find_element(By.ID, "user_username").send_keys(USER)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, '//input[@type="submit"]').click()
        logger.info("Login feito com SUCESSO!!")

        logger.info("Indo para os Relatórios")
        time.sleep(5)
        driver.get("https://rastreioonline.seeflex.com.br/relatorios")
        logger.info("Selecionando a opção 100...")
        select_element = driver.find_element(By.NAME, "DataTables_Table_0_length")
        select = Select(select_element)
        select.select_by_value("100")
        logger.info("opção 100... Selecionada")
        time.sleep(2)

        WebDriverWait(driver, self.TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, f'//a[contains(@href, "{self.path}")]'))
        )
        logger.info(f"Buscando relatório: {self.name}")
        botao_relatorio = driver.find_element(By.XPATH, f'//a[contains(@href, "{self.path}")]')
        print(f"\n{botao_relatorio}\n")
        botao_relatorio.click()
        logger.info("Relatório encontrado e indo para o caminho!")
        time.sleep(5)

    def config_relatorio(self, driver):
        hoje = datetime.today()
        dias_anteriores = hoje - timedelta(days=self.days)

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="date"]'))
        )
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="time"]'))
        )
        logger.info("Preenchendo campos de datas e horas") 
        inputs_date = driver.find_elements(By.CSS_SELECTOR, 'input[type="date"]')
        
        if "FORA_DO_HORARIO_GERA" in self.name:
            hora_inicio = "20:30"
            hora_fim = "05:30"

            fim = hoje.strftime('%d/%m/%Y')
            inicio = dias_anteriores.strftime('%d/%m/%Y')

            inputs_hora = driver.find_elements(By.CSS_SELECTOR, 'input[type="time"]')

            

            inputs_date[0].clear()
            inputs_date[0].send_keys(inicio)
            inputs_hora[0].clear()
            inputs_hora[0].send_keys(hora_inicio)

            # Preenche o segundo input (Data Final) com a hora de hoje
            inputs_hora[1].clear()
            inputs_hora[1].send_keys(hora_fim)


            print(f"Datas preenchidas: {inicio} a {fim} entre {hora_inicio} à {hora_fim}")
            time.sleep(3)

            

    def run(self):
        self.login()
        print("Logado com sucesso")

BASES = [
    ("Velocidade_(Relatorio_para_robo)", "/relatorios/print?alias=CUSTOMIZADO&id=384"), 
    ("Tempo_Ocioso_veiculos_de_12v", "/relatorios/print?alias=CUSTOMIZADO&id=218"),
    ("Tempo_Ocioso_veiculos_de_24v", "/relatorios/print?alias=CUSTOMIZADO&id=389"),
    ("FORA_DO_HORARIO_GERAL", "/relatorios/print?alias=CUSTOMIZADO&id=375")
    ]

for name, path in BASES:
    bot = Megatron(name, path)
    bot.run()