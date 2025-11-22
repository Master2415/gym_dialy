
from db import get_connection
import time

def verify_registration_seeding():
    print("Verifying automated exercise seeding...")
    
    # 1. Create a unique username
    username = f"test_user_{int(time.time())}"
    password = "password123"
    
    print(f"Registering user: {username}")
    
    # Simulate registration via direct DB insertion and function call 
    # (Since we can't easily simulate the full Flask request context without running the server)
    # However, to test the actual integration, we should ideally use the app's test client or run the server.
    # For simplicity and speed, let's use the app's test client.
    
    from app import app
    
    with app.test_client() as client:
        response = client.post('/register', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
        
        if response.status_code != 200:
            print(f"Registration failed with status {response.status_code}")
            return

        print("Registration request sent.")
        
        # 2. Verify in database
        conn = get_connection()
        cur = conn.cursor()
        
        # Get user ID
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if not user:
            print("User was not created in DB.")
            conn.close()
            return
            
        user_id = user[0]
        print(f"User created with ID: {user_id}")
        
        # Check exercises
        cur.execute("SELECT COUNT(*) FROM exercises WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        
        print(f"Exercises found for user: {count}")
        
        if count > 0:
            print("SUCCESS: Exercises were automatically seeded!")
        else:
            print("FAILURE: No exercises found for the new user.")
            
        # Cleanup
        print("Cleaning up test user...")
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    verify_registration_seeding()
