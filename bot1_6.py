import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time
import random
import names
from selenium.webdriver.common.keys import Keys
from selenium_authenticated_proxy import SeleniumAuthenticatedProxy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import tempfile

# VERSÃO 1.5 TUALIZADO O METODO DE ABERTURA DE PROXY SEM USUARIO E ATUALIZAÇÃO AUTOMATICA DA LISTA DE USUARIOS CRIADOS E ALGUMAS MODIFICAÇÕES VISUAIS
# VERSÃO 1.6 FOI CORRIGIDO O BUG DE ATUALIZAR A LISTA E NÃO ABRIR O USUARIO 

temp_dir = os.path.join(tempfile.gettempdir(), "selenium_authenticated_proxy", "tmp")
os.makedirs(temp_dir, exist_ok=True)


# Caminho para a pasta onde o chromedriver está
ROOT_FOLDER = Path(__file__).parent
CHROME_DRIVER_PATH = Path("C:/Users/Eduardo/Desktop/bot/drivers/chrome_proxy.exe")
REPORT_FILE = ROOT_FOLDER / 'relatorio.txt'
TIME_TO_WAIT = 5

def create_report_file(report_file):
    """Cria o arquivo de relatório se ele não existir."""
    if not report_file.exists():
        # Cria a pasta _internal se ela não existir
        report_file.parent.mkdir(parents=True, exist_ok=True)
        # Cria o arquivo relatorio.txt
        report_file.touch()
        print(f"Arquivo {report_file} criado.")
    else:
        print(f"Arquivo {report_file} já existe.")


