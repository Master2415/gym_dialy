from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.db import get_connection
from app.utils import login_required
import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/analytics")
@login_required
def analytics():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Récords Personales (PR) - Max peso y 1RM Estimado
    # Updated to use workout_series
    cur.execute("""
        SELECT 
            e.nombre, 
            MAX(ws.peso) as max_peso, 
            MAX(ws.peso * (1 + ws.reps/30)) as estimated_1rm,
            DATE_FORMAT(MAX(w.fecha), '%Y-%m-%d') as fecha
        FROM workout_series ws
        JOIN workout_details wd ON ws.workout_detail_id = wd.id
        JOIN workouts w ON wd.workout_id = w.id
        JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s AND ws.peso > 0
        GROUP BY e.id, e.nombre
        ORDER BY estimated_1rm DESC
        LIMIT 10
    """, (session['user_id'],))
    prs = [{'nombre': row[0], 'max_peso': row[1], 'one_rm': round(row[2], 1), 'fecha': row[3]} for row in cur.fetchall()]
    
    # 2. Datos para el gráfico (Evolución de peso de los 5 ejercicios más frecuentes)
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
        format_strings = ','.join(['%s'] * len(top_exercises))
        # Get max weight per workout for these exercises
        query = f"""
            SELECT e.nombre, w.fecha, MAX(ws.peso)
            FROM workout_series ws
            JOIN workout_details wd ON ws.workout_detail_id = wd.id
            JOIN workouts w ON wd.workout_id = w.id
            JOIN exercises e ON wd.exercise_id = e.id
            WHERE w.user_id = %s AND wd.exercise_id IN ({format_strings}) AND ws.peso > 0
            GROUP BY w.id, e.nombre, w.fecha
            ORDER BY w.fecha ASC
        """
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
            
    # 3. Volumen por Grupo Muscular (Últimos 30 días)
    thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
    cur.execute("""
        SELECT e.grupo_muscular, SUM(ws.reps * ws.peso) as volumen
        FROM workout_series ws
        JOIN workout_details wd ON ws.workout_detail_id = wd.id
        JOIN workouts w ON wd.workout_id = w.id
        JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s AND w.fecha >= %s
        GROUP BY e.grupo_muscular
    """, (session['user_id'], thirty_days_ago))
    volume_data = {row[0]: float(row[1]) for row in cur.fetchall() if row[1] is not None}
            
    conn.close()
    
    return render_template("analytics.html", personal_records=prs, chart_data=chart_data, volume_data=volume_data)

@analytics_bp.route("/measurements", methods=["GET", "POST"])
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
        return redirect(url_for('analytics.measurements'))

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

    return render_template("measurements.html", chart_data=chart_data, today=datetime.date.today().strftime('%Y-%m-%d'))

@analytics_bp.route("/history/<int:exercise_id>")
@login_required
def history(exercise_id):
    conn = get_connection()
    cur = conn.cursor()
    
    # Obtener nombre del ejercicio
    cur.execute("SELECT nombre FROM exercises WHERE id = %s", (exercise_id,))
    exercise_name = cur.fetchone()[0]
    
    # Obtener historial completo (Max weight per session)
    cur.execute("""
        SELECT 
            w.fecha,
            COUNT(ws.id) as series,
            SUM(ws.reps) as total_reps,
            MAX(ws.peso) as max_peso,
            GROUP_CONCAT(CONCAT(ws.reps, 'x', ws.peso, 'kg') SEPARATOR ', ') as detalle,
            MAX(ws.peso * (1 + ws.reps/30)) as estimated_1rm
        FROM workout_series ws
        JOIN workout_details wd ON ws.workout_detail_id = wd.id
        JOIN workouts w ON wd.workout_id = w.id
        WHERE wd.exercise_id = %s AND w.user_id = %s
        GROUP BY w.id, w.fecha
        ORDER BY w.fecha DESC
    """, (exercise_id, session['user_id']))
    history_data = cur.fetchall()
    
    # Datos para el gráfico
    chart_data = {
        'Peso': [],
        '1RM': []
    }
    
    for row in reversed(history_data):
        date = row[0].strftime('%Y-%m-%d')
        weight = float(row[3]) if row[3] else 0
        one_rm = float(row[5]) if row[5] else 0
        
        chart_data['Peso'].append({'x': date, 'y': weight})
        chart_data['1RM'].append({'x': date, 'y': round(one_rm, 1)})
        
    conn.close()
    
    return render_template("history.html", 
                           exercise_name=exercise_name, 
                           history=history_data, 
                           chart_data=chart_data)
