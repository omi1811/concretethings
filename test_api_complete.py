#!/usr/bin/env python3
"""
Comprehensive API Test Suite for ConcreteThings QMS

Tests all 8 API modules:
1. Authentication
2. RMC Vendor Management
3. Batch Register
4. Cube Test Register
5. Third-Party Lab Management
6. Third-Party Cube Test
7. Material Management
8. Material Test Register
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"
TEST_EMAIL = "admin@demo.com"
TEST_PASSWORD = "adminpass"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")


def test_health():
    """Test main health endpoint"""
    print_test("Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print_success(f"Health check passed: {response.json()}")
        return True
    else:
        print_error(f"Health check failed: {response.status_code}")
        return False


def test_auth():
    """Test authentication endpoints"""
    print_test("Authentication")
    
    # Test login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print_success(f"Login successful")
        print_info(f"Token: {token[:50]}...")
        return token
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None


def test_vendor_api(token, project_id=1):
    """Test RMC Vendor Management API"""
    print_test("RMC Vendor Management API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET vendors
    response = requests.get(
        f"{BASE_URL}/api/vendors",
        headers=headers,
        params={"project_id": project_id}
    )
    
    if response.status_code == 200:
        vendors = response.json().get('vendors', [])
        print_success(f"GET vendors: Found {len(vendors)} vendors")
        return True
    else:
        print_error(f"GET vendors failed: {response.status_code}")
        return False


def test_batch_api(token, project_id=1):
    """Test Batch Register API"""
    print_test("Batch Register API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET batches
    response = requests.get(
        f"{BASE_URL}/api/batches",
        headers=headers,
        params={"project_id": project_id}
    )
    
    if response.status_code == 200:
        batches = response.json().get('batches', [])
        print_success(f"GET batches: Found {len(batches)} batches")
        return True
    else:
        print_error(f"GET batches failed: {response.status_code}")
        return False


def test_cube_test_api(token, project_id=1):
    """Test Cube Test Register API"""
    print_test("Cube Test Register API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET cube tests
    response = requests.get(
        f"{BASE_URL}/api/cube-tests",
        headers=headers,
        params={"project_id": project_id}
    )
    
    if response.status_code == 200:
        tests = response.json().get('cube_tests', [])
        print_success(f"GET cube tests: Found {len(tests)} tests")
        return True
    else:
        print_error(f"GET cube tests failed: {response.status_code}")
        return False


def test_third_party_lab_api(token, company_id=1):
    """Test Third-Party Lab API"""
    print_test("Third-Party Lab API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET third-party labs
    response = requests.get(
        f"{BASE_URL}/api/third-party-labs",
        headers=headers,
        params={"company_id": company_id, "approved_only": "false"}
    )
    
    if response.status_code == 200:
        labs = response.json().get('labs', [])
        print_success(f"GET third-party labs: Found {len(labs)} labs")
        return True
    else:
        print_error(f"GET third-party labs failed: {response.status_code}")
        return False


def test_third_party_cube_test_api(token, project_id=1):
    """Test Third-Party Cube Test API"""
    print_test("Third-Party Cube Test API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET third-party cube tests
    response = requests.get(
        f"{BASE_URL}/api/third-party-cube-tests",
        headers=headers,
        params={"project_id": project_id}
    )
    
    if response.status_code == 200:
        tests = response.json().get('tests', [])
        print_success(f"GET third-party cube tests: Found {len(tests)} tests")
        return True
    else:
        print_error(f"GET third-party cube tests failed: {response.status_code}")
        return False


def test_material_management_api(token, company_id=1):
    """Test Material Management API"""
    print_test("Material Management API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET material categories
    response = requests.get(
        f"{BASE_URL}/api/material-categories",
        headers=headers,
        params={"company_id": company_id}
    )
    
    if response.status_code == 200:
        categories = response.json().get('categories', [])
        print_success(f"GET material categories: Found {len(categories)} categories")
    else:
        print_error(f"GET material categories failed: {response.status_code}")
        return False
    
    # Test GET approved brands
    response = requests.get(
        f"{BASE_URL}/api/approved-brands",
        headers=headers,
        params={"company_id": company_id, "approved_only": "false"}
    )
    
    if response.status_code == 200:
        brands = response.json().get('brands', [])
        print_success(f"GET approved brands: Found {len(brands)} brands")
        return True
    else:
        print_error(f"GET approved brands failed: {response.status_code}")
        return False


def test_material_test_api(token, project_id=1):
    """Test Material Test Register API"""
    print_test("Material Test Register API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET material tests
    response = requests.get(
        f"{BASE_URL}/api/material-tests",
        headers=headers,
        params={"project_id": project_id}
    )
    
    if response.status_code == 200:
        tests = response.json().get('tests', [])
        print_success(f"GET material tests: Found {len(tests)} tests")
        return True
    else:
        print_error(f"GET material tests failed: {response.status_code}")
        return False


def run_all_tests():
    """Run all API tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}ConcreteThings QMS - API Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Test health
    results["total"] += 1
    if test_health():
        results["passed"] += 1
    else:
        results["failed"] += 1
        return results  # Exit if health check fails
    
    # Test authentication
    results["total"] += 1
    token = test_auth()
    if token:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("Cannot proceed without authentication token")
        return results
    
    # Test all API modules
    tests = [
        ("RMC Vendor API", test_vendor_api, [token]),
        ("Batch Register API", test_batch_api, [token]),
        ("Cube Test API", test_cube_test_api, [token]),
        ("Third-Party Lab API", test_third_party_lab_api, [token]),
        ("Third-Party Cube Test API", test_third_party_cube_test_api, [token]),
        ("Material Management API", test_material_management_api, [token]),
        ("Material Test API", test_material_test_api, [token])
    ]
    
    for test_name, test_func, args in tests:
        results["total"] += 1
        try:
            if test_func(*args):
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print_error(f"{test_name} crashed: {str(e)}")
            results["failed"] += 1
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Total Tests: {results['total']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return results


if __name__ == "__main__":
    try:
        results = run_all_tests()
        exit(0 if results["failed"] == 0 else 1)
    except KeyboardInterrupt:
        print_info("\nTest suite interrupted by user")
        exit(1)
    except Exception as e:
        print_error(f"Test suite crashed: {str(e)}")
        exit(1)
