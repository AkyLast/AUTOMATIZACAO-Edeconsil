import os
import time
import pandas as pd

from dotenv import load_dotenv
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
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
        self.driver = None

    def inicializar(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        driver.get("https://rastreioonline.seeflex.com.br/users/login")
        time.sleep(2)

        return driver

class Armadura():
    def __init__(self, file: str, name: str = None):
        self.file = file
        self.name = name
        self.nameToSave = None
        self.download_path = r"C:\Users\edeconsil\Downloads"
        self.path = os.path.join(self.download_path, self.file)

        self._header = self.search_header(self.file)
        self.__df = None
       
    def search_header(self, file):
        header = 0
        if "Tempo_Ocioso_veiculos_de_12v" in file or "Tempo_Ocioso_veiculos_de_24v" in file:
            header = 5

        elif "Velocidade_(Relatorio_para_robo)" in file:
            header = 5

        elif "FORA_DO_HORARIO_GERAL" in file:
            header = 4

        return header

    def read_file(self):
        df = pd.read_csv(self.path, encoding="ISO-8859-1", header = self._header, sep = ";")
        df.columns = df.columns.str.upper().str.strip()
        if "DATA INICIAL" in df.columns:
            df.rename(columns = {"DATA INICIAL": "DATA"}, inplace = True)
            try:
                df[["DATA", "HORA"]] = df["DATA"].astype(str).apply(lambda x: pd.Series(x.strip().split(" ")))
            except Exception as error:
                print(f"Erro ao dividir hora da data: {error}")

        if "VEÍCULO" in df.columns:
            df.rename(columns = {"VEÍCULO": "TAG"}, inplace = True)

        if "DADOS ADICIONAIS" in df.columns and "DURAÇÃO" not in df.columns:
            df.rename(columns = {"DADOS ADICIONAIS": "VELOCIDADE"}, inplace = True)
            df = df[df["DATA"].notna() & df["VELOCIDADE"].notna()]
            df["VELOCIDADE"] = df["VELOCIDADE"].astype("int16")

        elif "DADOS ADICIONAIS" in df.columns :
            df.drop("DADOS ADICIONAIS", axis = 1, inplace = True)

        elif "DURAÇÃO" in df.columns:  
            df = df[df["DATA FINAL"].notna() | df["DURAÇÃO"].notna()]

        if "LAT./LONG." in df.columns:
            df[["LATITUDE", "LONGITUDE"]] = df["LAT./LONG."].astype(str).apply(lambda x: pd.Series(x.split(",")))
            df.drop("LAT./LONG.", axis = 1, inplace = True)
        
        if "PLACA" in df.columns:
            df["PLACA"] = df["PLACA"].apply(lambda x: x.strip().upper())

        self.__df = df

    def config_file(self):
        def format_status(row):
            if row["VELOCIDADE"] > 110 and row["TAG"][0:2] == "CA":
                valor = "ALTA"
            elif row["VELOCIDADE"] > 85 and row["TAG"][0:2] != "CA":
                valor = "ALTA"
            else:
                valor = "MODERADA"
            return valor

        def format_time(duracao):
            try:
                hh, mm, ss = duracao.strip().split(":")
                segundos = ((int(hh) * 60 + int(mm)) * 60) + int(ss)
                return (int(segundos // 60))
            except Exception as error:
                logger.error(f"Erro ao formatar a duração em minutos: {error}")
                return duracao

        def format_placa(placa):
            try:
                new_placa = placa.replace("-", "")
                return new_placa
            except Exception as error:
                logger.error(f"Error ao formatar a placa: {error}")
                return placa
            
        df = self.__df
        
        df["TAG"] = df["TAG"].apply(lambda x: x.upper().strip().replace(" ", ""))

        if "VELOCIDADE" in df.columns:
            df["STATUS"] = df.apply(format_status, axis = 1)
            df = df[df["STATUS"] == "ALTA"]
        
        if "DURAÇÃO" in df.columns: 
            df["TEMPO OCIOSO"] = df["DURAÇÃO"].apply(format_time)
        
        if "PLACA" in df.columns:
            df["PLACA"] = df["PLACA"].apply(format_placa)

        hoje = datetime.today().date()
        data_limite = datetime(2025, 6, 30).date()

        if "FORA_DO_HORARIO_GERAL" in self.file:
            df.drop("KM PERCORRIDA", axis = 1, inplace = True)
            if hoje <= data_limite:
                df = df[~df["TAG"].isin(["CB258", "CB170", "CE22", "CA134"])]

            ##############---------------##############
            #          Tempo indertermindado          #
            if True:
                df = df[~df["TAG"].isin(["CA157", "CA159"])]
            ##############---------------##############

        self.__df = df

    def ordem_toSave(self):
        df = self.__df
        if "FORA_DO_HORARIO_GERAL" in self.file:
            self.nameToSave = "FORAHORARIO"
            df = df[["DATA", "HORA", "TAG", "ENDEREÇO"]]
        
        if "Velocidade_(Relatorio_para_robo)" in self.file:
            self.nameToSave = "VELOCIDADE"
            df = df[["DATA", "HORA", "TAG", "MOTORISTA", "ENDEREÇO", "LATITUDE", "LONGITUDE", "VELOCIDADE", "STATUS"]]

        if "Tempo_Ocioso" in self.file:
            self.nameToSave =  "OCIOSIDADE_12v" if "12v" in self.file else "OCIOSIDADE_24V"
            df = df[["DATA FINAL", "TAG", "ENDEREÇO", "DURAÇÃO", "TEMPO OCIOSO"]]

        self.__df = df

    def save(self):
        df = self.__df

        diretorio_arquivo = self.download_path
    
        # Define o caminho completo para o arquivo Excel (mesmo diretório)
        caminho_excel = os.path.join(diretorio_arquivo, f"Relatorio_Formatado - {self.nameToSave}.xlsx")
        
        # Salva o DataFrame no Excel
        df.to_excel(caminho_excel, index=False)

    def run(self):
        self.read_file()
        self.config_file()
        self.ordem_toSave()
        self.save()

class Megatron(Motor):
    def __init__(self, name: str, path: str, days: int = 1, TIMEOUT: int = 120):
        super().__init__()
        self.name = name
        self.path = path
        self.file = None
        self.days = days
        self.TIMEOUT = TIMEOUT
        self.download_path = r"C:\Users\edeconsil\Downloads"

    def login(self):
        driver = self.inicializar()
        self.driver = driver

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
        
        botao_relatorio.click()
        logger.info("Relatório encontrado e indo para o caminho!")
        logger.info("Logado com sucesso!!!!")

    def config_relatorio(self):
        driver = self.driver
        
        hoje = datetime.today()
        dias_anteriores = hoje - timedelta(days=self.days)
        d_1 = hoje - timedelta(days = 1) # d-1

        fim = d_1.strftime('%d/%m/%Y')
        inicio = dias_anteriores.strftime('%d/%m/%Y')

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

            # Data Inicial
            inputs_hora[0].clear()
            inputs_hora[0].send_keys(hora_inicio)

            # Preenche o segundo input (Data Final) com a hora de hoje
            inputs_hora[1].clear()
            inputs_hora[1].send_keys(hora_fim)

            logger.info(f"Horas preenchidas: {hora_inicio} a {hora_fim}")

        inputs_date[0].clear()
        inputs_date[0].send_keys(inicio) # começo dos dias
        inputs_date[1].clear()
        inputs_date[1].send_keys(fim) # fim dos dias

        logger.info(f"Datas preenchidas: {inicio} a {fim}")

        logger.info("Procurando Excel/CSV")

        try:
            select_element = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, '(//select[@class="form-control"])[2]'))
            )
            select = Select(select_element)
            select.select_by_visible_text("Excel/CSV")
        except TimeoutException as error:
            #não existe o excel/csv
            print(error)
            select_element = driver.find_element(By.XPATH, '//select[@class="form-control"]')
            select = Select(select_element)
            select.select_by_value("CSV")

        logger.info("Opção 'Excel/CSV' selecionada com sucesso.")

        botao_pesquisa = driver.find_element(By.XPATH, '//button[contains(@class, "btn-pesquisa")]')
        botao_pesquisa.click()  
        logger.info("Bottton of search on clicked")

        self.download_file()
        driver.quit()

    def download_file(self):
        timeout = self.TIMEOUT
        for _ in range(timeout):
            arquivo = self.search_file()
            if arquivo:
                print(f"Download concluído: {arquivo}")
                self.file = arquivo
                break
            time.sleep(1)
        else:
            print("⚠️ Tempo esgotado. Arquivo não encontrado.")
    
    def search_file(self):
        for filename in os.listdir(self.download_path):
                if self.name in filename and not filename.endswith('.crdownload'):
                    return filename
        return None
    
    def adjust_data(self):
        file = Armadura(self.file)
        file.run()

    def run(self):

        self.login()
        self.config_relatorio()
        self.adjust_data()

        #driver.quit()

BASES = [
    #("Velocidade_(Relatorio_para_robo)", "/relatorios/print?alias=CUSTOMIZADO&id=384"), 
    #("Tempo_Ocioso_veiculos_de_12v", "/relatorios/print?alias=CUSTOMIZADO&id=218"),
    #("Tempo_Ocioso_veiculos_de_24v", "/relatorios/print?alias=CUSTOMIZADO&id=389"),
    ("FORA_DO_HORARIO_GERAL", "/relatorios/print?alias=CUSTOMIZADO&id=375")
    ]

for name, path in BASES:
    bot = Megatron(name, path, days = 4)
    bot.run()

