"""
============================================
MÓDULO DE CONFIGURACIÓN
============================================
Este módulo maneja todas las rutas relacionadas con la configuración del usuario,
incluyendo edición de perfil, selección de tema e importación/exportación de datos.

Autor: Douglas (Master2415)
"""

from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.utils import login_required
from app.db import get_connection

# Crear el blueprint para las rutas de configuración
settings_bp = Blueprint('settings', __name__)

@settings_bp.route("/settings")
@login_required
def index():
    """
    Página principal de configuración.
    
    Muestra las opciones de configuración organizadas en categorías:
    - Perfil: Editar información personal
    - Preferencias: Seleccionar tema de color
    - Datos: Importar/Exportar información
    
    Returns:
        Template renderizado con las opciones de configuración
    """
    # Estructura de opciones de configuración organizadas por categorías
    options = [
        {
            'category': 'Perfil',
            'menu_items': [
                {'name': 'Editar Perfil', 'desc': 'Cambiar nombre, email', 'link': '/settings/profile'},
            ]
        },
        {
            'category': 'Preferencias',
            'menu_items': [
                {'name': 'Tema', 'desc': 'Seleccionar tema de color', 'link': '/settings/theme'},
            ]
        },
        {
            'category': 'Datos',
            'menu_items': [
                {'name': 'Exportar CSV', 'desc': 'Descargar historial en CSV', 'link': '/export/csv'},
                {'name': 'Exportar JSON', 'desc': 'Descargar copia de seguridad completa', 'link': '/export/json'},
                {'name': 'Importar CSV', 'desc': 'Cargar datos desde archivo CSV', 'link': '/settings/import'},
            ]
        }
    ]
    return render_template("settings.html", options=options)

@settings_bp.route("/settings/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """
    Editar perfil del usuario.
    
    GET: Muestra el formulario con los datos actuales del usuario
    POST: Actualiza el nombre completo y email del usuario en la base de datos
    
    Returns:
        GET: Template con formulario de edición
        POST: Redirección a configuración con mensaje de éxito/error
    """
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        # Obtener datos del formulario
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        print(f"DEBUG: Updating profile for user {session.get('user_id')}: {full_name}, {email}")
        
        try:
            # Actualizar información del usuario en la base de datos
            cur.execute("""
                UPDATE users 
                SET full_name = %s, email = %s 
                WHERE id = %s
            """, (full_name, email, session['user_id']))
            conn.commit()
            print(f"DEBUG: Update committed. Row count: {cur.rowcount}")
            
            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for('settings.index'))
        except Exception as e:
            flash(f"Error al actualizar perfil: {e}", "error")
        finally:
            conn.close()

    # GET request - Cargar datos actuales del usuario
    cur.execute("SELECT full_name, email FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    conn.close()
    
    user_data = {
        'full_name': user[0] if user else '',
        'email': user[1] if user else ''
    }

    return render_template("edit_profile.html", user=user_data)

@settings_bp.route("/settings/import", methods=["GET", "POST"])
@login_required
def import_csv():
    """
    Importar datos de entrenamientos desde un archivo CSV.
    
    Formato esperado del CSV:
    fecha,grupo_muscular,ejercicio,series,reps,peso,comentario
    
    El proceso:
    1. Valida el archivo CSV
    2. Lee y parsea cada fila
    3. Crea ejercicios si no existen
    4. Inserta workouts y detalles en la base de datos
    5. Reporta éxitos y errores
    
    Returns:
        GET: Template con formulario de importación
        POST: Redirección a configuración con resumen de importación
    """
    if request.method == "POST":
        # Validar que se haya enviado un archivo
        if 'csv_file' not in request.files:
            flash("No se seleccionó ningún archivo", "error")
            return redirect(url_for('settings.import_csv'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash("No se seleccionó ningún archivo", "error")
            return redirect(url_for('settings.import_csv'))
        
        # Validar extensión del archivo
        if not file.filename.endswith('.csv'):
            flash("El archivo debe ser un CSV", "error")
            return redirect(url_for('settings.import_csv'))
        
        try:
            import csv
            from io import StringIO
            from datetime import datetime
            
            # Leer y parsear el archivo CSV
            stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            conn = get_connection()
            cur = conn.cursor()
            
            imported_count = 0  # Contador de registros importados exitosamente
            error_count = 0     # Contador de errores
            
            # Procesar cada fila del CSV
            for row in csv_reader:
                try:
                    # Validar y extraer campos requeridos
                    fecha = row.get('fecha', '').strip()
                    grupo_muscular = row.get('grupo_muscular', '').strip()
                    ejercicio = row.get('ejercicio', '').strip()
                    series = int(row.get('series', 0))
                    reps = int(row.get('reps', 0))
                    peso = float(row.get('peso', 0))
                    comentario = row.get('comentario', '').strip()
                    
                    # Validar que los campos obligatorios no estén vacíos
                    if not all([fecha, grupo_muscular, ejercicio]):
                        error_count += 1
                        continue
                    
                    # Parsear fecha al formato correcto
                    workout_date = datetime.strptime(fecha, '%Y-%m-%d')
                    
                    # Verificar si el ejercicio ya existe, si no, crearlo
                    cur.execute("""
                        SELECT id FROM exercises 
                        WHERE user_id = %s AND nombre = %s AND grupo_muscular = %s
                    """, (session['user_id'], ejercicio, grupo_muscular))
                    
                    exercise = cur.fetchone()
                    if not exercise:
                        # Crear nuevo ejercicio
                        cur.execute("""
                            INSERT INTO exercises (user_id, grupo_muscular, nombre)
                            VALUES (%s, %s, %s)
                        """, (session['user_id'], grupo_muscular, ejercicio))
                        exercise_id = cur.lastrowid
                    else:
                        exercise_id = exercise[0]
                    
                    # Crear registro de workout
                    cur.execute("""
                        INSERT INTO workouts (user_id, fecha, notas)
                        VALUES (%s, %s, %s)
                    """, (session['user_id'], workout_date, comentario))
                    workout_id = cur.lastrowid
                    
                    # Crear detalle del workout (series, reps, peso)
                    cur.execute("""
                        INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (workout_id, exercise_id, series, reps, peso, comentario))
                    
                    imported_count += 1
                    
                except Exception as e:
                    # Registrar error y continuar con la siguiente fila
                    print(f"Error importing row: {e}")
                    error_count += 1
                    continue
            
            # Guardar todos los cambios en la base de datos
            conn.commit()
            conn.close()
            
            # Mostrar resumen de la importación
            flash(f"Importación completada: {imported_count} registros importados, {error_count} errores", "success")
            return redirect(url_for('settings.index'))
            
        except Exception as e:
            flash(f"Error al procesar el archivo CSV: {e}", "error")
            return redirect(url_for('settings.import_csv'))
    
    # GET request - Mostrar formulario de importación
    return render_template("import_csv.html")

@settings_bp.route("/settings/theme")
@login_required
def theme_selector():
    """
    Página de selección de tema visual.
    
    Muestra una interfaz visual con 6 opciones de temas de color:
    - Light (Claro)
    - Dark (Oscuro)
    - Blue (Azul)
    - Green (Verde)
    - Purple (Púrpura)
    - Amber (Ámbar)
    
    Returns:
        Template con selector visual de temas
    """
    return render_template("theme_selector.html")
