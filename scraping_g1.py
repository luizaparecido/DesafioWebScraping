from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Configurando o driver do Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Acessando a página inicial do G1
    driver.get('https://g1.globo.com/')
    
    # Localizando a barra de pesquisa e enviando o termo "inteligência artificial"
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="q"]'))
    )
    search_box.send_keys('inteligência artificial')
    search_box.send_keys(Keys.RETURN)

    # Esperando os resultados carregarem
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.widget.widget--card.widget--info'))
    )

    # Rolar a página para carregar mais notícias
    last_height = driver.execute_script("return document.body.scrollHeight")
    noticias_coletadas = set()

    while True:
        # Captura as notícias visíveis na página
        noticias = driver.find_elements(By.CSS_SELECTOR, 'li.widget.widget--card.widget--info')

        # Se encontrou novas notícias, processa e salva
        if noticias:
            for noticia in noticias:
                try:
                    # Extraindo o título
                    titulo_element = noticia.find_element(By.CSS_SELECTOR, '.widget--info__title')
                    titulo = titulo_element.text.strip()

                    # Extraindo a data (buscando pela data mais precisa)
                    try:
                        data_element = noticia.find_element(By.CSS_SELECTOR, '.widget--info__meta')
                        data = data_element.text.strip()
                    except Exception as e:
                        data = "Data não disponível"
                        print(f"Erro ao capturar data: {e}")

                    # Verificar se a notícia já foi coletada
                    noticia_info = (titulo, data)
                    if noticia_info not in noticias_coletadas:
                        noticias_coletadas.add(noticia_info)
                        
                        # Salvando no arquivo
                        with open('noticias_inteligencia_artificial.txt', 'a', encoding='utf-8') as file:
                            file.write(f"Título: {titulo}\n")
                            file.write(f"Data de Publicação: {data}\n")
                            file.write("-" * 50 + "\n")

                        print(f"Título: {titulo}")
                        print(f"Data de Publicação: {data}")
                        print("-" * 50)
                except Exception as e:
                    print(f"Erro ao processar uma notícia: {e}")

        # Rolar para baixo para carregar mais resultados
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Espera o conteúdo carregar

        # Verifica a altura da página após rolar
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Se a altura não mudou, significa que não há mais conteúdo a ser carregado
            break
        last_height = new_height

finally:
    # Fechando o navegador
    driver.quit()
