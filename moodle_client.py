import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

# Constantes de User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def get_login_url(moodle_base_url):
    """Construye la URL de login a partir de la URL base de Moodle."""
    return urljoin(moodle_base_url, "login/index.php")

def get_my_courses_url(moodle_base_url):
    """Construye la URL de la página 'Mis cursos'."""
    # Apuntamos a /my/courses.php basado en el HTML que el usuario proveyó.
    return urljoin(moodle_base_url, "my/courses.php")

def login(moodle_base_url, username, password, session):
    """
    Intenta iniciar sesión en la plataforma Moodle.
    Actualiza el objeto session con las cookies si el login es exitoso.
    """
    login_url = get_login_url(moodle_base_url)
    session.headers.update({'User-Agent': USER_AGENT})

    try:
        login_page_response = session.get(login_url, timeout=10)
        login_page_response.raise_for_status()
        soup = BeautifulSoup(login_page_response.text, 'html.parser')

        logintoken_input = soup.find('input', {'name': 'logintoken'})
        if not logintoken_input:
            print(f"CLIENT_WARN: No se encontró logintoken en {login_url}. Intentando sin él.")
            logintoken = None
        else:
            logintoken = logintoken_input['value']
            print(f"CLIENT_DEBUG: Logintoken encontrado: {logintoken}")

        payload = {
            'username': username,
            'password': password,
            'rememberusername': 1,
        }
        if logintoken:
            payload['logintoken'] = logintoken

        response = session.post(login_url, data=payload, timeout=10)
        response.raise_for_status()

        if "login/index.php" in response.url:
            soup_response = BeautifulSoup(response.text, 'html.parser')
            error_message_div = soup_response.find('div', {'class': 'loginerrors'})
            if error_message_div:
                error_text = error_message_div.get_text(strip=True)
                print(f"CLIENT_ERROR: Error de inicio de sesión (detectado en página): {error_text}")
            else:
                feedback_error = soup_response.find('div', {'id': 'loginerrormessage'})
                if feedback_error:
                     print(f"CLIENT_ERROR: Error de inicio de sesión (feedback): {feedback_error.get_text(strip=True)}")
                else:
                     print("CLIENT_ERROR: Error de inicio de sesión: credenciales incorrectas o problema desconocido (permanece en login).")
            return False

        soup_response = BeautifulSoup(response.text, 'html.parser')
        logout_link_old = soup_response.find('a', href=lambda href: href and 'logout.php' in href)
        user_menu_m4 = soup_response.find('div', {'data-region': 'usermenu'})
        user_fullname_span = soup_response.find('span', class_='userfullname')

        if logout_link_old or user_menu_m4 or user_fullname_span:
            print("CLIENT_INFO: Inicio de sesión exitoso.")
            return True
        else:
            print("CLIENT_WARN: Inicio de sesión posiblemente fallido (no se encontraron indicadores claros de sesión activa post-login).")
            return False

    except requests.exceptions.Timeout:
        print(f"CLIENT_ERROR: Timeout durante el inicio de sesión en {login_url}.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"CLIENT_ERROR: Error de red o HTTP durante el inicio de sesión: {e}")
        return False
    except Exception as e:
        print(f"CLIENT_ERROR: Ocurrió un error inesperado durante el inicio de sesión: {e}")
        return False

def get_active_courses(moodle_base_url, session):
    """
    Versión mínima para depuración. No busca cursos, solo asegura que no hay errores de sintaxis.
    La lógica real de guardado de HTML se ha movido a una ruta de debug en app.py.
    """
    print("CLIENT_DEBUG: [get_active_courses en moodle_client.py] - Versión mínima solo para evitar SyntaxErrors.")
    return {} # Devuelve un diccionario vacío para que la app no falle, pero muestre el mensaje de "no cursos".

def get_course_documents(course_url, session, moodle_base_url):
    """
    Navega a la página de un curso y extrae enlaces a documentos.
    (Esta función mantiene su lógica original, pero dependerá de que get_active_courses funcione primero)
    """
    documents = []
    doc_extensions = [
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar',
    '.odt', '.odp', '.ods', '.rtf', '.csv',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    '.mp3', '.wav', '.ogg', '.aac',
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
    '.html', '.htm',
    '.ipynb',
    '.key',
    '.pages'
    ]

    print(f"CLIENT_DEBUG: [get_course_documents] Accediendo a la página del curso: {course_url}")
    try:
        response = session.get(course_url, timeout=25)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        potential_elements = soup.select('li[id^="module-"].activity, div.activityinstance, [data-draggroups="activity"]')

        print(f"CLIENT_DEBUG: [get_course_documents] Encontrados {len(potential_elements)} elementos de actividad/recurso potenciales.")

        processed_resource_urls = set()

        for element in potential_elements:
            link_tag = element.find('a', href=True)
            if not link_tag:
                continue

            href = link_tag.get('href')
            if not href:
                continue

            instance_name_span = link_tag.find('span', class_='instancename')
            link_text = ""
            if instance_name_span:
                link_text = instance_name_span.get_text(strip=True)

            if not link_text:
                temp_link_text_parts = []
                for content_part in link_tag.contents:
                    if isinstance(content_part, str):
                        cleaned_text_part = content_part.strip()
                        if cleaned_text_part:
                            temp_link_text_parts.append(cleaned_text_part)
                    elif hasattr(content_part, 'name') and content_part.name not in ['span', 'img', 'i', 'picture']:
                        cleaned_text_part = content_part.get_text(strip=True)
                        if cleaned_text_part:
                             temp_link_text_parts.append(cleaned_text_part)

                link_text = " ".join(temp_link_text_parts).strip()

            if not link_text:
                link_text = link_tag.get('title', '').strip()

            if not link_text:
                link_text = "Documento sin nombre"

            link_text = re.sub(r'\s{2,}', ' ', link_text)

            abs_link_url = urljoin(moodle_base_url, href)

            is_direct_document_by_ext = any(abs_link_url.lower().endswith(ext) for ext in doc_extensions)
            if is_direct_document_by_ext and 'pluginfile.php' not in abs_link_url and '/mod/' not in abs_link_url:
                doc_type = abs_link_url.split('.')[-1].lower()
                if not any(d['url'] == abs_link_url for d in documents):
                    documents.append({'name': link_text, 'url': abs_link_url, 'type': doc_type})
                    print(f"  CLIENT_DEBUG: [Doc Directo] '{link_text}' ({doc_type}) @ {abs_link_url}")
                continue

            if '/resource/view.php' in href:
                if abs_link_url in processed_resource_urls: continue
                processed_resource_urls.add(abs_link_url)
                print(f"  CLIENT_DEBUG: [*] Recurso Moodle: '{link_text}' ({abs_link_url})")
                try:
                    res_page = session.get(abs_link_url, timeout=15, allow_redirects=True)
                    res_page.raise_for_status()
                    final_url = res_page.url

                    if any(final_url.lower().endswith(ext) for ext in doc_extensions):
                        doc_type = final_url.split('.')[-1].lower()
                        if not any(d['url'] == final_url for d in documents):
                            documents.append({'name': link_text, 'url': final_url, 'type': doc_type})
                            print(f"    CLIENT_DEBUG: [+] (Recurso-Redir) '{link_text}' ({doc_type}) @ {final_url}")
                    else:
                        res_soup = BeautifulSoup(res_page.text, 'html.parser')
                        main_content_div = res_soup.find('div', role='main')
                        if not main_content_div: main_content_div = res_soup
                        found_in_resource_page = False
                        for potential_doc_link in main_content_div.find_all('a', href=True):
                            p_href = potential_doc_link['href']
                            p_abs_href = urljoin(moodle_base_url, p_href)
                            if any(p_abs_href.lower().endswith(ext) for ext in doc_extensions):
                                p_doc_type = p_abs_href.split('.')[-1].lower()
                                p_name = potential_doc_link.get_text(strip=True) or link_text
                                if not any(d['url'] == p_abs_href for d in documents):
                                    documents.append({'name': p_name, 'url': p_abs_href, 'type': p_doc_type})
                                    print(f"    CLIENT_DEBUG: [+] (Recurso-Pág) '{p_name}' ({p_doc_type}) @ {p_abs_href}")
                                    found_in_resource_page = True
                                    break
                        if not found_in_resource_page:
                             print(f"    CLIENT_WARN: [!] No se pudo extraer doc de pág. recurso: {abs_link_url}")
                except requests.exceptions.RequestException as e_res:
                    print(f"    CLIENT_ERROR: [!] Error accediendo a recurso {abs_link_url}: {e_res}")
                except Exception as e_detail_res:
                    print(f"    CLIENT_ERROR: [!] Error procesando detalle recurso {abs_link_url}: {e_detail_res}")

            elif '/folder/view.php' in href:
                if abs_link_url in processed_resource_urls: continue
                processed_resource_urls.add(abs_link_url)
                print(f"  CLIENT_DEBUG: [*] Carpeta Moodle: '{link_text}' ({abs_link_url})")
                try:
                    folder_page = session.get(abs_link_url, timeout=15)
                    folder_page.raise_for_status()
                    folder_soup = BeautifulSoup(folder_page.text, 'html.parser')
                    for file_link_el in folder_soup.select('span.fp-filename a[href*="pluginfile.php"]'):
                        f_href = file_link_el['href']
                        f_abs_href = urljoin(moodle_base_url, f_href)
                        f_name = file_link_el.get_text(strip=True)
                        if f_href and f_name:
                            f_doc_type = 'archivo'
                            parsed_file_url = urlparse(f_abs_href)
                            file_path_part = parsed_file_url.path
                            if '.' in file_path_part:
                                temp_ext = file_path_part.split('.')[-1].lower()
                                if temp_ext in [ext.replace('.', '') for ext in doc_extensions]:
                                    f_doc_type = temp_ext

                            if not any(d['url'] == f_abs_href for d in documents):
                                documents.append({'name': f_name, 'url': f_abs_href, 'type': f_doc_type})
                                print(f"    CLIENT_DEBUG: [+] (Carpeta) '{f_name}' ({f_doc_type}) @ {f_abs_href}")
                except requests.exceptions.RequestException as e_folder:
                    print(f"    CLIENT_ERROR: [!] Error accediendo a carpeta {abs_link_url}: {e_folder}")
                except Exception as e_detail_folder:
                    print(f"    CLIENT_ERROR: [!] Error procesando detalle carpeta {abs_link_url}: {e_detail_folder}")

            elif '/pluginfile.php/' in href:
                filename_from_url = abs_link_url.split('/')[-1].split('?')[0]
                doc_type = 'archivo'
                if any(filename_from_url.lower().endswith(ext) for ext in doc_extensions):
                    doc_type = filename_from_url.split('.')[-1].lower()

                descriptive_name = link_text
                if link_text == "Documento sin nombre" and '.' in filename_from_url and len(filename_from_url) > 4 :
                     descriptive_name = filename_from_url

                if not any(d['url'] == abs_link_url for d in documents):
                    documents.append({'name': descriptive_name, 'url': abs_link_url, 'type': doc_type})
                    print(f"  CLIENT_DEBUG: [Pluginfile] '{descriptive_name}' ({doc_type}) @ {abs_link_url}")

            elif '/url/view.php' in href:
                if abs_link_url in processed_resource_urls: continue
                processed_resource_urls.add(abs_link_url)
                print(f"  CLIENT_DEBUG: [*] URL Externa Moodle: '{link_text}' ({abs_link_url})")
                try:
                    url_page_res = session.get(abs_link_url, timeout=15, allow_redirects=True)
                    url_page_res.raise_for_status()
                    final_external_url = url_page_res.url

                    if any(final_external_url.lower().endswith(ext) for ext in doc_extensions):
                        ext_doc_type = final_external_url.split('.')[-1].lower()
                        if not any(d['url'] == final_external_url for d in documents):
                            documents.append({'name': link_text, 'url': final_external_url, 'type': ext_doc_type})
                            print(f"    CLIENT_DEBUG: [+] (URL Externa) '{link_text}' ({ext_doc_type}) @ {final_external_url}")
                    else:
                        print(f"    CLIENT_WARN: [!] URL externa '{final_external_url}' no parece ser un doc directo.")
                except requests.exceptions.RequestException as e_url_mod:
                    print(f"    CLIENT_ERROR: [!] Error accediendo/resolviendo URL externa {abs_link_url}: {e_url_mod}")
                except Exception as e_detail_url_mod:
                     print(f"    CLIENT_ERROR: [!] Error procesando detalle URL externa {abs_link_url}: {e_detail_url_mod}")

        if not documents:
            print(f"CLIENT_WARN: [get_course_documents] No se encontraron documentos con los criterios actuales en el curso.")

    except requests.exceptions.Timeout:
        print(f"CLIENT_ERROR: [get_course_documents] Timeout al acceder a la página del curso {course_url}.")
    except requests.exceptions.RequestException as e:
        print(f"CLIENT_ERROR: [get_course_documents] Error de red o HTTP al acceder a {course_url}: {e}")
    except Exception as e:
        print(f"CLIENT_ERROR: [get_course_documents] Ocurrió un error inesperado al analizar {course_url}: {e}")
        import traceback
        traceback.print_exc()
    return documents

def sanitize_filename(name):
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    reserved_names = {"CON", "PRN", "AUX", "NUL",
                      "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                      "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if name.upper() in reserved_names:
        name = "_" + name + "_"
    if re.match(r'^\.+$', name):
        name = "archivo_descargado"
    name = name.rstrip('. ')
    if not name:
        name = "archivo_descargado"
    return name[:150]

if __name__ == '__main__':
    print("Módulo moodle_client.py: Contiene lógica para interactuar con Moodle.")
    pass
