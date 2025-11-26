import mysql.connector
from db import get_connection

try:
    conn = get_connection()
    print("Connection successful")
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print("Tables:", tables)
    
    cur.execute("SELECT * FROM exercises")
    exercises = cur.fetchall()
    print("Exercises count:", len(exercises))
    
    conn.close()
except Exception as e:
    print("Error:", e)
