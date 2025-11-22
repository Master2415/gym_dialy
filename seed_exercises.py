import mysql.connector
from db import get_connection

def seed_exercises(user_id=None):
    exercises = [
        ("Pecho", "Press de Banca"),
        ("Pecho", "Press de Banca inclinado"),
        ("Pecho", "Press de Banca declinado"),
        ("Pecho", "Poleas pecho"),
        ("Pecho", "Aperturas"),
        ("Espalda", "Dominadas"),
        ("Espalda", "Remo con Barra"),
        ("Pierna", "Sentadilla"),
        ("Pierna", "Bulgara"),
        ("Pierna", "Extencion"),
        ("Pierna", "Haka"),
        ("Pierna", "Prensa"),
        ("Hombro", "Press Militar"),
        ("Hombro", "Elevaciones Laterales"),
        ("Bíceps", "Curl con Barra"),
        ("Tríceps", "Fondos"),
        ("Abdomen", "Crunches")
    ]

    try:
        conn = get_connection()
        cur = conn.cursor()
        
        target_user_id = user_id
        
        # If no user_id provided, get the first user
        if target_user_id is None:
            cur.execute("SELECT id FROM users LIMIT 1")
            user = cur.fetchone()
            
            if not user:
                print("Error: No users found. Please register a user first.")
                conn.close()
                return
            target_user_id = user[0]
        
        # Check if exercises already exist for this user
        cur.execute("SELECT COUNT(*) FROM exercises WHERE user_id = %s", (target_user_id,))
        count = cur.fetchone()[0]
        
        if count == 0:
            print(f"Seeding exercises for user ID {target_user_id}...")
            # Prepare data with user_id
            exercises_with_user = [(target_user_id, group, name) for group, name in exercises]
            
            cur.executemany("INSERT INTO exercises (user_id, grupo_muscular, nombre) VALUES (%s, %s, %s)", exercises_with_user)
            conn.commit()
            print(f"Inserted {cur.rowcount} exercises.")
        else:
            print(f"Exercises table already has {count} entries for user {target_user_id}. Skipping seed.")
            
        conn.close()
    except Exception as e:
        print(f"Error seeding exercises: {e}")

if __name__ == "__main__":
    seed_exercises()
