import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

def run_verification():
    print("Starting verification...")
    
    # 1. Login with seeded user
    email = "admin@example.com"
    password = "password123"
    
    print(f"Logging in as {email}...")
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return

    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in.")

    # 2. Create Project (if needed, or use default)
    # We'll assume project ID 1 exists or create one
    project_id = 1
    
    # 3. Create Pour Activity with Schedule
    print("Creating Pour Activity...")
    pour_payload = {
        "projectId": project_id,
        "pourDate": datetime.now().isoformat(),
        "location": {
            "buildingName": "Test Building",
            "floorLevel": "L1",
            "zone": "Z1",
            "gridReference": "A-1",
            "structuralElementType": "Slab",
            "elementId": "S-1",
            "description": "Test Slab"
        },
        "concreteType": "PT",
        "designGrade": "M40",
        "totalQuantityPlanned": 10.0,
        "remarks": "Test Pour",
        "cubeSchedule": [
            {"age": 5, "sets": 1},
            {"age": 28, "sets": 1}
        ]
    }
    
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

def run_verification():
    print("Starting verification...")
    
    # 1. Login with seeded user
    email = "admin@example.com"
    password = "password123"
    
    print(f"Logging in as {email}...")
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return

    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in.")

    # 2. Create Project (if needed, or use default)
    # We'll assume project ID 1 exists or create one
    project_id = 1
    
    # 3. Create Pour Activity with Schedule
    print("Creating Pour Activity...")
    pour_payload = {
        "projectId": project_id,
        "pourDate": datetime.now().isoformat(),
        "location": {
            "buildingName": "Test Building",
            "floorLevel": "L1",
            "zone": "Z1",
            "gridReference": "A-1",
            "structuralElementType": "Slab",
            "elementId": "S-1",
            "description": "Test Slab"
        },
        "concreteType": "PT",
        "designGrade": "M40",
        "totalQuantityPlanned": 10.0,
        "remarks": "Test Pour",
        "cubeSchedule": [
            {"age": 5, "sets": 1},
            {"age": 28, "sets": 1}
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/api/pour-activities", json=pour_payload, headers=headers)
    if resp.status_code != 201:
        print(f"Create Pour failed: {resp.text}")
        return
    
    pour_data = resp.json().get("pourActivity")
    pour_id = pour_data.get("id")
    print(f"Pour Activity created: ID {pour_id}")

    # 4. Verify Cube Tests Created
    print("Verifying Cube Tests...")
    resp = requests.get(f"{BASE_URL}/api/cube-tests?project_id={project_id}", headers=headers)
    print(f"Cube Tests Response: {resp.text}")
    
    cube_tests_list = resp.json().get('cube_tests', [])
    
    planned_tests = [t for t in cube_tests_list if t.get('batch_number') == 'Planned']
    
    found_5_day = False
    found_28_day = False
    
    for t in planned_tests:
        # Check testAgeDays (camelCase from to_dict)
        age = t.get('testAgeDays')
        if age == 5:
            found_5_day = True
        if age == 28:
            found_28_day = True
            
    if found_5_day and found_28_day:
        print("SUCCESS: Found planned tests for 5 and 28 days.")
        
        # 5. Record Result for the 5-day test
        print("Recording result for 5-day test...")
        # Find the 5-day test ID
        test_5_day = next((t for t in planned_tests if t.get('testAgeDays') == 5), None)
        
        if test_5_day:
            test_id = test_5_day['id']
            # Simulate Load Input (e.g., 900KN on 150x150mm = 40MPa)
            # 900 * 1000 / 22500 = 40
            result_payload = {
                "project_id": project_id,
                "cube_1_load_kn": 900,
                "cube_2_load_kn": 910,
                "cube_3_load_kn": 890,
                "testing_date": datetime.now().isoformat(),
                "remarks": "Automated Verification Test"
            }
            
            resp = requests.put(f"{BASE_URL}/api/cube-tests/{test_id}", json=result_payload, headers=headers)
            if resp.status_code == 200:
                print("Result recorded successfully.")
                updated_test = resp.json().get('cube_test')
                print(f"Updated Status: {updated_test.get('passFailStatus')}")
                print(f"Avg Strength: {updated_test.get('averageStrengthMpa')} MPa")
                
                if updated_test.get('averageStrengthMpa') > 0:
                    print("SUCCESS: Strength calculated from load.")
                else:
                    print("FAILURE: Strength not calculated.")
            else:
                print(f"Failed to record result: {resp.text}")
        
    else:
        print("FAILURE: Did not find expected planned tests.")
        print(f"Found ages: {[t.get('test_age_days') for t in planned_tests]}")
        print(f"All planned tests: {planned_tests}")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"Verification failed with error: {e}")
