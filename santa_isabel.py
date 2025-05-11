from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
import re
import json

def obtener_productos(nombre_producto):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    browser = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(browser, 10)
    url = f'https://www.santaisabel.cl/busqueda?ft={nombre_producto}'
    browser.get(url)

    productos_resultado = []  # lista de json

    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "page-number")))
        paginador = browser.find_elements(By.CLASS_NAME, "page-number")       
        paginas = []
        for el in paginador:
            texto = el.text.strip()
            if re.match(r'^\d+$', texto):  # Solo números enteros
                paginas.append(int(texto))

        print(f"Páginas disponibles encontradas: {paginas}")

        if paginas:
            paginas_continuas = list(range(min(paginas), max(paginas) + 1))
            print(f"Páginas continuas: {paginas_continuas}")
        else:
            paginas_continuas = []

        for pagina in paginas_continuas:
            print(f"Accediendo a la página {pagina}...")
            
            if pagina > 1:
                url_pagina = f'https://www.santaisabel.cl/busqueda?ft={nombre_producto}&page={pagina}'
                browser.get(url_pagina)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-card-name")))

            #nombres de productos
            productos = browser.find_elements(By.CLASS_NAME, "product-card-name")

            #precios
            precios = browser.find_elements(By.CLASS_NAME, 'prices-main-price')

            #imagenes
            imagenes = browser.find_elements(By.CLASS_NAME, "lazy-image")
            for i in range(min(len(productos), len(precios), len(imagenes))):
                try:
                    nombre = productos[i].text.strip()
                    if nombre_producto.lower() in nombre.lower():  # ver si nombre del producto contiene el nombre
                        precio = precios[i].text.strip()
                        imagen = imagenes[i].get_attribute("src").strip()
                        producto_info = {
                            "nombre": nombre,
                            "precio": precio,
                            "imagen": imagen
                        }
                        productos_resultado.append(producto_info)
                except StaleElementReferenceException:
                    print("elemento actualizado, cuidado")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    time.sleep(2)
    browser.quit()
    return json.dumps(productos_resultado, ensure_ascii=False, indent=4)

resultado_json = obtener_productos("pan")
print(resultado_json)