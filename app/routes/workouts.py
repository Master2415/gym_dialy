from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.db import get_connection
from app.utils import login_required
import datetime

workouts_bp = Blueprint('workouts', __name__)

@workouts_bp.route("/")
@workouts_bp.route("/workouts")
@login_required
def workouts():
    conn = get_connection()
    cur = conn.cursor()
    
    # --- DASHBOARD STATS ---
    # 1. Días entrenados este mes
    today = datetime.date.today()
    first_day = today.replace(day=1)
    cur.execute("""
        SELECT COUNT(DISTINCT DATE(fecha)) 
        FROM workouts 
        WHERE user_id = %s AND fecha >= %s
    """, (session['user_id'], first_day))
    days_trained = cur.fetchone()[0]
    
    # 2. Mejor 1RM (Sentadilla como ejemplo motivacional, o el máximo general)
    # Calculamos 1RM = Peso * (1 + Reps/30)
    cur.execute("""
        SELECT MAX(wd.peso * (1 + wd.reps/30)) 
        FROM workout_details wd
        JOIN workouts w ON wd.workout_id = w.id
        WHERE w.user_id = %s
    """, (session['user_id'],))
    best_1rm = cur.fetchone()[0]
    best_1rm = round(best_1rm, 1) if best_1rm else 0

    # --- FILTROS Y ORDENAMIENTO ---
    search = request.args.get('search', '')
    group_filter = request.args.get('group', '')
    date_filter = request.args.get('date', '')
    sort_by = request.args.get('sort', 'date_desc')
    
    query = """
        SELECT 
            w.fecha,
            e.grupo_muscular,
            e.nombre,
            wd.series,
            wd.reps,
            wd.peso,
            wd.comentario,
            w.id,
            w.notas,
            e.id as exercise_id
        FROM workouts w
        LEFT JOIN workout_details wd ON w.id = wd.workout_id
        LEFT JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s
    """
    params = [session['user_id']]
    
    if search:
        query += " AND e.nombre LIKE %s"
        params.append(f"%{search}%")
        
    if group_filter:
        query += " AND e.grupo_muscular = %s"
        params.append(group_filter)

    if date_filter:
        query += " AND DATE(w.fecha) = %s"
        params.append(date_filter)
        
    if sort_by == 'date_desc':
        query += " ORDER BY w.fecha DESC, w.id DESC"
    elif sort_by == 'date_asc':
        query += " ORDER BY w.fecha ASC, w.id ASC"
    elif sort_by == 'weight_desc':
        query += " ORDER BY wd.peso DESC"
    elif sort_by == 'reps_desc':
        query += " ORDER BY wd.reps DESC"
    else:
        query += " ORDER BY w.fecha DESC, w.id DESC"

    cur.execute(query, tuple(params))
    data = cur.fetchall()
    
    # Extraer fechas únicas para el calendario
    cur.execute("SELECT DISTINCT DATE(fecha) FROM workouts WHERE user_id = %s", (session['user_id'],))
    workout_dates = [row[0].strftime('%Y-%m-%d') for row in cur.fetchall()]
    
    # Obtener grupos musculares para el filtro
    cur.execute("SELECT DISTINCT grupo_muscular FROM exercises WHERE user_id = %s ORDER BY grupo_muscular", (session['user_id'],))
    muscle_groups = [row[0] for row in cur.fetchall()]

    conn.close()
    
    dashboard_stats = {
        'days_trained': days_trained,
        'best_1rm': best_1rm
    }
    
    return render_template("workouts.html", 
                           workouts=data, 
                           workout_dates=workout_dates, 
                           dashboard=dashboard_stats,
                           muscle_groups=muscle_groups,
                           filters={'search': search, 'group': group_filter, 'date': date_filter, 'sort': sort_by})

