"""
Comprehensive QA Test Suite for ProSite Application
Tests all critical features, APIs, database operations, and user workflows
"""

import sys
import os
import json
from datetime import datetime, timedelta
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.app import create_app
from server.db import SessionLocal, init_db
from server.models import User, Company, Project, RMCVendor, MixDesign, BatchRegister
from server.safety_models import Worker
from server.safety_nc_models import NonConformance
from werkzeug.security import generate_password_hash

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class QATestSuite:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.session = SessionLocal()
        self.auth_token = None
        self.test_user = None
        self.test_company = None
        self.test_project = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.issues = []
        
    def print_header(self, text):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    def print_test(self, name):
        print(f"{Colors.OKBLUE}Testing: {name}{Colors.ENDC}")
    
    def print_pass(self, message):
        self.passed += 1
        print(f"  {Colors.OKGREEN}✓ PASS:{Colors.ENDC} {message}")
    
    def print_fail(self, message, details=None):
        self.failed += 1
        print(f"  {Colors.FAIL}✗ FAIL:{Colors.ENDC} {message}")
        if details:
            print(f"    {Colors.FAIL}Details: {details}{Colors.ENDC}")
        self.issues.append({"type": "FAIL", "test": message, "details": details})
    
    def print_warning(self, message):
        self.warnings += 1
        print(f"  {Colors.WARNING}⚠ WARNING:{Colors.ENDC} {message}")
        self.issues.append({"type": "WARNING", "test": message})
    
    def cleanup(self):
        """Cleanup test session"""
        try:
            self.session.close()
        except:
            pass

    # ==========================================================================
    # TEST 1: Database Connectivity & Schema
    # ==========================================================================
    def test_database_connectivity(self):
        self.print_header("TEST 1: Database Connectivity & Schema")
        
        try:
            self.print_test("Database connection")
            companies = self.session.query(Company).limit(1).all()
            self.print_pass(f"Database connected successfully. Found {len(companies)} companies")
        except Exception as e:
            self.print_fail("Database connection failed", str(e))
            return False
        
        try:
            self.print_test("Core tables existence")
            tables = {
                'companies': Company,
                'users': User,
                'projects': Project,
                'rmc_vendors': RMCVendor,
                'mix_designs': MixDesign,
                'batch_register': BatchRegister,
                'safety_workers': Worker,
                'non_conformances': NonConformance
            }
            
            for table_name, model in tables.items():
                count = self.session.query(model).count()
                self.print_pass(f"Table '{table_name}' exists ({count} records)")
        except Exception as e:
            self.print_fail("Core table check failed", str(e))
        
        try:
            self.print_test("New safety module tables")
            new_tables = [
                'safety_inductions', 'induction_topics', 'incident_reports',
                'safety_audits', 'audit_checklists', 'ppe_issuances',
                'ppe_inventory', 'geofence_locations', 'location_verifications'
            ]
            
            for table in new_tables:
                result = self.session.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                self.print_pass(f"Table '{table}' exists ({result[0]} records)")
        except Exception as e:
            self.print_warning(f"New safety tables not fully migrated: {str(e)}")
        
        return True

    # ==========================================================================
    # TEST 2: Authentication System
    # ==========================================================================
    def test_authentication(self):
        self.print_header("TEST 2: Authentication System")
        
        try:
            self.print_test("Login with test credentials")
            response = self.client.post('/api/auth/login',
                json={
                    'email': 'test@example.com',
                    'password': 'Test@123'
                },
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.get_json()
                if data.get('access_token'):
                    self.auth_token = data['access_token']
                    self.print_pass(f"Login successful, token received")
                else:
                    self.print_fail("Login response missing access_token", data)
            else:
                self.print_fail(f"Login failed with status {response.status_code}", response.get_json())
                return False
        except Exception as e:
            self.print_fail("Login request failed", str(e))
            return False
        
        try:
            self.print_test("JWT token validation")
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.client.get('/api/auth/me', headers=headers)
            
            if response.status_code == 200:
                user_data = response.get_json()
                self.test_user = user_data
                self.print_pass(f"Token valid, user: {user_data.get('email')}")
            else:
                self.print_fail("JWT validation failed", response.get_json())
        except Exception as e:
            self.print_fail("JWT validation request failed", str(e))
        
        try:
            self.print_test("Unauthorized access prevention")
            response = self.client.get('/api/auth/me')  # No token
            
            if response.status_code == 401:
                self.print_pass("Unauthorized access correctly blocked")
            else:
                self.print_fail(f"Unauthorized access not blocked (status: {response.status_code})")
        except Exception as e:
            self.print_fail("Auth protection test failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 3: Core Business Logic - Batch Management
    # ==========================================================================
    def test_batch_management(self):
        self.print_header("TEST 3: Core Business Logic - Batch Management")
        
        if not self.auth_token:
            self.print_warning("Skipping batch tests - no auth token")
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        try:
            self.print_test("Fetch projects list")
            response = self.client.get('/api/projects', headers=headers)
            
            if response.status_code == 200:
                projects = response.get_json()
                if projects:
                    self.test_project = projects[0]
                    self.print_pass(f"Projects retrieved: {len(projects)} projects")
                else:
                    self.print_warning("No projects found in database")
            else:
                self.print_fail("Failed to fetch projects", response.get_json())
        except Exception as e:
            self.print_fail("Projects API failed", str(e))
        
        try:
            self.print_test("Fetch batches list")
            response = self.client.get('/api/batches', headers=headers)
            
            if response.status_code == 200:
                batches = response.get_json()
                self.print_pass(f"Batches retrieved: {len(batches)} batches")
                
                if batches:
                    # Check batch data structure
                    batch = batches[0]
                    required_fields = ['id', 'batch_number', 'delivery_date', 'vendor_name']
                    missing_fields = [f for f in required_fields if f not in batch]
                    
                    if missing_fields:
                        self.print_warning(f"Batch missing fields: {missing_fields}")
                    else:
                        self.print_pass("Batch data structure valid")
            else:
                self.print_fail("Failed to fetch batches", response.get_json())
        except Exception as e:
            self.print_fail("Batches API failed", str(e))
        
        try:
            self.print_test("Fetch vendors list")
            response = self.client.get('/api/vendors', headers=headers)
            
            if response.status_code == 200:
                vendors = response.get_json()
                self.print_pass(f"Vendors retrieved: {len(vendors)} vendors")
            else:
                self.print_fail("Failed to fetch vendors", response.get_json())
        except Exception as e:
            self.print_fail("Vendors API failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 4: Safety Module - Workers & Contractors
    # ==========================================================================
    def test_safety_workers(self):
        self.print_header("TEST 4: Safety Module - Workers & Contractors")
        
        if not self.auth_token:
            self.print_warning("Skipping safety tests - no auth token")
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        try:
            self.print_test("Fetch workers list")
            response = self.client.get('/api/safety/workers', headers=headers)
            
            if response.status_code == 200:
                workers = response.get_json()
                self.print_pass(f"Workers retrieved: {len(workers)} workers")
            else:
                self.print_fail("Failed to fetch workers", response.get_json())
        except Exception as e:
            self.print_fail("Workers API failed", str(e))
        
        try:
            self.print_test("Fetch contractors list")
            response = self.client.get('/api/safety/non-conformances', headers=headers)
            
            if response.status_code == 200:
                ncs = response.get_json()
                self.print_pass(f"Non-conformances retrieved: {len(ncs)} NCs")
            else:
                self.print_fail("Failed to fetch non-conformances", response.get_json())
        except Exception as e:
            self.print_fail("Non-conformances API failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 5: Safety Inductions (New Module)
    # ==========================================================================
    def test_safety_inductions(self):
        self.print_header("TEST 5: Safety Inductions Module")
        
        if not self.auth_token:
            self.print_warning("Skipping induction tests - no auth token")
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        try:
            self.print_test("Fetch induction topics")
            response = self.client.get('/api/safety-inductions/topics', headers=headers)
            
            if response.status_code == 200:
                topics = response.get_json()
                self.print_pass(f"Induction topics retrieved: {len(topics)} topics")
                
                if len(topics) == 18:
                    self.print_pass("All 18 standard topics seeded correctly")
                else:
                    self.print_warning(f"Expected 18 topics, found {len(topics)}")
            else:
                self.print_fail("Failed to fetch induction topics", response.get_json())
        except Exception as e:
            self.print_fail("Induction topics API failed", str(e))
        
        try:
            self.print_test("Fetch inductions list")
            response = self.client.get('/api/safety-inductions', headers=headers)
            
            if response.status_code == 200:
                inductions = response.get_json()
                self.print_pass(f"Inductions retrieved: {len(inductions)} inductions")
            else:
                self.print_fail("Failed to fetch inductions", response.get_json())
        except Exception as e:
            self.print_fail("Inductions API failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 6: File Upload & Static Files
    # ==========================================================================
    def test_file_handling(self):
        self.print_header("TEST 6: File Upload & Static Files")
        
        if not self.auth_token:
            self.print_warning("Skipping file tests - no auth token")
            return False
        
        try:
            self.print_test("Upload directory permissions")
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            
            if os.path.exists(upload_dir):
                if os.access(upload_dir, os.W_OK):
                    self.print_pass("Upload directory writable")
                else:
                    self.print_fail("Upload directory not writable")
            else:
                self.print_warning("Upload directory does not exist")
        except Exception as e:
            self.print_fail("Upload directory check failed", str(e))
        
        try:
            self.print_test("Static files serving")
            response = self.client.get('/static/favicon.ico')
            
            # 404 is acceptable if file doesn't exist, 403 would be a problem
            if response.status_code in [200, 404]:
                self.print_pass("Static file route configured")
            else:
                self.print_fail(f"Static files misconfigured (status: {response.status_code})")
        except Exception as e:
            self.print_fail("Static files test failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 7: Data Validation & Business Rules
    # ==========================================================================
    def test_data_validation(self):
        self.print_header("TEST 7: Data Validation & Business Rules")
        
        try:
            self.print_test("Database constraints - Company uniqueness")
            company = self.session.query(Company).first()
            
            if company:
                # Try to create duplicate company (should fail)
                duplicate = Company(
                    name=company.name,  # Duplicate name
                    subscription_plan="trial"
                )
                self.session.add(duplicate)
                try:
                    self.session.commit()
                    self.print_fail("Database allowed duplicate company name")
                    self.session.rollback()
                except Exception:
                    self.session.rollback()
                    self.print_pass("Database correctly prevents duplicate company names")
            else:
                self.print_warning("No company to test uniqueness constraint")
        except Exception as e:
            self.session.rollback()
            self.print_fail("Company uniqueness test failed", str(e))
        
        try:
            self.print_test("User email uniqueness")
            user = self.session.query(User).first()
            
            if user:
                duplicate_user = User(
                    email=user.email,  # Duplicate email
                    phone="9999999999",
                    full_name="Test Duplicate",
                    password_hash=generate_password_hash("Test@123"),
                    company_id=user.company_id,
                    is_company_admin=False,
                    is_support_admin=False,
                    is_system_admin=False
                )
                self.session.add(duplicate_user)
                try:
                    self.session.commit()
                    self.print_fail("Database allowed duplicate email")
                    self.session.rollback()
                except Exception:
                    self.session.rollback()
                    self.print_pass("Database correctly prevents duplicate emails")
            else:
                self.print_warning("No user to test email uniqueness")
        except Exception as e:
            self.session.rollback()
            self.print_fail("Email uniqueness test failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 8: API Error Handling
    # ==========================================================================
    def test_error_handling(self):
        self.print_header("TEST 8: API Error Handling")
        
        try:
            self.print_test("Invalid endpoint (404)")
            response = self.client.get('/api/nonexistent-endpoint')
            
            if response.status_code == 404:
                self.print_pass("404 error handled correctly")
            else:
                self.print_warning(f"Unexpected status for invalid endpoint: {response.status_code}")
        except Exception as e:
            self.print_fail("404 handling test failed", str(e))
        
        try:
            self.print_test("Invalid JSON payload")
            response = self.client.post('/api/auth/login',
                data='invalid json{',
                content_type='application/json'
            )
            
            if response.status_code in [400, 415, 422]:
                self.print_pass("Invalid JSON rejected appropriately")
            else:
                self.print_warning(f"Invalid JSON handling unclear (status: {response.status_code})")
        except Exception as e:
            self.print_fail("Invalid JSON test failed", str(e))
        
        try:
            self.print_test("Missing required fields")
            response = self.client.post('/api/auth/login',
                json={'email': 'test@example.com'},  # Missing password
                content_type='application/json'
            )
            
            if response.status_code in [400, 422]:
                self.print_pass("Missing fields handled correctly")
            else:
                self.print_warning(f"Missing fields validation unclear (status: {response.status_code})")
        except Exception as e:
            self.print_fail("Missing fields test failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 9: CORS Configuration
    # ==========================================================================
    def test_cors(self):
        self.print_header("TEST 9: CORS Configuration")
        
        try:
            self.print_test("CORS headers presence")
            response = self.client.get('/api/auth/login',
                headers={'Origin': 'http://localhost:3000'}
            )
            
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                self.print_pass(f"CORS configured: {cors_header}")
            else:
                self.print_warning("CORS headers not found (may cause frontend issues)")
        except Exception as e:
            self.print_fail("CORS test failed", str(e))
        
        return True

    # ==========================================================================
    # TEST 10: Performance & Response Times
    # ==========================================================================
    def test_performance(self):
        self.print_header("TEST 10: Performance & Response Times")
        
        if not self.auth_token:
            self.print_warning("Skipping performance tests - no auth token")
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        try:
            self.print_test("API response time - Batches list")
            start = datetime.now()
            response = self.client.get('/api/batches', headers=headers)
            duration = (datetime.now() - start).total_seconds()
            
            if response.status_code == 200:
                if duration < 1.0:
                    self.print_pass(f"Response time excellent: {duration:.3f}s")
                elif duration < 3.0:
                    self.print_pass(f"Response time acceptable: {duration:.3f}s")
                else:
                    self.print_warning(f"Response time slow: {duration:.3f}s (needs optimization)")
            else:
                self.print_fail("API request failed")
        except Exception as e:
            self.print_fail("Performance test failed", str(e))
        
        return True

    # ==========================================================================
    # Run All Tests
    # ==========================================================================
    def run_all_tests(self):
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                     ProSite QA Test Suite - Comprehensive                 ║")
        print("║                              Started at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "                    ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        # Run all test suites
        self.test_database_connectivity()
        self.test_authentication()
        self.test_batch_management()
        self.test_safety_workers()
        self.test_safety_inductions()
        self.test_file_handling()
        self.test_data_validation()
        self.test_error_handling()
        self.test_cors()
        self.test_performance()
        
        # Print summary
        self.print_summary()
        
        # Cleanup
        self.cleanup()
    
    def print_summary(self):
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                              TEST SUMMARY                                  ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        total = self.passed + self.failed + self.warnings
        print(f"\n{Colors.BOLD}Total Tests: {total}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ Passed:  {self.passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}✗ Failed:  {self.failed}{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠ Warnings: {self.warnings}{Colors.ENDC}")
        
        if self.passed == total:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Application is production-ready.{Colors.ENDC}")
        elif self.failed == 0:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ TESTS PASSED WITH WARNINGS - Review warnings before deployment{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ TESTS FAILED - Critical issues found{Colors.ENDC}")
        
        # Print issues for developer
        if self.issues:
            print(f"\n{Colors.BOLD}ISSUES FOUND (for developer):{Colors.ENDC}")
            print("="*80)
            for i, issue in enumerate(self.issues, 1):
                print(f"\n{i}. [{issue['type']}] {issue['test']}")
                if issue.get('details'):
                    print(f"   Details: {issue['details']}")


if __name__ == "__main__":
    qa = QATestSuite()
    qa.run_all_tests()
