import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"
TEST_USER = "douglas" # Assuming douglas exists
TEST_PASS = "password123" # Assuming password. If not, I'll use the test user I created.

# Let's use the 'advanced_tester' user I created earlier which definitely has exercises
TEST_USER = "advanced_tester"
TEST_PASS = "pass123"

def verify_form():
    session = requests.Session()
    
    # Login
    print(f"Logging in as {TEST_USER}...")
    resp = session.post(f"{BASE_URL}/login", data={"username": TEST_USER, "password": TEST_PASS})
    if "Iniciar Sesión" in resp.text:
        print("Login failed. Trying to register...")
        session.post(f"{BASE_URL}/register", data={"username": TEST_USER, "password": TEST_PASS, "full_name": "Tester", "email": "test@example.com"})
        session.post(f"{BASE_URL}/login", data={"username": TEST_USER, "password": TEST_PASS})
    
    # Get New Workout Page
    print("Fetching /workouts/new...")
    resp = session.get(f"{BASE_URL}/workouts/new")
    
    if "Grupo Muscular:" in resp.text and "Ejercicio:" in resp.text:
        print("SUCCESS: Form elements found.")
        # Check if dropdowns are populated (at least the group one)
        soup = BeautifulSoup(resp.text, 'html.parser')
        group_select = soup.find('select', {'id': 'grupo_muscular'})
        if group_select and len(group_select.find_all('option')) > 1:
            print(f"SUCCESS: Group dropdown has {len(group_select.find_all('option'))} options.")
            return True
        else:
            print("FAIL: Group dropdown is empty or missing options.")
            print(resp.text[:500])
            return False
    else:
        print("FAIL: Form elements NOT found.")
        print("Response snippet:")
        print(resp.text[:500])
        return False

if __name__ == "__main__":
    verify_form()
