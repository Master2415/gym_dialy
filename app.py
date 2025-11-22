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
    conn.close()
    return render_template("workouts.html", workouts=data)


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
    # Por ahora asumimos ejercicios globales o filtramos por usuario si la tabla exercises tiene user_id
    # Según el script_bd.sql modificado, exercises tiene user_id.
    cur.execute("SELECT * FROM exercises WHERE user_id = %s", (session['user_id'],))
    ejercicios = cur.fetchall()
    conn.close()

    return render_template("workout_form.html", titulo="Nueva sesión", datos="", ejercicios=ejercicios)


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
    cur.execute("SELECT * FROM exercises WHERE user_id = %s", (session['user_id'],))
    ejercicios = cur.fetchall()
    
    conn.close()
    
    # Preparar datos para el template
    datos = {
        'notas': notas,
        'exercise_id': detail[0] if detail else None,
        'series': detail[1] if detail else 0,
        'reps': detail[2] if detail else 0,
        'peso': detail[3] if detail else 0,
        'comentario': detail[4] if detail else "-"
    }

    return render_template("workout_form.html", titulo="Editar sesión", datos=datos, ejercicios=ejercicios)


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


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=5000)
