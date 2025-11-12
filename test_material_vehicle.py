"""
Test Material Vehicle Register and Bulk Entry APIs
"""
import requests
import json
from datetime import datetime
from werkzeug.security import generate_password_hash

# Setup test data
BASE_URL = "http://localhost:8001"

def setup_test_data():
    """Create test user, company, and project"""
    from server.db import SessionLocal
    from server.models import User, Company, Project, ProjectMembership
    
    session = SessionLocal()
    
    try:
        # Check if test user exists
        test_user = session.query(User).filter_by(email='test@example.com').first()
        if not test_user:
            # Create company
            company = Company(
                name="Test Construction Co.",
                subscription_plan="trial",
                active_projects_limit=5,
                billing_status="active"
            )
            session.add(company)
            session.flush()
            
            # Create user
            test_user = User(
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                full_name='Test User',
                phone='+919876543210',
                company_id=company.id,
                is_active=True
            )
            session.add(test_user)
            session.flush()
            
            # Create project
            project = Project(
                name='Test Building Project',
                project_code='TBP-001',
                location='Mumbai, India',
                client_name='Test Client',
                description='Test project for Material Vehicle Register',
                company_id=company.id
            )
            session.add(project)
            session.flush()
            
            # Create project membership (as Quality Engineer)
            membership = ProjectMembership(
                user_id=test_user.id,
                project_id=project.id,
                role='QualityEngineer'
            )
            session.add(membership)
            
            session.commit()
            print(f"✓ Created test user: {test_user.email}")
            print(f"✓ Created test project: {project.name} (ID: {project.id})")
            return test_user.id, project.id
        else:
            # Get existing user's project
            membership = session.query(ProjectMembership).filter_by(user_id=test_user.id).first()
            print(f"✓ Using existing test user: {test_user.email}")
            print(f"✓ Using existing project ID: {membership.project_id if membership else 'None'}")
            return test_user.id, membership.project_id if membership else None
            
    except Exception as e:
        session.rollback()
        print(f"✗ Error setting up test data: {e}")
        return None, None
    finally:
        session.close()

