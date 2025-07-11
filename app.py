from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests # Necesario para la sesión de requests
import moodle_downloader # Importaremos nuestro módulo existente

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_muy_segura_para_desarrollo' # Cambiar en producción

# Mantendremos la sesión de requests globalmente o dentro de la sesión de Flask.
# Por simplicidad inicial, y sabiendo que Flask por defecto es single-threaded en desarrollo,
# podríamos usar una global, pero es mejor asociarla a la sesión de Flask.
# Ejemplo: session['moodle_session'] = requests.Session()

@app.route('/', methods=['GET'])
def index():
    if 'moodle_user_active' in session and session['moodle_user_active']:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Usuario y contraseña son requeridos.', 'danger')
            return render_template('login.html')

        # Crear una nueva sesión de requests para este intento de login
        moodle_s = requests.Session()
        moodle_s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        if moodle_downloader.login(moodle_s, username, password):
            session['moodle_user_active'] = True
            # Guardar la sesión de requests serializable o recrearla.
            # requests.Session no es directamente serializable en la sesión de Flask.
            # Una opción es guardar las cookies.
            session['moodle_cookies'] = requests.utils.dict_from_cookiejar(moodle_s.cookies)
            flash('Inicio de sesión en Moodle exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error al iniciar sesión en Moodle. Verifica tus credenciales.', 'danger')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('moodle_user_active'):
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('login_page'))

    # Recrear la sesión de requests a partir de las cookies almacenadas
    if 'moodle_cookies' not in session:
        flash('Sesión de Moodle no encontrada. Por favor, inicia sesión de nuevo.', 'danger')
        return redirect(url_for('login_page'))

    moodle_s = requests.Session()
    moodle_s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    requests.utils.add_dict_to_cookiejar(moodle_s.cookies, session['moodle_cookies'])

    # Verificar si la sesión sigue siendo válida (opcional pero recomendado)
    # Por ejemplo, intentando acceder a una página protegida
    test_response = moodle_s.get(moodle_downloader.BASE_URL + "/my/")
    if "login/index.php" in test_response.url:
        flash('Tu sesión de Moodle ha expirado. Por favor, inicia sesión de nuevo.', 'warning')
        session.pop('moodle_user_active', None)
        session.pop('moodle_cookies', None)
        return redirect(url_for('login_page'))

    # Por ahora, solo mostramos un mensaje. Luego cargaremos cursos y documentos.
    # return f"Dashboard: ¡Bienvenido! Sesión de Moodle activa. Cookies: {session['moodle_cookies']}"

    print("Recuperando cursos...")
    courses_data = moodle_downloader.get_active_courses(moodle_s)
    if not courses_data:
        flash('No se pudieron recuperar los cursos o no tienes cursos activos.', 'warning')
        return render_template('dashboard.html', courses_with_docs=None)

    all_documents_by_course = {}
    print(f"Cursos encontrados: {courses_data.keys()}")

    for course_name, course_url in courses_data.items():
        print(f"Buscando documentos en el curso: {course_name} ({course_url})")
        # Pasamos el nombre del curso para que se almacene en los diccionarios de documentos
        docs_in_course = moodle_downloader.find_document_links_in_course(moodle_s, course_url, course_name)
        if docs_in_course:
            # Ordenar documentos por nombre antes de añadirlos
            all_documents_by_course[course_name] = sorted(docs_in_course, key=lambda x: x.get('name', '').lower())
        else:
            all_documents_by_course[course_name] = [] # Dejar la lista vacía si no hay documentos
        print(f"Documentos encontrados en {course_name}: {len(all_documents_by_course[course_name])}")


    # Ordenar cursos por nombre para la vista
    sorted_courses_names = sorted(all_documents_by_course.keys())

    # Reestructurar para la plantilla: una lista de tuplas (nombre_curso, lista_docs)
    # para mantener el orden
    ordered_courses_with_docs = []
    for course_name in sorted_courses_names:
        ordered_courses_with_docs.append( (course_name, all_documents_by_course[course_name]) )


    if not any(docs for _, docs in ordered_courses_with_docs):
        flash('No se encontraron documentos descargables en tus cursos.', 'info')

    return render_template('dashboard.html', courses_with_docs=ordered_courses_with_docs)

import io
import zipfile
from flask import send_file

