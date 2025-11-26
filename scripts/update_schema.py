import mysql.connector
from app.db import get_connection

def update_schema():
    print("Connecting to database...")
    conn = get_connection()
    cur = conn.cursor()

    print("Creating workout_series table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workout_series (
        id INT AUTO_INCREMENT PRIMARY KEY,
        workout_detail_id INT NOT NULL,
        serie_numero INT NOT NULL,
        reps INT NOT NULL,
        peso DECIMAL(5,2),
        comentario VARCHAR(255),
        FOREIGN KEY (workout_detail_id) REFERENCES workout_details(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Schema updated successfully.")

if __name__ == "__main__":
    update_schema()
