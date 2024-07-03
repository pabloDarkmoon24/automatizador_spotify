from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

resultados = []
webdrivers = []
cantidad_artistas = 0

# Leer el archivo Excel y crear el diccionario de datos
nombre_archivo_excel = './cuentaspotify.xlsx'
da = pd.read_excel(nombre_archivo_excel)
diccionario_datos = da.set_index('correo')['contraseña'].to_dict()

for usuario, clave in diccionario_datos.items():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    driver.get('https://accounts.spotify.com/es-ES/login?continue=https%3A%2F%2Fopen.spotify.com%2Fintl-es')
    driver.implicitly_wait(6)

    # Iniciar sesión
    search_mail = driver.find_element(By.XPATH, '//*[@id="login-username"]')
    search_password = driver.find_element(By.XPATH, '//*[@id="login-password"]')
    search_ingresar = driver.find_element(By.XPATH, '//*[@id="login-button"]')

    search_mail.send_keys(usuario)
    search_password.send_keys(clave)
    search_ingresar.click()

    # Manejo de cookies y posibles pop-ups
    try:
        botton_cookies = driver.find_element(By.XPATH, '//div[@id="onetrust-close-btn-container"]')
        botton_cookies.click()
    except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
        print("El botón 'cookies' no es interactuable")

    try:
        botton_cookies = driver.find_element(By.XPATH, '//Button[@aria-label="Cerrar"]')
        botton_cookies.click()
        print("Clic en el botón 'pestaña emergente'")
    except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
        print("No se encontró el botón 'pestaña emergente'")

    # Obtener todos los elementos <li> con role="listitem"
    list_items = driver.find_elements(By.XPATH, '//li[@role="listitem"]')

    # Cuenta el número de elementos
    count = len(list_items)
    print(f"Número de elementos <li> con role='listitem': {count}")

    index = 1
    while count> 2:
        try:
            # Encontrar las listas 
            list_items = driver.find_elements(By.XPATH, '//li[@role="listitem"]')
            item = list_items[index]
            actions = ActionChains(driver)
            actions.context_click(item).perform()
            
            try:
                #validar si esta la opcion de de eliminar la lista o el megusta
                span_element = driver.find_element(By.XPATH, '//span[@data-encore-id="type" and (contains(text(),"Quitar de Tu biblioteca") or contains(text(),"Dejar de seguir") or contains(text(),"Eliminar de Tu biblioteca"))]')
                span_element.click()

                eliminar = driver.find_element(By.XPATH, '//span[contains(text(),"Eliminar")]').click()
                time.sleep(0.5)
            except NoSuchElementException:

                try:
                    
                    span_element_likes = driver.find_element(By.XPATH, '//span[text()="Desanclar playlist"]')
                    actions.context_click(item).perform()
                    item.click()
                    input("paremos")
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "div")))
                    song_rows = driver.find_elements(By.CSS_SELECTOR, "div[role='row']")

                    print(len(song_rows))
    
                except NoSuchElementException:    
                    print("Elemento no encontrado: Quitar de Tu biblioteca, Dejar de seguir, o Eliminar de Tu biblioteca")
                
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException) as e:
            print(f"No se pudo hacer clic derecho en el elemento {index}: {e}")
            break

        list_items = driver.find_elements(By.XPATH, '//li[@role="listitem"]')
        count = len(list_items)
        print(index, count)

    input("vamos bien")  # Mantiene el script en pausa para verificación manual

    # Cerrar el navegador después de cada iteración
driver.quit()