@workouts_bp.route("/workouts/new", methods=["GET", "POST"])
@login_required
def new_workout():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        notas = request.form["notas"]
        if not notas:
            notas = "-"
        
        cur.execute("INSERT INTO workouts (user_id, notas) VALUES (%s, %s)", (session['user_id'], notas))
        new_workout_id = cur.lastrowid
        
        exercise_id = request.form.get("exercise_id")
        if exercise_id:
            series = request.form["series"] or 0
            reps = request.form["reps"] or 0
            peso = request.form["peso"] or 0
            comentario = request.form["comentario"] or "-"

            cur.execute("""
                INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_workout_id, exercise_id, series, reps, peso, comentario))

        conn.commit()
        conn.close()
        return redirect(url_for('workouts.workouts'))

    # GET: Obtener ejercicios agrupados por grupo muscular
    cur.execute("SELECT id, grupo_muscular, nombre FROM exercises WHERE user_id = %s ORDER BY grupo_muscular, nombre", (session['user_id'],))
    rows = cur.fetchall()
    
    # Estructurar datos: { 'Pecho': [{'id': 1, 'nombre': 'Press Banca'}, ...], ... }
    ejercicios_por_grupo = {}
    for row in rows:
        eid, grupo, nombre = row
        if grupo not in ejercicios_por_grupo:
            ejercicios_por_grupo[grupo] = []
        ejercicios_por_grupo[grupo].append({'id': eid, 'nombre': nombre})
        
    conn.close()

    return render_template("workout_form.html", titulo="Nueva sesión", datos="", ejercicios=ejercicios_por_grupo)

@workouts_bp.route("/workouts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_workout(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM workouts WHERE id=%s AND user_id=%s", (id, session['user_id']))
    if not cur.fetchone():
        conn.close()
        return "Acceso denegado", 403

    if request.method == "POST":
        notas = request.form["notas"] or "-"
        cur.execute("UPDATE workouts SET notas=%s WHERE id=%s", (notas, id))
        
        exercise_id = request.form.get("exercise_id")
        if exercise_id:
            series = request.form.get("series", 0)
            reps = request.form.get("reps", 0)
            peso = request.form.get("peso", 0)
            comentario = request.form.get("comentario", "-")
            
            cur.execute("SELECT id FROM workout_details WHERE workout_id=%s LIMIT 1", (id,))
            existing_detail = cur.fetchone()
            
            if existing_detail:
                cur.execute("""
                    UPDATE workout_details 
                    SET exercise_id=%s, series=%s, reps=%s, peso=%s, comentario=%s 
                    WHERE id=%s
                """, (exercise_id, series, reps, peso, comentario, existing_detail[0]))
            else:
                cur.execute("""
                    INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id, exercise_id, series, reps, peso, comentario))
        
        conn.commit()
        conn.close()
        return redirect(url_for('workouts.workouts'))

    cur.execute("SELECT notas FROM workouts WHERE id=%s", (id,))
    result = cur.fetchone()
    notas = result[0] if result else ""
    
    cur.execute("""
        SELECT wd.exercise_id, wd.series, wd.reps, wd.peso, wd.comentario
        FROM workout_details wd
        WHERE wd.workout_id = %s
        LIMIT 1
    """, (id,))
    detail = cur.fetchone()
    datos = {
        'notas': notas,
        'exercise_id': detail[0] if detail else None,
        'series': detail[1] if detail else 0,
        'reps': detail[2] if detail else 0,
        'peso': detail[3] if detail else 0,
        'comentario': detail[4] if detail else "-"
    }
    
    # Obtener ejercicios agrupados
    cur.execute("SELECT id, grupo_muscular, nombre FROM exercises WHERE user_id = %s ORDER BY grupo_muscular, nombre", (session['user_id'],))
    rows = cur.fetchall()
    ejercicios_por_grupo = {}
    for row in rows:
        eid, grupo, nombre = row
        if grupo not in ejercicios_por_grupo:
            ejercicios_por_grupo[grupo] = []
        ejercicios_por_grupo[grupo].append({'id': eid, 'nombre': nombre})

    conn.close()
    return render_template("workout_form.html", titulo="Editar sesión", datos=datos, ejercicios=ejercicios_por_grupo)

@workouts_bp.route("/workouts/delete/<int:id>")
@login_required
def delete_workout(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM workouts WHERE id=%s AND user_id=%s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('workouts.workouts'))
