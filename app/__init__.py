from flask import Flask
from .db import get_connection

def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_key"  # Change this in production

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.workouts import workouts_bp
    from .routes.analytics import analytics_bp
    from .routes.export import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(export_bp)

    # Initialize DB
    init_db()

    return app

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Tabla de usuarios
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

    # Tabla de ejercicios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            grupo_muscular VARCHAR(50),
            nombre VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Tabla de entrenamientos (sesiones)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            notas TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Tabla de detalles del entrenamiento
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
    
    # Tabla de mediciones corporales
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
