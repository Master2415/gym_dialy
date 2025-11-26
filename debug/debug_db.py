from app.db import get_connection
import json

def debug_workout(workout_id):
    print(f"--- Debugging Workout ID: {workout_id} ---")
    conn = get_connection()
    cur = conn.cursor()

    # 1. Check Workout
    print("\n[Table: workouts]")
    cur.execute("SELECT * FROM workouts WHERE id = %s", (workout_id,))
    workout = cur.fetchone()
    if workout:
        # Assuming columns: id, user_id, fecha, notas, created_at... (need to verify schema by printing)
        # But fetchone returns a tuple. Let's get column names too.
        col_names = [desc[0] for desc in cur.description]
        print(dict(zip(col_names, workout)))
    else:
        print("Workout not found!")
        return

    # 2. Check Workout Details
    print("\n[Table: workout_details]")
    cur.execute("SELECT * FROM workout_details WHERE workout_id = %s", (workout_id,))
    details = cur.fetchall()
    detail_ids = []
    if details:
        col_names = [desc[0] for desc in cur.description]
        for d in details:
            d_dict = dict(zip(col_names, d))
            print(d_dict)
            detail_ids.append(d_dict['id'])
    else:
        print("No details found for this workout.")

    # 3. Check Workout Series
    if detail_ids:
        print("\n[Table: workout_series]")
        for did in detail_ids:
            print(f"Details for Detail ID {did}:")
            cur.execute("SELECT * FROM workout_series WHERE workout_detail_id = %s ORDER BY serie_numero", (did,))
            series = cur.fetchall()
            if series:
                col_names = [desc[0] for desc in cur.description]
                for s in series:
                    print(dict(zip(col_names, s)))
            else:
                print("No series found.")

    conn.close()
    print("\n--- End Debug ---")

if __name__ == "__main__":
    # We need to mock session or just run this standalone if db connection doesn't depend on flask context
    # app.db.get_connection usually just connects to mysql.
    try:
        debug_workout(22)
    except Exception as e:
        print(f"Error: {e}")