def create_driver_with_proxy(proxy, port, username, password):
    """Cria uma instância do navegador com proxy autenticado."""
    chrome_options = Options()
    chrome_options.add_argument("--force-webrtc-ip-handling-policy=default_public_interface_only")
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--mute-audio")

    preferences = {
    "webrtc.ip_handling_policy" : "disable_non_proxied_udp",
    "webrtc.multiple_routes_enabled": False,
    "webrtc.nonproxied_udp_enabled" : False
    }
    chrome_options.add_experimental_option("prefs", preferences)

    proxy_helper = SeleniumAuthenticatedProxy(proxy_url=f"http://{username}:{password}@{proxy}:{port}")
    proxy_helper.enrich_chrome_options(chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def generate_random_nick():
    """Gera um nick aleatório."""
    return names.get_first_name() + str(random.randint(100, 999))

def gerar_telefone():
    ddd = random.randint(11, 99)  # DDD aleatório entre 11 e 99
    primeiro_digito = 9  # O primeiro dígito é 9 para celulares no Brasil
    restante = "".join([str(random.randint(0, 9)) for _ in range(7)])  # 7 dígitos aleatórios
    telefone = f"({ddd}) {primeiro_digito}{restante[:4]}-{restante[4:]}"
    return telefone

def create_user_bkp(driver, user_link, user_password, proxy):
    """Preenche o formulário de criação de usuário automaticamente e salva no relatório."""

    # Número máximo de tentativas
    MAX_ATTEMPTS = 5
    attempt = 0

    while attempt < MAX_ATTEMPTS:
        try:
            # Tenta acessar a página de criação de usuário
            driver.get(user_link)
            time.sleep(3
            )  # Espera fixa (melhor usar esperas explícitas)

            # Gera um nick aleatório
            random_nick = generate_random_nick()
            random_name = names.get_full_name()
            random_tel = gerar_telefone()
            meu_cpf = '49307549842'

            # Tenta encontrar o campo de nome de usuário
            username_field = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'username') or contains(@class, 'usernameInput') or contains(@class,'login-register-account-input')]//input"))
            )
            username_field.send_keys(random_nick)
            username_field.send_keys(Keys.TAB)
            time.sleep(1)

            driver.switch_to.active_element.send_keys(user_password)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(user_password)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(random_tel)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(random_name)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.ENTER)
            time.sleep(2)

            # Esperar até que o elemento <div> com a classe 'registerSuccess-btn-QPIyr' esteja clicável
            deposit_now = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'registerSuccess-btn-QPIyr')]"))
            )
            deposit_now.click()       
            value_deposit = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.visibility_of_element_located((By.XPATH, "//input[contains(@class, 'ant-input')]"))
            )     
            value_deposit.send_keys('30')   
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(meu_cpf)      

            # Salva o usuário gerado no relatório
            with open(REPORT_FILE, 'a') as file:
                file.write(f"CONTA PERFIL: {random_nick} / {user_password} / {proxy}\n")

            print(f"Usuário {random_nick} criado com sucesso!")
            return  # Sai da função se o usuário foi criado com sucesso

        except Exception as e:
            attempt += 1
            print(f"Erro ao criar usuário na tentativa {attempt}: {e}")
            if attempt < MAX_ATTEMPTS:
                print(f"Tentando novamente (tentativa {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(3)  # Aguardar um tempo antes de tentar novamente
            else:
                print(f"Falha ao criar usuário após {MAX_ATTEMPTS} tentativas.")
                # Pode salvar alguma informação adicional no relatório se necessário
                with open(REPORT_FILE, 'a') as file:
                    file.write(f"FALHA AO CRIAR USUÁRIO APÓS {MAX_ATTEMPTS} TENTATIVAS: {proxy}\n")

def create_user_bkp2(driver, user_link, user_password, proxy):
    """Preenche o formulário de criação de usuário automaticamente e salva no relatório."""

    # Número máximo de tentativas
    MAX_ATTEMPTS = 5
    attempt = 0
    meu_cpf = '49307549842'

    while attempt < MAX_ATTEMPTS:
        try:
            # Tenta acessar a página de criação de usuário
            driver.get(user_link)
            time.sleep(3
            )  # Espera fixa (melhor usar esperas explícitas)

            # Gera um nick aleatório
            random_nick = generate_random_nick()
            random_name = names.get_full_name()
            random_tel = gerar_telefone()

            # Tenta encontrar o campo de nome de usuário
            username_field = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'username') or contains(@class, 'usernameInput') or contains(@class,'login-register-account-input')]//input"))
            )
            username_field.send_keys(random_nick)
            username_field.send_keys(Keys.TAB)
            time.sleep(1)

            driver.switch_to.active_element.send_keys(user_password)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(user_password)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(random_tel)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(random_name)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.ENTER)
            time.sleep(2)

            # Esperar até que o elemento <div> com a classe 'registerSuccess-btn-QPIyr' esteja clicável
            deposit_now = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'registerSuccess-btn-QPIyr')]"))
            )
            deposit_now.click()       
            value_deposit = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.visibility_of_element_located((By.XPATH, "//input[contains(@class, 'ant-input')]"))
            )     
            value_deposit.send_keys('30')     
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(meu_cpf)             

            # Salva o usuário gerado no relatório
            with open(REPORT_FILE, 'a') as file:
                file.write(f"CONTA PERFIL: {random_nick} / {user_password} / {proxy}\n")

            print(f"Usuário {random_nick} criado com sucesso!")
            return  # Sai da função se o usuário foi criado com sucesso

        except Exception as e:
            attempt += 1
            print(f"Erro ao criar usuário na tentativa {attempt}: {e}")
            if attempt < MAX_ATTEMPTS:
                print(f"Tentando novamente (tentativa {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(3)  # Aguardar um tempo antes de tentar novamente
            else:
                print(f"Falha ao criar usuário após {MAX_ATTEMPTS} tentativas.")
                # Pode salvar alguma informação adicional no relatório se necessário
                with open(REPORT_FILE, 'a') as file:
                    file.write(f"FALHA AO CRIAR USUÁRIO APÓS {MAX_ATTEMPTS} TENTATIVAS: {proxy}\n")

def create_user(driver, user_link, user_password, proxy):
    """Preenche o formulário de criação de usuário automaticamente e salva no relatório."""

    # Número máximo de tentativas
    MAX_ATTEMPTS = 5
    attempt = 0
    cpf = generate_cpf()

    while attempt < MAX_ATTEMPTS:
        try:
            # Tenta acessar a página de criação de usuário
            driver.get(user_link)
            time.sleep(3
            )  # Espera fixa (melhor usar esperas explícitas)

            # Gera um nick aleatório
            random_nick = generate_random_nick()
            random_name = names.get_full_name()
            random_tel = gerar_telefone()

            # Tenta encontrar o campo de nome de usuário
            username_field = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'username') or contains(@class, 'usernameInput') or contains(@class,'login-register-account-input')]//input"))
            )
            username_field.send_keys(random_nick)
            username_field.send_keys(Keys.TAB)
            time.sleep(1)

            driver.switch_to.active_element.send_keys(user_password)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(user_password)
            driver.switch_to.active_element.send_keys(Keys.TAB)           
            # driver.switch_to.active_element.send_keys(Keys.TAB)          
            # driver.switch_to.active_element.send_keys(random_tel)            
            # driver.switch_to.active_element.send_keys(Keys.TAB) 
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(random_name)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.ENTER)
            time.sleep(2)

            # Salva o usuário gerado no relatório
            with open(REPORT_FILE, 'a') as file:
                file.write(f"CONTA PERFIL: {random_nick} / {user_password} / {proxy}\n")

            
            time.sleep(2)

            # # Esperar até que o elemento <div> com a classe 'registerSuccess-btn-QPIyr' esteja clicável
            # deposit_now = WebDriverWait(driver, TIME_TO_WAIT).until(
            #     EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'registerSuccess-btn-QPIyr')]"))
            # )
            # deposit_now.click()       
            # value_deposit = WebDriverWait(driver, TIME_TO_WAIT).until(
            #     EC.visibility_of_element_located((By.XPATH, "//input[contains(@class, 'ant-input')]"))
            # )     
            # value_deposit.send_keys('30')                
            # driver.switch_to.active_element.send_keys(Keys.TAB)
            # driver.switch_to.active_element.send_keys(cpf)    
                       
            print(f"Usuário {random_nick} criado com sucesso!")
            return  # Sai da função se o usuário foi criado com sucesso
        

            

        except Exception as e:
            attempt += 1
            print(f"Erro ao criar usuário na tentativa {attempt}: {e}")
            if attempt < MAX_ATTEMPTS:
                print(f"Tentando novamente (tentativa {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(3)  # Aguardar um tempo antes de tentar novamente
            else:
                print(f"Falha ao criar usuário após {MAX_ATTEMPTS} tentativas.")
                # Pode salvar alguma informação adicional no relatório se necessário
                with open(REPORT_FILE, 'a') as file:
                    file.write(f"FALHA AO CRIAR USUÁRIO APÓS {MAX_ATTEMPTS} TENTATIVAS: {proxy}\n")


def just_open_browser_with_proxy(driver, userlink):
    """Abre o link do usuário e tenta encontrar um elemento específico na página."""
    MAX_ATTEMPTS = 5  # Número máximo de tentativas
    attempt = 0  # Contador de tentativas

    while attempt < MAX_ATTEMPTS:
        try:
            # Tenta abrir o link do usuário
            driver.get(userlink)
            time.sleep(3)  # Aguarda o carregamento da página

            # Aqui você pode verificar se o elemento que você está esperando está presente
            # Por exemplo, se você espera que um campo de login apareça
            # username_field = WebDriverWait(driver, TIME_TO_WAIT).until(
            #     EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'username') or contains(@class,'login-register-account-input')]//input"))
            # )
            print(f"A página {userlink} foi aberta e o elemento foi encontrado com sucesso.")
            return  # Se o elemento foi encontrado, sai da função

        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou: {e}")
            attempt += 1
            print("Atualizando a página...")
            time.sleep(2)  # Atraso antes de atualizar a página

    print(f"Não foi possível encontrar o elemento após {MAX_ATTEMPTS} tentativas.")


def login_user(driver, user_link, username_login, password_login):
    """Faz o login automaticamente utilizando os dados do relatório."""
    # Número máximo de tentativas
    MAX_ATTEMPTS = 5
    attempt = 0

    while attempt < MAX_ATTEMPTS:
        try:
            # Tenta acessar a página de login
            driver.get(user_link)
            time.sleep(3)  # Espera fixa (melhor usar esperas explícitas)

            # Tenta encontrar o campo de login
            # "van-tabs-6-1" 
            login_field = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "van-tabs-9-1" or 'loginTabButton'))
            )
            login_field.click()    
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(username_login)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(password_login)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            time.sleep(1)
            driver.switch_to.active_element.send_keys(Keys.ENTER)          

            # Insere a senha
            
            print(f"Usuário {username_login} logado com sucesso!")  # Corrigido para usar username_login
            return  # Sai da função se o login foi bem-sucedido

        except Exception as e:
            attempt += 1
            print(f"Erro ao fazer login na tentativa {attempt}: {e}")
            if attempt < MAX_ATTEMPTS:
                print(f"Tentando novamente (tentativa {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(5)  # Aguardar um tempo antes de tentar novamente
            else:
                print(f"Falha ao fazer login após {MAX_ATTEMPTS} tentativas.")

def login_user_backup(driver, user_link, username_login, password_login):
    """Faz o login automaticamente utilizando os dados do relatório."""
    # Número máximo de tentativas
    MAX_ATTEMPTS = 5
    attempt = 0

    while attempt < MAX_ATTEMPTS:
        try:
            # Tenta acessar a página de login
            driver.get(user_link)
            time.sleep(3)  # Espera fixa (melhor usar esperas explícitas)

            # Tenta encontrar o campo de login
            login_field = WebDriverWait(driver, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "van-tabs-6-1" or 'loginTabButton'))
            )
            login_field.click()    
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(username_login)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            driver.switch_to.active_element.send_keys(password_login)
            driver.switch_to.active_element.send_keys(Keys.TAB)
            time.sleep(1)
            driver.switch_to.active_element.send_keys(Keys.ENTER)          

            # Insere a senha
            
            print(f"Usuário {username_login} logado com sucesso!")  # Corrigido para usar username_login
            return  # Sai da função se o login foi bem-sucedido

        except Exception as e:
            attempt += 1
            print(f"Erro ao fazer login na tentativa {attempt}: {e}")
            if attempt < MAX_ATTEMPTS:
                print(f"Tentando novamente (tentativa {attempt + 1}/{MAX_ATTEMPTS})...")
                time.sleep(5)  # Aguardar um tempo antes de tentar novamente
            else:
                print(f"Falha ao fazer login após {MAX_ATTEMPTS} tentativas.")



