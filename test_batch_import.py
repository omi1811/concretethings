#!/usr/bin/env python3
"""
Test script for batch import API endpoints

Tests:
1. Quick Entry endpoint
2. Bulk Import endpoint  
3. Template Download endpoint
"""

import requests
import json
import sys
import os
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/batches"

# Test credentials (update with actual test user)
TEST_TOKEN = None  # Will be set after login

def login():
    """Login and get JWT token"""
    global TEST_TOKEN
    
    url = f"{BASE_URL}/api/auth/login"
    payload = {
        "username": "admin",  # Update with test credentials
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            TEST_TOKEN = data.get('token')
            print("✓ Login successful")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False

def test_quick_entry():
    """Test quick entry endpoint"""
    print("\n--- Testing Quick Entry Endpoint ---")
    
    url = f"{API_BASE}/quick-entry"
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "projectId": 1,
        "vehicleNumber": "TEST-QUICK-001",
        "vendorName": "Test Concrete Co.",
        "grade": "M30",
        "quantityReceived": 1.5,
        "deliveryDate": "2025-11-12",
        "deliveryTime": "10:30",
        "slump": 100,
        "temperature": 32,
        "location": "Test Grid A-1",
        "remarks": "Test batch from quick entry"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✓ Quick entry test PASSED")
            return True
        else:
            print("✗ Quick entry test FAILED")
            return False
    except Exception as e:
        print(f"✗ Quick entry test ERROR: {e}")
        return False

def test_template_download():
    """Test template download endpoint"""
    print("\n--- Testing Template Download ---")
    
    url = f"{API_BASE}/import-template?format=xlsx"
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Save template to file for inspection
            with open("test_template.xlsx", "wb") as f:
                f.write(response.content)
            print("✓ Template download test PASSED")
            print("  Template saved as: test_template.xlsx")
            return True
        else:
            print("✗ Template download test FAILED")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Template download test ERROR: {e}")
        return False

def test_bulk_import():
    """Test bulk import endpoint"""
    print("\n--- Testing Bulk Import Endpoint ---")
    
    # First, download template to use as test file
    url_template = f"{API_BASE}/import-template?format=xlsx"
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        response = requests.get(url_template, headers=headers)
        if response.status_code != 200:
            print("✗ Cannot download template for test")
            return False
        
        # Use the template as test file
        files = {
            'file': ('test_batches.xlsx', BytesIO(response.content), 
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        data = {
            'projectId': 1
        }
        
        url_import = f"{API_BASE}/bulk-import"
        response = requests.post(url_import, files=files, data=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('summary', {})
            print(f"\nImport Summary:")
            print(f"  Total Rows: {summary.get('total_rows', 0)}")
            print(f"  Success: {summary.get('success', 0)}")
            print(f"  Errors: {summary.get('errors', 0)}")
            
            if summary.get('errors', 0) > 0:
                print("\nErrors:")
                for error in result.get('errors', []):
                    print(f"  Row {error.get('row')}: {error.get('error')}")
            
            print("✓ Bulk import test PASSED")
            return True
        else:
            print("✗ Bulk import test FAILED")
            return False
    except Exception as e:
        print(f"✗ Bulk import test ERROR: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("--- Checking Dependencies ---")
    
    try:
        import pandas
        print(f"✓ pandas: {pandas.__version__}")
    except ImportError:
        print("✗ pandas not installed")
        return False
    
    try:
        import openpyxl
        print(f"✓ openpyxl: {openpyxl.__version__}")
    except ImportError:
        print("✗ openpyxl not installed")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Batch Import API Tests")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n✗ Missing dependencies. Run: pip install pandas openpyxl")
        sys.exit(1)
    
    # Login
    print("\n--- Logging In ---")
    if not login():
        print("\n✗ Cannot proceed without authentication")
        print("  Update TEST credentials in script")
        sys.exit(1)
    
    # Run tests
    results = []
    
    results.append(("Quick Entry", test_quick_entry()))
    results.append(("Template Download", test_template_download()))
    results.append(("Bulk Import", test_bulk_import()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests PASSED!")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) FAILED")
        sys.exit(1)

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"Server is running at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {BASE_URL}")
        print("  Make sure Flask server is running:")
        print("  python server/app.py")
        sys.exit(1)
    
    main()
