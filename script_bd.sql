CREATE DATABASE IF NOT EXISTS gym_diario;

USE gym_diario;

-- ==============================
-- 1. Tabla de usuarios
-- ==============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

-- ==============================
-- 2. Tabla de sesiones del día
-- ==============================
CREATE TABLE workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notas TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ==============================
-- 3. Tabla de ejercicios
-- ==============================
CREATE TABLE exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    grupo_muscular VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ==============================
-- 4. Detalles de cada entrenamiento del día
-- ==============================
CREATE TABLE workout_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workout_id INT NOT NULL,
    exercise_id INT NOT NULL,
    series INT NOT NULL,
    reps INT NOT NULL,
    peso DECIMAL(5, 2),
    comentario VARCHAR(255),
    FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ==============================
-- 5. Tabla de series (sets)
-- ==============================
CREATE TABLE workout_series (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workout_detail_id INT NOT NULL,
    serie_numero INT NOT NULL,
    reps INT NOT NULL,
    peso DECIMAL(5, 2),
    comentario VARCHAR(255),
    FOREIGN KEY (workout_detail_id) REFERENCES workout_details (id) ON DELETE CASCADE
);

-- ==============================
-- 6. Tabla de mediciones corporales
-- ==============================
CREATE TABLE body_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    fecha DATE NOT NULL,
    peso DECIMAL(5, 2),
    cintura DECIMAL(5, 2),
    brazos DECIMAL(5, 2),
    piernas DECIMAL(5, 2),
    pecho DECIMAL(5, 2),
    grasa_corporal DECIMAL(5, 2),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);