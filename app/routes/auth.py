from flask import Blueprint, render_template, request, redirect, session, flash, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_connection
from app.utils import login_required
from authlib.integrations.flask_client import OAuth
import secrets

auth_bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with app context"""
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={'scope': 'openid email profile'}
    )

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
                from scripts.seed_exercises import seed_exercises
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

@auth_bp.route("/login/google")
def google_login():
    """Initiate Google OAuth login"""
    # Initialize OAuth if not already done
    if 'google' not in oauth._clients:
        init_oauth(current_app)
    
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/auth/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Initialize OAuth if not already done
        if 'google' not in oauth._clients:
            init_oauth(current_app)
        
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            flash("Error al obtener información de Google.")
            return redirect(url_for('auth.login'))
        
        email = user_info.get('email')
        full_name = user_info.get('name', email.split('@')[0])
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT id, username FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user:
            # User exists, log them in
            session['user_id'] = user[0]
            session['username'] = user[1]
        else:
            # Create new user
            username = email.split('@')[0]
            # Generate a random password (user won't need it for Google login)
            random_password = generate_password_hash(secrets.token_urlsafe(32))
            
            try:
                cur.execute(
                    "INSERT INTO users (username, password, full_name, email) VALUES (%s, %s, %s, %s)",
                    (username, random_password, full_name, email)
                )
                new_user_id = cur.lastrowid
                conn.commit()
                
                # Seed exercises for new user
                try:
                    from scripts.seed_exercises import seed_exercises
                    seed_exercises(new_user_id)
                except Exception as e:
                    print(f"Error seeding exercises for user {new_user_id}: {e}")
                
                session['user_id'] = new_user_id
                session['username'] = username
                flash("¡Bienvenido! Tu cuenta ha sido creada.")
            except Exception as e:
                print(f"Error creating user: {e}")
                flash("Error al crear la cuenta. El nombre de usuario puede estar en uso.")
                conn.close()
                return redirect(url_for('auth.login'))
        
        conn.close()
        return redirect(url_for('workouts.workouts'))
        
    except Exception as e:
        print(f"OAuth error: {e}")
        flash("Error durante la autenticación con Google.")
        return redirect(url_for('auth.login'))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
