from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.db import get_connection
from app.utils import login_required

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route("/exercises")
@login_required
def index():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, grupo_muscular, nombre FROM exercises WHERE user_id = %s ORDER BY grupo_muscular, nombre", (session['user_id'],))
    exercises = cur.fetchall()
    
    # Group by muscle group
    exercises_by_group = {}
    for ex in exercises:
        # ex = (id, grupo_muscular, nombre)
        group = ex[1]
        if group not in exercises_by_group:
            exercises_by_group[group] = []
        exercises_by_group[group].append(ex)
    
    conn.close()
    return render_template("exercises.html", exercises_by_group=exercises_by_group)

@exercises_bp.route("/exercises/new", methods=["GET", "POST"])
@login_required
def new_exercise():
    if request.method == "POST":
        nombre = request.form["nombre"]
        grupo = request.form["grupo_muscular"]
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO exercises (user_id, nombre, grupo_muscular) VALUES (%s, %s, %s)", 
                    (session['user_id'], nombre, grupo))
        conn.commit()
        conn.close()
        flash("Ejercicio creado correctamente.")
        return redirect(url_for('exercises.index'))
        
    group_param = request.args.get('group')
    return render_template("exercise_form.html", title="Nuevo Ejercicio", exercise=None, selected_group=group_param)

@exercises_bp.route("/exercises/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_exercise(id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, nombre, grupo_muscular FROM exercises WHERE id = %s AND user_id = %s", (id, session['user_id']))
    exercise = cur.fetchone()
    
    if not exercise:
        conn.close()
        flash("Ejercicio no encontrado.")
        return redirect(url_for('exercises.index'))
        
    if request.method == "POST":
        nombre = request.form["nombre"]
        grupo = request.form["grupo_muscular"]
        
        cur.execute("UPDATE exercises SET nombre = %s, grupo_muscular = %s WHERE id = %s", (nombre, grupo, id))
        conn.commit()
        conn.close()
        flash("Ejercicio actualizado correctamente.")
        return redirect(url_for('exercises.index'))
        
    conn.close()
    return render_template("exercise_form.html", title="Editar Ejercicio", exercise=exercise)

@exercises_bp.route("/exercises/delete/<int:id>")
@login_required
def delete_exercise(id):
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if used in workouts
    cur.execute("SELECT COUNT(*) FROM workout_details WHERE exercise_id = %s", (id,))
    count = cur.fetchone()[0]
    
    if count > 0:
        flash("No se puede eliminar este ejercicio porque tiene entrenamientos asociados. Edítalo en su lugar.")
    else:
        cur.execute("DELETE FROM exercises WHERE id = %s AND user_id = %s", (id, session['user_id']))
        conn.commit()
        flash("Ejercicio eliminado correctamente.")
        
    conn.close()
    return redirect(url_for('exercises.index'))
