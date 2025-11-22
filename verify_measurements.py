import requests
from bs4 import BeautifulSoup

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

def verify_measurements_page(session):
    print("Verifying /measurements page...")
    response = session.get(f"{BASE_URL}/measurements")
    
    if response.status_code != 200:
        print("FAIL: Failed to access /measurements")
        return False
        
    if "Calculadora de Calorías" not in response.text:
        print("FAIL: Calculator not found")
        return False
        
    if 'id="measurementsChart"' not in response.text:
        print("FAIL: Chart canvas not found")
        return False
        
    print("SUCCESS: Measurements page elements found")
    return True

def verify_add_measurement(session):
    print("Verifying adding measurement...")
    data = {
        "fecha": "2023-10-27",
        "peso": "75.5",
        "cintura": "80",
        "brazos": "35",
        "piernas": "60",
        "pecho": "100",
        "grasa_corporal": "15"
    }
    response = session.post(f"{BASE_URL}/measurements", data=data)
    
    if response.status_code != 200:
        print("FAIL: Failed to post measurement")
        return False
        
    # Check if it appears in the chart data (simple check if the value is in the page source)
    response = session.get(f"{BASE_URL}/measurements")
    if "75.5" not in response.text:
        print("FAIL: Added measurement not found in page source")
        return False
        
    print("SUCCESS: Measurement added and verified")
    return True

def main():
    session = requests.Session()
    try:
        login(session)
        
        if not verify_measurements_page(session):
            print("Measurements page verification failed")
            
        if not verify_add_measurement(session):
            print("Add measurement verification failed")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
