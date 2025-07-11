import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

# Constantes de User-Agent (podría ser configurable en el futuro)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def get_login_url(moodle_base_url):
    """Construye la URL de login a partir de la URL base de Moodle."""
    return urljoin(moodle_base_url, "login/index.php")

def login(moodle_base_url, username, password, session):
    """
    Intenta iniciar sesión en la plataforma Moodle.
    Actualiza el objeto session con las cookies si el login es exitoso.

    Args:
        moodle_base_url: La URL base del sitio Moodle (ej. "https://campus.example.com").
        username: El nombre de usuario.
        password: La contraseña.
        session: Un objeto requests.Session.

    Returns:
        True si el inicio de sesión fue exitoso, False en caso contrario.
    """
    login_url = get_login_url(moodle_base_url)
    session.headers.update({'User-Agent': USER_AGENT})

    try:
        # GET inicial a la página de login para obtener el logintoken
        login_page_response = session.get(login_url, timeout=10)
        login_page_response.raise_for_status()
        soup = BeautifulSoup(login_page_response.text, 'html.parser')

        logintoken_input = soup.find('input', {'name': 'logintoken'})
        if not logintoken_input:
            print(f"ADVERTENCIA: No se encontró logintoken en {login_url}. Intentando sin él.")
            logintoken = None
        else:
            logintoken = logintoken_input['value']
            print(f"Logintoken encontrado: {logintoken}")

        payload = {
            'username': username,
            'password': password,
            'rememberusername': 1,
        }
        if logintoken:
            payload['logintoken'] = logintoken

        # Enviar la petición POST para iniciar sesión
        response = session.post(login_url, data=payload, timeout=10)
        response.raise_for_status()

        # Verificar si el inicio de sesión fue exitoso
        # Criterio 1: No estamos más en la página de login
        if "login/index.php" in response.url:
            soup_response = BeautifulSoup(response.text, 'html.parser')
            error_message_div = soup_response.find('div', {'class': 'loginerrors'})
            if error_message_div:
                error_text = error_message_div.get_text(strip=True)
                print(f"Error de inicio de sesión (detectado en página): {error_text}")
            else:
                # Buscar errores más genéricos si loginerrors no está
                feedback_error = soup_response.find('div', {'id': 'loginerrormessage'}) # Moodle 4.x
                if feedback_error:
                     print(f"Error de inicio de sesión (feedback): {feedback_error.get_text(strip=True)}")
                else:
                     print("Error de inicio de sesión: credenciales incorrectas o problema desconocido (permanece en login).")
            return False

        # Criterio 2: Buscar un enlace de logout o el menú de usuario en la página resultante
        # Esto es más robusto que solo chequear la URL.
        soup_response = BeautifulSoup(response.text, 'html.parser')

        # Intentar varios selectores comunes para el enlace de logout o el menú de usuario
        # Selector para Moodle 3.x y anteriores (aproximado)
        logout_link_old = soup_response.find('a', href=lambda href: href and 'logout.php' in href)
        # Selector para Moodle 4.x (el menú de usuario es un div con data-region="usermenu")
        user_menu_m4 = soup_response.find('div', {'data-region': 'usermenu'})
        # Otro indicador podría ser el nombre del usuario en algún lugar prominente
        user_fullname_span = soup_response.find('span', class_='userfullname')

        if logout_link_old or user_menu_m4 or user_fullname_span:
            print("Inicio de sesión exitoso.")
            return True
        else:
            # Si no estamos en login/index.php pero tampoco vemos indicadores de sesión exitosa
            print("Inicio de sesión posiblemente fallido (no se encontraron indicadores claros de sesión activa post-login).")
            # Podrías guardar response.text aquí para depurar qué página se cargó si esto ocurre.
            # with open("debug_post_login_page.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return False

    except requests.exceptions.Timeout:
        print(f"Error de Timeout durante el inicio de sesión en {login_url}.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP durante el inicio de sesión: {e}")
        return False
    except Exception as e:
        print(f"Ocurrió un error inesperado durante el inicio de sesión: {e}")
        # import traceback
        # traceback.print_exc()
        return False

def get_my_courses_url(moodle_base_url):
    """Construye la URL de la página 'Mis cursos'."""
    return urljoin(moodle_base_url, "my/")