@app.route('/download', methods=['POST'])
def handle_download():
    if not session.get('moodle_user_active'):
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('login_page'))

    selected_docs_raw = request.form.getlist('selected_docs')
    if not selected_docs_raw:
        flash('No seleccionaste ningún documento para descargar.', 'warning')
        return redirect(url_for('dashboard'))

    # Recrear la sesión de Moodle
    moodle_s = requests.Session()
    moodle_s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    if 'moodle_cookies' in session:
        requests.utils.add_dict_to_cookiejar(moodle_s.cookies, session['moodle_cookies'])
    else:
        flash('Sesión de Moodle no encontrada. Por favor, inicia sesión de nuevo.', 'danger')
        return redirect(url_for('login_page'))

    # Verificar si la sesión sigue siendo válida
    test_response = moodle_s.get(moodle_downloader.BASE_URL + "/my/")
    if "login/index.php" in test_response.url:
        flash('Tu sesión de Moodle ha expirado. Por favor, inicia sesión de nuevo.', 'warning')
        session.pop('moodle_user_active', None)
        session.pop('moodle_cookies', None)
        return redirect(url_for('login_page'))

    documents_to_download_info = []
    for doc_str in selected_docs_raw:
        try:
            url, name, type, course = doc_str.split('|', 3)
            documents_to_download_info.append({'url': url, 'name': name, 'type': type, 'course': course})
        except ValueError:
            print(f"Advertencia: No se pudo parsear la información del documento: {doc_str}")
            continue # Ignorar este documento

    if not documents_to_download_info:
        flash('No hay documentos válidos para descargar después del parseo.', 'warning')
        return redirect(url_for('dashboard'))

    # Crear un archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    # Es importante usar allowZip64=True si se esperan archivos ZIP grandes o muchos archivos.
    # Sin embargo, Python por defecto lo habilita si es necesario desde 3.7+ para zipfile.ZipFile.
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        download_count = 0
        for doc_info in documents_to_download_info:
            try:
                course_name_sanitized = moodle_downloader.sanitize_filename(doc_info['course'])
                course_name_sanitized = moodle_downloader.sanitize_filename(doc_info['course'])

                # Nombre base del documento (sin extensión)
                base_name_for_zip = moodle_downloader.sanitize_filename(os.path.splitext(doc_info['name'])[0])

                # Determinar la extensión
                doc_type_ext = doc_info['type'].lower()
                if '/' in doc_type_ext: # ej. 'application/pdf' o de Moodle 'doc/docx'
                    doc_type_ext = doc_type_ext.split('/')[-1]

                if doc_type_ext and doc_type_ext != "archivo" and len(doc_type_ext) < 6:
                    extension = "." + doc_type_ext
                else:
                    # Si doc_type no es útil, intentar obtenerla del nombre original del documento
                    original_name_ext = os.path.splitext(doc_info['name'])[1]
                    if original_name_ext and len(original_name_ext) > 1 and len(original_name_ext) < 6:
                        extension = original_name_ext.lower()
                    else:
                        extension = "" # Sin extensión clara

                zip_filename = base_name_for_zip + extension
                if not base_name_for_zip: # Si el nombre base quedó vacío después de sanitizar y quitar extensión
                    zip_filename = "documento_descargado" + extension
                if not zip_filename: # Si todo falla
                    zip_filename = "documento_descargado_sin_extension"


                # Ruta dentro del ZIP
                zip_path = os.path.join(course_name_sanitized, zip_filename)

                print(f"Descargando para ZIP: '{doc_info['name']}' ({doc_info['type']}) desde '{doc_info['url']}' como '{zip_path}'")
                response = moodle_s.get(doc_info['url'], stream=True)
                response.raise_for_status()

                # Escribir el contenido del archivo en el ZIP
                zf.writestr(zip_path, response.content) # response.content para archivos pequeños/medianos
                                                        # para muy grandes, response.raw podría ser mejor con shutil.copyfileobj
                download_count += 1
                print(f"Añadido al ZIP: {zip_path}")

            except requests.exceptions.RequestException as e_req:
                print(f"Error descargando {doc_info['name']}: {e_req}")
                flash(f"Error descargando '{doc_info['name']}': {e_req}", 'danger')
            except Exception as e_zip:
                print(f"Error añadiendo {doc_info['name']} al ZIP: {e_zip}")
                flash(f"Error añadiendo '{doc_info['name']}' al ZIP: {e_zip}", 'danger')

    if download_count == 0:
        flash('No se pudo descargar ningún archivo. Revisa los mensajes de error si los hay.', 'danger')
        return redirect(url_for('dashboard'))

    zip_buffer.seek(0)

    # Enviar el archivo ZIP
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='UNAHUR_documentos.zip', # Nombre del archivo ZIP que el usuario verá
        mimetype='application/zip'
    )


@app.route('/logout')
def logout():
    # Aquí también se podría intentar cerrar la sesión en Moodle si hay una URL de logout
    # moodle_s = ... recrear sesión ...
    # moodle_s.get(moodle_downloader.BASE_URL + "/login/logout.php?sesskey=...") # Requiere sesskey

    session.pop('moodle_user_active', None)
    session.pop('moodle_cookies', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    # Crear directorio 'templates' si no existe
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
