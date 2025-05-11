from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
import re
import json

def obtener_productos_general(nombre_producto, sitio):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(browser, 10)

    if sitio == "unimarc":
        base_url = f"https://www.unimarc.cl/search?q={nombre_producto}"
        page_param = "&page="
        selectores = {
            "paginador": "Text_text--black__zYYxI",
            "producto_nombre": "Shelf_nameProduct__CXI5M",
            "producto_precio": "Text_text--primary__OoK0C",
            "producto_imagen": "Shelf_defaultImgStyle__ylyx2"
        }
    elif sitio == "santa_isabel":
        base_url = f"https://www.santaisabel.cl/busqueda?ft={nombre_producto}"
        page_param = "&page="
        selectores = {
            "paginador": "page-number",
            "producto_nombre": "product-card-name",
            "producto_precio": "prices-main-price",
            "producto_imagen": "lazy-image"
        }
    else:
        raise ValueError("Sitio no soportado")

    browser.get(base_url)
    productos_resultado = []

    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selectores["paginador"])))
        paginador = browser.find_elements(By.CLASS_NAME, selectores["paginador"])
        paginas = [int(el.text.strip()) for el in paginador if re.match(r'^\d+$', el.text.strip())]
        paginas_continuas = list(range(min(paginas), max(paginas)+1)) if paginas else [1]

        for pagina in paginas_continuas:
            print(f"Accediendo a página {pagina}...")

            if pagina > 1:
                browser.get(base_url + page_param + str(pagina))
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, selectores["producto_nombre"])))

            nombres = browser.find_elements(By.CLASS_NAME, selectores["producto_nombre"])
            precios = browser.find_elements(By.CLASS_NAME, selectores["producto_precio"])
            imagenes = browser.find_elements(By.CLASS_NAME, selectores["producto_imagen"])

            for i in range(min(len(nombres), len(precios), len(imagenes))):
                try:
                    nombre = nombres[i].text.strip()
                    if nombre_producto.lower() in nombre.lower():
                        precio = precios[i].text.strip()
                        imagen = imagenes[i].get_attribute("src").strip()
                        productos_resultado.append({
                            "nombre": nombre,
                            "precio": precio,
                            "imagen": imagen
                        })
                except StaleElementReferenceException:
                    print("Elemento actualizado, se omitió uno")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2)
    browser.quit()
    return json.dumps(productos_resultado, ensure_ascii=False, indent=4)

print(obtener_productos_general("pan", "unimarc"))
print(obtener_productos_general("pan", "santa_isabel"))

