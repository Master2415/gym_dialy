import requests
import csv
import io
import json

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

def verify_csv_export(session):
    print("Verifying CSV export...")
    response = session.get(f"{BASE_URL}/export/csv")
    
    if response.status_code != 200:
        print("FAIL: Failed to download CSV")
        return False
        
    if 'text/csv' not in response.headers['Content-Type']:
        print(f"FAIL: Incorrect Content-Type: {response.headers['Content-Type']}")
        return False
        
    # Parse CSV
    try:
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        if header[0] != 'Fecha':
            print("FAIL: Incorrect CSV header")
            return False
    except Exception as e:
        print(f"FAIL: Error parsing CSV: {e}")
        return False
        
    print("SUCCESS: CSV export verified")
    return True

def verify_json_export(session):
    print("Verifying JSON export...")
    response = session.get(f"{BASE_URL}/export/json")
    
    if response.status_code != 200:
        print("FAIL: Failed to download JSON")
        return False
        
    if response.headers['Content-Type'] != 'application/json':
        print(f"FAIL: Incorrect Content-Type: {response.headers['Content-Type']}")
        return False
        
    # Parse JSON
    try:
        data = response.json()
        if 'workouts' not in data:
            print("FAIL: JSON does not contain 'workouts' key")
            return False
    except Exception as e:
        print(f"FAIL: Error parsing JSON: {e}")
        return False
        
    print("SUCCESS: JSON export verified")
    return True

def main():
    session = requests.Session()
    try:
        login(session)
        
        if not verify_csv_export(session):
            print("CSV verification failed")
            
        if not verify_json_export(session):
            print("JSON verification failed")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
