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
    
    # 2. Mejor Peso Levantado (Récord Personal)
    cur.execute("""
        SELECT MAX(ws.peso) 
        FROM workout_series ws
        JOIN workout_details wd ON ws.workout_detail_id = wd.id
        JOIN workouts w ON wd.workout_id = w.id
        WHERE w.user_id = %s
    """, (session['user_id'],))
    best_weight = cur.fetchone()[0]
    best_weight = round(best_weight, 1) if best_weight else 0

    # --- FILTROS Y ORDENAMIENTO ---
    search = request.args.get('search', '')
    group_filter = request.args.get('group', '')
    date_filter = request.args.get('date', '')
    sort_by = request.args.get('sort', 'date_desc')
    
    today = datetime.date.today()
    
    # Default to today if no date filter is provided
    if not date_filter and not search and not group_filter:
        date_filter = today.strftime('%Y-%m-%d')
    
    query = """
        SELECT 
            w.fecha, 
            e.grupo_muscular, 
            e.nombre, 
            wd.series, 
            (SELECT AVG(ws.reps) FROM workout_series ws WHERE ws.workout_detail_id = wd.id) as avg_reps,
            (SELECT AVG(ws.peso) FROM workout_series ws WHERE ws.workout_detail_id = wd.id) as avg_peso,
            wd.comentario, 
            w.id, 
            w.notas,
            e.id
        FROM workouts w
        JOIN workout_details wd ON w.id = wd.workout_id
        JOIN exercises e ON wd.exercise_id = e.id
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
        # Sort by the calculated average weight is complex in this query structure without a subquery or CTE
        # For simplicity, we'll keep sorting by the 'avg_peso' if possible, or just wd.peso (which is 0 now)
        # Let's try to sort by the scalar subquery alias if supported, or just ignore for now as user didn't strictly request sort fix
        # MySQL allows sorting by alias in HAVING or ORDER BY usually.
        query += " ORDER BY avg_peso DESC"
    elif sort_by == 'reps_desc':
        query += " ORDER BY avg_reps DESC"
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

    # Calcular Previous y Next Day
    prev_date = None
    next_date = None
    
    if date_filter:
        current_date_obj = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
        
        # Buscar fecha anterior con entrenamientos
        cur.execute("SELECT MAX(DATE(fecha)) FROM workouts WHERE user_id = %s AND DATE(fecha) < %s", (session['user_id'], date_filter))
        prev_row = cur.fetchone()
        if prev_row and prev_row[0]:
            prev_date = prev_row[0].strftime('%Y-%m-%d')
            
        # Buscar fecha posterior con entrenamientos
        cur.execute("SELECT MIN(DATE(fecha)) FROM workouts WHERE user_id = %s AND DATE(fecha) > %s", (session['user_id'], date_filter))
        next_row = cur.fetchone()
        if next_row and next_row[0]:
            next_date = next_row[0].strftime('%Y-%m-%d')

    conn.close()
    
    dashboard_stats = {
        'days_trained': days_trained,
        'best_weight': best_weight,
        'prev_date': prev_date,
        'next_date': next_date,
        'current_date': date_filter
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
        
        fecha = request.form.get("fecha")
        
        if fecha:
            cur.execute("INSERT INTO workouts (user_id, notas, fecha) VALUES (%s, %s, %s)", (session['user_id'], notas, fecha))
        else:
            cur.execute("INSERT INTO workouts (user_id, notas) VALUES (%s, %s)", (session['user_id'], notas))
        new_workout_id = cur.lastrowid
        
        exercise_id = request.form.get("exercise_id")

        # exercise_id is now always provided from the select dropdown

        if exercise_id:
            # Total series count from the main input
            total_series = int(request.form.get("series", 0))
            
            # Insert the main detail record
            cur.execute("""
                INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_workout_id, exercise_id, total_series, 0, 0, "-"))
            new_detail_id = cur.lastrowid

            # Insert each series
            for i in range(1, total_series + 1):
                reps = request.form.get(f"reps_{i}", 0)
                peso = request.form.get(f"peso_{i}", 0)
                comentario = request.form.get(f"comentario_{i}", "-")
                
                cur.execute("""
                    INSERT INTO workout_series (workout_detail_id, serie_numero, reps, peso, comentario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (new_detail_id, i, reps, peso, comentario))

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
        fecha = request.form.get("fecha")
        
        if fecha:
            cur.execute("UPDATE workouts SET notas=%s, fecha=%s WHERE id=%s", (notas, fecha, id))
        else:
            cur.execute("UPDATE workouts SET notas=%s WHERE id=%s", (notas, id))
        
        exercise_id = request.form.get("exercise_id")
        grupo_muscular = request.form.get("grupo_muscular")

        # exercise_id is now always provided from the select dropdown

        if exercise_id:
            total_series = int(request.form.get("series", 0))
            
            cur.execute("SELECT id FROM workout_details WHERE workout_id=%s LIMIT 1", (id,))
            existing_detail = cur.fetchone()
            
            detail_id = None
            if existing_detail:
                detail_id = existing_detail[0]
                cur.execute("""
                    UPDATE workout_details 
                    SET exercise_id=%s, series=%s 
                    WHERE id=%s
                """, (exercise_id, total_series, detail_id))
            else:
                cur.execute("""
                    INSERT INTO workout_details (workout_id, exercise_id, series, reps, peso, comentario)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id, exercise_id, total_series, 0, 0, "-"))
                detail_id = cur.lastrowid
            
            # Update series: Delete existing and re-insert (simplest approach)
            cur.execute("DELETE FROM workout_series WHERE workout_detail_id=%s", (detail_id,))
            
            for i in range(1, total_series + 1):
                reps = request.form.get(f"reps_{i}", 0)
                peso = request.form.get(f"peso_{i}", 0)
                comentario = request.form.get(f"comentario_{i}", "-")
                
                cur.execute("""
                    INSERT INTO workout_series (workout_detail_id, serie_numero, reps, peso, comentario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (detail_id, i, reps, peso, comentario))
        
        conn.commit()
        conn.close()
        return redirect(url_for('workouts.workouts'))

    cur.execute("SELECT notas, fecha FROM workouts WHERE id=%s", (id,))
    result = cur.fetchone()
    notas = result[0] if result else ""
    fecha = result[1].strftime('%Y-%m-%d') if result and result[1] else ""
    
    cur.execute("""
        SELECT wd.id, wd.exercise_id, wd.series, wd.reps, wd.peso, wd.comentario, e.nombre, e.grupo_muscular
        FROM workout_details wd
        JOIN exercises e ON wd.exercise_id = e.id
        WHERE wd.workout_id = %s
        LIMIT 1
    """, (id,))
    detail = cur.fetchone()
    
    series_details = []
    if detail:
        detail_id = detail[0]
        cur.execute("""
            SELECT serie_numero, reps, peso, comentario 
            FROM workout_series 
            WHERE workout_detail_id = %s 
            ORDER BY serie_numero ASC
        """, (detail_id,))
        series_rows = cur.fetchall()
        for row in series_rows:
            series_details.append({
                'numero': row[0],
                'reps': row[1],
                'peso': row[2],
                'comentario': row[3]
            })

    datos = {
        'notas': notas,
        'fecha': fecha,
        'exercise_id': detail[1] if detail else None,
        'series': detail[2] if detail else 0,
        'series_details': series_details,
        'exercise_name': detail[6] if detail else "",
        'muscle_group': detail[7] if detail else ""
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
