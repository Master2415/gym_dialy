import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

def verify_fixes():
    session = requests.Session()

    print("1. Creating a new session with empty notes...")
    # Simulate form submission
    response = session.post(f"{BASE_URL}/workouts/new", data={"notas": ""})
    if response.status_code != 200: # Redirects are followed by default in requests, but let's check history if needed or just final page
        pass # requests follows redirects by default and returns 200 for the final page usually

    # Check if the new session appears on the main page
    response = session.get(f"{BASE_URL}/workouts")
    soup = BeautifulSoup(response.text, "html.parser")
    
    # We expect to find a row with "-" in the notes column (2nd column, index 1) and "-" in exercise columns
    rows = soup.find_all("tr")[1:] # Skip header
    found_new_session = False
    new_session_id = None
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 8:
            # notes is col 1
            # exercise is col 3
            if cols[1].text.strip() == "-" and cols[3].text.strip() == "-":
                found_new_session = True
                # Extract ID from edit link: /workouts/edit/123
                edit_link = row.find("a", href=True, string="Editar")['href']
                new_session_id = edit_link.split("/")[-1]
                print(f"   Found new session with ID: {new_session_id}")
                break
    
    if not found_new_session:
        print("   FAIL: New session with empty notes not found or defaults not applied.")
        return

    print("2. Adding details with empty fields...")
    if new_session_id:
        # Get a valid exercise ID first (assuming seed data exists or we can pick one)
        # For this test, we'll just try to post. If no exercises, we might fail, but let's assume there's at least one.
        # Let's fetch the details page to get an exercise ID
        details_page = session.get(f"{BASE_URL}/workouts/{new_session_id}/details")
        details_soup = BeautifulSoup(details_page.text, "html.parser")
        options = details_soup.find_all("option")
        if options:
            exercise_id = options[0]['value']
            
            post_data = {
                "exercise_id": exercise_id,
                "series": "",
                "reps": "",
                "peso": "",
                "comentario": ""
            }
            session.post(f"{BASE_URL}/workouts/{new_session_id}/details", data=post_data)
            
            # Verify on main page
            response = session.get(f"{BASE_URL}/workouts")
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")[1:]
            found_details = False
            for row in rows:
                cols = row.find_all("td")
                # check if this row corresponds to our session and has 0s
                # We might have multiple rows for the same session now, but let's look for the one with the exercise
                # We can't easily identify the exact row without more unique data, but let's check if ANY row has 0 series/reps/peso and "-" comment
                if cols[4].text.strip() == "0" and cols[5].text.strip() == "0" and cols[7].text.strip() == "-":
                     found_details = True
                     break
            
            if found_details:
                print("   SUCCESS: Details added with defaults (0 and -).")
            else:
                print("   FAIL: Details defaults not applied correctly.")
        else:
            print("   SKIP: No exercises found to test adding details.")

    print("3. Editing session notes...")
    if new_session_id:
        # Check if pre-filled
        edit_page = session.get(f"{BASE_URL}/workouts/edit/{new_session_id}")
        edit_soup = BeautifulSoup(edit_page.text, "html.parser")
        textarea = edit_soup.find("textarea", {"name": "notas"})
        if textarea and textarea.text.strip() == "-":
             print("   SUCCESS: Edit form pre-filled correctly with '-'.")
        else:
             print(f"   FAIL: Edit form not pre-filled correctly. Found: '{textarea.text if textarea else 'None'}'")

        # Update notes
        new_note = "Updated Note Test"
        session.post(f"{BASE_URL}/workouts/edit/{new_session_id}", data={"notas": new_note})
        
        # Verify update
        response = session.get(f"{BASE_URL}/workouts")
        if new_note in response.text:
            print("   SUCCESS: Session note updated.")
        else:
            print("   FAIL: Session note update not reflected.")

    # Cleanup (optional, but good practice)
    if new_session_id:
        print("4. Cleaning up...")
        session.get(f"{BASE_URL}/workouts/delete/{new_session_id}")
        print("   Cleanup done.")

if __name__ == "__main__":
    try:
        verify_fixes()
    except Exception as e:
        print(f"An error occurred: {e}")
