#!/usr/bin/env python3
"""Test authentication endpoints."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Test login endpoint."""
    print("Testing login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@demo.com", "password": "adminpass"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"\n✓ Login successful!")
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"\n✗ Login failed: {response.json().get('error')}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint."""
    print("\n\nTesting protected endpoint (GET /api/mix-designs)...")
    response = requests.get(
        f"{BASE_URL}/api/mix-designs",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success! Found {len(data)} mix designs")
        if data:
            print(f"First mix: {data[0]['mixDesignId']} - {data[0]['projectName']}")
    else:
        print(f"✗ Failed: {response.json().get('error')}")

def test_me_endpoint(token):
    """Test getting current user info."""
    print("\n\nTesting /api/auth/me...")
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"✓ User info retrieved:")
        print(f"  Name: {user['fullName']}")
        print(f"  Email: {user['email']}")
        print(f"  Phone: {user['phone']}")
        print(f"  System Admin: {user['isSystemAdmin']}")
        print(f"  Company Admin: {user['isCompanyAdmin']}")
    else:
        print(f"✗ Failed: {response.json().get('error')}")

def test_invalid_login():
    """Test login with wrong password."""
    print("\n\nTesting login with wrong password...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@demo.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 401:
        print("✓ Correctly rejected invalid credentials")
    else:
        print("✗ Expected 401 status")

def test_no_token():
    """Test accessing protected endpoint without token."""
    print("\n\nTesting protected endpoint without token...")
    response = requests.get(f"{BASE_URL}/api/mix-designs")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Correctly rejected request without token")
        print(f"Response: {response.json()}")
    else:
        print("✗ Expected 401 status")

if __name__ == "__main__":
    print("=" * 60)
    print("Authentication System Test Suite")
    print("=" * 60)
    
    # Test 1: Login
    token = test_login()
    
    if token:
        # Test 2: Get user info
        test_me_endpoint(token)
        
        # Test 3: Access protected endpoint
        test_protected_endpoint(token)
    
    # Test 4: Invalid login
    test_invalid_login()
    
    # Test 5: No token
    test_no_token()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)
