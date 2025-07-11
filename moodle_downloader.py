import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://campus2025.unahur.edu.ar/login/index.php"
BASE_URL = "https://campus2025.unahur.edu.ar"

def login(session, username, password):
    """
    Intenta iniciar sesión en la plataforma Moodle.

    Args:
        session: Un objeto requests.Session para mantener la sesión.
        username: El nombre de usuario.
        password: La contraseña.

    Returns:
        True si el inicio de sesión fue exitoso (o parece serlo), False en caso contrario.
    """
    try:
        # Primero, obtener el logintoken
        login_page_response = session.get(LOGIN_URL)
        login_page_response.raise_for_status()
        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        logintoken_input = soup.find('input', {'name': 'logintoken'})

        if not logintoken_input:
            print("No se pudo encontrar el logintoken en la página de inicio de sesión.")
            # Intentar iniciar sesión sin logintoken si no se encuentra (puede ser necesario en algunas versiones de Moodle)
            payload = {
                'username': username,
                'password': password,
                'rememberusername': 1, # Para simular el comportamiento del navegador
            }
        else:
            logintoken = logintoken_input['value']
            payload = {
                'username': username,
                'password': password,
                'logintoken': logintoken,
                'rememberusername': 1, # Para simular el comportamiento del navegador
            }

        # Enviar la petición POST para iniciar sesión
        response = session.post(LOGIN_URL, data=payload)
        response.raise_for_status() # Lanza una excepción para códigos de error HTTP

        # Verificar si el inicio de sesión fue exitoso
        # Una forma común es verificar si la URL cambió a la página principal o si aparece el nombre del usuario.
        # O si ya no vemos elementos típicos de la página de login.
        if "login/index.php" in response.url: # Si seguimos en la página de login, probablemente falló
            soup_response = BeautifulSoup(response.text, 'html.parser')
            error_message = soup_response.find('div', {'class': 'loginerrors'})
            if error_message:
                print(f"Error de inicio de sesión: {error_message.get_text(strip=True)}")
            else:
                print("Error de inicio de sesión: credenciales incorrectas o problema desconocido.")
            return False

        # Otra verificación: buscar un enlace de "Cerrar sesión" o el nombre del usuario,
        # que usualmente indica una sesión activa.
        # Esto es más robusto que solo chequear la URL.
        soup_response = BeautifulSoup(response.text, 'html.parser')
        logout_link = soup_response.find('a', href=lambda href: href and 'logout.php' in href)
        user_menu = soup_response.find('div', class_='usermenu')

        if logout_link or user_menu:
            print("Inicio de sesión exitoso.")
            return True
        else:
            # Si no estamos en login/index.php pero tampoco vemos indicadores de sesión exitosa
            print("Inicio de sesión posiblemente fallido (no se encontraron indicadores de sesión activa).")
            # Puedes imprimir parte del contenido para depurar qué página se cargó:
            # print(response.text[:1000])
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP durante el inicio de sesión: {e}")
        return False
    except Exception as e:
        print(f"Ocurrió un error inesperado durante el inicio de sesión: {e}")
        return False