def browse_with_proxy(proxy, user_link, user_password):
    """Navega utilizando o proxy fornecido e abre o link informado pelo usuário."""
    try:
        proxy_host, proxy_port, username, password = extract_proxy_info(proxy)
        driver = create_driver_with_proxy(proxy_host, proxy_port, username, password)
        # check_ip(driver)
        create_user(driver, user_link, user_password, proxy)

    except Exception as e:
        print(f'Ocorreu um erro ao abrir o navegador com proxy {proxy}: {e}')
    finally:
        input("Pressione Enter para fechar o navegador...")

def browse_with_proxy_login(proxy, user_link, username_login, password_login):
    """Navega utilizando o proxy fornecido e abre o link informado pelo usuário, sem criação de usuário."""
    try:
        proxy_host, proxy_port, username, password = extract_proxy_info(proxy)
        driver = create_driver_with_proxy(proxy_host, proxy_port, username, password)
        login_user(driver, user_link, username_login, password_login)  # Agora passa todos os parâmetros corretos

    except Exception as e:
        print(f'Ocorreu um erro ao abrir o navegador com proxy {proxy}: {e}')
    finally:
        input("Pressione Enter para fechar o navegador...")

def browser_just_open(proxy, user_link):
    """Navega utilizando o proxy fornecido e abre o link informado pelo usuário, sem criação de usuário."""  
    try:
        proxy_host, proxy_port, username, password = extract_proxy_info(proxy)
        driver = create_driver_with_proxy(proxy_host, proxy_port, username, password)
        just_open_browser_with_proxy(driver, user_link)  # Abre o link do usuário

    except Exception as e:
        print(f'Ocorreu um erro ao abrir o navegador com proxy1 {proxy}: {e}')
    finally:
        input("Pressione Enter para fechar o navegador...")

