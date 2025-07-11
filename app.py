from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import requests
import moodle_client # Nuestro nuevo módulo cliente
import io
import zipfile
import os # Para os.path.join y os.path.splitext
from pathlib import Path # Para la ruta del escritorio
from urllib.parse import urljoin, urlparse # Para el nombre del zip

app = Flask(__name__)
# Es crucial cambiar esto en un entorno de producción.
app.secret_key = os.urandom(24)

# --- Rutas de la Aplicación ---

@app.route('/', methods=['GET', 'POST'])
def config_moodle_url():
    if request.method == 'POST':
        moodle_url = request.form.get('moodle_url', '').strip()
        if not moodle_url:
            flash('Por favor, ingresa la URL base de Moodle.', 'danger')
            return render_template('config_moodle.html', submitted_url=session.get('moodle_base_url', ''))

        # Validar URL (básica)
        if not (moodle_url.startswith('http://') or moodle_url.startswith('https://')):
            flash('URL inválida. Debe comenzar con http:// o https://', 'danger')
            return render_template('config_moodle.html', submitted_url=moodle_url)

        # Limpiar trailing slash para consistencia
        if moodle_url.endswith('/'):
            moodle_url = moodle_url[:-1]

        # Verificar si la URL parece ser un sitio Moodle (opcional, intento básico)
        try:
            test_login_url = moodle_client.get_login_url(moodle_url)
            print(f"APP.PY DEBUG: Probando acceso a URL de login: {test_login_url}")
            ping = requests.get(test_login_url, timeout=7, headers={'User-Agent': moodle_client.USER_AGENT}, allow_redirects=True)
            ping.raise_for_status() # Lanza error para 4xx/5xx

            # Verificar si la URL final después de redirecciones sigue siendo la esperada o razonable
            if not ping.url.startswith(moodle_url): # Si redirige a un dominio completamente diferente
                 print(f"APP.PY WARN: URL de login redirigió de {test_login_url} a {ping.url}")
                 # Podríamos ser más estrictos aquí

            if 'moodle' not in ping.text.lower() and 'username' not in ping.text.lower() and 'password' not in ping.text.lower():
                 flash(f'La página en {ping.url} no parece ser un login de Moodle. Intenta con la URL base (ej: https://campus.example.com).', 'warning')
                 # return render_template('config_moodle.html', submitted_url=moodle_url) # Descomentar para ser más estricto
        except requests.exceptions.Timeout:
            flash(f'Timeout al intentar conectar con {moodle_url}. Verifica la URL y tu conexión.', 'danger')
            return render_template('config_moodle.html', submitted_url=moodle_url)
        except requests.exceptions.RequestException as e:
            flash(f'Error al intentar conectar con la URL ({moodle_url}): {e}', 'danger')
            return render_template('config_moodle.html', submitted_url=moodle_url)

        session['moodle_base_url'] = moodle_url
        flash(f'URL de Moodle configurada: {moodle_url}', 'info')
        return redirect(url_for('login_moodle'))

    # Si ya hay una URL configurada y el usuario vuelve a '/', redirigir a login o dashboard
    if 'moodle_base_url' in session:
        if session.get('moodle_user_active'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('login_moodle'))

    return render_template('config_moodle.html', submitted_url=session.get('moodle_base_url', ''))