if __name__ == '__main__':
    # Crear una sesión para mantener las cookies
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    user_username = input("Introduce tu nombre de usuario de Moodle: ")
    user_password = input("Introduce tu contraseña de Moodle: ")

    if login(s, user_username, user_password):
        print("Procediendo con las siguientes etapas...")
        # Aquí irían las llamadas a las funciones para listar cursos, etc.
    else:
        print("No se pudo iniciar sesión. Revisa tus credenciales o la conexión.")

    if login(s, user_username, user_password):
        print("Procediendo con las siguientes etapas...")
        courses = get_active_courses(s)
        if courses:
            print("\nCursos encontrados:")
            all_documents = {} # Almacenará {course_name: [{doc_name: doc_url}, ...]}
            for name, url in courses.items():
                print(f"\nAnalizando curso: {name} ({url})")
                documents_in_course = find_document_links_in_course(s, url, name)
                if documents_in_course:
                    all_documents[name] = documents_in_course
                    print(f"  Documentos encontrados en '{name}':")
                    for doc_info in documents_in_course:
                        print(f"    - {doc_info['name']}: {doc_info['url']}")
                else:
                    print(f"  No se encontraron documentos en '{name}'.")

            # Presentar documentos y permitir selección
            selected_documents_for_download = []
            if all_documents:
                print("\n--- Documentos Encontrados ---")
                doc_counter = 1
                # Mapeo para que el usuario pueda seleccionar por número
                selectable_docs_map = {}

                for course_name_sorted in sorted(all_documents.keys()): # Ordenar cursos alfabéticamente
                    docs = all_documents[course_name_sorted]
                    if not docs: continue
                    print(f"\nCurso: {course_name_sorted}")
                    # Ordenar documentos dentro de cada curso por nombre
                    sorted_docs_in_course = sorted(docs, key=lambda x: x['name'])
                    for doc_info in sorted_docs_in_course:
                        print(f"  [{doc_counter}] {doc_info['name']} ({doc_info['type']})")
                        selectable_docs_map[doc_counter] = doc_info
                        doc_counter += 1

                if not selectable_docs_map:
                    print("\nNo se encontró ningún documento descargable en los cursos analizados.")
                else:
                    print("\n--- Selección de Documentos ---")
                    print("Introduce los números de los documentos que deseas descargar, separados por comas (ej: 1,3,5) o 'todos' para descargar todos.")
                    user_choice = input("> ")

                    if user_choice.strip().lower() == 'todos':
                        selected_documents_for_download = list(selectable_docs_map.values())
                    else:
                        try:
                            chosen_numbers = [int(n.strip()) for n in user_choice.split(',')]
                            for num in chosen_numbers:
                                if num in selectable_docs_map:
                                    selected_documents_for_download.append(selectable_docs_map[num])
                                else:
                                    print(f"Advertencia: El número {num} no es válido y será ignorado.")
                        except ValueError:
                            print("Entrada no válida. No se descargarán documentos.")

                    if selected_documents_for_download:
                        print("\nDocumentos seleccionados para descargar:")
                        for doc_info in selected_documents_for_download:
                            print(f"- {doc_info['name']} ({doc_info['type']}) del curso '{doc_info['course']}'")
                        print("\n--- Iniciando Descarga ---")
                        download_selected_documents(s, selected_documents_for_download)
                        print("\n--- Descarga Finalizada ---")
                    else:
                        print("No se seleccionó ningún documento para descargar.")
            else:
                print("\nNo se encontró ningún documento en ningún curso.")

        else:
            print("No se encontraron cursos o hubo un error al recuperarlos.")
    else:
        print("No se pudo iniciar sesión. Revisa tus credenciales o la conexión.")

