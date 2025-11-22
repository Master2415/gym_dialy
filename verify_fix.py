import mysql.connector
from db import get_connection
import requests

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM workouts")
    workouts = cur.fetchall()
    
    cur.execute("SELECT * FROM exercises")
    exercises = cur.fetchall()
    
    if len(workouts) > 0 and len(exercises) > 0:
        wid = workouts[0][0]
        eid = exercises[0][0]
        print(f"Testing POST to /workouts/{wid}/details with exercise_id={eid}")
        
        try:
            r = requests.post(f"http://localhost:5000/workouts/{wid}/details", data={
                "exercise_id": eid,
                "series": 3,
                "reps": 10,
                "peso": 20,
                "comentario": "Verification test"
            })
            print("Status Code:", r.status_code)
            if r.status_code == 200:
                print("Success! (Redirect or OK)")
            elif r.status_code == 302:
                 print("Success! (Redirected as expected)")
            else:
                print("Failed with status:", r.status_code)
                print("Response:", r.text[:200])
        except Exception as req_err:
            print("Could not connect to app:", req_err)
    else:
        print("Missing workouts or exercises to test with.")

    conn.close()
except Exception as e:
    print("Error:", e)