def get_active_courses(moodle_base_url, session):
    """
    Navega a la página de listado de cursos y extrae los cursos activos.
    IMPORTANTE: Los selectores HTML aquí son genéricos y probablemente
    necesiten ser ajustados para una instancia específica de Moodle.

    Args:
        moodle_base_url: La URL base del sitio Moodle.
        session: Un objeto requests.Session con una sesión de Moodle activa.

    Returns:
        Un diccionario con los nombres de los cursos como clave y sus URLs absolutas como valor,
        o un diccionario vacío si no se encuentran cursos o hay un error.
    """
    my_courses_url = get_my_courses_url(moodle_base_url)
    courses = {}
    print(f"CLIENT_DEBUG: Accediendo a la página de cursos en: {my_courses_url}")

    try:
        response = session.get(my_courses_url, timeout=10)
        response.raise_for_status()
        # Guardar HTML para depuración de selectores (descomentar si es necesario)
        # with open("debug_my_courses_page.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)
        # print("CLIENT_DEBUG: HTML de 'Mis Cursos' guardado en debug_my_courses_page.html")

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- INICIO DE LÓGICA DE SELECTORES DE CURSOS (MUY PROPENSA A CAMBIOS) ---
        # Intento 1: Selector común en Moodle 4.x para bloques de cursos en el dashboard
        # Estos elementos suelen tener un data-courseid y un enlace dentro.
        # Buscamos dentro de 'div[data-region="main-content-blocks"]' o similar si es posible acotar.
        # O un selector más general primero.

        # Selector para Moodle 4.x (tarjetas de curso en el dashboard)
        # class="card dashboard-card" o similar, con un enlace que contiene el courseid
        course_cards = soup.select('div[data-region="paged-content-page"] div.dashboard-card, div.card.course-item') # Combinando posibles selectores

        print(f"CLIENT_DEBUG: Encontrados {len(course_cards)} elementos con selectores de tarjeta de curso.")

        if course_cards:
            for card in course_cards:
                link_tag = card.find('a', href=lambda href: href and "course/view.php?id=" in href)
                if link_tag:
                    course_url = link_tag['href']
                    course_name_tag = card.find(['h4', 'h5', 'span'], class_=lambda c: c and ('course-title' in c or 'multiline' in c)) # Clases comunes para títulos
                    if not course_name_tag : # Fallback si no encuentra esas clases
                         course_name_tag = link_tag.find(['span', 'div'], recursive=False) # Texto directo dentro del enlace

                    course_name = course_name_tag.get_text(strip=True) if course_name_tag else "Curso sin nombre"

                    if "course/view.php?id=" in course_url and course_name:
                        # Asegurar URL absoluta
                        abs_course_url = urljoin(moodle_base_url, course_url)
                        courses[course_name] = abs_course_url
                        print(f"  CLIENT_DEBUG: Curso (tarjeta): '{course_name}' - URL: {abs_course_url}")

        # Intento 2: Selectores más antiguos o alternativos si el primero falla o es incompleto
        if not courses: # Solo si el método anterior no encontró nada
            print("CLIENT_DEBUG: Método de tarjetas de curso no encontró nada, intentando selectores alternativos.")
            # Este selector es de Moodle 4.x para el bloque "Course overview"
            course_list_items = soup.select('div[data-region="course-overview"] a[data-courseid][href*="course/view.php"]')
            print(f"CLIENT_DEBUG: Encontrados {len(course_list_items)} elementos con selector 'course-overview'.")
            for link_el in course_list_items:
                course_url = link_el['href']
                # El nombre suele estar dentro de un span.instancename o directamente en el texto del enlace
                name_span = link_el.find('span', class_='instancename')
                course_name = name_span.get_text(strip=True) if name_span else link_el.get_text(strip=True)

                if course_name and "course/view.php?id=" in course_url:
                    abs_course_url = urljoin(moodle_base_url, course_url)
                    if course_name not in courses or courses[course_name] != abs_course_url : # Evitar sobrescribir si un nombre es igual pero url distinta (raro)
                        courses[course_name] = abs_course_url
                        print(f"  CLIENT_DEBUG: Curso (overview): '{course_name}' - URL: {abs_course_url}")

        # Intento 3: El selector 'coursebox' más antiguo
        if not courses:
            print("CLIENT_DEBUG: Aún sin cursos, intentando selector 'coursebox'.")
            coursebox_elements = soup.find_all('div', class_=lambda x: x and 'coursebox' in x and 'future' not in x and 'past' not in x)
            print(f"CLIENT_DEBUG: Encontrados {len(coursebox_elements)} con selector 'coursebox'.")
            for course_el in coursebox_elements:
                title_el = course_el.find(['h3', 'h4'], class_='coursename')
                link_el = title_el.find('a', href=True) if title_el else None
                if not link_el: link_el = course_el.find('a', href=True) # A veces el coursebox es el enlace

                if link_el and title_el:
                    course_name = title_el.get_text(strip=True)
                    course_url = link_el['href']
                    if "course/view.php?id=" in course_url and course_name:
                        abs_course_url = urljoin(moodle_base_url, course_url)
                        courses[course_name] = abs_course_url
                        print(f"  CLIENT_DEBUG: Curso (coursebox): '{course_name}' - URL: {abs_course_url}")
        # --- FIN DE LÓGICA DE SELECTORES DE CURSOS ---

        if not courses:
            print("CLIENT_DEBUG: No se encontraron cursos utilizando los selectores conocidos.")

    except requests.exceptions.Timeout:
        print(f"Error de Timeout al acceder a {my_courses_url}.")
    except requests.exceptions.RequestException as e:
        print(f"CLIENT_DEBUG: Error de red o HTTP al acceder a la página de cursos: {e}")
    except Exception as e:
        print(f"CLIENT_DEBUG: Ocurrió un error inesperado al obtener los cursos: {e}")
        # import traceback
        # traceback.print_exc()
    return courses

