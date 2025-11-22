from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambiar por una clave segura en producción

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------
# INICIALIZACIÓN BD
# ---------------------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Tabla de mediciones corporales
    cur.execute("""
        CREATE TABLE IF NOT EXISTS body_measurements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            fecha DATE NOT NULL,
            peso DECIMAL(5,2),
            cintura DECIMAL(5,2),
            brazos DECIMAL(5,2),
            piernas DECIMAL(5,2),
            pecho DECIMAL(5,2),
            grasa_corporal DECIMAL(5,2),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# Inicializar tablas al arrancar (o llamar manualmente)
try:
    init_db()
except Exception as e:
    print(f"Error initializing DB: {e}")

# ---------------------------------------
# RUTAS DE AUTENTICACIÓN
# ---------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            new_user_id = cur.lastrowid
            conn.commit()
            
            # Seed exercises for the new user
            try:
                from seed_exercises import seed_exercises
                seed_exercises(new_user_id)
            except Exception as e:
                print(f"Error seeding exercises for user {new_user_id}: {e}")
                
            flash("Registro exitoso, por favor inicia sesión.")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Error: El usuario ya existe o hubo un problema.")
        finally:
            conn.close()
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('workouts'))
        else:
            flash("Usuario o contraseña incorrectos.")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------------------------
# LISTAR SESIONES
# ---------------------------------------
@app.route("/")
@app.route("/workouts")
@login_required
def workouts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            w.fecha,
            e.grupo_muscular,
            e.nombre,
            wd.series,
            wd.reps,
            wd.peso,
            wd.comentario,
            w.id,
            w.notas
        FROM workouts w
        LEFT JOIN workout_details wd ON w.id = wd.workout_id
        LEFT JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s
        ORDER BY w.fecha DESC, w.id DESC, e.grupo_muscular
    """, (session['user_id'],))
    data = cur.fetchall()
    
    # Extraer fechas únicas para el calendario
    # data[i][0] es la fecha (datetime)
    workout_dates = []
    if data:
        # Usamos un set para fechas únicas y convertimos a string YYYY-MM-DD
        dates_set = set()
        for row in data:
            if row[0]:
                dates_set.add(row[0].strftime('%Y-%m-%d'))
        workout_dates = list(dates_set)
        
    conn.close()
    return render_template("workouts.html", workouts=data, workout_dates=workout_dates)


