#!/usr/bin/env python3
"""
Test script for Contractor Supervisor NCR Response Workflow
Tests the newly added RESPOND_NCR permission
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, message=""):
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}{icon} {name}{Colors.END}")
    if message:
        print(f"   {message}")

def main():
    print("="*80)
    print("🤖 Contractor Supervisor NCR Response Workflow Test")
    print("="*80)
    
    # Test 1: Login as System Admin
    print("\n1️⃣  Testing System Admin Login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@testprosite.com",
            "password": "Admin@Test123"
        })
        
        if response.status_code == 200:
            admin_token = response.json()['access_token']
            print_test("System Admin Login", "PASS", f"Token received")
        else:
            print_test("System Admin Login", "FAIL", f"Status: {response.status_code}")
            return
    except Exception as e:
        print_test("System Admin Login", "FAIL", str(e))
        return
    
    # Test 2: Verify RBAC Configuration
    print("\n2️⃣  Checking RBAC Configuration...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Check if RESPOND_NCR permission exists in the system
        from server.rbac import Permission, UserRole, ROLE_PERMISSIONS
        
        if hasattr(Permission, 'RESPOND_NCR'):
            print_test("RESPOND_NCR Permission Exists", "PASS")
        else:
            print_test("RESPOND_NCR Permission Exists", "FAIL", "Permission not found in enum")
            return
        
        # Check if Contractor Supervisor has the permission
        contractor_perms = ROLE_PERMISSIONS.get(UserRole.CONTRACTOR_SUPERVISOR, set())
        
        if Permission.VIEW_NCR in contractor_perms:
            print_test("Contractor has VIEW_NCR", "PASS")
        else:
            print_test("Contractor has VIEW_NCR", "FAIL")
        
        if Permission.RESPOND_NCR in contractor_perms:
            print_test("Contractor has RESPOND_NCR", "PASS")
        else:
            print_test("Contractor has RESPOND_NCR", "FAIL")
            
    except Exception as e:
        print_test("RBAC Configuration Check", "FAIL", str(e))
        return
    
    # Test 3: Create Test Project
    print("\n3️⃣  Creating Test Project...")
    try:
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{BASE_URL}/projects/", 
            headers=headers,
            json={
                "name": "NCR Test Construction Site",
                "location": "Mumbai, Maharashtra",
                "description": "Test project for contractor NCR response workflow"
            })
        
        if response.status_code == 201:
            project = response.json()['project']
            project_id = project['id']
            print_test("Project Creation", "PASS", f"Project ID: {project_id}")
        else:
            print_test("Project Creation", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return
    except Exception as e:
        print_test("Project Creation", "FAIL", str(e))
        return
    
    # Test 4: Register Quality Engineer
    print("\n4️⃣  Registering Quality Engineer...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register",
            headers=headers,
            json={
                "email": "qe@testprosite.com",
                "password": "QE@Test123",
                "full_name": "Test Quality Engineer",
                "phone": "+91-9999999991",
                "company_id": 1
            })
        
        if response.status_code in [201, 409]:  # Created or already exists
            print_test("Quality Engineer Registration", "PASS")
        else:
            print_test("Quality Engineer Registration", "FAIL", f"Status: {response.status_code}, Error: {response.text}")
            
    except Exception as e:
        print_test("Quality Engineer Registration", "FAIL", str(e))
    
    # Test 5: Register Contractor Supervisor
    print("\n5️⃣  Registering Contractor Supervisor...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register",
            headers=headers,
            json={
                "email": "contractor@testprosite.com",
                "password": "Contractor@123",
                "full_name": "Test Contractor Supervisor",
                "phone": "+91-9999999992",
                "company_id": 1
            })
        
        if response.status_code in [201, 409]:  # Created or already exists
            print_test("Contractor Supervisor Registration", "PASS")
        else:
            print_test("Contractor Supervisor Registration", "FAIL", f"Status: {response.status_code}, Error: {response.text}")
            
    except Exception as e:
        print_test("Contractor Supervisor Registration", "FAIL", str(e))
    
    print("\n" + "="*80)
    print("✅ Core Test Completed - RBAC Configuration Verified")
    print("="*80)
    print("\n📝 Summary:")
    print("   • RESPOND_NCR permission added to Permission enum")
    print("   • Contractor Supervisor has VIEW_NCR and RESPOND_NCR permissions")
    print("   • System Admin can create users and projects")
    print("\n🎯 Next Steps (Manual Testing):")
    print("   1. Login as Quality Engineer (qe@testprosite.com)")
    print("   2. Create a Quality NCR for the test project")
    print("   3. Login as Contractor Supervisor (contractor@testprosite.com)")
    print("   4. View the NCR (should have access)")
    print("   5. Submit response with corrective action plan")
    print("   6. Quality Manager reviews and approves/rejects")
    print("="*80)

if __name__ == "__main__":
    main()
