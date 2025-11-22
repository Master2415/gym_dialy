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

def verify_exercise_grouping(session):
    print("Verifying exercise grouping in /workouts/new...")
    response = session.get(f"{BASE_URL}/workouts/new")
    
    if response.status_code != 200:
        print("Failed to access /workouts/new")
        return False
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for muscle group select
    grupo_select = soup.find('select', {'id': 'grupo_muscular'})
    if not grupo_select:
        print("FAIL: Muscle group select not found")
        return False
        
    # Check for exercise select
    exercise_select = soup.find('select', {'id': 'exercise_id'})
    if not exercise_select:
        print("FAIL: Exercise select not found")
        return False
        
    # Check for JavaScript data object
    if "const exercisesData =" not in response.text:
        print("FAIL: exercisesData JS object not found")
        return False
        
    print("SUCCESS: Exercise grouping elements found")
    return True

def verify_details_button_removed(session):
    print("Verifying details button removal in /workouts...")
    response = session.get(f"{BASE_URL}/workouts")
    
    if "📄" in response.text:
        print("FAIL: Details button (📄) still present")
        return False
        
    print("SUCCESS: Details button removed")
    return True

def verify_calendar_present(session):
    print("Verifying calendar in /workouts...")
    response = session.get(f"{BASE_URL}/workouts")
    
    if 'id="calendar"' not in response.text:
        print("FAIL: Calendar container not found")
        return False
        
    if "const workoutDates =" not in response.text:
        print("FAIL: workoutDates JS variable not found")
        return False
        
    print("SUCCESS: Calendar elements found")
    return True

def main():
    session = requests.Session()
    try:
        login(session)
        
        if not verify_exercise_grouping(session):
            print("Exercise grouping verification failed")
        
        if not verify_details_button_removed(session):
            print("Details button removal verification failed")
            
        if not verify_calendar_present(session):
            print("Calendar verification failed")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
