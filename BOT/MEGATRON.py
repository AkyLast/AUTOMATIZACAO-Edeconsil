import os
import time
import pandas as pd
from numpy import ndarray

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
    def __init__(self, headleass = True):
        self.options = webdriver.ChromeOptions()
        if headleass:
            self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.driver = None

    def inicializar(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

        return driver

class Armadura():
    def __init__(self, file: str, name: str = None, status_site: str = None, start_date = None, end_date = None):
        self.status_site = status_site
        self.file = file
        self.name = name
        self.nameToSave = None
        self.download_path = r"C:\Users\edeconsil\Downloads"
        self.df_DeepWeb_path = r"C:\Users\edeconsil\Documents\Luis - Programação\Automatização - BOT\Sources\DB - MOTORISTAS.xlsx"
        self.path = os.path.join(self.download_path, self.file)

        self._header = self.search_header(self.file)
        self.df_DeepWeb_DATA = None
        self.__df = None
        self.start_date = start_date
        self.end_date = end_date

        self.columns = {
            "DATA INICIAL": 0,
            "DATA": 0,
            "HORA": 0,
            "VEÍCULO": 0, 
            "TAG": 0, 
            "MOTORISTA": 0,
            "DURAÇÃO": 0,
            "DADOS ADICIONAIS": 0,
            "ENDEREÇO": 0,
            "VELOCIDADE": 0,
            "LAT./LONG.": 0,
            "LATITUDE": 0,
            "LONGITUDE": 0,
            "PLACA": 0,
            "STATUS": 0,
            "TEMPO OCIOSO": 0,

            "CÓD. VIOLAÇÃO": 0,
            "IDENTIFICAÇÃO": 0,
            "PROPRIETÁRIO": 0,
            "FROTA": 0,
            "MARCA/MODELO": 0, 
            "ALERTA": 0,
            "DATA DO EVENTO": 0,
            "DATA DO REGISTRO": 0,
            "CONCLUÍDO POR": 0,
            "DATA DA CONCLUSÃO": 0,
            "LOCALIZAÇÃO": 0,
            "PERMANÊNCIA": 0,

            'LOC TIME': 0, 
            'VEHICLE NAME': 0, 
            'DRIVER NAME': 0, 
            'ADDRESS': 0, 
            'SPEED': 0,
            "IDLE TIME": 0,
            "STATUS NAME": 0
        }
        
    def search_header(self, file):
        header = 0
        if "Tempo_Ocioso_veiculos_de_12v" in file or "Tempo_Ocioso_veiculos_de_24v" in file:
            header = 5

        elif "Velocidade_(Relatorio_para_robo)" in file:
            header = 5

        elif "FORA_DO_HORARIO_GERAL" in file:
            header = 4

        elif "Speeding_Report" in file:
            header = 7
        
        elif "Idle_Report" in file:
            header = 8

        elif "Ignition_Report" in file:
            header = 6

        elif self.status_site == 0:
            header = 7
        
        return header

    def search_columns(self, column: str = None, set = False, should_print = False):
        if should_print:
            return self.columns

        if isinstance(column, list) or isinstance(column, ndarray):  
            for column_idx in column:
                self.search_columns(column_idx, set = True)
        else: 
            if not set: 
                return self.columns.get(column, 0) 
            else:  
                if self.columns.get(column, 0) == 1:
                    self.columns[column] = 0
                else:
                    self.columns[column] = 1
            
    def read_file(self):
        if self.status_site == 0:
            df = pd.read_excel(self.path, header = self._header)
        elif self.status_site == 1:
            df = pd.read_csv(self.path, encoding="ISO-8859-1", header = self._header, sep = ";")
        elif self.status_site == 2:
            df = pd.read_excel(self.path, header = self._header)
            df.drop(columns = ["Status Name", "Rule Name", "POI Original", "POI Recalc", "Odometer"], inplace = True)

        df.columns = df.columns.str.upper().str.strip()
        self.search_columns(column = df.columns.values)

        if self.status_site == 1:
            if self.search_columns("DATA INICIAL"):
                df.rename(columns = {"DATA INICIAL": "DATA"}, inplace = True)
                self.search_columns(["DATA INICIAL", "DATA"], set = True)

                try:
                    df[["DATA", "HORA"]] = df["DATA"].astype(str).apply(lambda x: pd.Series(x.strip().split(" ")))
                    self.search_columns("HORA", set = True)
                except Exception as error:
                    print(f"Erro ao dividir hora da data: {error}")

            if self.search_columns("VEÍCULO"):
                df.rename(columns = {"VEÍCULO": "TAG"}, inplace = True)
                self.search_columns(["VEÍCULO", "TAG"], set = True)

            if self.search_columns("DADOS ADICIONAIS")  and not self.search_columns("DURAÇÃO"):
                df.rename(columns = {"DADOS ADICIONAIS": "VELOCIDADE"}, inplace = True)
                self.search_columns(["DADOS ADICIONAIS", "VELOCIDADE"])

                df = df[df["DATA"].notna() & df["VELOCIDADE"].notna()]
                df["VELOCIDADE"] = df["VELOCIDADE"].astype("int16")

            elif self.search_columns("DADOS ADICIONAIS"):
                df.drop("DADOS ADICIONAIS", axis = 1, inplace = True)
                self.search_columns("DADOS ADICIONAIS", set = True)

            elif self.search_columns("DURAÇÃO"):  
                df = df[df["DATA FINAL"].notna() & df["DURAÇÃO"].notna()]

            if self.search_columns("LAT./LONG."):
                df[["LATITUDE", "LONGITUDE"]] = df["LAT./LONG."].astype(str).apply(lambda x: pd.Series(x.split(",")))
                df.drop("LAT./LONG.", axis = 1, inplace = True)
                self.search_columns(["LATITUDE", "LONGITUDE", "LAT./LONG."], set = True)

            if self.search_columns("PLACA"):
                df["PLACA"] = df["PLACA"].apply(lambda x: x.strip().upper())
                self.search_columns("PLACA", set = True)

            if self.search_columns("KM PERCORRIDA") and "FORA_DO_HORARIO_GERAL" in self.file:
                df.drop("KM PERCORRIDA", axis = 1, inplace = True)
                self.search_columns("KM PERCORRIDA", set = True)
            
        elif self.status_site == 0:
            if self.search_columns("CÓD. VIOLAÇÃO"):
                df.drop("CÓD. VIOLAÇÃO", axis = 1, inplace = True)
                self.search_columns("CÓD. VIOLAÇÃO", set = True)

            if self.search_columns("PROPRIETÁRIO"):
                df.drop("PROPRIETÁRIO", axis = 1, inplace = True)
                self.search_columns("PROPRIETÁRIO", set = True)

            if self.search_columns("MARCA/MODELO"):
                df.drop("MARCA/MODELO", axis = 1, inplace = True)
                self.search_columns("MARCA/MODELO", set = True)

            if self.search_columns("DATA DO REGISTRO"):
                df.drop("DATA DO REGISTRO", axis = 1, inplace = True)
                self.search_columns("DATA DO REGISTRO", set = True)


            if self.search_columns("CONCLUÍDO POR"):
                df.drop("CONCLUÍDO POR", axis = 1, inplace = True)
                self.search_columns("CONCLUÍDO POR", set = True)

            if self.search_columns("ALERTA"):
                df.drop("ALERTA", axis = 1, inplace = True)
                self.search_columns("ALERTA", set = True)

            if self.search_columns("PERMANÊNCIA"):
                df.drop("PERMANÊNCIA", axis = 1, inplace = True)
                self.search_columns("PERMANÊNCIA", set = True)
            
            if self.search_columns("DATA DA CONCLUSÃO"):
                df.rename(columns = {"DATA DA CONCLUSÃO": "DURAÇÃO"}, inplace = True)
                self.search_columns(["DATA DA CONCLUSÃO", "DURAÇÃO"], set = True)

            if self.search_columns("IDENTIFICAÇÃO"):
                df.rename(columns = {"IDENTIFICAÇÃO": "PLACA"}, inplace = True)
                df["PLACA"] = df["PLACA"].apply(lambda x: x.strip().upper())
                self.search_columns(["IDENTIFICAÇÃO", "PLACA"], set = True)

            if self.search_columns("LOCALIZAÇÃO"):
                df.rename(columns = {"LOCALIZAÇÃO": "ENDEREÇO"}, inplace = True)
                self.search_columns(["LOCALIZAÇÃO", "ENDEREÇO"], set = True)

            if self.search_columns("DATA DO EVENTO"):
                df.rename(columns = {"DATA DO EVENTO": "DATA"}, inplace = True)
                df[["DATA", "HORA"]] = df["DATA"].astype(str).apply(lambda x: pd.Series(x.strip().split(" ")))
                self.search_columns(["DATA DO EVENTO", "DATA", "HORA"], set = True)
        
        elif self.status_site == 2:
            df = df[~df['LOC TIME'].str.contains("Vehicle Name:|Summary", na=False)]
            if self.search_columns("LOC TIME"):
                df.rename(columns = {"LOC TIME": "DATA"}, inplace = True)
                df[["DATA", "HORA"]] = df["DATA"].astype(str).apply(lambda x: pd.Series(x.strip().split(" ")))
                self.search_columns(["LOC TIME", "DATA", "HORA"], set = True)
            
            if self.search_columns("VEHICLE NAME"):
                df.rename(columns = {"VEHICLE NAME": "TAG"}, inplace = True)
                df["TAG"] = df["TAG"].apply(lambda x: x.strip().upper())
                self.search_columns(["VEHICLE NAME", "TAG"], set = True)
            
            if self.search_columns("DRIVER NAME"):
                df.rename(columns = {"DRIVER NAME": "MOTORISTA"}, inplace = True)
                self.search_columns(["DRIVER NAME", "MOTORISTA"], set = True)

            if self.search_columns("ADDRESS"):
                df.rename(columns = {"ADDRESS": "ENDEREÇO"}, inplace = True)
                self.search_columns(["ADDRESS", "ENDEREÇO"], set = True)
            
            if self.search_columns("SPEED"):
                df.rename(columns = {"SPEED": "VELOCIDADE"}, inplace = True)
                self.search_columns(["SPEED", "VELOCIDADE"])

                df = df[df["DATA"].notna() & df["VELOCIDADE"].notna()]
                df["VELOCIDADE"] = df["VELOCIDADE"].astype("int16")

            if self.search_columns("IDLE TIME"):
                df.rename(columns = {"IDLE TIME": "DURAÇÃO"}, inplace = True)
                self.search_columns(["IDLE TIME", "DURAÇÃO"], set = True)

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
        
        if self.search_columns("TAG"):
            df["TAG"] = df["TAG"].apply(lambda x: x.upper().strip().replace(" ", ""))

        if self.search_columns("VELOCIDADE"):
            df["STATUS"] = df.apply(format_status, axis = 1)
            self.search_columns("STATUS", set = True)
            df = df[df["STATUS"] == "ALTA"]
            
        if self.search_columns("DURAÇÃO"): 
            df["TEMPO OCIOSO"] = df["DURAÇÃO"].apply(format_time)
            self.search_columns("TEMPO OCIOSO", set = True)    
            
        if self.search_columns("PLACA"):
            df["PLACA"] = df["PLACA"].apply(format_placa)

        hoje = datetime.today().date()
        data_limite = datetime(2025, 6, 30).date()

        if self.status_site == 0:
            # print("Foramtação:",self.start_date, self.end_date)
            try:
                fim = pd.to_datetime(self.end_date, dayfirst=True)
                inicio = pd.to_datetime(self.start_date, dayfirst=True)
                df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True, format= "%d/%m/%Y")  
                df = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]
                df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")

            except ValueError as e:
                print(f"Erro ao converter as datas: {e}")
        
        if "Ignition_Report" in self.file or "Movimentação Fora do Horário Permitido" in self.name:
            try:
                limite_noite_inicio_str = "20:30:00"
                limite_madrugada_fim_str = "05:30:00"
                    
                limite_noite_inicio = pd.to_datetime(limite_noite_inicio_str, format="%H:%M:%S").time()
                limite_madrugada_fim = pd.to_datetime(limite_madrugada_fim_str, format="%H:%M:%S").time()
                    
                df.loc[:, 'HORA'] = pd.to_datetime(df['HORA'], format="%H:%M:%S").dt.time

                df = df[
                    (df['HORA'] >= limite_noite_inicio) | 
                    (df['HORA'] <= limite_madrugada_fim)
                ]
                    
            except ValueError as e:
                print(f"Erro ao converter os horários: {e}")

        if "FORA_DO_HORARIO_GERAL" in self.file or "Movimentação Fora do Horário Permitido" in self.name:
            if hoje <= data_limite:
                df = df[~df["TAG"].isin([])]

            ##############---------------##############
            #          Tempo indertermindado          #
            if True:
                SEMOSP = [
                    "BT02", "BT03", "BT07",
                    "CA26", "CA70", "CA76", "CA80", "CA100", "CA104", "CA109", "CA121", "CA126", "CA130", "CA134", "CA137", "CA144",
                    "CB64", "CB72", "CB99", "CB100", "CB102", "CB129", "CB133", "CB137", "CB170", "CB173", "CB192", "CB208", "CB225",
                    "CB230", "CB235", "CB256", "CB257", "CB258", "CB264", "CB271", "CB272", "CB280", "CB283", "CB287", "CB293",
                    "CBVI02",
                    "CC10",
                    "CE18", "CE21", "CE22",
                    "CG04", "CG06", "CG08",
                    "CO18",
                    "CT44"
                ]
                
                REDUCAO = ["CA110", "CA155", "CA156", "CB119", "CT59", "CT75", "PC40", "TP22"]

                EXCETOS = SEMOSP + REDUCAO + ["CA157", "CA159"]

                df = df[~df["TAG"].isin(EXCETOS)]
            ##############---------------##############

        self.__df = df

    def connection_db(self):
        df_base = pd.read_excel(self.df_DeepWeb_path, sheet_name = "FINAL")
        df_base.drop(columns = ["Unnamed: 0"], inplace = True)
        df_base = df_base[["TAG", "MOTORISTA", "CR", "PLACA"]]
        
        self.df_DeepWeb_DATA = df_base

    def read_db(self):
        print(self.df_DeepWeb_DATA)

    def get_motoristas(self, tag):
        try:
            return self.df_DeepWeb_DATA[self.df_DeepWeb_DATA["TAG"] == tag]["MOTORISTA"].values[0].upper().strip()
        except Exception as e:
            logger.error(f"Erro ao buscar o motorista no DF: {e}")
            return None
        
    def get_CR(self, tag):
        try:
            return self.df_DeepWeb_DATA[self.df_DeepWeb_DATA["TAG"] == tag]["CR"].values[0].upper().strip()
        except Exception as e:
            logger.error(f"Erro ao buscar o CR no DF: {e}")

            return None
        
    def get_TAG(self, PLACA):
        try:
            if self.status_site:
                return self.df_DeepWeb_DATA[self.df_DeepWeb_DATA["TAG"] == PLACA]["CR"].values[0].upper().strip()
            else:
                return self.df_DeepWeb_DATA[self.df_DeepWeb_DATA["PLACA"] == PLACA]["TAG"].values[0].upper().strip()
        except Exception as e:
            logger.error(f"Erro ao buscar o CR no DF: {e}")
            return None

    def update_df(self):
        if not self.status_site:
            self.__df["TAG"] = self.__df["PLACA"].apply(self.get_TAG)

        self.__df["MOTORISTA"] = self.__df["TAG"].apply(self.get_motoristas)
        self.__df["CR"] = self.__df["TAG"].apply(self.get_CR)
        self.__df = self.__df

    def ordem_toSave(self):
        df = self.__df
        if "FORA_DO_HORARIO_GERAL" in self.file or self.name == "Movimentação Fora do Horário Permitido" or self.name == "Ignition_Report":
            self.nameToSave = "FORAHORARIO (rastreonline)" if self.status_site == 1 else "FORAHORARIO (ceabs)" if self.status_site == 0 else "FORAHORARIO (ituran)"
            df = df[["DATA", "HORA", "TAG", "MOTORISTA", "CR", "ENDEREÇO"]]
        
        if any(keyword in self.file for keyword in ["Velocidade_(Relatorio_para_robo)", "Speeding_Report"]) or self.name == "Velocidade":
            if self.status_site == 1 or self.status_site == 0:
                self.nameToSave = "VELOCIDADE (rastreonline)" if self.status_site == 1 else "VELOCIDADE (ceabs)"
            elif self.status_site == 2:
                self.nameToSave = "VELOCIDADE (ituran)"
            
            colunas = ["DATA", "HORA", "TAG", "MOTORISTA", "CR", "ENDEREÇO", "LATITUDE", "LONGITUDE", "VELOCIDADE", "STATUS"] \
                if self.status_site != 2 else ["DATA", "HORA", "TAG", "MOTORISTA", "CR", "ENDEREÇO", "VELOCIDADE", "STATUS"]
            df = df[colunas]

        if "Tempo_Ocioso" in self.file or self.status_site == 0 and "Ociosidade" in self.name or "Idle_Report" in self.name:
            self.nameToSave =  "OCIOSIDADE_12v" if "12v" in self.file else "OCIOSIDADE_24V" if self.status_site == 1 else "OCIOSIDADE (ceabs)" if self.status_site == 0 else "OCIOSIDADE (ituran)"
            
            colunas = ["DATA FINAL", "TAG", "MOTORISTA", "CR", "ENDEREÇO", "DURAÇÃO", "TEMPO OCIOSO"] if self.status_site == 1 else ["DATA", "HORA", "TAG", "MOTORISTA", "CR", "ENDEREÇO", "DURAÇÃO", "TEMPO OCIOSO"]
            df = df[colunas]

        self.__df = df

    def delete_file(self):
        try:
            if os.path.exists(self.path):
                os.remove(self.path)
                print(f"O arquivo '{self.file}' foi excluído com sucesso de: {self.download_path}")
            else:
                print(f"O arquivo '{self.file}' não foi encontrado em: {self.download_path}")
        except OSError as e:
            print(f"Erro ao tentar excluir o arquivo '{self.file}': {e}")
            
    def save(self):
        df = self.__df

        diretorio_arquivo = self.download_path
    
        caminho_excel = os.path.join(diretorio_arquivo, f"Relatorio_Formatado - {self.nameToSave}.xlsx")

        df.to_excel(caminho_excel, index=False)

    def run(self):
        self.read_file()
        self.connection_db()
        self.update_df()
        self.config_file()
        self.ordem_toSave()
        self.save()
        self.delete_file()