def find_document_links_in_course(session, course_url, course_name):
    """
    Navega a la página de un curso y extrae enlaces a documentos.

    Args:
        session: Un objeto requests.Session con una sesión de Moodle activa.
        course_url: La URL de la página principal del curso.
        course_name: El nombre del curso (para referencia).

    Returns:
        Una lista de diccionarios, donde cada diccionario contiene:
        {'name': nombre_del_documento, 'url': url_del_documento, 'type': tipo_de_documento (ej. 'pdf', 'docx')}
        o una lista vacía si no se encuentran documentos o hay un error.
    """
    documents = []
    # Tipos de archivo comunes a buscar (extensiones)
    doc_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar', '.odt', '.odp', '.ods']
    # Tipos de recursos de Moodle que suelen enlazar directamente a archivos o a páginas que los contienen
    # modtype_resource = Archivo, modtype_folder = Carpeta, modtype_url = URL externa
    activity_selectors = "a.aalink[href*='/resource/view.php'], a.aalink[href*='/folder/view.php'], a.aalink[href*='/url/view.php']"


    try:
        print(f"  Accediendo a la página del curso: {course_url}")
        response = session.get(course_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar todos los enlaces de actividad que podrían contener documentos
        activity_links = soup.select(activity_selectors)

        # También buscar enlaces directos a archivos en la página del curso
        direct_links = soup.find_all('a', href=True)

        # Combinar y procesar enlaces
        # Usamos un set para URLs para evitar procesar la misma URL varias veces si es capturada por múltiples selectores
        processed_urls = set()

        print(f"  Encontrados {len(activity_links)} enlaces de actividad y {len(direct_links)} enlaces directos.")

        for link_el in activity_links + direct_links:
            href = link_el.get('href')
            if not href or href in processed_urls:
                continue

            processed_urls.add(href)

            # Priorizar span.instancename si existe, es común en Moodle para nombres de actividad
            span_instance_name = link_el.find('span', class_='instancename')
            if span_instance_name:
                link_text = span_instance_name.get_text(strip=True)
            else:
                # Si no hay instancename, tomar todo el texto del enlace.
                link_text = link_el.get_text(separator=' ', strip=True)

            if not link_text:
                 # Si sigue vacío, intentar con el atributo title, a veces está ahí
                 link_text = link_el.get('title', '').strip()

            if not link_text: # Último recurso
                 link_text = "Enlace sin nombre"


            # 1. Enlaces directos a documentos
            is_direct_document = any(href.lower().endswith(ext) for ext in doc_extensions)
            if is_direct_document:
                doc_type = href.split('.')[-1].lower()
                doc_url = href if href.startswith('http') else BASE_URL + (href if href.startswith('/') else '/' + href)

                # Evitar añadir el mismo documento si ya fue detectado (por si acaso)
                if not any(d['url'] == doc_url for d in documents):
                    documents.append({'name': link_text, 'url': doc_url, 'type': doc_type, 'course': course_name})
                    print(f"    [+] Documento directo: '{link_text}' ({doc_type}) - {doc_url}")
                continue

            # 2. Enlaces a módulos de Moodle (resource, folder, url)
            # Módulo "resource" (Archivo): suele llevar a una página intermedia o directamente al archivo.
            if '/resource/view.php' in href:
                resource_url = href if href.startswith('http') else BASE_URL + (href if href.startswith('/') else '/' + href)
                print(f"    [*] Analizando recurso Moodle: {link_text} ({resource_url})")
                try:
                    res_page = session.get(resource_url)
                    res_page.raise_for_status()
                    # Si la respuesta es directamente un archivo (Content-Type) o si la URL final tras redirecciones es un archivo
                    content_type = res_page.headers.get('Content-Type', '').lower()
                    final_url_lower = res_page.url.lower()

                    file_ext_from_url = next((ext for ext in doc_extensions if final_url_lower.endswith(ext)), None)

                    if file_ext_from_url or any(ft in content_type for ft in ['pdf', 'document', 'presentation', 'sheet', 'octet-stream', 'zip']):
                        doc_type = ""
                        if file_ext_from_url:
                             doc_type = file_ext_from_url.replace('.', '')
                        elif 'pdf' in content_type: doc_type = 'pdf'
                        elif 'word' in content_type or 'opendocument.text' in content_type : doc_type = 'doc/docx' # Genérico
                        elif 'presentation' in content_type or 'vnd.ms-powerpoint' in content_type : doc_type = 'ppt/pptx'
                        elif 'sheet' in content_type or 'excel' in content_type: doc_type = 'xls/xlsx'
                        else: doc_type = 'archivo' # Tipo genérico si no podemos determinarlo mejor

                        if not any(d['url'] == res_page.url for d in documents):
                            documents.append({'name': link_text, 'url': res_page.url, 'type': doc_type, 'course': course_name})
                            print(f"      [+] Encontrado (recurso): '{link_text}' ({doc_type}) - {res_page.url}")
                    else:
                        # Si no es un archivo directo, parsear la página del recurso
                        res_soup = BeautifulSoup(res_page.text, 'html.parser')
                        # Buscar un enlace dentro de la página del recurso que sí sea el archivo
                        # Esto es común si Moodle muestra una página intermedia antes de la descarga
                        main_content = res_soup.find('div', role='main')
                        if not main_content: main_content = res_soup # Fallback a todo el soup

                        found_in_resource_page = False
                        for potential_doc_link_el in main_content.find_all('a', href=True):
                            p_href = potential_doc_link_el['href']
                            if any(p_href.lower().endswith(ext) for ext in doc_extensions):
                                p_doc_type = p_href.split('.')[-1].lower()
                                p_doc_url = p_href if p_href.startswith('http') else BASE_URL + (p_href if p_href.startswith('/') else '/' + p_href)
                                p_doc_name = potential_doc_link_el.get_text(strip=True) or link_text # Usar el texto del enlace original si este no tiene
                                if not any(d['url'] == p_doc_url for d in documents):
                                    documents.append({'name': p_doc_name, 'url': p_doc_url, 'type': p_doc_type, 'course': course_name})
                                    print(f"      [+] Encontrado (pág. recurso): '{p_doc_name}' ({p_doc_type}) - {p_doc_url}")
                                    found_in_resource_page = True
                                    break # Suponemos que solo hay un documento principal por página de recurso
                        if not found_in_resource_page:
                             print(f"      [!] No se pudo extraer un enlace de documento directo desde la página del recurso: {resource_url}")

                except requests.exceptions.RequestException as e_res:
                    print(f"      [!] Error al acceder a la página del recurso {resource_url}: {e_res}")
                except Exception as e_detail:
                    print(f"      [!] Error procesando detalle del recurso {resource_url}: {e_detail}")


            # Módulo "folder" (Carpeta): lista varios archivos.
            elif '/folder/view.php' in href:
                folder_url = href if href.startswith('http') else BASE_URL + (href if href.startswith('/') else '/' + href)
                print(f"    [*] Analizando carpeta Moodle: {link_text} ({folder_url})")
                try:
                    folder_page = session.get(folder_url)
                    folder_page.raise_for_status()
                    folder_soup = BeautifulSoup(folder_page.text, 'html.parser')

                    # Los archivos dentro de una carpeta suelen estar en elementos con clase 'fp-filename-icon' o similar
                    for file_link_el in folder_soup.select('span.fp-filename a[href*="pluginfile.php"]'):
                        f_href = file_link_el['href']
                        f_name = file_link_el.get_text(strip=True)
                        if f_href and f_name:
                            f_doc_type = f_href.split('.')[-1].lower() if '.' in f_href else 'archivo' # Intenta obtener extensión
                            # Heurística para mejorar el tipo si no hay extensión clara
                            if not any(f_doc_type == ext.replace('.','') for ext in doc_extensions if ext != '.'):
                                if any(kw in f_name.lower() for kw in ['pdf']): f_doc_type = 'pdf'
                                elif any(kw in f_name.lower() for kw in ['doc']): f_doc_type = 'doc'
                                # ... más heurísticas si es necesario

                            f_doc_url = f_href if f_href.startswith('http') else BASE_URL + (f_href if f_href.startswith('/') else '/' + f_href)
                            if not any(d['url'] == f_doc_url for d in documents):
                                documents.append({'name': f_name, 'url': f_doc_url, 'type': f_doc_type, 'course': course_name})
                                print(f"      [+] Encontrado (carpeta): '{f_name}' ({f_doc_type}) - {f_doc_url}")
                except requests.exceptions.RequestException as e_folder:
                    print(f"      [!] Error al acceder a la página de la carpeta {folder_url}: {e_folder}")
                except Exception as e_detail:
                    print(f"      [!] Error procesando detalle de carpeta {folder_url}: {e_detail}")

            # Módulo "url" (URL externa): podría enlazar a un documento externo.
            elif '/url/view.php' in href:
                external_url_page_link = href if href.startswith('http') else BASE_URL + (href if href.startswith('/') else '/' + href)
                print(f"    [*] Analizando URL externa Moodle: {link_text} ({external_url_page_link})")
                try:
                    # La página de url/view.php suele ser una redirección o una página intermedia
                    # Necesitamos obtener la URL final a la que apunta.
                    # Es importante usar la session para que Moodle resuelva el enlace correctamente.
                    url_page_res = session.get(external_url_page_link, allow_redirects=True) # Sigue redirecciones
                    url_page_res.raise_for_status()
                    final_external_url = url_page_res.url # Esta es la URL a la que realmente apunta

                    if any(final_external_url.lower().endswith(ext) for ext in doc_extensions):
                        ext_doc_type = final_external_url.split('.')[-1].lower()
                        # El nombre del enlace original es probablemente más descriptivo que el nombre del archivo
                        if not any(d['url'] == final_external_url for d in documents):
                            documents.append({'name': link_text, 'url': final_external_url, 'type': ext_doc_type, 'course': course_name})
                            print(f"      [+] Encontrado (URL externa): '{link_text}' ({ext_doc_type}) - {final_external_url}")
                    else:
                        print(f"      [!] La URL externa '{final_external_url}' no parece ser un documento directo.")

                except requests.exceptions.RequestException as e_url:
                    print(f"      [!] Error al acceder/resolver la URL externa {external_url_page_link}: {e_url}")
                except Exception as e_detail:
                    print(f"      [!] Error procesando detalle de URL externa {external_url_page_link}: {e_detail}")


        if not documents:
            print(f"  No se encontraron documentos con los criterios actuales en el curso '{course_name}'.")
            # Guardar HTML de la página del curso para depuración si es necesario:
            # with open(f"course_page_{course_name.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            # print(f"  HTML del curso '{course_name}' guardado para análisis.")


    except requests.exceptions.RequestException as e:
        print(f"  Error de red o HTTP al acceder a la página del curso {course_url}: {e}")
    except Exception as e:
        print(f"  Ocurrió un error inesperado al analizar el curso {course_url}: {e}")
        # import traceback
        # traceback.print_exc()
    return documents

import os
import re
from pathlib import Path

def sanitize_filename(name):
    """Sanitiza un string para ser usado como nombre de archivo o carpeta."""
    # Eliminar caracteres no válidos
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', name)
    # Reducir espacios múltiples a uno solo
    name = re.sub(r'\s+', ' ', name).strip()
    # Evitar nombres vacíos o solo puntos
    if not name or name == '.' or name == '..':
        name = "archivo_descargado"
    # Limitar longitud (opcional, pero bueno para compatibilidad)
    return name[:150]


def download_selected_documents(session, documents_to_download):
    """
    Descarga los documentos seleccionados a una carpeta específica.

    Args:
        session: El objeto requests.Session activo.
        documents_to_download: Una lista de diccionarios, donde cada diccionario
                               representa un documento a descargar (con 'name', 'url', 'course', 'type').
    """
    # Carpeta base en el escritorio
    desktop_path = Path.home() / "Desktop"
    base_download_folder = desktop_path / "UNAHUR"

    try:
        base_download_folder.mkdir(parents=True, exist_ok=True)
        print(f"Directorio base de descarga: {base_download_folder}")
    except Exception as e:
        print(f"Error al crear el directorio base de descarga '{base_download_folder}': {e}")
        print("Por favor, crea la carpeta manualmente o revisa los permisos.")
        return

    for doc_info in documents_to_download:
        try:
            course_name = doc_info.get('course', 'Curso Desconocido')
            doc_name = doc_info.get('name', 'Documento Sin Nombre')
            doc_url = doc_info.get('url')
            doc_type = doc_info.get('type', '')

            if not doc_url:
                print(f"  [!] Omitiendo '{doc_name}' (URL no válida).")
                continue

            sanitized_course_name = sanitize_filename(course_name)
            course_folder = base_download_folder / sanitized_course_name
            course_folder.mkdir(parents=True, exist_ok=True)

            # Construir nombre de archivo con extensión
            # A veces el doc_name ya tiene extensión, otras veces no.
            # Priorizamos la extensión de doc_type si existe y es válida.
            base_doc_name_sanitized = sanitize_filename(Path(doc_name).stem) # Nombre sin extensión

            # Si doc_type es algo como 'doc/docx', tomar la parte después del '/' o la primera parte
            if '/' in doc_type:
                effective_extension = doc_type.split('/')[-1] # ej: docx de doc/docx
            else:
                effective_extension = doc_type

            # Asegurarse de que la extensión no esté vacía y sea razonable
            if effective_extension and len(effective_extension) < 6 and effective_extension != "archivo":
                file_extension = "." + effective_extension
            else: # Intentar obtenerla del nombre del documento si no, o dejarla vacía
                original_extension = Path(doc_name).suffix
                if original_extension and len(original_extension) > 1 and len(original_extension) < 6 :
                    file_extension = original_extension
                else: # Si no hay extensión clara o es genérica, no añadir una por defecto.
                      # El servidor podría proveerla a través de Content-Disposition o la URL final.
                    file_extension = ""


            # Si el nombre sanitizado ya tiene una extensión (por ej. del parseo original) y es la misma que la esperada, no duplicarla.
            if base_doc_name_sanitized.lower().endswith(file_extension.lower()) and file_extension:
                 filename = base_doc_name_sanitized
            else:
                 filename = base_doc_name_sanitized + file_extension

            filepath = course_folder / filename

            # Evitar sobrescribir: si el archivo existe, añadir un contador.
            counter = 1
            temp_filepath = filepath
            while temp_filepath.exists():
                temp_filepath = course_folder / f"{filepath.stem}_{counter}{filepath.suffix}"
                counter += 1
            filepath = temp_filepath

            print(f"  Descargando '{doc_name}' de '{course_name}'...")
            print(f"    URL: {doc_url}")
            print(f"    Guardando en: {filepath}")

            # Realizar la descarga
            response = session.get(doc_url, stream=True)
            response.raise_for_status() # Verificar errores HTTP

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"    [+] Descargado: {filepath.name}")

        except requests.exceptions.RequestException as e_req:
            print(f"    [!] Error de red/HTTP al descargar '{doc_name}': {e_req}")
        except IOError as e_io:
            print(f"    [!] Error de E/S al guardar '{doc_name}': {e_io}")
        except Exception as e:
            print(f"    [!] Error inesperado al procesar '{doc_name}': {e}")
            # import traceback
            # traceback.print_exc()