# ---------------------------------------
# CREAR SESIÓN
# ---------------------------------------
@app.route("/workouts/new", methods=["GET", "POST"])
@login_required
def new_workout():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        notas = request.form["notas"]
        if not notas:
            notas = "-"
        
        # 1. Crear la sesión (workout) vinculada al usuario
        cur.execute("INSERT INTO workouts (user_id, notas) VALUES (%s, %s)", (session['user_id'], notas))
        new_workout_id = cur.lastrowid  # Obtener el ID generado
        
        # 2. Verificar si vienen detalles de ejercicio
        exercise_id = request.form.get("exercise_id")
        if exercise_id:
            series = request.form["series"]
            if not series: series = 0
            
            reps = request.form["reps"]
            if not reps: reps = 0
            
            peso = request.form["peso"]
            if not peso: peso = 0
            
            comentario = request.form["comentario"]
            if not comentario: comentario = "-"

            cur.execute("""
                INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_workout_id, exercise_id, series, reps, peso, comentario))

        conn.commit()
        conn.close()
        return redirect("/workouts")

    # GET: Obtener ejercicios para el dropdown (globales o del usuario si se implementa)
    cur.execute("SELECT * FROM exercises WHERE user_id = %s ORDER BY grupo_muscular, nombre", (session['user_id'],))
    ejercicios_raw = cur.fetchall()
    conn.close()

    # Agrupar ejercicios por grupo muscular
    ejercicios_por_grupo = {}
    for ej in ejercicios_raw:
        grupo = ej[2] # grupo_muscular
        if grupo not in ejercicios_por_grupo:
            ejercicios_por_grupo[grupo] = []
        ejercicios_por_grupo[grupo].append(ej)

    return render_template("workout_form.html", titulo="Nueva sesión", datos="", ejercicios=ejercicios_por_grupo)


# ---------------------------------------
# EDITAR SESIÓN
# ---------------------------------------
@app.route("/workouts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_workout(id):
    conn = get_connection()
    cur = conn.cursor()

    # Verificar que el workout pertenezca al usuario
    cur.execute("SELECT id FROM workouts WHERE id=%s AND user_id=%s", (id, session['user_id']))
    if not cur.fetchone():
        conn.close()
        return "Acceso denegado", 403

    if request.method == "POST":
        notas = request.form["notas"]
        if not notas:
            notas = "-"
        cur.execute("UPDATE workouts SET notas=%s WHERE id=%s", (notas, id))
        
        # Actualizar o crear workout_details si se proporcionan
        exercise_id = request.form.get("exercise_id")
        if exercise_id:
            series = request.form.get("series", 0)
            reps = request.form.get("reps", 0)
            peso = request.form.get("peso", 0)
            comentario = request.form.get("comentario", "-")
            
            # Verificar si ya existe un detalle para este workout
            cur.execute("SELECT id FROM workout_details WHERE workout_id=%s LIMIT 1", (id,))
            existing_detail = cur.fetchone()
            
            if existing_detail:
                # Actualizar el detalle existente
                cur.execute("""
                    UPDATE workout_details 
                    SET exercise_id=%s, series=%s, reps=%s, peso=%s, comentario=%s 
                    WHERE id=%s
                """, (exercise_id, series, reps, peso, comentario, existing_detail[0]))
            else:
                # Crear nuevo detalle
                cur.execute("""
                    INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id, exercise_id, series, reps, peso, comentario))
        
        conn.commit()
        conn.close()
        return redirect("/workouts")

    # GET: Cargar datos del workout y sus detalles
    cur.execute("SELECT notas FROM workouts WHERE id=%s", (id,))
    result = cur.fetchone()
    notas = result[0] if result else ""
    
    # Cargar detalles del ejercicio si existen
    cur.execute("""
        SELECT wd.exercise_id, wd.series, wd.reps, wd.peso, wd.comentario
        FROM workout_details wd
        WHERE wd.workout_id = %s
        LIMIT 1
    """, (id,))
    detail = cur.fetchone()
    
    # Cargar lista de ejercicios disponibles
    cur.execute("SELECT * FROM exercises WHERE user_id = %s ORDER BY grupo_muscular, nombre", (session['user_id'],))
    ejercicios_raw = cur.fetchall()
    
    conn.close()

    # Agrupar ejercicios por grupo muscular
    ejercicios_por_grupo = {}
    for ej in ejercicios_raw:
        grupo = ej[2] # grupo_muscular
        if grupo not in ejercicios_por_grupo:
            ejercicios_por_grupo[grupo] = []
        ejercicios_por_grupo[grupo].append(ej)
    
    # Preparar datos para el template
    datos = {
        'notas': notas,
        'exercise_id': detail[0] if detail else None,
        'series': detail[1] if detail else 0,
        'reps': detail[2] if detail else 0,
        'peso': detail[3] if detail else 0,
        'comentario': detail[4] if detail else "-"
    }

    return render_template("workout_form.html", titulo="Editar sesión", datos=datos, ejercicios=ejercicios_por_grupo)


# ---------------------------------------
# ELIMINAR SESIÓN
# ---------------------------------------
@app.route("/workouts/delete/<int:id>")
@login_required
def delete_workout(id):
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar propiedad
    cur.execute("SELECT id FROM workouts WHERE id=%s AND user_id=%s", (id, session['user_id']))
    if not cur.fetchone():
        conn.close()
        return "Acceso denegado", 403

    cur.execute("DELETE FROM workouts WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/workouts")


