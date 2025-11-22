from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_connection
from app.utils import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        full_name = request.form["full_name"]
        email = request.form["email"]
        
        hashed_password = generate_password_hash(password)
        
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Verificar si el email ya existe
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash("Error: El correo electrónico ya está registrado.")
                conn.close()
                return render_template("register.html")

            cur.execute("INSERT INTO users (username, password, full_name, email) VALUES (%s, %s, %s, %s)", (username, hashed_password, full_name, email))
            new_user_id = cur.lastrowid
            conn.commit()
            
            # Seed exercises for the new user
            try:
                from seed_exercises import seed_exercises
                seed_exercises(new_user_id)
            except Exception as e:
                print(f"Error seeding exercises for user {new_user_id}: {e}")
                
            flash("Registro exitoso, por favor inicia sesión.")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            flash("Error: El usuario ya existe o hubo un problema.")
        finally:
            conn.close()
            
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password, username FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = user[2]
            return redirect(url_for('workouts.workouts'))
        else:
            flash("Usuario o contraseña incorrectos.")
            
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