def login(email='test@example.com', password='password123'):
    """Login and get JWT token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✓ Login successful, got token")
        return token
    else:
        print(f"✗ Login failed: {response.status_code} - {response.text}")
        return None

def test_create_vehicle(token, project_id):
    """Test creating a vehicle entry"""
    print("\n=== Test 1: Create RMC Vehicle ===")
    
    vehicle_data = {
        "projectId": project_id,
        "vehicleNumber": "MH-01-1234",
        "vehicleType": "Concrete Mixer",
        "materialType": "Concrete",
        "supplierName": "ABC Concrete Pvt Ltd",
        "challanNumber": "CH-2024-001",
        "driverName": "John Doe",
        "driverPhone": "+919876543210",
        "driverLicense": "MH-01-1234567",
        "purpose": "Slab casting - Building A",
        "allowedTimeHours": 3.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/material-vehicles/create",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 201:
        result = response.json()
        vehicle = result.get('vehicleEntry', result)  # Handle nested or flat response
        print(f"✓ Created vehicle: {vehicle['vehicleNumber']} (ID: {vehicle['id']})")
        return vehicle['id']
    else:
        print(f"✗ Failed to create vehicle: {response.status_code} - {response.text}")
        return None

def test_create_steel_vehicle(token, project_id):
    """Test creating a steel vehicle entry (should NOT trigger time warnings)"""
    print("\n=== Test 2: Create Steel Vehicle (No Time Warning) ===")
    
    vehicle_data = {
        "projectId": project_id,
        "vehicleNumber": "MH-02-5678",
        "vehicleType": "Truck",
        "materialType": "Steel",
        "supplierName": "XYZ Steel Suppliers",
        "challanNumber": "ST-2024-001",
        "driverName": "Jane Smith",
        "driverPhone": "+919876543211",
        "purpose": "Steel delivery"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/material-vehicles/create",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 201:
        result = response.json()
        vehicle = result.get('vehicleEntry', result)  # Handle nested or flat response
        print(f"✓ Created steel vehicle: {vehicle['vehicleNumber']} (ID: {vehicle['id']})")
        return vehicle['id']
    else:
        print(f"✗ Failed to create steel vehicle: {response.status_code} - {response.text}")
        return None

def test_list_vehicles(token, project_id):
    """Test listing vehicles"""
    print("\n=== Test 3: List All Vehicles ===")
    
    response = requests.get(
        f"{BASE_URL}/api/material-vehicles/list",
        params={"projectId": project_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        vehicles = result.get('vehicleEntries', [])
        print(f"✓ Found {len(vehicles)} vehicles")
        for v in vehicles:
            print(f"  - {v['vehicleNumber']}: {v['materialType']} ({v['status']})")
        return vehicles
    else:
        print(f"✗ Failed to list vehicles: {response.status_code}")
        return []

def test_available_vehicles_for_bulk_entry(token, project_id):
    """Test getting available RMC vehicles for bulk entry"""
    print("\n=== Test 4: Get Available Vehicles for Bulk Entry ===")
    
    response = requests.get(
        f"{BASE_URL}/api/bulk-entry/available-vehicles",
        params={"projectId": project_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        vehicles = result.get('vehicles', [])
        print(f"✓ Found {len(vehicles)} available RMC vehicles (Steel should be excluded)")
        for v in vehicles:
            print(f"  - {v['vehicleNumber']}: {v['materialType']}")
        return [v['id'] for v in vehicles]
    else:
        print(f"✗ Failed to get available vehicles: {response.status_code}")
        return []

def test_bulk_entry_preview(token, project_id, vehicle_ids):
    """Test bulk entry preview"""
    print("\n=== Test 5: Preview Bulk Entry ===")
    
    preview_data = {
        "projectId": project_id,
        "vehicleIds": vehicle_ids,
        "totalQuantity": float(len(vehicle_ids))  # 1 m³ per vehicle
    }
    
    response = requests.post(
        f"{BASE_URL}/api/bulk-entry/preview",
        json=preview_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        summary = result.get('summary', {})
        print(f"✓ Preview generated:")
        print(f"  - Total quantity: {summary.get('totalQuantity', 0)} m³")
        print(f"  - Number of batches: {summary.get('totalVehicles', 0)}")
        print(f"  - Quantity per batch: {summary.get('quantityPerVehicle', 0)} m³")
        return True
    else:
        print(f"✗ Failed to preview: {response.status_code} - {response.text}")
        return False

def test_create_batches_from_vehicles(token, project_id, vehicle_ids):
    """Test creating batches from vehicles"""
    print("\n=== Test 6: Create Batches from Vehicles ===")
    
    batch_data = {
        "projectId": project_id,
        "vehicleIds": vehicle_ids,
        "concreteDetails": {
            "vendorName": "ABC Concrete Pvt Ltd",
            "grade": "M45FF",
            "totalQuantity": float(len(vehicle_ids)),
            "location": "Building A / 5th Floor Slab",
            "slump": 100,
            "temperature": 32
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/bulk-entry/create-batches",
        json=batch_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        batches = result.get('batches', [])
        summary = result.get('summary', {})
        print(f"✓ Created {summary.get('batchesCreated', len(batches))} batches")
        print("  Batch details:")
        for batch in batches:
            print(f"  - {batch.get('batchNumber', 'N/A')}: {batch.get('quantity', 0)} m³ (Vehicle: {batch.get('vehicleNumber', 'N/A')})")
        return batches
    else:
        print(f"✗ Failed to create batches: {response.status_code} - {response.text}")
        return []

def test_check_time_limits(token, project_id):
    """Test checking time limits (should only check RMC vehicles)"""
    print("\n=== Test 7: Check Time Limits (RMC Only) ===")
    
    response = requests.post(
        f"{BASE_URL}/api/material-vehicles/check-time-limits",
        json={"projectId": project_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Time check completed")
        print(f"  - Total vehicles checked: {result.get('totalChecked', 0)}")
        print(f"  - Exceeded vehicles: {result.get('exceededCount', 0)}")
        print(f"  - Warnings sent: {result.get('warningsSent', 0)}")
        
        if result.get('exceededVehicles'):
            print("  Exceeded vehicles:")
            for v in result['exceededVehicles']:
                print(f"    - {v['vehicleNumber']}: {v['durationHours']}h (limit: {v['allowedTimeHours']}h)")
        return True
    else:
        print(f"✗ Failed to check time limits: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Material Vehicle Register & Bulk Entry API Tests")
    print("=" * 60)
    
    # Setup test data
    user_id, project_id = setup_test_data()
    if not user_id or not project_id:
        print("✗ Failed to setup test data")
        return
    
    # Login
    token = login()
    if not token:
        print("✗ Failed to login")
        return
    
    # Run tests
    rmc_vehicle_id = test_create_vehicle(token, project_id)
    steel_vehicle_id = test_create_steel_vehicle(token, project_id)
    
    all_vehicles = test_list_vehicles(token, project_id)
    
    rmc_vehicle_ids = test_available_vehicles_for_bulk_entry(token, project_id)
    
    if rmc_vehicle_ids:
        test_bulk_entry_preview(token, project_id, rmc_vehicle_ids)
        batches = test_create_batches_from_vehicles(token, project_id, rmc_vehicle_ids)
    
    test_check_time_limits(token, project_id)
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
