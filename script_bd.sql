CREATE DATABASE IF NOT EXISTS gym_diario;
USE gym_diario;

-- ==============================
-- 1. Tabla de usuarios
-- ==============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- ==============================
-- 2. Tabla de sesiones del día
-- ==============================
CREATE TABLE workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT NOW(),
    notas TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==============================
-- 3. Tabla de ejercicios
-- ==============================
CREATE TABLE exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    grupo_muscular VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
    peso DECIMAL(5,2),
    comentario VARCHAR(255),

    FOREIGN KEY (workout_id) REFERENCES workouts(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