def get_course_documents(course_url, session, moodle_base_url):
    """
    Navega a la página de un curso y extrae enlaces a documentos.
    IMPORTANTE: Los selectores HTML aquí son genéricos y probablemente
    necesiten ser ajustados para una instancia específica de Moodle.

    Args:
        course_url: La URL absoluta de la página principal del curso.
        session: Un objeto requests.Session con una sesión de Moodle activa.
        moodle_base_url: La URL base del sitio Moodle (para resolver URLs relativas).

    Returns:
        Una lista de diccionarios, donde cada diccionario contiene:
        {'name': nombre_del_documento, 'url': url_absoluta_del_documento, 'type': tipo_de_documento}
        o una lista vacía si no se encuentran documentos o hay un error.
    """
    documents = []
    doc_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar', '.odt', '.odp', '.ods', '.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.avi', '.mkv']

    print(f"CLIENT_DEBUG: Accediendo a la página del curso: {course_url}")
    try:
        response = session.get(course_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Guardar HTML para depuración de selectores de documentos (descomentar si es necesario)
        # course_id_match = re.search(r'id=(\d+)', course_url)
        # course_id = course_id_match.group(1) if course_id_match else "unknown_course"
        # with open(f"debug_course_page_{course_id}.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)
        # print(f"CLIENT_DEBUG: HTML de página de curso guardado en debug_course_page_{course_id}.html")

        # Buscar enlaces de actividad (módulos de Moodle)
        # Selectores comunes para módulos: 'activityinstance' o enlaces con 'mod/' en href
        activity_links = soup.select('li.activity a.aalink[href*="/mod/"], div.activityinstance a[href*="/mod/"], a.aalink[href*="/pluginfile.php/"]')

        # También buscar enlaces directos a archivos en la página del curso (menos común que estén sueltos)
        direct_links = soup.find_all('a', href=True)

        all_potential_links = list(set(activity_links + direct_links)) # Usar set para eliminar duplicados de elementos 'a'
        processed_resource_urls = set() # Para evitar procesar la misma URL de recurso/folder varias veces

        print(f"CLIENT_DEBUG: Encontrados {len(all_potential_links)} enlaces potenciales en la página del curso.")

        for link_el in all_potential_links:
            href = link_el.get('href')
            if not href:
                continue

            # Nombre del recurso/documento
            instance_name_span = link_el.find('span', class_='instancename')
            link_text = instance_name_span.get_text(strip=True) if instance_name_span else link_el.get_text(strip=True)
            if not link_text: link_text = link_el.get('title', "Documento sin nombre")
            link_text = link_text.strip()
            if not link_text: link_text = "Documento sin nombre"


            abs_link_url = urljoin(moodle_base_url, href)

            # 1. Enlaces directos a documentos (por extensión en la URL del enlace)
            is_direct_document_by_ext = any(abs_link_url.lower().endswith(ext) for ext in doc_extensions)
            if is_direct_document_by_ext:
                doc_type = abs_link_url.split('.')[-1].lower()
                if not any(d['url'] == abs_link_url for d in documents): # Evitar duplicados estrictos por URL
                    documents.append({'name': link_text, 'url': abs_link_url, 'type': doc_type})
                    print(f"  CLIENT_DEBUG: [Directo] '{link_text}' ({doc_type}) - {abs_link_url}")
                continue # Ya lo procesamos

            # 2. Enlaces a módulos de Moodle (resource, folder, url)
            # Módulo "resource" (Archivo): puede ser descarga directa o página intermedia
            if '/resource/view.php' in href:
                if abs_link_url in processed_resource_urls: continue
                processed_resource_urls.add(abs_link_url)
                print(f"  CLIENT_DEBUG: [*] Recurso Moodle: {link_text} ({abs_link_url})")
                try:
                    # Acceder a la página del recurso, permitir redirecciones
                    res_page = session.get(abs_link_url, timeout=10, allow_redirects=True)
                    res_page.raise_for_status()
                    final_url = res_page.url # URL después de redirecciones

                    # Verificar si la URL final es un archivo descargable por extensión
                    if any(final_url.lower().endswith(ext) for ext in doc_extensions):
                        doc_type = final_url.split('.')[-1].lower()
                        if not any(d['url'] == final_url for d in documents):
                            documents.append({'name': link_text, 'url': final_url, 'type': doc_type}) # Usar link_text original
                            print(f"    CLIENT_DEBUG: [+] (Recurso-Redir) '{link_text}' ({doc_type}) - {final_url}")
                    else:
                        # Si no es un archivo directo por URL, buscar en el contenido de la página del recurso
                        res_soup = BeautifulSoup(res_page.text, 'html.parser')
                        # Moodle a veces tiene un div.resourceworkaround o un enlace directo en el 'main'
                        resource_main_content = res_soup.find('div', role='main')
                        if not resource_main_content: resource_main_content = res_soup

                        found_in_page = False
                        # Buscar un enlace que apunte a un archivo dentro de esta página de recurso
                        for potential_doc_link in resource_main_content.find_all('a', href=True):
                            p_href = potential_doc_link['href']
                            p_abs_href = urljoin(moodle_base_url, p_href)
                            if any(p_abs_href.lower().endswith(ext) for ext in doc_extensions):
                                p_doc_type = p_abs_href.split('.')[-1].lower()
                                p_name = potential_doc_link.get_text(strip=True) or link_text
                                if not any(d['url'] == p_abs_href for d in documents):
                                    documents.append({'name': p_name, 'url': p_abs_href, 'type': p_doc_type})
                                    print(f"    CLIENT_DEBUG: [+] (Recurso-Pág) '{p_name}' ({p_doc_type}) - {p_abs_href}")
                                    found_in_page = True
                                    break # Suponemos un solo archivo principal
                        if not found_in_page:
                             print(f"    CLIENT_DEBUG: [!] No se pudo extraer doc de pág. recurso: {abs_link_url}")
                except requests.exceptions.RequestException as e_res:
                    print(f"    CLIENT_DEBUG: [!] Error accediendo a recurso {abs_link_url}: {e_res}")
                except Exception as e_detail:
                    print(f"    CLIENT_DEBUG: [!] Error procesando detalle recurso {abs_link_url}: {e_detail}")

            # Módulo "folder" (Carpeta)
            elif '/folder/view.php' in href:
                if abs_link_url in processed_resource_urls: continue
                processed_resource_urls.add(abs_link_url)
                print(f"  CLIENT_DEBUG: [*] Carpeta Moodle: {link_text} ({abs_link_url})")
                try:
                    folder_page = session.get(abs_link_url, timeout=10)
                    folder_page.raise_for_status()
                    folder_soup = BeautifulSoup(folder_page.text, 'html.parser')
                    # Enlaces a archivos dentro de carpetas suelen usar pluginfile.php
                    for file_link_el in folder_soup.select('span.fp-filename a[href*="pluginfile.php"]'):
                        f_href = file_link_el['href']
                        f_abs_href = urljoin(moodle_base_url, f_href)
                        f_name = file_link_el.get_text(strip=True)
                        if f_href and f_name:
                            f_doc_type = f_abs_href.split('.')[-1].lower() if '.' in f_abs_href else 'archivo'
                            # Mejorar tipo si no tiene extensión clara
                            if f_doc_type == 'archivo' or len(f_doc_type) > 5 : # si la extensión es 'archivo' o muy larga/rara
                                for known_ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']: # Comunes
                                    if known_ext.replace('.', '') in f_name.lower():
                                        f_doc_type = known_ext.replace('.', '')
                                        break
                            if not any(d['url'] == f_abs_href for d in documents):
                                documents.append({'name': f_name, 'url': f_abs_href, 'type': f_doc_type})
                                print(f"    CLIENT_DEBUG: [+] (Carpeta) '{f_name}' ({f_doc_type}) - {f_abs_href}")
                except requests.exceptions.RequestException as e_folder:
                    print(f"    CLIENT_DEBUG: [!] Error accediendo a carpeta {abs_link_url}: {e_folder}")
                except Exception as e_detail:
                    print(f"    CLIENT_DEBUG: [!] Error procesando detalle carpeta {abs_link_url}: {e_detail}")

            # Enlaces directos a pluginfile.php (a veces son PDFs de tareas o foros)
            elif '/pluginfile.php/' in href:
                # Estos enlaces ya suelen ser descargas directas o abren en el navegador
                # Es importante obtener el nombre del archivo de la URL si es posible, o del texto del enlace
                # Ejemplo: .../pluginfile.php/12345/mod_resource/content/1/MiArchivo.pdf
                filename_from_url = href.split('/')[-1] # Toma la última parte de la URL
                # Quitar query params si los hay
                filename_from_url = filename_from_url.split('?')[0]

                if any(filename_from_url.lower().endswith(ext) for ext in doc_extensions):
                    doc_type = filename_from_url.split('.')[-1].lower()
                    # El link_text del 'a' tag es probablemente más descriptivo que el nombre de archivo de la URL
                    descriptive_name = link_text if link_text != "Documento sin nombre" else filename_from_url
                    if not any(d['url'] == abs_link_url for d in documents):
                        documents.append({'name': descriptive_name, 'url': abs_link_url, 'type': doc_type})
                        print(f"  CLIENT_DEBUG: [Pluginfile Directo] '{descriptive_name}' ({doc_type}) - {abs_link_url}")

        if not documents:
            print(f"CLIENT_DEBUG: No se encontraron documentos con los criterios actuales en el curso.")

    except requests.exceptions.Timeout:
        print(f"Error de Timeout al acceder a la página del curso {course_url}.")
    except requests.exceptions.RequestException as e:
        print(f"CLIENT_DEBUG: Error de red o HTTP al acceder a la página del curso {course_url}: {e}")
    except Exception as e:
        print(f"CLIENT_DEBUG: Ocurrió un error inesperado al analizar el curso {course_url}: {e}")
        # import traceback
        # traceback.print_exc()
    return documents

def sanitize_filename(name):
    """Sanitiza un string para ser usado como nombre de archivo o carpeta."""
    if not isinstance(name, str):
        name = str(name)
    # Eliminar caracteres no válidos para la mayoría de los FS
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name) # Incluye caracteres de control
    # Reducir espacios múltiples a uno solo y quitar de los extremos
    name = re.sub(r'\s+', ' ', name).strip()
    # Evitar nombres reservados o problemáticos en Windows
    reserved_names = {"CON", "PRN", "AUX", "NUL",
                      "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                      "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if name.upper() in reserved_names:
        name = "_" + name + "_"
    # Evitar que el nombre sea solo puntos o termine con punto o espacio (problemático en Windows)
    if re.match(r'^\.+$', name): # Si es solo uno o más puntos
        name = "archivo_descargado"
    name = name.rstrip('. ') # Quitar puntos o espacios al final
    if not name: # Si después de todo queda vacío
        name = "archivo_descargado"
    # Limitar longitud (opcional, pero bueno para compatibilidad)
    return name[:150]

# Ejemplo de uso (para pruebas directas de este módulo, si es necesario)
if __name__ == '__main__':
    print("Módulo moodle_client.py (no diseñado para ejecución directa sin un caso de prueba específico)")
    # Aquí podrías añadir código para probar funciones individualmente si lo deseas.
    # Ejemplo:
    # test_session = requests.Session()
    # test_moodle_url = "URL_DE_PRUEBA_MOODLE"
    # logged_in = login(test_moodle_url, "tu_usuario", "tu_contraseña", test_session)
    # if logged_in:
    #     print("Login de prueba exitoso.")
    #     active_courses = get_active_courses(test_moodle_url, test_session)
    #     print("Cursos activos:", active_courses)
    #     if active_courses:
    #         first_course_name = list(active_courses.keys())[0]
    #         first_course_url = active_courses[first_course_name]
    #         docs = get_course_documents(first_course_url, test_session, test_moodle_url)
    #         print(f"Documentos en '{first_course_name}':", docs)
    # else:
    #     print("Login de prueba fallido.")
    pass
