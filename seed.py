#!/usr/bin/env python3
"""Seed script to populate the database with sample mix designs."""
from server.db import init_db, session_scope
from server.models import MixDesign, Company, User, Project, ProjectMembership
from werkzeug.security import generate_password_hash


def seed_data():
    """Create sample mix design data."""
    init_db()
    
    sample_designs = [
        {
            "project_name": "Downtown Plaza",
            "mix_design_id": "MD-3000-A",
            "specified_strength_psi": 3000,
            "slump_inches": 4.0,
            "air_content_percent": 6.0,
            "batch_volume": 1.0,
            "volume_unit": "cubic_yards",
            "materials": "Portland Cement Type I/II: 517 lbs\nCoarse Aggregate: 1840 lbs\nFine Aggregate: 1326 lbs\nWater: 275 lbs",
            "notes": "Standard mix for foundations and footings",
        },
        {
            "project_name": "Highway Bridge Deck",
            "mix_design_id": "MD-4000-B",
            "specified_strength_psi": 4000,
            "slump_inches": 3.5,
            "air_content_percent": 6.5,
            "batch_volume": 2.0,
            "volume_unit": "cubic_yards",
            "materials": "Portland Cement Type II: 611 lbs\nCoarse Aggregate: 1753 lbs\nFine Aggregate: 1247 lbs\nWater: 267 lbs\nAdmixture: 8 oz",
            "notes": "High-strength mix for bridge deck, 28-day target",
        },
        {
            "project_name": "Parking Structure",
            "mix_design_id": "MD-3500-C",
            "specified_strength_psi": 3500,
            "slump_inches": 4.5,
            "air_content_percent": 5.5,
            "batch_volume": 1.5,
            "volume_unit": "cubic_yards",
            "materials": "Portland Cement Type I: 564 lbs\nCoarse Aggregate: 1796 lbs\nFine Aggregate: 1286 lbs\nWater: 271 lbs",
            "notes": "Elevated slab pour, pump mix",
        },
    ]
    
    with session_scope() as session:
        # Check if data already exists
        existing_count = session.query(MixDesign).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} mix design(s). Skipping seed.")
            return
        
        # Insert sample data
        for design_data in sample_designs:
            mix = MixDesign(**design_data)
            session.add(mix)
        
        session.flush()
        print(f"✓ Successfully seeded {len(sample_designs)} mix designs!")

    # Create sample company and admin user if not present
    with session_scope() as session:
        if session.query(Company).count() == 0:
            comp = Company(name='Demo Concrete Co')
            session.add(comp)
            session.flush()

            admin = User(
                email='admin@demo.com',
                phone='+15551234567',  # Sample phone number
                full_name='System Admin',
                password_hash=generate_password_hash('adminpass', method='pbkdf2:sha256'),
                company_id=comp.id,
                is_company_admin=1,
                is_system_admin=1,  # Make this user a system admin
            )
            session.add(admin)
            session.flush()

            proj = Project(company_id=comp.id, name='Demo Project')
            session.add(proj)
            session.flush()

            pm = ProjectMembership(project_id=proj.id, user_id=admin.id, role='Admin')
            session.add(pm)
            session.flush()

            print('✓ Created sample company, admin user, and demo project (adminpass)')


if __name__ == "__main__":
    seed_data()
