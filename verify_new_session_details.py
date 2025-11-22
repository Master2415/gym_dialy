import urllib.request
import urllib.parse
import mysql.connector
from db import get_connection

# Configuration
BASE_URL = "http://localhost:5000"

def verify_new_session_with_details():
    print("Verifying new session with details...")
    
    # 1. Get a valid exercise ID
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM exercises LIMIT 1")
    exercise = cur.fetchone()
    if not exercise:
        print("Error: No exercises found in DB. Cannot test.")
        return
    exercise_id = exercise[0]
    print(f"Using exercise_id: {exercise_id}")
    conn.close()
    
    # 2. Define payload
    payload = {
        "notas": "Verification Session",
        "exercise_id": exercise_id,
        "series": 3,
        "reps": 10,
        "peso": 50.5,
        "comentario": "Test comment"
    }
    data = urllib.parse.urlencode(payload).encode()
    
    # 3. Send POST request
    try:
        req = urllib.request.Request(f"{BASE_URL}/workouts/new", data=data)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("POST request successful (redirected/rendered).")
            else:
                print(f"POST request failed with status: {response.status}")
    except Exception as e:
        print(f"Request failed: {e}")
        return

    # 4. Verify in DB
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM workouts WHERE notas = 'Verification Session' ORDER BY id DESC LIMIT 1")
    workout = cur.fetchone()
    if not workout:
        print("Error: Workout not found in DB.")
        conn.close()
        return
    
    workout_id = workout[0]
    print(f"Created workout_id: {workout_id}")
    
    cur.execute("SELECT * FROM workout_details WHERE workout_id = %s", (workout_id,))
    details = cur.fetchone()
    conn.close()
    
    if details:
        print("Details found in DB:")
        print(f"  Workout ID: {details[1]}")
        print(f"  Exercise ID: {details[2]}")
        print(f"  Series: {details[3]}")
        print(f"  Reps: {details[4]}")
        print(f"  Peso: {details[5]}")
        print(f"  Comentario: {details[6]}")
        
        if (details[2] == exercise_id and 
            details[3] == 3 and 
            details[4] == 10 and 
            float(details[5]) == 50.5 and 
            details[6] == "Test comment"):
            print("SUCCESS: Data matches expected values.")
        else:
            print("FAILURE: Data does not match expected values.")
    else:
        print("FAILURE: No details found for this workout.")

if __name__ == "__main__":
    verify_new_session_with_details()
