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

# Leer el archivo Excel y crear el diccionario de datos
nombre_archivo_excel = './cuentaspotify.xlsx'
da = pd.read_excel(nombre_archivo_excel)
diccionario_datos = da.set_index('correo')['contraseña'].to_dict()

# Configuración del servicio de Chrome y listas para almacenar los webdrivers
chrome_service = ChromeService(ChromeDriverManager().install())
webdrivers = []

for usuario, clave in diccionario_datos.items():
    try:
        # Iniciar WebDriver
        driver = webdriver.Chrome(service=chrome_service)
        webdrivers.append(driver)

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
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="onetrust-close-btn-container"]'))).click()
            print("Clic en el botón 'cookies'")
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
            print("El botón 'cookies' no es interactuable")

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//Button[@aria-label="Cerrar"]'))).click()
            print("Clic en el botón 'pestaña emergente'")
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
            print("No se encontró el botón 'pestaña emergente'")

        # Ejemplo de iteración y acciones sobre elementos de lista (aquí debes ajustar según la estructura de Spotify)
        # Esto es un ejemplo básico para demostración
        list_items = driver.find_elements(By.XPATH, '//li[@role="listitem"]')

        for index, item in enumerate(list_items):
            # Aquí puedes realizar acciones como context_click, click, etc.
            actions = ActionChains(driver)
            actions.context_click(item).perform()
            
            # Ejemplo de manejo de opciones en el menú contextual (ajustar según lo que necesites hacer)
            try:
                span_element = driver.find_element(By.XPATH, '//span[@data-encore-id="type" and (contains(text(),"Quitar de Tu biblioteca") or contains(text(),"Dejar de seguir") or contains(text(),"Eliminar de Tu biblioteca"))]')
                span_element.click()

                eliminar = driver.find_element(By.XPATH, '//span[contains(text(),"Eliminar")]').click()
                time.sleep(0.5)
            except NoSuchElementException:
                print("Elemento no encontrado: Quitar de Tu biblioteca, Dejar de seguir, o Eliminar de Tu biblioteca")

    except Exception as e:
        print(f"Error en el usuario {usuario}: {e}")

    finally:
        # Cerrar el navegador después de cada iteración
        if driver:
            driver.quit()

# Cerrar el servicio de Chrome al finalizar
chrome_service.stop()