# ---------------------------------------
# AGREGAR DETALLE DE EJERCICIO
# ---------------------------------------
@app.route("/workouts/<int:id>/details", methods=["GET", "POST"])
@login_required
def workout_details(id):
    conn = get_connection()
    cur = conn.cursor()

    # Verificar propiedad del workout
    cur.execute("SELECT id FROM workouts WHERE id=%s AND user_id=%s", (id, session['user_id']))
    if not cur.fetchone():
        conn.close()
        return "Acceso denegado", 403

    # datos de ejercicios disponibles para el usuario
    cur.execute("SELECT * FROM exercises WHERE user_id = %s", (session['user_id'],))
    ejercicios = cur.fetchall()

    if request.method == "POST":
        exercise_id = request.form.get("exercise_id")
        if not exercise_id:
            return "Error: Debes seleccionar un ejercicio", 400

        series = request.form["series"]
        if not series: series = 0
        
        reps = request.form["reps"]
        if not reps: reps = 0
        
        peso = request.form["peso"]
        if not peso: peso = 0
        
        comentario = request.form["comentario"]
        if not comentario: comentario = "-"

        cur.execute("""
            INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (id, exercise_id, series, reps, peso, comentario))
        conn.commit()
        conn.close()
        return redirect("/workouts")

    conn.close()
    return render_template("details_form.html", ejercicios=ejercicios)


# ---------------------------------------
# ANALYTICS
# ---------------------------------------
@app.route("/analytics")
@login_required
def analytics():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Récords Personales (PR) - Max peso por ejercicio
    cur.execute("""
        SELECT e.nombre, MAX(wd.peso) as max_peso, DATE_FORMAT(MAX(w.fecha), '%Y-%m-%d') as fecha
        FROM workout_details wd
        JOIN workouts w ON wd.workout_id = w.id
        JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s AND wd.peso > 0
        GROUP BY e.id, e.nombre
        ORDER BY max_peso DESC
        LIMIT 10
    """, (session['user_id'],))
    prs = [{'nombre': row[0], 'max_peso': row[1], 'fecha': row[2]} for row in cur.fetchall()]
    
    # 2. Datos para el gráfico (Evolución de peso de los 5 ejercicios más frecuentes)
    # Primero encontramos los 5 ejercicios más usados
    cur.execute("""
        SELECT exercise_id 
        FROM workout_details wd
        JOIN workouts w ON wd.workout_id = w.id
        WHERE w.user_id = %s
        GROUP BY exercise_id
        ORDER BY COUNT(*) DESC
        LIMIT 5
    """, (session['user_id'],))
    top_exercises = [row[0] for row in cur.fetchall()]
    
    chart_data = {}
    
    if top_exercises:
        # Para cada ejercicio top, obtenemos el historial de peso
        format_strings = ','.join(['%s'] * len(top_exercises))
        query = f"""
            SELECT e.nombre, w.fecha, wd.peso
            FROM workout_details wd
            JOIN workouts w ON wd.workout_id = w.id
            JOIN exercises e ON wd.exercise_id = e.id
            WHERE w.user_id = %s AND wd.exercise_id IN ({format_strings}) AND wd.peso > 0
            ORDER BY w.fecha ASC
        """
        # params: user_id + list of exercise_ids
        params = [session['user_id']] + top_exercises
        cur.execute(query, tuple(params))
        
        rows = cur.fetchall()
        for row in rows:
            name = row[0]
            date = row[1].strftime('%Y-%m-%d')
            weight = float(row[2])
            
            if name not in chart_data:
                chart_data[name] = []
            
            chart_data[name].append({'x': date, 'y': weight})
            
    conn.close()
    
    return render_template("analytics.html", personal_records=prs, chart_data=chart_data)


# ---------------------------------------
# MEDICIONES CORPORALES
# ---------------------------------------
@app.route("/measurements", methods=["GET", "POST"])
@login_required
def measurements():
    conn = get_connection()
    cur = conn.cursor()
    
    if request.method == "POST":
        fecha = request.form["fecha"]
        peso = request.form["peso"]
        cintura = request.form.get("cintura") or None
        brazos = request.form.get("brazos") or None
        piernas = request.form.get("piernas") or None
        pecho = request.form.get("pecho") or None
        grasa = request.form.get("grasa_corporal") or None
        
        cur.execute("""
            INSERT INTO body_measurements (user_id, fecha, peso, cintura, brazos, piernas, pecho, grasa_corporal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], fecha, peso, cintura, brazos, piernas, pecho, grasa))
        conn.commit()
        flash("Medición guardada correctamente.")
        conn.close()
        return redirect("/measurements")

    # GET: Obtener historial para gráficos
    cur.execute("""
        SELECT fecha, peso, cintura, brazos, piernas, pecho, grasa_corporal
        FROM body_measurements
        WHERE user_id = %s
        ORDER BY fecha ASC
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    
    # Preparar datos para Chart.js
    chart_data = {
        'Peso': [],
        'Cintura': [],
        'Brazos': [],
        'Piernas': [],
        'Pecho': [],
        '% Grasa': []
    }
    
    for row in rows:
        date = row[0].strftime('%Y-%m-%d')
        if row[1]: chart_data['Peso'].append({'x': date, 'y': float(row[1])})
        if row[2]: chart_data['Cintura'].append({'x': date, 'y': float(row[2])})
        if row[3]: chart_data['Brazos'].append({'x': date, 'y': float(row[3])})
        if row[4]: chart_data['Piernas'].append({'x': date, 'y': float(row[4])})
        if row[5]: chart_data['Pecho'].append({'x': date, 'y': float(row[5])})
        if row[6]: chart_data['% Grasa'].append({'x': date, 'y': float(row[6])})

    from datetime import date
    return render_template("measurements.html", chart_data=chart_data, today=date.today().strftime('%Y-%m-%d'))


# ---------------------------------------
# EXPORT & BACKUP
# ---------------------------------------
@app.route("/export/csv")
@login_required
def export_csv():
    import csv
    import io
    from flask import Response

    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            w.fecha,
            e.grupo_muscular,
            e.nombre as ejercicio,
            wd.series,
            wd.reps,
            wd.peso,
            wd.comentario,
            w.notas
        FROM workouts w
        LEFT JOIN workout_details wd ON w.id = wd.workout_id
        LEFT JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s
        ORDER BY w.fecha DESC
    """, (session['user_id'],))
    
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Fecha', 'Grupo Muscular', 'Ejercicio', 'Series', 'Reps', 'Peso', 'Comentario', 'Notas Sesion'])
    writer.writerows(rows)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gym_backup.csv"}
    )

