#!/usr/bin/env python3
"""
Test Safety NC Scoring and Reporting API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_safety_nc_scoring():
    """Test Safety NC scoring system"""
    print("=" * 80)
    print("SAFETY NC SCORING SYSTEM TEST")
    print("=" * 80)
    
    # 1. Login
    print("\n1. Login as admin...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "shrotrio@gmail.com",
        "password": "Admin@123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 2. Get projects
    print("\n2. Get projects...")
    projects_response = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    
    if projects_response.status_code != 200:
        print(f"❌ Get projects failed: {projects_response.status_code}")
        return
    
    projects = projects_response.json()
    if not projects:
        print("❌ No projects found. Need to create a project first.")
        return
    
    project_id = projects[0]['id']
    print(f"✅ Using project: {projects[0]['name']} (ID: {project_id})")
    
    # 3. Create a test Safety NC
    print("\n3. Creating test Safety NC...")
    nc_data = {
        "project_id": project_id,
        "nc_type": "observation",
        "severity": "major",
        "category": "ppe",
        "description": "Test Safety NC for scoring",
        "assigned_to_contractor": "Test Contractor",
        "raised_by_user_id": 1,
        "target_closure_date": datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/safety/nc",
        headers=headers,
        json=nc_data
    )
    
    if create_response.status_code not in [200, 201]:
        print(f"❌ Create NC failed: {create_response.status_code}")
        print(create_response.text)
        return
    
    nc = create_response.json()
    nc_id = nc.get('id')
    print(f"✅ Created Safety NC (ID: {nc_id})")
    print(f"   Severity: {nc.get('severity')}")
    print(f"   Severity Score: {nc.get('severity_score', 'N/A')}")
    print(f"   Score Month: {nc.get('score_month', 'N/A')}")
    print(f"   Score Week: {nc.get('score_week', 'N/A')}")
    
    # 4. Test Dashboard
    print("\n4. Testing NC Dashboard...")
    dashboard_response = requests.get(
        f"{BASE_URL}/api/safety/nc/dashboard",
        headers=headers,
        params={"project_id": project_id}
    )
    
    if dashboard_response.status_code != 200:
        print(f"❌ Dashboard failed: {dashboard_response.status_code}")
        print(dashboard_response.text)
        return
    
    dashboard = dashboard_response.json()
    print("✅ Dashboard retrieved:")
    print(f"   Total NCs: {dashboard.get('total')}")
    print(f"   Open: {dashboard.get('open')}")
    print(f"   Closed: {dashboard.get('closed')}")
    print(f"   Overdue: {dashboard.get('overdue')}")
    print(f"   Total Score: {dashboard.get('total_score')}")
    print(f"   Performance Grade: {dashboard.get('performance_grade')}")
    print(f"   Severity Breakdown: {dashboard.get('severity_counts')}")
    print(f"   Status Breakdown: {dashboard.get('status_counts')}")
    
    # 5. Generate Monthly Report
    print("\n5. Generating Monthly Contractor Report...")
    current_period = datetime.utcnow().strftime('%Y-%m')
    report_response = requests.get(
        f"{BASE_URL}/api/safety/nc/reports/monthly",
        headers=headers,
        params={
            "project_id": project_id,
            "contractor": "Test Contractor",
            "period": current_period
        }
    )
    
    if report_response.status_code != 200:
        print(f"❌ Report failed: {report_response.status_code}")
        print(report_response.text)
        return
    
    report_data = report_response.json()
    report = report_data.get('report', {})
    print("✅ Monthly report generated:")
    print(f"   Period: {report.get('period')}")
    print(f"   Contractor: {report.get('contractor_name')}")
    print(f"   Critical: {report.get('critical_count')}")
    print(f"   Major: {report.get('major_count')}")
    print(f"   Minor: {report.get('minor_count')}")
    print(f"   Total Issues: {report.get('total_issues_count')}")
    print(f"   Open: {report.get('open_issues_count')}")
    print(f"   Closed: {report.get('closed_issues_count')}")
    print(f"   Total Score: {report.get('total_score')}")
    print(f"   Closure Rate: {report.get('closure_rate')}%")
    print(f"   Performance Grade: {report.get('performance_grade')}")
    
    # 6. Generate Weekly Report
    print("\n6. Generating Weekly Contractor Report...")
    current_week = datetime.utcnow().strftime('%Y-W%U')
    weekly_response = requests.get(
        f"{BASE_URL}/api/safety/nc/reports/weekly",
        headers=headers,
        params={
            "project_id": project_id,
            "contractor": "Test Contractor",
            "period": current_week
        }
    )
    
    if weekly_response.status_code != 200:
        print(f"❌ Weekly report failed: {weekly_response.status_code}")
        print(weekly_response.text)
        return
    
    weekly_data = weekly_response.json()
    weekly = weekly_data.get('report', {})
    print("✅ Weekly report generated:")
    print(f"   Period: {weekly.get('period')}")
    print(f"   Total Score: {weekly.get('total_score')}")
    print(f"   Performance Grade: {weekly.get('performance_grade')}")
    
    # 7. Test different severity scores
    print("\n7. Testing Severity Score Calculation...")
    severities = [
        ("critical", 1.5),
        ("major", 1.0),
        ("minor", 0.5)
    ]
    
    for severity, expected_score in severities:
        nc_test = {
            "project_id": project_id,
            "nc_type": "observation",
            "severity": severity,
            "category": "ppe",
            "description": f"Test {severity} NC",
            "assigned_to_contractor": "Test Contractor",
            "raised_by_user_id": 1,
            "target_closure_date": datetime.utcnow().strftime('%Y-%m-%d')
        }
        
        test_response = requests.post(
            f"{BASE_URL}/api/safety/nc",
            headers=headers,
            json=nc_test
        )
        
        if test_response.status_code in [200, 201]:
            test_nc = test_response.json()
            actual_score = test_nc.get('severity_score')
            match = "✅" if actual_score == expected_score else "❌"
            print(f"   {match} {severity.upper()}: Expected {expected_score}, Got {actual_score}")
    
    print("\n" + "=" * 80)
    print("✅ SAFETY NC SCORING TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_safety_nc_scoring()
