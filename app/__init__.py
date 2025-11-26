from flask import Flask
from .db import get_connection
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key")  # Change this in production

    # Configure OAuth
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
    app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.workouts import workouts_bp
    from .routes.analytics import analytics_bp
    from .routes.export import export_bp
    from .routes.exercises import exercises_bp
    from .routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(settings_bp)

    # Initialize DB
    init_db()

    return app

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    db_type = os.environ.get("DB_TYPE", "mysql")
    
    if db_type == "sqlite":
        # Enable foreign keys for SQLite
        cur.execute("PRAGMA foreign_keys = ON")
        
        # SQLite Tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                email TEXT UNIQUE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                grupo_muscular TEXT,
                nombre TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                notas TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                series INTEGER,
                reps INTEGER,
                peso REAL,
                comentario TEXT,
                FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_detail_id INTEGER NOT NULL,
                serie_numero INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                peso REAL,
                comentario TEXT,
                FOREIGN KEY (workout_detail_id) REFERENCES workout_details(id) ON DELETE CASCADE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS body_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                peso REAL,
                cintura REAL,
                brazos REAL,
                piernas REAL,
                pecho REAL,
                grasa_corporal REAL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
    else:
        # MySQL Tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        
        # Verificar si existen las columnas nuevas, si no, agregarlas
        cur.execute("SHOW COLUMNS FROM users LIKE 'full_name'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(100)")
            
        cur.execute("SHOW COLUMNS FROM users LIKE 'email'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100) UNIQUE")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                grupo_muscular VARCHAR(50),
                nombre VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                notas TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                workout_id INT NOT NULL,
                exercise_id INT NOT NULL,
                series INT,
                reps INT,
                peso DECIMAL(5,2),
                comentario TEXT,
                FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_series (
                id INT AUTO_INCREMENT PRIMARY KEY,
                workout_detail_id INT NOT NULL,
                serie_numero INT NOT NULL,
                reps INT NOT NULL,
                peso DECIMAL(5,2),
                comentario VARCHAR(255),
                FOREIGN KEY (workout_detail_id) REFERENCES workout_details(id) ON DELETE CASCADE
            )
        """)
        
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
