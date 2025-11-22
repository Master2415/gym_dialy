import requests
import random
import string

# Configuration
BASE_URL = "http://127.0.0.1:5000"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def verify_db_cleanup():
    # This requires running a python command on the server side, or we can assume if we can login as douglas it's fine.
    # But to verify DELETION, we'd need to check the DB directly.
    # Since I can run commands, I'll do that in the main execution flow, but here I'll test the web app behavior.
    pass

def verify_registration_flow():
    print("Verifying registration flow...")
    session = requests.Session()
    
    username = f"user_{generate_random_string()}"
    email = f"{username}@example.com"
    password = "password123"
    full_name = "Test User"
    
    # 1. Register
    data = {
        "username": username,
        "password": password,
        "full_name": full_name,
        "email": email
    }
    response = session.post(f"{BASE_URL}/register", data=data)
    
    if response.status_code != 200:
        print("FAIL: Registration request failed")
        return False
        
    # Check if redirected to login or success message
    if "Registro exitoso" not in response.text and "Inicia Sesión" not in response.text:
        print("FAIL: Registration might have failed (success message not found)")
        # print(response.text) # Debug
        return False
        
    print("SUCCESS: Registration successful")
    
    # 2. Try to register again with SAME email
    print("Verifying duplicate email check...")
    response = session.post(f"{BASE_URL}/register", data=data)
    
    if "El correo electrónico ya está registrado" not in response.text:
        print("FAIL: Duplicate email check failed")
        return False
        
    print("SUCCESS: Duplicate email check passed")
    return True

def main():
    try:
        if not verify_registration_flow():
            print("Auth verification failed")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
