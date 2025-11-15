#!/usr/bin/env python3
"""
Create comprehensive demo users for all roles in ProSite QMS
"""

import sys
sys.path.insert(0, '/workspaces/concretethings')

from server.app import app, db
from server.models import User, Company, Project, ProjectMembership
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_users():
    """Create demo users for all roles"""
    
    with app.app_context():
        print("🚀 Creating Demo Users for ProSite QMS")
        print("=" * 60)
        
        # Get existing company and project
        company = db.session.query(Company).first()
        if not company:
            print("❌ No company found. Creating default company...")
            company = Company(
                name="Demo Construction Company",
                subscription_plan="professional",
                active_projects_limit=10,
                price_per_project=10000.0,
                billing_status="active",
                is_active=1
            )
            db.session.add(company)
            db.session.commit()
        
        project = db.session.query(Project).first()
        if not project:
            print("❌ No project found. Creating default project...")
            project = Project(
                company_id=company.id,
                name="Skyline Tower Project",
                project_code="SKY-001",
                description="Residential high-rise construction",
                location="Mumbai, India",
                client_name="ABC Developers",
                status="active",
                is_active=1
            )
            db.session.add(project)
            db.session.commit()
        
        print(f"\n✅ Using Company: {company.name} (ID: {company.id})")
        print(f"✅ Using Project: {project.name} (ID: {project.id})")
        print()
        
        # Demo users configuration
        demo_users = [
            {
                "email": "admin@demo.com",
                "full_name": "System Administrator",
                "phone": "+919876543200",
                "designation": "System Admin",
                "is_system_admin": 1,
                "is_company_admin": 0,
                "is_support_admin": 1,
                "role": None,  # No project membership
                "password": "admin123"
            },
            {
                "email": "company.admin@demo.com",
                "full_name": "Company Administrator",
                "phone": "+919876543201",
                "designation": "Company Admin",
                "is_system_admin": 0,
                "is_company_admin": 1,
                "is_support_admin": 0,
                "role": None,  # Company-level, not project-specific
                "password": "admin123"
            },
            {
                "email": "project.admin@demo.com",
                "full_name": "Project Administrator",
                "phone": "+919876543202",
                "designation": "Project Manager",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "ProjectAdmin",
                "password": "admin123"
            },
            {
                "email": "quality.manager@demo.com",
                "full_name": "Quality Manager",
                "phone": "+919876543203",
                "designation": "Senior QC Manager",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "QualityManager",
                "password": "qm123"
            },
            {
                "email": "quality.engineer@demo.com",
                "full_name": "Quality Engineer",
                "phone": "+919876543204",
                "designation": "QC Engineer",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "QualityEngineer",
                "password": "qe123"
            },
            {
                "email": "site.engineer@demo.com",
                "full_name": "Site Engineer",
                "phone": "+919876543205",
                "designation": "Site Engineer",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "SiteEngineer",
                "password": "site123"
            },
            {
                "email": "data.entry@demo.com",
                "full_name": "Data Entry Operator",
                "phone": "+919876543206",
                "designation": "Data Entry",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "DataEntry",
                "password": "entry123"
            },
            {
                "email": "watchman@demo.com",
                "full_name": "Security Watchman",
                "phone": "+919876543207",
                "designation": "Gate Security",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "Watchman",
                "password": "watch123"
            },
            {
                "email": "viewer@demo.com",
                "full_name": "Read-Only Viewer",
                "phone": "+919876543208",
                "designation": "Observer",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "Viewer",
                "password": "view123"
            },
            {
                "email": "rmc.vendor@demo.com",
                "full_name": "RMC Vendor Representative",
                "phone": "+919876543209",
                "designation": "Vendor Rep",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "RMCVendor",
                "password": "vendor123"
            },
            {
                "email": "safety.officer@demo.com",
                "full_name": "Safety Officer",
                "phone": "+919876543210",
                "designation": "HSE Officer",
                "is_system_admin": 0,
                "is_company_admin": 0,
                "is_support_admin": 0,
                "role": "QualityManager",  # Safety officer gets QM permissions
                "password": "safety123"
            },
        ]
        
        created_users = []
        
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.session.query(User).filter_by(email=user_data["email"]).first()
            
            if existing_user:
                print(f"⚠️  User exists: {user_data['email']} (skipping)")
                user = existing_user
            else:
                # Create new user
                user = User(
                    email=user_data["email"],
                    phone=user_data["phone"],
                    full_name=user_data["full_name"],
                    password_hash=generate_password_hash(user_data["password"]),
                    company_id=company.id,
                    is_system_admin=user_data["is_system_admin"],
                    is_company_admin=user_data["is_company_admin"],
                    is_support_admin=user_data["is_support_admin"],
                    designation=user_data["designation"],
                    is_active=1,
                    is_email_verified=1
                )
                db.session.add(user)
                db.session.commit()
                print(f"✅ Created: {user_data['full_name']:30} | {user_data['email']:30} | Password: {user_data['password']}")
                
                # Add project membership if role is specified
                if user_data["role"]:
                    # Define permissions based on role
                    role_permissions = {
                        "ProjectAdmin": {
                            "can_create_batch": 1,
                            "can_edit_batch": 1,
                            "can_delete_batch": 1,
                            "can_approve_batch": 1,
                            "can_create_test": 1,
                            "can_edit_test": 1,
                            "can_delete_test": 1,
                            "can_approve_test": 1,
                            "can_manage_team": 1,
                            "can_generate_reports": 1,
                            "can_export_data": 1,
                            "can_manage_settings": 1,
                        },
                        "QualityManager": {
                            "can_create_batch": 1,
                            "can_edit_batch": 1,
                            "can_delete_batch": 0,
                            "can_approve_batch": 1,
                            "can_create_test": 1,
                            "can_edit_test": 1,
                            "can_delete_test": 0,
                            "can_approve_test": 1,
                            "can_manage_team": 0,
                            "can_generate_reports": 1,
                            "can_export_data": 1,
                            "can_manage_settings": 0,
                        },
                        "QualityEngineer": {
                            "can_create_batch": 1,
                            "can_edit_batch": 1,
                            "can_delete_batch": 0,
                            "can_approve_batch": 0,
                            "can_create_test": 1,
                            "can_edit_test": 1,
                            "can_delete_test": 0,
                            "can_approve_test": 0,
                            "can_manage_team": 0,
                            "can_generate_reports": 1,
                            "can_export_data": 0,
                            "can_manage_settings": 0,
                        },
                        "SiteEngineer": {
                            "can_create_batch": 1,
                            "can_edit_batch": 1,
                            "can_delete_batch": 0,
                            "can_approve_batch": 0,
                            "can_create_test": 0,
                            "can_edit_test": 0,
                            "can_delete_test": 0,
                            "can_approve_test": 0,
                            "can_manage_team": 0,
                            "can_generate_reports": 1,
                            "can_export_data": 0,
                            "can_manage_settings": 0,
                        },
                        "DataEntry": {
                            "can_create_batch": 1,
                            "can_edit_batch": 1,
                            "can_delete_batch": 0,
                            "can_approve_batch": 0,
                            "can_create_test": 0,
                            "can_edit_test": 0,
                            "can_delete_test": 0,
                            "can_approve_test": 0,
                            "can_manage_team": 0,
                            "can_generate_reports": 0,
                            "can_export_data": 0,
                            "can_manage_settings": 0,
                        },
                        "Watchman": {
                            "can_create_batch": 0,
                            "can_edit_batch": 0,
                            "can_delete_batch": 0,
                            "can_approve_batch": 0,
                            "can_create_test": 0,
                            "can_edit_test": 0,
                            "can_delete_test": 0,
                            "can_approve_test": 0,
                            "can_manage_team": 0,
                            "can_generate_reports": 0,
                            "can_export_data": 0,
                            "can_manage_settings": 0,
                        },
                        "Viewer": {
                            "can_create_batch": 0,
                            "can_edit_batch": 0,
                            "can_delete_batch": 0,
                            "can_approve_batch": 0,
                            "can_create_test": 0,
                            "can_edit_test": 0,
                            "can_delete_test": 0,
                            "can_approve_test": 0,
                            "can_manage_team": 0,
                            "can_generate_reports": 1,
                            "can_export_data": 0,
                            "can_manage_settings": 0,
                        },
                        "RMCVendor": {
                            "can_create_batch": 0,
                            "can_edit_batch": 0,
                            "can_delete_batch": 0,
                            "can_approve_batch": 0,
                            "can_create_test": 0,
                            "can_edit_test": 0,
                            "can_delete_test": 0,
                            "can_approve_test": 0,
                            "can_manage_team": 0,
                            "can_generate_reports": 0,
                            "can_export_data": 0,
                            "can_manage_settings": 0,
                        },
                    }
                    
                    perms = role_permissions.get(user_data["role"], role_permissions["Viewer"])
                    
                    membership = ProjectMembership(
                        project_id=project.id,
                        user_id=user.id,
                        role=user_data["role"],
                        **perms,
                        is_active=1,
                        joined_at=datetime.utcnow()
                    )
                    db.session.add(membership)
                    db.session.commit()
                    print(f"   └─ Added to project as: {user_data['role']}")
            
            created_users.append(user)
        
        print("\n" + "=" * 60)
        print("✅ Demo Users Setup Complete!")
        print("=" * 60)
        print("\n📋 Login Credentials Summary:\n")
        
        for user_data in demo_users:
            print(f"Email: {user_data['email']:35} | Password: {user_data['password']:15} | Role: {user_data['role'] or 'System/Company Admin'}")
        
        print("\n" + "=" * 60)
        print("🔐 All users have been created with their respective roles and permissions")
        print("🌐 Use these credentials to login at: http://localhost:3000/login")

if __name__ == "__main__":
    create_demo_users()