@app.route("/export/json")
@login_required
def export_json():
    import json
    from flask import Response
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Fetch all workouts
    cur.execute("SELECT id, fecha, notas FROM workouts WHERE user_id = %s", (session['user_id'],))
    workouts = []
    workout_rows = cur.fetchall()
    
    for w_row in workout_rows:
        w_id = w_row[0]
        workout = {
            'id': w_id,
            'fecha': w_row[1].strftime('%Y-%m-%d %H:%M:%S'),
            'notas': w_row[2],
            'details': []
        }
        
        # Fetch details for this workout
        cur.execute("""
            SELECT e.grupo_muscular, e.nombre, wd.series, wd.reps, wd.peso, wd.comentario
            FROM workout_details wd
            JOIN exercises e ON wd.exercise_id = e.id
            WHERE wd.workout_id = %s
        """, (w_id,))
        
        details = cur.fetchall()
        for d in details:
            workout['details'].append({
                'grupo': d[0],
                'ejercicio': d[1],
                'series': d[2],
                'reps': d[3],
                'peso': float(d[4]),
                'comentario': d[5]
            })
            
        workouts.append(workout)
        
    conn.close()
    
    return Response(
        json.dumps({'workouts': workouts}, indent=4),
        mimetype="application/json",
        headers={"Content-disposition": "attachment; filename=gym_backup.json"}
    )


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=5000)
