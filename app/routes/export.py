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
    
    cur.execute("""
        SELECT 
            w.fecha, 
            e.grupo_muscular, 
            e.nombre, 
            wd.series, 
            wd.reps, 
            wd.peso, 
            wd.comentario, 
            w.notas,
            (wd.peso * (1 + wd.reps/30)) as estimated_1rm,
            (wd.series * wd.reps * wd.peso) as volumen
        FROM workouts w
        LEFT JOIN workout_details wd ON w.id = wd.workout_id
        LEFT JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s
        ORDER BY w.fecha DESC
    """, (session['user_id'],))
    
    data = cur.fetchall()
    conn.close()
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Fecha', 'Grupo Muscular', 'Ejercicio', 'Series', 'Reps', 'Peso', 'Comentario', 'Notas Sesion', '1RM Estimado', 'Volumen'])
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
    
    cur.execute("""
        SELECT 
            w.id, w.fecha, w.notas,
            e.nombre, e.grupo_muscular,
            wd.series, wd.reps, wd.peso, wd.comentario,
            (wd.peso * (1 + wd.reps/30)) as estimated_1rm,
            (wd.series * wd.reps * wd.peso) as volumen
        FROM workouts w
        LEFT JOIN workout_details wd ON w.id = wd.workout_id
        LEFT JOIN exercises e ON wd.exercise_id = e.id
        WHERE w.user_id = %s
        ORDER BY w.fecha DESC
    """, (session['user_id'],))
    
    rows = cur.fetchall()
    conn.close()
    
    workouts_dict = {}
    for row in rows:
        wid = row[0]
        if wid not in workouts_dict:
            workouts_dict[wid] = {
                'id': wid,
                'fecha': row[1].strftime('%Y-%m-%d'),
                'notas': row[2],
                'ejercicios': []
            }
        
        if row[3]:
            workouts_dict[wid]['ejercicios'].append({
                'nombre': row[3],
                'grupo': row[4],
                'series': row[5],
                'reps': row[6],
                'peso': row[7],
                'comentario': row[8],
                '1rm_estimado': round(row[9], 2) if row[9] else 0,
                'volumen': round(row[10], 2) if row[10] else 0
            })
            
    final_data = {'workouts': list(workouts_dict.values())}
    
    return jsonify(final_data)
