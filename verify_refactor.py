import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app import create_app

def verify_app_structure():
    print("Verifying App Structure...")
    try:
        app = create_app()
        client = app.test_client()
        
        # Check if routes are registered
        routes = [str(p) for p in app.url_map.iter_rules()]
        
        required_routes = [
            '/login', '/register', '/workouts', '/analytics', '/export/csv'
        ]
        
        for route in required_routes:
            found = any(route in r for r in routes)
            if not found:
                print(f"FAIL: Route {route} not found")
                return False
                
        print("SUCCESS: App structure and routes verified")
        return True
    except Exception as e:
        print(f"FAIL: Error creating app: {e}")
        return False

if __name__ == "__main__":
    if verify_app_structure():
        print("Refactor verification passed")
    else:
        print("Refactor verification failed")
