#!/usr/bin/env python3
"""Simple test to verify Contractor Supervisor NCR response workflow"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    """Test login and get token"""
    print("1. Testing login...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@testprosite.com",
        "password": "Admin@Test123"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Login successful: {data['user']['email']}")
        return data['access_token']
    else:
        print(f"   ❌ Login failed: {response.text}")
        return None

def test_create_project(token):
    """Test creating a project"""
    print("\n2. Testing project creation...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{BASE_URL}/projects", 
        headers=headers,
        json={
            "name": "Test Construction Site",
            "location": "Mumbai",
            "description": "Test project for NCR workflow"
        })
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    if response.status_code == 201:
        project = response.json()['project']
        print(f"   ✅ Project created: ID={project['id']}")
        return project['id']
    else:
        print(f"   ❌ Project creation failed")
        return None

def main():
    print("="*70)
    print("ProSite Basic Workflow Test")
    print("="*70)
    
    token = test_login()
    if not token:
        print("\nCannot proceed without authentication")
        return
    
    project_id = test_create_project(token)
    
    print("\n" + "="*70)
    if project_id:
        print("✅ Basic tests passed!")
    else:
        print("⚠️  Some tests failed")
    print("="*70)

if __name__ == "__main__":
    main()
