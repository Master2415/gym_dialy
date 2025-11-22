import sys
import os
from app.db import get_connection

def fix_exercises():
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all users
    cur.execute("SELECT id, username FROM users")
    users = cur.fetchall()
    
    for user_id, username in users:
        print(f"Checking user {username} (ID: {user_id})...")
        cur.execute("SELECT COUNT(*) FROM exercises WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        
        if count == 0:
            print(f"  No exercises found. Seeding...")
            from seed_exercises import seed_exercises
            seed_exercises(user_id)
            print(f"  Seeded exercises for {username}.")
        else:
            print(f"  Found {count} exercises.")
            
    conn.close()

if __name__ == "__main__":
    fix_exercises()
