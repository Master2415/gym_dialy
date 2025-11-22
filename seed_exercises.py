import mysql.connector
from db import get_connection

def seed_exercises(user_id=None):
    exercises = [
        # PECHO - Ya tienes buenos
        ("Pecho", "Press de Banca plano"),
        ("Pecho", "Press de Banca inclinado"),
        ("Pecho", "Press de Banca declinado"),
        ("Pecho", "Poleas pecho"),
        ("Pecho", "Aperturas"),
        ("Pecho", "Aperturas con mancuernas"),  # NUEVO
        ("Pecho", "Press con mancuernas"),  # NUEVO
        ("Pecho", "Flexiones"),  # NUEVO
        
        # ESPALDA - Buenos básicos
        ("Espalda", "Dominadas"),
        ("Espalda", "Remo con Barra"),
        ("Espalda", "Polea abierta"),
        ("Espalda", "Polea cerrada"),
        ("Espalda", "Remo con mancuerna"),  # NUEVO
        ("Espalda", "Pullover"),  # NUEVO
        ("Espalda", "Face pull"),  # NUEVO
        ("Espalda", "Remo en maquina"),  # NUEVO
        
        # PIERNA - Muy completa
        ("Pierna", "Sentadilla libre"),
        ("Pierna", "Bulgara"),
        ("Pierna", "Extensión"),  # Corregido
        ("Pierna", "Haka"),
        ("Pierna", "Prensa"),
        ("Pierna", "Isquiotibiales acostado"),
        ("Pierna", "Isquiotibiales sentado"),
        ("Pierna", "Aductores"),  # Corregido
        ("Pierna", "Peso muerto"),
        ("Pierna", "Zancadas"),  # NUEVO
        ("Pierna", "Peso muerto rumano"),  # NUEVO
        ("Pierna", "Hack squat"),  # NUEVO
        
        # PANTORRILLAS
        ("Pantorrillas", "De pie"),
        ("Pantorrillas", "Sentado"),  # Corregido
        ("Pantorrillas", "En prensa"),  # NUEVO
        
        # GLÚTEOS
        ("Glúteos", "Hip thrust"),  # Corregido
        ("Glúteos", "Patada de glúteo"),  # NUEVO
        ("Glúteos", "Abducción de cadera"),  # NUEVO
        ("Glúteos", "Puente de glúteo"),  # NUEVO
        
        # HOMBRO - Necesita más variedad
        ("Hombro", "Press Militar"),
        ("Hombro", "Elevaciones Laterales"),
        ("Hombro", "Elevaciones frontales"),  # NUEVO
        ("Hombro", "Pájaros"),  # NUEVO (deltoides posterior)
        ("Hombro", "Press con mancuernas"),  # NUEVO
        ("Hombro", "Press Arnold"),  # NUEVO
        ("Hombro", "Remo al mentón"),  # NUEVO
        
        # BÍCEPS - Muy limitado
        ("Bíceps", "Curl con Barra"),
        ("Bíceps", "Curl con mancuernas"),  # NUEVO
        ("Bíceps", "Curl martillo"),  # NUEVO
        ("Bíceps", "Curl concentrado"),  # NUEVO
        ("Bíceps", "Curl predicador"),  # NUEVO
        ("Bíceps", "Curl en polea"),  # NUEVO
        
        # TRÍCEPS - Muy limitado
        ("Tríceps", "Fondos"),
        ("Tríceps", "Press francés"),  # NUEVO
        ("Tríceps", "Extensiones en polea"),  # NUEVO
        ("Tríceps", "Patada de tríceps"),  # NUEVO
        ("Tríceps", "Press cerrado"),  # NUEVO
        ("Tríceps", "Fondos en banco"),  # NUEVO
        
        # ABDOMEN - Muy limitado
        ("Abdomen", "Crunches"),
        ("Abdomen", "Plancha"),  # NUEVO
        ("Abdomen", "Elevación de piernas"),  # NUEVO
        ("Abdomen", "Bicicleta"),  # NUEVO
        ("Abdomen", "Ab wheel"),  # NUEVO
        ("Abdomen", "Russian twist"),  # NUEVO
        ("Abdomen", "Plancha lateral"),  # NUEVO
        
        # CARDIO - Falta completamente
        ("Cardio", "Caminadora"),  # NUEVO
        ("Cardio", "Elíptica"),  # NUEVO
        ("Cardio", "Bicicleta"),  # NUEVO
        ("Cardio", "Remo"),  # NUEVO
        ("Cardio", "Saltar cuerda"),  # NUEVO
        
        # ANTEBRAZO - Falta completamente
        ("Antebrazo", "Curl de muñeca"),  # NUEVO
        ("Antebrazo", "Curl invertido"),  # NUEVO
        ("Antebrazo", "Farmer walk"),  # NUEVO
    
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
        
        # Get existing exercises for this user
        cur.execute("SELECT grupo_muscular, nombre FROM exercises WHERE user_id = %s", (target_user_id,))
        existing_exercises = set((row[0], row[1]) for row in cur.fetchall())
        
        exercises_to_add = []
        for group, name in exercises:
            if (group, name) not in existing_exercises:
                exercises_to_add.append((target_user_id, group, name))
        
        if exercises_to_add:
            print(f"Adding {len(exercises_to_add)} new exercises for user ID {target_user_id}...")
            cur.executemany("INSERT INTO exercises (user_id, grupo_muscular, nombre) VALUES (%s, %s, %s)", exercises_to_add)
            conn.commit()
            print("Done.")
        else:
            print(f"User {target_user_id} already has all exercises.")
            
        conn.close()
    except Exception as e:
        print(f"Error seeding exercises: {e}")

if __name__ == "__main__":
    seed_exercises()