def just_open_browser(proxies, user_link):
    """Inicia a navegação em diferentes proxies com threads, apenas para abrir sites."""
    threads = []
    for proxy in proxies:
        thread = threading.Thread(target=browser_just_open, args=(proxy, user_link))
        threads.append(thread)
        thread.start()
        time.sleep(2)

def extract_proxy_info(proxy):
    """Extrai e retorna informações de um proxy no formato 'host:port:username:password'."""
    proxy_parts = proxy.split(":")
    return proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]

def start_browsing_with_proxies(proxies, user_link, user_password):
    """Inicia a navegação em diferentes proxies com threads."""
    threads = []
    for proxy in proxies:
        thread = threading.Thread(target=browse_with_proxy, args=(proxy, user_link, user_password))
        threads.append(thread)
        thread.start()
        time.sleep(2)

def start_browsing_with_proxies_login(proxies, user_link, username_login, password_login):
    """Inicia a navegação em diferentes proxies com threads, apenas para abrir sites."""
    threads = []
    for proxy in proxies:
        thread = threading.Thread(target=browser_just_open, args=(proxy, user_link))
        threads.append(thread)
        thread.start()
        time.sleep(2)


def check_password_match(password_input, confirm_password_input, label):
    """Verifica se a senha e a confirmação correspondem e atualiza a interface."""
    password = password_input.get().strip()
    confirm_password = confirm_password_input.get().strip()

    if password != confirm_password:
        label.config(text="Senhas não coincidem", fg="red")
    else:
        label.config(text="Senhas coincidem", fg="green")