@app.route('/login', methods=['GET', 'POST'])
def login_moodle():
    moodle_base_url = session.get('moodle_base_url')
    if not moodle_base_url:
        flash('Primero debes configurar la URL de Moodle.', 'warning')
        return redirect(url_for('config_moodle_url'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Usuario y contraseña son requeridos.', 'danger')
            return render_template('login.html', moodle_base_url=moodle_base_url)

        req_session = requests.Session() # Siempre crear una nueva sesión para el intento de login

        if moodle_client.login(moodle_base_url, username, password, req_session):
            session['moodle_user_active'] = True
            session['moodle_cookies'] = requests.utils.dict_from_cookiejar(req_session.cookies)
            flash('Inicio de sesión en Moodle exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error al iniciar sesión en Moodle. Verifica tus credenciales o la URL de Moodle.', 'danger')
            return render_template('login.html', moodle_base_url=moodle_base_url)

    # Si el usuario ya está logueado en la app y tiene cookies, no debería estar aquí a menos que la URL se ingrese manualmente
    if session.get('moodle_user_active') and session.get('moodle_cookies'):
         return redirect(url_for('dashboard'))

    return render_template('login.html', moodle_base_url=moodle_base_url)

def _get_moodle_session_from_flask_session():
    """Recrea la sesión de requests a partir de las cookies almacenadas en la sesión de Flask."""
    if 'moodle_cookies' not in session:
        return None

    req_session = requests.Session()
    req_session.headers.update({'User-Agent': moodle_client.USER_AGENT})
    requests.utils.add_dict_to_cookiejar(req_session.cookies, session['moodle_cookies'])
    return req_session

def _is_moodle_session_still_valid(req_session, moodle_base_url):
    """Verifica si la sesión de Moodle (representada por req_session) sigue siendo válida."""
    if not req_session or not moodle_base_url:
        return False
    try:
        my_courses_test_url = moodle_client.get_my_courses_url(moodle_base_url)
        test_response = req_session.get(my_courses_test_url, timeout=7, allow_redirects=True)
        test_response.raise_for_status()

        # Si la URL final es la página de login, la sesión ya no es válida.
        # Comparamos las rutas de las URLs para ser más robustos a pequeños cambios (www, no-www, http/s)
        login_url_path = urlparse(moodle_client.get_login_url(moodle_base_url)).path
        current_url_path = urlparse(test_response.url).path

        if login_url_path == current_url_path:
            print("APP.PY WARN: Sesión de Moodle inválida, redirigido a login.")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"APP.PY WARN: Error verificando validez de sesión de Moodle: {e}")
        return False

@app.route('/dashboard')
def dashboard():
    moodle_base_url = session.get('moodle_base_url')
    if not moodle_base_url: # Si no hay URL base, no podemos hacer nada
        flash('URL de Moodle no configurada.', 'warning')
        return redirect(url_for('config_moodle_url'))

    if not session.get('moodle_user_active'):
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('login_moodle'))

    req_session = _get_moodle_session_from_flask_session()

    if not _is_moodle_session_still_valid(req_session, moodle_base_url):
        session.pop('moodle_user_active', None)
        session.pop('moodle_cookies', None)
        flash('Tu sesión de Moodle ha expirado o es inválida. Por favor, inicia sesión de nuevo.', 'warning')
        return redirect(url_for('login_moodle'))

    print("APP.PY DEBUG: Recuperando cursos...")
    courses_data = moodle_client.get_active_courses(moodle_base_url, req_session)

    # Actualizar cookies en sesión de Flask por si cambiaron durante la navegación en el cliente Moodle
    session['moodle_cookies'] = requests.utils.dict_from_cookiejar(req_session.cookies)

    if courses_data is None: # Error explícito al obtener cursos
        flash('Ocurrió un error al intentar recuperar los cursos desde Moodle.', 'danger')
        return render_template('dashboard.html', courses_with_docs=None, moodle_base_url=moodle_base_url, error_ocurrido=True)
    if not courses_data: # Lista vacía
        flash('No se encontraron cursos activos o no se pudieron recuperar.', 'info')
        return render_template('dashboard.html', courses_with_docs=[], moodle_base_url=moodle_base_url)

    all_documents_by_course = {}
    print(f"APP.PY DEBUG: Cursos encontrados: {list(courses_data.keys())}")

    for course_name, course_url in courses_data.items():
        print(f"APP.PY DEBUG: Buscando documentos en el curso: {course_name} ({course_url})")
        # Pasamos moodle_base_url para resolver URLs relativas de documentos si es necesario
        docs_in_course = moodle_client.get_course_documents(course_url, req_session, moodle_base_url)
        all_documents_by_course[course_name] = sorted(docs_in_course, key=lambda x: x.get('name', '').lower()) if docs_in_course else []
        print(f"APP.PY DEBUG: Documentos encontrados en {course_name}: {len(all_documents_by_course[course_name])}")

    # Actualizar cookies de nuevo por si get_course_documents navegó más
    session['moodle_cookies'] = requests.utils.dict_from_cookiejar(req_session.cookies)

    sorted_course_names = sorted(all_documents_by_course.keys())
    ordered_courses_with_docs = [(name, all_documents_by_course[name]) for name in sorted_course_names]

    if not any(docs for _, docs in ordered_courses_with_docs):
        flash('No se encontraron documentos descargables en tus cursos.', 'info')

    return render_template('dashboard.html', courses_with_docs=ordered_courses_with_docs, moodle_base_url=moodle_base_url)

