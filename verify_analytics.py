import requests
from bs4 import BeautifulSoup
import re

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "testuser"
PASSWORD = "password123"

def login(session):
    # Register first to ensure user exists
    session.post(f"{BASE_URL}/register", data={"username": USERNAME, "password": PASSWORD})
    
    # Login
    response = session.post(f"{BASE_URL}/login", data={"username": USERNAME, "password": PASSWORD})
    return response

def verify_analytics_page(session):
    print("Verifying /analytics page...")
    response = session.get(f"{BASE_URL}/analytics")
    
    if response.status_code != 200:
        print("FAIL: Failed to access /analytics")
        return False
        
    if "Récords Personales" not in response.text:
        print("FAIL: PR table not found")
        return False
        
    if 'id="weightChart"' not in response.text:
        print("FAIL: Chart canvas not found")
        return False
        
    if "const chartData =" not in response.text:
        print("FAIL: chartData JS variable not found")
        return False
        
    print("SUCCESS: Analytics page elements found")
    return True

def verify_exercises_seeded(session):
    print("Verifying exercise count in /workouts/new...")
    response = session.get(f"{BASE_URL}/workouts/new")
    
    # Count occurrences of "option value" or check the JS object size
    # A rough check: if we have > 50 exercises, seeding likely worked (default was ~17)
    
    # We can check the JS object: "Pecho": [ ... ]
    # Let's count how many exercise objects { id: ... } are in the source
    matches = re.findall(r'\{ id: \d+, name:', response.text)
    count = len(matches)
    
    print(f"Found {count} exercises available in the form.")
    
    if count > 20:
        print("SUCCESS: Exercise count indicates full seeding")
        return True
    else:
        print("FAIL: Exercise count is low, seeding might have failed")
        return False

def main():
    session = requests.Session()
    try:
        login(session)
        
        if not verify_analytics_page(session):
            print("Analytics verification failed")
            
        if not verify_exercises_seeded(session):
            print("Seeding verification failed")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