class Megatron(Motor):
    def __init__(self, name: str, path: str, site: str,days: int = 1, TIMEOUT: int = 60, headless: bool = True):
        super().__init__(headleass = headless)
        self.site = site
        self.name = name
        self.path = path
        self.file = None
        self.days = days
        self.start_date = None
        self.end_date = None
        self.status_login = 1 if self.site == "RASTREONLINE" else 0 if self.site == "CEABS" else 2 # ituran

        self.TIMEOUT = TIMEOUT
        self.havedata = True
        self.download_path = r"C:\Users\edeconsil\Downloads"

    def login(self):
        driver = self.inicializar()
        self.driver = driver

        print("analise de status:", self.status_login)

        if self.status_login == 1:
            driver.get("https://rastreioonline.seeflex.com.br/users/login")
            time.sleep(2)

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

        elif self.status_login == 0:
            driver.get("https://cps.ceabs.com.br/Login/")
            time.sleep(2)
            
            usuario = os.getenv("USERNAME_CEABS")
            password = os.getenv("PASSWORD_CEABS")

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
            time.sleep(1)

        elif self.status_login == 2:
            driver.get("https://iweb.ituran.com.br/iweb2/login.aspx")
            time.sleep(2)

            USERNAME = os.getenv("USERNAME_ITURAN")
            PASSWORD = os.getenv("PASWORD_ITURAN")

            print("Fazendo Login")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txt_username"))
            )
            driver.find_element(By.ID, "txt_username").send_keys(USERNAME)
            driver.find_element(By.ID, "txt_password").send_keys(PASSWORD)
            driver.find_element(By.XPATH, '//input[@type="submit"]').click()
            print("Login Feito")
            time.sleep(5)

            print("Indo por Relatórios")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "Main_ReportsandPlaybackImg"))
            )
            driver.get("https://iweb.ituran.com.br/iweb2/PeleReports/Pelereports.aspx")

    def config_relatorio(self):
        driver = self.driver
        if self.status_login == 1:
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
        
        elif self.status_login == 0:
            hoje = datetime.today()
            dias_anteriores = hoje - timedelta(days=self.days)
            if self.name == "Movimentação Fora do Horário Permitido":
                d_1 = hoje - timedelta(days = 0)
            else:
                d_1 = hoje - timedelta(days = 1) # d-1

            fim = d_1.strftime('%d/%m/%Y')  
            inicio = dias_anteriores.strftime('%d/%m/%Y')

            self.start_date = inicio
            self.end_date = fim

            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='form-group']//div[@class='chosen-group']"))
            )

            try:
                chosen_container_id = "AlertaId_chosen"
                
                chosen_container = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, chosen_container_id))
                )
                #print(f"Contêiner do Chosen.js com id='{chosen_container_id}' encontrado e clicável.")

                # Clique no contêiner para abrir o dropdown
                chosen_container.click()
                # print("Dropdown do Chosen.js clicado.")

                option_text = self.name
                chosen_option_xpath = f"//div[@id='{chosen_container_id}']//div[@class='chosen-drop']//ul[@class='chosen-results']/li[text()='{option_text}']"

                chosen_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, chosen_option_xpath))
                )

                # Clique na opção gerada pelo Chosen.js
                chosen_option.click()
                time.sleep(1) 

            except Exception as e:
                print(f"Ocorreu um erro: {e}")

            btn_days = driver.find_element(By.ID, "dtr-periodo")
            btn_days.click()

            try:
                teste = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ranges > ul > li"))
                )

                teste[3].click()  # Últimos 7 dias

            except Exception as e:
                print(f"Ocorreu um erro ao tentar encontrar os elementos: {e}")

            time.sleep(1)

            btn_exportar = driver.find_element(By.CSS_SELECTOR, ".btn.btn-info.dropdown-toggle")
            btn_exportar.click()

            btn_baixar = driver.find_element(By.ID, "btn-exportar-excel")
            print(btn_baixar.text)
            btn_baixar.click()

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@data-bb-handler="ok"]'))
                )
                button = driver.find_element(By.XPATH, '//button[@data-bb-handler="ok"]')

                if button.is_displayed():
                    print("Botão encontrado!")
                    self.havedata = False
                else:
                    print("Botão não está visível na página.")
            except:
                print("Botão não encontrado.")

        elif self.status_login == 2:
            hoje = datetime.today()
            dias_anteriores = hoje - timedelta(days=self.days)
            d_1 = hoje - timedelta(days = 1) # d-1
            
            select_element = driver.find_element(By.NAME, "SelectReportType")
            select = Select(select_element)
            if self.name == "Speeding_Report":
                select.select_by_value("4")
            elif self.name == "Idle_Report":
                select.select_by_value("9") 
            elif self.name == "Ignition_Report":
                d_1 = hoje - timedelta(days = 0)
                select.select_by_value("7") 

            fim = d_1.strftime('%d/%m/%Y')
            inicio = dias_anteriores.strftime('%d/%m/%Y')

            script_javascript = f"$('#fromInput').datepicker('setDate', '{inicio}');"
            driver.execute_script(script_javascript)
            script_javascript = f"$('#toInput').datepicker('setDate', '{fim}');"
            driver.execute_script(script_javascript)

            hora_desejada = '23:59:59'
            script_javascript = f"$('#end_time').val('{hora_desejada}');"
            driver.execute_script(script_javascript)

            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.NAME, "SelectReportParameter"))
            )
            select_element = driver.find_element(By.NAME, "SelectReportParameter")
            select = Select(select_element)
            if self.name == "Speeding_Report":
                select.select_by_value("85")
            elif self.name == "Idle_Report":
                select.select_by_value("15.00") 
            
            driver.find_element(By.XPATH, "//a[@href='#tab-3']").click()
            time.sleep(2)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fancytree-checkbox"))
            ).click()
            time.sleep(2)                     

            driver.find_element(By.XPATH, "//a[@href='#tab-9']").click()

            driver.find_element(By.ID, "reportButton").click()

            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Ok' and not(contains(@class, 'hidden'))]"))
            )
            element.click()

            print("Clicando em exportar")
            btn_export = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@id='exportButton' and text()='Export']"))
            )

            if btn_export:
                print(btn_export.text)
                btn_export.click()
                print("btn clicador")

            try:
                btn_ok = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@id='ModalWizard_OkButton_0']"))
                )

                btn_ok.click()
            except:
                print("Erro ao baixar o relatório")

        if self.havedata: 
            self.download_file()
        driver.quit()

    def download_file(self):
        timeout = self.TIMEOUT
        
        name_temp = self.name
        if not self.status_login:
            self.name = "Relatorio_Alertas_Violacoes_"

        for _ in range(timeout):
            arquivo = self.search_file()
            if arquivo:
                print(f"Download concluído: {arquivo}")
                self.file = arquivo
                self.name = name_temp
                break
            time.sleep(1)
        else:
            self.name = name_temp
            print("⚠️ Tempo esgotado. Arquivo não encontrado.")
    
    def search_file(self):
        for filename in os.listdir(self.download_path):
                if self.name in filename and not filename.endswith('.crdownload'):

                    return filename
        return None
    
    def adjust_data(self):
        if self.havedata:
            file = Armadura(self.file, name = self.name, status_site = self.status_login, start_date = self.start_date, end_date = self.end_date)
            file.run()
        else:
            print("Nenhum aquivo baixado")

    def run(self):
        self.login()
        print("Erro está por aqui: v")
        self.config_relatorio()
        print("Erro está por aqui: ^")
        self.adjust_data()

BASES = {
    "SITES": {
        "RASTREONLINE": [
            ("Velocidade_(Relatorio_para_robo)", "/relatorios/print?alias=CUSTOMIZADO&id=384"), 
            ("Tempo_Ocioso_veiculos_de_12v", "/relatorios/print?alias=CUSTOMIZADO&id=218"),
            ("Tempo_Ocioso_veiculos_de_24v", "/relatorios/print?alias=CUSTOMIZADO&id=389"),
            ("FORA_DO_HORARIO_GERAL", "/relatorios/print?alias=CUSTOMIZADO&id=375")
        ],
        "CEABS": [
            ("Movimentação Fora do Horário Permitido", 0),
            ("Velocidade", 0),
            ("Ociosidade ", 0)
        ],
        "ITURAN": [
            ("Speeding_Report", 0),
            ("Idle_Report", 0),
            ("Ignition_Report", 0)
        ]
    }
}

for site, relatorios in BASES["SITES"].items():
    if site:
        for name, path in relatorios:
            if name:
                try:
                    bot = Megatron(site = site, name = name, path = path, days = 1, headless = True)
                    bot.run()
                except Exception as e:
                    print(f"Erro ao fazer a busca do arquivo {name}. Erro: {e}")