def on_start_click(proxies_input, link_input, password_input, confirm_password_input, label):
    """Callback quando o botão 'Iniciar' é clicado para criar usuário."""
    proxies_text = proxies_input.get("1.0", tk.END).strip()
    proxies = proxies_text.split("\n")
    
    user_link = link_input.get().strip()
    user_password = password_input.get().strip()
    confirm_password = confirm_password_input.get().strip()

    # Verifica se as senhas coincidem
    if user_password != confirm_password:
        messagebox.showwarning("Aviso", "As senhas não coincidem.")
        return

    if len(proxies) < 1:
        messagebox.showwarning("Aviso", "Por favor, insira ao menos 1 proxy.")
    elif not user_link:
        messagebox.showwarning("Aviso", "Por favor, insira o link.")
    elif not user_password:
        messagebox.showwarning("Aviso", "Por favor, insira a senha.")
    else:
        threading.Thread(target=start_browsing_with_proxies, args=(proxies, user_link, user_password)).start()


def on_user_double_click(event, users, listbox, link_input):
    """Chama a função ao dar um duplo clique em um usuário da lista."""
    widget = event.widget
    index = widget.curselection()  # Pega o índice do item selecionado
    if index:  # Verifica se algum item está selecionado
        index = index[0]  # Pega o primeiro índice da seleção
        selected_user = users[index]

        user, password, proxy = selected_user
        user_link = link_input.get().strip()  # Pega o valor do link

        if not user_link:
            messagebox.showwarning("Aviso", "Por favor, insira o link.")
            return

        print(f"Selecionado: {user}, {password}, {proxy}, Link: {user_link}")

        # Abre o navegador com as credenciais selecionadas em uma nova thread
        threading.Thread(target=browse_with_proxy_login, args=(proxy, user_link, user, password)).start()

        # Pintar o item de azul para indicar que foi aberto
        listbox.itemconfig(index, {'bg': 'lightblue'})

def on_start_click_just_open(proxies_input, link_input):
    """Callback quando o botão 'Iniciar' é clicado para abrir navegador com proxy."""
    proxies_text = proxies_input.get("1.0", tk.END).strip()
    proxies = proxies_text.split("\n")
    
    user_link = link_input.get().strip()    

    if len(proxies) < 1:
        messagebox.showwarning("Aviso", "Por favor, insira ao menos 1 proxy.")
    elif not user_link:
        messagebox.showwarning("Aviso", "Por favor, insira o link.")    
    else:
        threading.Thread(target=just_open_browser, args=(proxies, user_link)).start()

def generate_cpf():
    """Gera um CPF válido no formato XXX.XXX.XXX-XX"""
    
    # Gera os primeiros 9 dígitos aleatoriamente
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcula o primeiro dígito verificador
    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
        cpf.append(0 if val < 2 else 11 - val)
    
    # Formata o CPF como XXX.XXX.XXX-XX
    cpf_str = ''.join(map(str, cpf))
    formatted_cpf = f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"
    
    return formatted_cpf

