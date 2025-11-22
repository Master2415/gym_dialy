import requests
from bs4 import BeautifulSoup
import csv
import io

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "douglas" # Assuming douglas exists and has data, or we use the test user created before
PASSWORD = "password123" # We might need to reset password or use the one we know. 
# Actually, let's use the test user flow to be safe, as we deleted others but 'douglas' password is unknown to me.
# Wait, I deleted everyone EXCEPT douglas. I should register a new user to test.

TEST_USER = "advanced_tester"
TEST_PASS = "pass123"
TEST_EMAIL = "advanced@test.com"

def login_or_register(session):
    # Try login first
    response = session.post(f"{BASE_URL}/login", data={"username": TEST_USER, "password": TEST_PASS})
    if "Iniciar Sesión" in response.text: # Failed login
        # Register
        data = {
            "username": TEST_USER, 
            "password": TEST_PASS,
            "full_name": "Advanced Tester",
            "email": TEST_EMAIL
        }
        session.post(f"{BASE_URL}/register", data=data)
        # Login again
        session.post(f"{BASE_URL}/login", data={"username": TEST_USER, "password": TEST_PASS})
        
    # Create a dummy workout to ensure data exists for analytics
    # First get an exercise ID (assuming seed_exercises ran)
    # We can just pick ID 1, usually Squat or something common if seeded.
    # But we need to be sure. Let's just post a workout with exercise_id=1
    data = {
        "notas": "Test Workout",
        "exercise_id": "1",
        "series": "3",
        "reps": "10",
        "peso": "100",
        "comentario": "Light weight"
    }
    session.post(f"{BASE_URL}/workouts/new", data=data)

def verify_dashboard(session):
    print("Verifying Dashboard...")
    response = session.get(f"{BASE_URL}/workouts")
    if "Días Entrenados" not in response.text:
        print("FAIL: Dashboard stats not found")
        return False
    print("SUCCESS: Dashboard found")
    return True

def verify_filters(session):
    print("Verifying Filters...")
    # Just check if inputs exist
    response = session.get(f"{BASE_URL}/workouts")
    soup = BeautifulSoup(response.text, 'html.parser')
    if not soup.find('input', {'name': 'search'}):
        print("FAIL: Search input not found")
        return False
    if not soup.find('select', {'name': 'sort'}):
        print("FAIL: Sort select not found")
        return False
    print("SUCCESS: Filters found")
    return True

def verify_analytics_advanced(session):
    print("Verifying Advanced Analytics...")
    response = session.get(f"{BASE_URL}/analytics")
    
    if "1RM Est." not in response.text:
        print("FAIL: 1RM column not found in Analytics")
        print(f"Page Title: {BeautifulSoup(response.text, 'html.parser').title.string}")
        print(f"Snippet: {response.text[:500]}")
        return False
    if "volumeChart" not in response.text:
        print("FAIL: Volume chart not found")
        return False
    print("SUCCESS: Advanced Analytics found")
    return True

def verify_export_enhanced(session):
    print("Verifying Enhanced Export...")
    response = session.get(f"{BASE_URL}/export/csv")
    content = response.content.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    if "1RM Estimado" not in header or "Volumen" not in header:
        print(f"FAIL: New columns missing in CSV. Header: {header}")
        return False
    print("SUCCESS: Enhanced Export verified")
    return True

def main():
    session = requests.Session()
    try:
        login_or_register(session)
        
        if not verify_dashboard(session):
            print("Dashboard verification failed")
        
        if not verify_filters(session):
            print("Filters verification failed")
            
        if not verify_analytics_advanced(session):
            print("Analytics verification failed")
            
        if not verify_export_enhanced(session):
            print("Export verification failed")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
