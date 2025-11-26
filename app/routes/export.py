from flask import Blueprint, session, make_response, jsonify
from app.db import get_connection
from app.utils import login_required
import csv
import io

export_bp = Blueprint('export', __name__)

@export_bp.route("/export/csv")
@login_required
def export_csv():
    conn = get_connection()
    cur = conn.cursor()
    
    # Query to get all series data with exercise and workout info
    cur.execute("""
        SELECT 
            w.fecha, 
            e.grupo_muscular, 
            e.nombre,
            ws.serie_numero,
            ws.reps, 
            ws.peso, 
            ws.comentario as serie_comentario,
            w.notas,
            (ws.peso * (1 + ws.reps/30)) as estimated_1rm,
            (ws.reps * ws.peso) as volumen_serie
        FROM workout_series ws
        JOIN workout_details wd ON ws.workout_detail_id = wd.id
        JOIN workouts w ON wd.workout_id = w.id
        JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s
        ORDER BY w.fecha DESC, e.nombre, ws.serie_numero
    """, (session['user_id'],))
    
    data = cur.fetchall()
    conn.close()
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Fecha', 'Grupo Muscular', 'Ejercicio', 'Serie #', 'Reps', 'Peso (kg)', 'Comentario Serie', 'Notas Sesion', '1RM Estimado', 'Volumen Serie'])
    cw.writerows(data)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=workouts_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@export_bp.route("/export/json")
@login_required
def export_json():
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all workouts for the user
    cur.execute("""
        SELECT id, fecha, notas
        FROM workouts 
        WHERE user_id = %s
        ORDER BY fecha DESC
    """, (session['user_id'],))
    
    workouts = cur.fetchall()
    workouts_list = []
    
    for workout in workouts:
        workout_id = workout[0]
        workout_data = {
            'id': workout_id,
            'fecha': workout[1].strftime('%Y-%m-%d'),
            'notas': workout[2],
            'ejercicios': []
        }
        
        # Get exercises for this workout
        cur.execute("""
            SELECT DISTINCT wd.id, e.nombre, e.grupo_muscular
            FROM workout_details wd
            JOIN exercises e ON wd.exercise_id = e.id
            WHERE wd.workout_id = %s
        """, (workout_id,))
        
        details = cur.fetchall()
        
        for detail in details:
            detail_id = detail[0]
            exercise_data = {
                'nombre': detail[1],
                'grupo': detail[2],
                'series': []
            }
            
            # Get all series for this exercise
            cur.execute("""
                SELECT serie_numero, reps, peso, comentario
                FROM workout_series
                WHERE workout_detail_id = %s
                ORDER BY serie_numero
            """, (detail_id,))
            
            series = cur.fetchall()
            
            for serie in series:
                serie_data = {
                    'numero': serie[0],
                    'reps': serie[1],
                    'peso': float(serie[2]) if serie[2] else 0,
                    'comentario': serie[3],
                    '1rm_estimado': round(serie[2] * (1 + serie[1]/30), 2) if serie[2] and serie[1] else 0,
                    'volumen': round(serie[1] * serie[2], 2) if serie[1] and serie[2] else 0
                }
                exercise_data['series'].append(serie_data)
            
            workout_data['ejercicios'].append(exercise_data)
        
        workouts_list.append(workout_data)
    
    conn.close()
    
    return jsonify({'workouts': workouts_list})
