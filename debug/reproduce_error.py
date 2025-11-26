import mysql.connector
from db import get_connection
import requests

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM workouts")
    workouts = cur.fetchall()
    print("Workouts count:", len(workouts))
    
    if len(workouts) > 0:
        wid = workouts[0][0]
        print(f"Testing POST to /workouts/{wid}/details without exercise_id")
        # Assuming app is running on port 5000
        try:
            r = requests.post(f"http://localhost:5000/workouts/{wid}/details", data={
                "series": 3,
                "reps": 10,
                "peso": 20,
                "comentario": "test"
            })
            print("Status Code:", r.status_code)
            if r.status_code == 400:
                print("Reproduced 400 Bad Request (likely missing exercise_id)")
            elif r.status_code == 500:
                print("Reproduced 500 Internal Server Error")
            else:
                print("Response:", r.text[:200])
        except Exception as req_err:
            print("Could not connect to app:", req_err)
    else:
        print("No workouts to test with.")
        # Create a dummy workout
        cur.execute("INSERT INTO workouts (notas) VALUES ('Dummy workout')")
        conn.commit()
        print("Created dummy workout. Run again to test.")

    conn.close()
except Exception as e:
    print("Error:", e)