@app.route('/download', methods=['POST'])
def handle_download():
    moodle_base_url = session.get('moodle_base_url')
    if not moodle_base_url:
        flash('URL de Moodle no configurada.', 'danger')
        return redirect(url_for('config_moodle_url'))

    if not session.get('moodle_user_active'):
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('login_moodle'))

    req_session = _get_moodle_session_from_flask_session()

    if not _is_moodle_session_still_valid(req_session, moodle_base_url):
        session.pop('moodle_user_active', None)
        session.pop('moodle_cookies', None)
        flash('Tu sesión de Moodle ha expirado. Por favor, inicia sesión de nuevo.', 'warning')
        return redirect(url_for('login_moodle'))

    selected_docs_raw = request.form.getlist('selected_docs')
    if not selected_docs_raw:
        flash('No seleccionaste ningún documento para descargar.', 'warning')
        return redirect(url_for('dashboard'))

    documents_to_download_info = []
    for doc_str in selected_docs_raw:
        try:
            url, name, type, course = doc_str.split('|', 3)
            documents_to_download_info.append({'url': url, 'name': name, 'type': type, 'course': course})
        except ValueError:
            print(f"APP.PY WARN: No se pudo parsear la información del documento: {doc_str}")
            continue

    if not documents_to_download_info:
        flash('No hay documentos válidos para descargar después del parseo.', 'warning')
        return redirect(url_for('dashboard'))

    zip_buffer = io.BytesIO()
    zip_base_folder = "MoodleDownloads" # Carpeta raíz dentro del ZIP

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        download_count = 0
        for doc_info in documents_to_download_info:
            try:
                course_name_sanitized = moodle_client.sanitize_filename(doc_info['course'])
                doc_name_base = moodle_client.sanitize_filename(os.path.splitext(doc_info['name'])[0])
                doc_type_ext = doc_info['type'].lower()

                if '/' in doc_type_ext: doc_type_ext = doc_type_ext.split('/')[-1]

                extension = ""
                if doc_type_ext and doc_type_ext != "archivo" and len(doc_type_ext) < 7:
                    extension = "." + doc_type_ext
                else:
                    original_name_ext = os.path.splitext(doc_info['name'])[1]
                    if original_name_ext and len(original_name_ext) > 1 and len(original_name_ext) < 7:
                        extension = original_name_ext.lower()

                zip_filename = doc_name_base + extension if doc_name_base else "documento_descargado" + extension
                if not zip_filename: zip_filename = "documento_descargado_sin_extension"

                zip_path = os.path.join(zip_base_folder, course_name_sanitized, zip_filename)

                print(f"APP.PY DEBUG: Descargando para ZIP: '{doc_info['name']}' como '{zip_path}'")
                # Usar un timeout más largo para descargas de archivos individuales
                response = req_session.get(doc_info['url'], stream=True, timeout=30)
                response.raise_for_status()

                zf.writestr(zip_path, response.content) # Para archivos grandes, considerar iter_content por chunks
                download_count += 1
                print(f"APP.PY DEBUG: Añadido al ZIP: {zip_path}")

            except requests.exceptions.Timeout:
                msg = f"Timeout al descargar '{doc_info['name']}'."
                print(f"APP.PY ERROR: {msg}")
                flash(msg, 'danger')
            except requests.exceptions.RequestException as e_req:
                msg = f"Error de red/HTTP al descargar '{doc_info['name']}': {str(e_req)[:200]}" # Limitar longitud del error
                print(f"APP.PY ERROR: {msg}")
                flash(msg, 'danger')
            except Exception as e_zip:
                msg = f"Error general al procesar '{doc_info['name']}': {str(e_zip)[:200]}"
                print(f"APP.PY ERROR: {msg}")
                flash(msg, 'danger')

    session['moodle_cookies'] = requests.utils.dict_from_cookiejar(req_session.cookies) # Actualizar cookies

    if download_count == 0:
        flash('No se pudo descargar ningún archivo. Revisa los mensajes si los hay.', 'danger')
        return redirect(url_for('dashboard'))

    zip_buffer.seek(0)

    moodle_domain_sanitized = moodle_client.sanitize_filename(urlparse(moodle_base_url).netloc)
    zip_download_name = f'{moodle_domain_sanitized}_documentos_{download_count}_archivos.zip'

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=zip_download_name,
        mimetype='application/zip'
    )

@app.route('/logout')
def logout():
    session.pop('moodle_user_active', None)
    session.pop('moodle_cookies', None)
    # No limpiar moodle_base_url, para conveniencia del usuario si quiere volver a loguearse al mismo sitio.
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login_moodle'))

@app.route('/reset_config')
def reset_config():
    session.pop('moodle_base_url', None)
    session.pop('moodle_user_active', None)
    session.pop('moodle_cookies', None)
    flash('Configuración de URL de Moodle y sesión reiniciadas.', 'info')
    return redirect(url_for('config_moodle_url'))

# --- Creación de Carpetas y Ejecución ---
def _ensure_folders_exist():
    """Asegura que la carpeta 'templates' exista."""
    if not os.path.exists('templates'):
        print("APP.PY INFO: Creando carpeta 'templates'...")
        os.makedirs('templates')

if __name__ == '__main__':
    _ensure_folders_exist()
    print("APP.PY INFO: Iniciando servidor Flask...")
    # debug=True es para desarrollo. En producción, usar un servidor WSGI como Gunicorn.
    # host='0.0.0.0' permite acceso desde la red local, '127.0.0.1' solo localmente.
    app.run(debug=True, host='127.0.0.1', port=5000)