def show_generated_cpf(cpf_entry): 
    """Gera um CPF e exibe no campo de entrada com o texto todo selecionado."""
    cpf = generate_cpf()
    cpf_entry.delete(0, tk.END)  # Limpa o campo de entrada
    cpf_entry.insert(0, cpf)      # Insere o CPF gerado
    cpf_entry.select_range(0, tk.END)  # Seleciona todo o texto

def load_users_from_report(report_file):
    """Carrega o relatório de usuários e retorna uma lista de tuplas (usuário, senha, proxy)."""
    users = []
    
    if not os.path.exists(report_file):
        messagebox.showerror("Erro", f"O arquivo {report_file} não foi encontrado.")
        return users
    
    # Tentar abrir o arquivo com a codificação utf-8
    try:
        with open(report_file, 'r', encoding='utf-8') as file:
            for line in file:
                if "CONTA PERFIL:" in line:
                    parts = line.strip().split(" / ")
                    if len(parts) == 3:
                        user = parts[0].replace("CONTA PERFIL: ", "")
                        password = parts[1]
                        proxy = parts[2]
                        users.append((user, password, proxy))
    except UnicodeDecodeError:
        # Se ocorrer um erro de codificação, tentar com ISO-8859-1 (latin1)
        try:
            with open(report_file, 'r', encoding='ISO-8859-1') as file:
                for line in file:
                    if "CONTA PERFIL:" in line:
                        parts = line.strip().split(" / ")
                        if len(parts) == 3:
                            user = parts[0].replace("CONTA PERFIL: ", "")
                            password = parts[1]
                            proxy = parts[2]
                            users.append((user, password, proxy))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo {report_file}: {str(e)}")
    
    return users

def update_users(user_listbox, report_file, last_modified_time_var):
    """Atualiza a lista de usuários se o arquivo foi modificado."""
    current_modified_time = os.path.getmtime(report_file)
    if current_modified_time != last_modified_time_var[0]:
        last_modified_time_var[0] = current_modified_time
        users = load_users_from_report(report_file)
        user_listbox.delete(0, tk.END)  # Limpa a lista existente na interface
        for user, password, proxy in users:
            user_listbox.insert(tk.END, f"{user} / {password} / {proxy}")        

    # Chama a função novamente após 5 segundos
    user_listbox.after(5000, update_users, user_listbox, report_file, last_modified_time_var)

def on_user_double_click(event, report_file, listbox, link_input):
    """Chama a função ao dar um duplo clique em um usuário da lista."""
    # Recarrega a lista de usuários do arquivo
    users = load_users_from_report(str(report_file))  # Converte para string se for um Path

    widget = event.widget
    index = widget.curselection()  # Pega o índice do item selecionado
    if index:  # Verifica se algum item está selecionado
        index = index[0]  # Pega o primeiro índice da seleção

        try:
            selected_user = users[index]
            user, password, proxy = selected_user
            user_link = link_input.get().strip()  # Pega o valor do link

            # Debug: Imprime o valor do link
            print(f"Link digitado: '{user_link}'")

            if not user_link:
                messagebox.showwarning("Aviso", "Por favor, insira o link.")
                return

            print(f"Selecionado: {user}, {password}, {proxy}, Link: {user_link}")

            # Abre o navegador com as credenciais selecionadas em uma nova thread
            threading.Thread(target=browse_with_proxy_login, args=(proxy, user_link, user, password)).start()

            # Pintar o item de azul para indicar que foi aberto
            listbox.itemconfig(index, {'bg': 'lightblue'})

        except IndexError:
            messagebox.showwarning("Aviso", "O índice selecionado está fora do alcance da lista de usuários.")
    else:
        messagebox.showwarning("Aviso", "Nenhum usuário foi selecionado.")

