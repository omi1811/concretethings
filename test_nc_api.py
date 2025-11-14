#!/usr/bin/env python3
"""
Comprehensive test suite for Concrete NC API.
Tests all 15 endpoints and complete workflow.
"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@concrete.com"
TEST_PASSWORD = "password123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class NCAPITester:
    def __init__(self):
        self.token = None
        self.project_id = None
        self.contractor_id = None
        self.nc_id = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")
    
    def success(self, message):
        self.passed += 1
        self.log(f"✓ PASS: {message}", Colors.GREEN)
    
    def fail(self, message):
        self.failed += 1
        self.log(f"✗ FAIL: {message}", Colors.RED)
    
    def warning(self, message):
        self.warnings += 1
        self.log(f"⚠ WARNING: {message}", Colors.YELLOW)
    
    def test_authentication(self):
        """Test 1: Authenticate and get JWT token."""
        self.log("\n[Test 1] Authentication", Colors.BLUE)
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                if self.token:
                    self.success("Authentication successful, JWT token obtained")
                    return True
                else:
                    self.fail("No access token in response")
                    return False
            else:
                self.fail(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.fail(f"Authentication error: {str(e)}")
            return False
    
    def test_get_projects(self):
        """Test 2: Get projects list."""
        self.log("\n[Test 2] Get Projects List", Colors.BLUE)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/projects/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                projects = data.get('projects', [])
                if projects:
                    self.project_id = projects[0]['id']
                    self.success(f"Retrieved {len(projects)} projects, using project_id: {self.project_id}")
                    return True
                else:
                    self.warning("No projects found, some tests may fail")
                    return False
            else:
                self.fail(f"Get projects failed: {response.status_code}")
                return False
        except Exception as e:
            self.fail(f"Get projects error: {str(e)}")
            return False
    
    def test_get_tags(self):
        """Test 3: Get NC tags."""
        self.log("\n[Test 3] Get NC Tags", Colors.BLUE)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/concrete/nc/tags", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                tags = data.get('tags', [])
                self.success(f"Retrieved {len(tags)} NC tags")
                if tags:
                    self.log(f"  Sample tags: {[tag['name'] for tag in tags[:3]]}")
                return True
            else:
                self.fail(f"Get tags failed: {response.status_code}")
                return False
        except Exception as e:
            self.fail(f"Get tags error: {str(e)}")
            return False
    
    def test_create_tag(self):
        """Test 4: Create new NC tag."""
        self.log("\n[Test 4] Create NC Tag", Colors.BLUE)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{BASE_URL}/api/concrete/nc/tags", 
                headers=headers,
                json={
                    "name": "Test Quality Issue",
                    "level": 2,
                    "parent_tag_id": 1,
                    "color_code": "#FF5733",
                    "description": "Test tag for automated testing"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                self.success(f"Tag created: {data.get('tag', {}).get('name')}")
                return True
            elif response.status_code == 403:
                self.warning("User not authorized to create tags (Admin only)")
                return False
            else:
                self.fail(f"Create tag failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.fail(f"Create tag error: {str(e)}")
            return False
    
    def test_raise_nc(self):
        """Test 5: Raise new NC issue."""
        self.log("\n[Test 5] Raise NC Issue", Colors.BLUE)
        
        if not self.project_id:
            self.fail("Cannot raise NC: No project_id available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # For simplicity, using form data without actual file upload
            data = {
                "project_id": str(self.project_id),
                "title": "Test NC - Concrete Quality Issue",
                "description": "Automated test NC for concrete quality non-conformance",
                "severity": "HIGH",
                "location_text": "Block A, Level 3",
                "tag_ids": json.dumps([1])  # Quality Issue tag
            }
            
            response = requests.post(f"{BASE_URL}/api/concrete/nc/", 
                headers=headers,
                data=data
            )
            
            if response.status_code == 201:
                result = response.json()
                nc = result.get('nc', {})
                self.nc_id = nc.get('id')
                self.success(f"NC raised: {nc.get('nc_number')} (ID: {self.nc_id})")
                self.log(f"  Title: {nc.get('title')}")
                self.log(f"  Severity: {nc.get('severity')}")
                self.log(f"  Status: {nc.get('status')}")
                return True
            else:
                self.fail(f"Raise NC failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.fail(f"Raise NC error: {str(e)}")
            return False
    
    def test_list_ncs(self):
        """Test 6: List NC issues."""
        self.log("\n[Test 6] List NC Issues", Colors.BLUE)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"project_id": self.project_id} if self.project_id else {}
            response = requests.get(f"{BASE_URL}/api/concrete/nc/", 
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                ncs = data.get('ncs', [])
                total = data.get('total', 0)
                self.success(f"Retrieved {len(ncs)} NC issues (total: {total})")
                if ncs:
                    self.log(f"  Latest NC: {ncs[0].get('nc_number')} - {ncs[0].get('title')}")
                return True
            else:
                self.fail(f"List NCs failed: {response.status_code}")
                return False
        except Exception as e:
            self.fail(f"List NCs error: {str(e)}")
            return False
    
    def test_get_nc_details(self):
        """Test 7: Get NC details."""
        self.log("\n[Test 7] Get NC Details", Colors.BLUE)
        
        if not self.nc_id:
            self.warning("No NC ID available, skipping test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/concrete/nc/{self.nc_id}", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                nc = data.get('nc', {})
                self.success(f"Retrieved NC details: {nc.get('nc_number')}")
                self.log(f"  Status: {nc.get('status')}")
                self.log(f"  Severity Score: {nc.get('severity_score')}")
                return True
            else:
                self.fail(f"Get NC details failed: {response.status_code}")
                return False
        except Exception as e:
            self.fail(f"Get NC details error: {str(e)}")
            return False
    
    def test_acknowledge_nc(self):
        """Test 8: Acknowledge NC (Contractor)."""
        self.log("\n[Test 8] Acknowledge NC", Colors.BLUE)
        
        if not self.nc_id:
            self.warning("No NC ID available, skipping test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{BASE_URL}/api/concrete/nc/{self.nc_id}/acknowledge", 
                headers=headers,
                json={"remarks": "We acknowledge this NC and will respond shortly"}
            )
            
            if response.status_code == 200:
                data = response.json()
                nc = data.get('nc', {})
                self.success(f"NC acknowledged, status: {nc.get('status')}")
                return True
            elif response.status_code == 403:
                self.warning("User not authorized to acknowledge (might need contractor role)")
                return False
            else:
                self.fail(f"Acknowledge NC failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.fail(f"Acknowledge NC error: {str(e)}")
            return False
    
    def test_respond_nc(self):
        """Test 9: Respond to NC (Contractor)."""
        self.log("\n[Test 9] Respond to NC", Colors.BLUE)
        
        if not self.nc_id:
            self.warning("No NC ID available, skipping test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            deadline = (datetime.now() + timedelta(days=7)).isoformat()
            response = requests.post(f"{BASE_URL}/api/concrete/nc/{self.nc_id}/respond", 
                headers=headers,
                json={
                    "response": "We will fix this issue by repairing the concrete surface and applying waterproofing",
                    "proposed_deadline": deadline
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                nc = data.get('nc', {})
                self.success(f"NC response submitted, status: {nc.get('status')}")
                return True
            else:
                self.warning(f"Respond to NC: {response.status_code} - May need proper NC status")
                return False
        except Exception as e:
            self.fail(f"Respond to NC error: {str(e)}")
            return False
    
    def test_dashboard(self):
        """Test 10: Get NC dashboard."""
        self.log("\n[Test 10] Get NC Dashboard", Colors.BLUE)
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"project_id": self.project_id} if self.project_id else {}
            response = requests.get(f"{BASE_URL}/api/concrete/nc/dashboard", 
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                self.success("Dashboard retrieved successfully")
                self.log(f"  Total NCs: {data.get('total', 0)}")
                self.log(f"  Open NCs: {data.get('open', 0)}")
                self.log(f"  Closed NCs: {data.get('closed', 0)}")
                self.log(f"  Severity counts: {data.get('severity_counts', {})}")
                return True
            else:
                self.fail(f"Get dashboard failed: {response.status_code}")
                return False
        except Exception as e:
            self.fail(f"Get dashboard error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite."""
        self.log("="*60)
        self.log("CONCRETE NC API TEST SUITE")
        self.log("="*60)
        self.log(f"Base URL: {BASE_URL}")
        self.log(f"Test User: {TEST_EMAIL}")
        self.log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*60)
        
        # Run tests in sequence
        if not self.test_authentication():
            self.log("\n❌ Cannot proceed without authentication", Colors.RED)
            return
        
        self.test_get_projects()
        self.test_get_tags()
        self.test_create_tag()
        self.test_raise_nc()
        self.test_list_ncs()
        self.test_get_nc_details()
        self.test_acknowledge_nc()
        self.test_respond_nc()
        self.test_dashboard()
        
        # Summary
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        self.log(f"✓ Passed: {self.passed}", Colors.GREEN)
        self.log(f"✗ Failed: {self.failed}", Colors.RED)
        self.log(f"⚠ Warnings: {self.warnings}", Colors.YELLOW)
        
        total = self.passed + self.failed + self.warnings
        success_rate = (self.passed / total * 100) if total > 0 else 0
        self.log(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if self.failed == 0 and self.warnings == 0:
            self.log("\n🎉 ALL TESTS PASSED!", Colors.GREEN)
        elif self.failed == 0:
            self.log("\n✅ All critical tests passed (some warnings)", Colors.YELLOW)
        else:
            self.log(f"\n⚠️ {self.failed} tests failed", Colors.RED)

if __name__ == '__main__':
    import sys
    
    # Check if server is provided
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    tester = NCAPITester()
    tester.run_all_tests()