if __name__ == '__main__':

def get_active_courses(session):
    """
    Navega a la página de listado de cursos y extrae los cursos activos.

    Args:
        session: Un objeto requests.Session con una sesión de Moodle activa.

    Returns:
        Un diccionario con los nombres de los cursos como clave y sus URLs como valor,
        o un diccionario vacío si no se encuentran cursos o hay un error.
    """
    # URL común para la página principal del usuario donde se listan los cursos.
    # A veces es /my/ o /my/courses.php. Vamos a probar con /my/ primero.
    my_courses_url = BASE_URL + "/my/"
    courses = {}

    try:
        print(f"Accediendo a la página de cursos en: {my_courses_url}")
        response = session.get(my_courses_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Moodle puede presentar los cursos de varias maneras.
        # Intentaremos algunos selectores comunes.
        # Selector 1: Basado en la estructura típica de Moodle con 'coursebox'
        course_elements = soup.find_all('div', class_=lambda x: x and 'coursebox' in x and 'future' not in x and 'past' not in x)

        if not course_elements:
            # Selector 2: Buscar enlaces dentro de elementos con clase 'coursename' o similar,
            # que estén dentro de una lista de cursos.
            # Este es un intento más genérico.
            # Podría ser necesario inspeccionar el HTML de la página real para encontrar los selectores correctos.
            course_links = soup.select('div.course_category_tree [data-courseid]') # Moodle 4.x usa esto a menudo
            if not course_links:
                 course_links = soup.select('h3.coursename a') # Un selector más antiguo

        print(f"Encontrados {len(course_elements)} elementos con 'coursebox' (Selector 1)")
        # print(f"Encontrados {len(course_links)} elementos con selectores alternativos (Selector 2)")


        if course_elements:
            for course_el in course_elements:
                title_el = course_el.find(['h3', 'h4'], class_='coursename')
                if not title_el: # Otro posible lugar para el título
                    title_el = course_el.find('a', class_='aalink')

                link_el = title_el.find('a', href=True) if title_el else None
                if not link_el : # A veces el coursebox en sí es un link
                    link_el = course_el.find('a', href=True)


                if link_el and title_el:
                    course_name = title_el.get_text(strip=True)
                    course_url = link_el['href']
                    if not course_url.startswith('http'):
                        course_url = BASE_URL + course_url if course_url.startswith('/') else BASE_URL + '/' + course_url

                    # Filtrar para asegurarse de que es un enlace a un curso válido
                    if "course/view.php?id=" in course_url and course_name:
                        courses[course_name] = course_url
                        print(f"  Curso detectado (S1): '{course_name}' - URL: {course_url}")

        # Procesar course_links si el primer método no dio resultados o para complementar
        # Esto puede ser redundante si course_elements ya encontró todo.
        # Necesitaría una lógica más sofisticada para fusionar si ambos selectores son válidos y devuelven cursos.
        # Por ahora, priorizamos course_elements y si no, usamos course_links.
        # if not courses and course_links: # Solo si el primer método no encontró nada
        processed_urls_s2 = set()
        if course_links: # Intentar siempre el selector 2 por si el 1 falla o es incompleto
            print(f"Procesando {len(course_links)} elementos del Selector 2...")
            for link_el in course_links:
                course_name = ""
                course_url = ""

                if link_el.has_attr('data-courseid') and link_el.has_attr('href'): # Para Moodle 4.x con 'data-courseid'
                    course_name = link_el.get_text(strip=True)
                    course_url = link_el['href']
                elif link_el.name == 'a' and link_el.has_attr('href'): # Para selectores más antiguos tipo 'h3.coursename a'
                    course_name = link_el.get_text(strip=True)
                    course_url = link_el['href']

                if course_name and course_url:
                    if not course_url.startswith('http'):
                        course_url = BASE_URL + course_url if course_url.startswith('/') else BASE_URL + '/' + course_url

                    if "course/view.php?id=" in course_url and course_url not in processed_urls_s2:
                        # Evitar duplicados si el nombre es muy similar y la URL es la misma
                        existing_course_with_url = next((name for name, url in courses.items() if url == course_url), None)
                        if not existing_course_with_url:
                             courses[course_name] = course_url
                             print(f"  Curso detectado (S2): '{course_name}' - URL: {course_url}")
                        processed_urls_s2.add(course_url)


        if not courses:
            print("No se encontraron cursos utilizando los selectores conocidos.")
            # Para depuración, se podría guardar el HTML de la página:
            # with open("my_courses_page.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            # print("HTML de la página de cursos guardado en my_courses_page.html para análisis.")

    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP al acceder a la página de cursos: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al obtener los cursos: {e}")
        # import traceback
        # traceback.print_exc() # Para depuración más detallada

    return courses

if __name__ == '__main__':
    # Crear una sesión para mantener las cookies
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    user_username = input("Introduce tu nombre de usuario de Moodle: ")
    user_password = input("Introduce tu contraseña de Moodle: ")

    if login(s, user_username, user_password):
        print("Procediendo con las siguientes etapas...")
        courses = get_active_courses(s)
        if courses:
            print("\nCursos encontrados:")
            for name, url in courses.items():
                print(f"- {name}: {url}")
        else:
            print("No se encontraron cursos o hubo un error al recuperarlos.")
    else:
        print("No se pudo iniciar sesión. Revisa tus credenciales o la conexión.")