def create_gui(report_file):
    """Cria a interface gráfica para inserir proxies, o link e a senha, e iniciar o navegador."""
    root = tk.Tk()
    root.title("Navegação com Proxy - brslot777")    
    last_modified_time_var = [0]

    # Cria um notebook para as abas
    notebook = ttk.Notebook(root)

    # Carregar usuários do relatório
    users = load_users_from_report(report_file)
    
    # Aba 1 - Lista de usuários
    aba1 = ttk.Frame(notebook)
    notebook.add(aba1, text="Usuários com Proxy")

    # Botão para atualizar a lista de usuários
    update_button = tk.Button(aba1, text="Atualizar Usuários", command=lambda: update_users(listbox, report_file, last_modified_time_var))
    update_button.pack(pady=10)

    # Frame para conter Listbox e Scrollbar
    listbox_frame = tk.Frame(aba1)
    listbox_frame.pack(pady=10)

    # Scrollbar
    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Criar a lista (Listbox)
    listbox = tk.Listbox(listbox_frame, height=20, width=80, yscrollcommand=scrollbar.set)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    # Configurar a Scrollbar para rolar a Listbox
    scrollbar.config(command=listbox.yview)

    instruction_label3 = tk.Label(aba1, text=('Insira o link da casa'))
    instruction_label3.pack(pady=5)

    link_input3 = tk.Entry(aba1, width=50)
    link_input3.pack(pady=5)

    # Adicionar os usuários na lista
    for user, password, proxy in users:
        listbox.insert(tk.END, f"{user} / {password} / {proxy}")

    # Adicionar callback ao clicar na lista
    listbox.bind("<Double-Button-1>", lambda event: on_user_double_click(event, report_file, listbox, link_input3))

    # Aba 2 - Abrir proxies e criar usuários
    aba2 = ttk.Frame(notebook)
    notebook.add(aba2, text="Criar Usuários com Proxies")

    instruction_label2 = tk.Label(aba2, text="Insira os proxies (um por linha):")
    instruction_label2.pack(pady=10)

    proxies_input2 = tk.Text(aba2, height=10, width=50)
    proxies_input2.pack(pady=10)

    link_label2 = tk.Label(aba2, text="Insira o link para abrir ou link conta main:")
    link_label2.pack(pady=10)

    link_input2 = tk.Entry(aba2, width=50)
    link_input2.pack(pady=10)

    password_label = tk.Label(aba2, text="Insira a senha para o usuário:")
    password_label.pack(pady=10)

    password_input = tk.Entry(aba2, show='*', width=50)
    password_input.pack(pady=10)

    password_label = tk.Label(aba2, text="Confirme sua senha:")
    password_label.pack(pady=5)

    confirm_password = tk.Entry(aba2, show='*', width=50)
    confirm_password.pack(pady=5)

    password_match_label = tk.Label(root, text="")
    password_match_label.pack()

    start_button2 = tk.Button(aba2, text="Criar Usuário com Proxy", command=lambda: on_start_click(proxies_input2, link_input2, password_input, confirm_password, password_match_label))
    start_button2.pack(pady=10)

    aba4 = ttk.Frame(notebook)
    notebook.add(aba4, text='Apenas abrir navegador com proxy')

    instruction_label1 = tk.Label(aba4, text="Insira os proxies (um por linha):")
    instruction_label1.pack(pady=10)

    proxies_input1 = tk.Text(aba4, height=10, width=50)
    proxies_input1.pack(pady=10)
    
    link_label1 = tk.Label(aba4, text="Insira o link para abrir:")
    link_label1.pack(pady=10)

    link_input1 = tk.Entry(aba4, width=50)
    link_input1.pack(pady=10)

    start_button1 = tk.Button(aba4, text="Abrir Navegador com Proxy", command=lambda: on_start_click_just_open(proxies_input1, link_input1))
    start_button1.pack(pady=10)
  
    #Aba gerador de CPF
    aba_cpf = ttk.Frame(notebook)
    notebook.add(aba_cpf, text="Gerador de CPF")

    cpf_entry = tk.Entry(aba_cpf, width=27, font=('Arial', 14))
    cpf_entry.pack(pady=10)

    generate_button = tk.Button(aba_cpf, text="Gerar CPF", command=lambda: show_generated_cpf(cpf_entry))
    generate_button.pack(pady=10)


    notebook.pack(expand=1, fill="both")   
    root.mainloop()

if __name__ == "__main__":
    create_report_file(REPORT_FILE)
    create_gui(REPORT_FILE)
