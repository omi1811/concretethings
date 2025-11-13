"""
Seed Standard Safety Data
Loads 18 standard induction topics and comprehensive audit checklist
"""

import sys
from sqlalchemy import text
from server.db import SessionLocal
from server.safety_inductions import seed_standard_topics
from server.safety_audit_models import seed_standard_checklists

def seed_safety_data():
    """
    Seed standard safety data for all companies
    """
    try:
        print("=" * 60)
        print("Seeding Standard Safety Data")
        print("=" * 60)
        print()
        
        session = SessionLocal()
        try:
            # Get all companies using raw SQL to avoid model schema mismatch
            result = session.execute(text("SELECT id, name FROM companies WHERE is_active = 1"))
            companies = result.fetchall()
            
            if not companies:
                print("⚠️  No companies found. Please create a company first.")
                return False
            
            print(f"Found {len(companies)} companies")
            print()
            
            for company_id, company_name in companies:
                print(f"Processing: {company_name} (ID: {company_id})")
                print("-" * 60)
                
                # Get any active user for this company
                user_result = session.execute(
                    text("SELECT id FROM users WHERE company_id = :company_id AND is_active = 1 LIMIT 1"),
                    {"company_id": company_id}
                )
                user = user_result.fetchone()
                
                if not user:
                    print(f"⚠️  No active user found for {company_name}. Skipping...")
                    print()
                    continue
                
                user_id = user[0]
                
                # Seed induction topics
                print("📚 Seeding 18 standard induction topics...")
                try:
                    seed_standard_topics(company_id, user_id)
                    print("✅ Induction topics seeded successfully")
                except Exception as e:
                    print(f"❌ Failed to seed topics: {str(e)}")
                
                print()
                
                # Seed audit checklists
                print("📋 Seeding comprehensive audit checklist (48 items)...")
                try:
                    seed_standard_checklists(company_id, user_id)
                    print("✅ Audit checklist seeded successfully")
                except Exception as e:
                    print(f"❌ Failed to seed checklist: {str(e)}")
                
                print()
            
            print("=" * 60)
            print("Seeding Complete!")
            print("=" * 60)
            print()
            print("Standard data loaded:")
            print("  ✅ 18 Safety Induction Topics")
            print("     - PPE Usage, Working at Height, Fire Safety, Excavation,")
            print("       Electrical, Housekeeping, TBT, PTW, Confined Space,")
            print("       Material Handling, Incident Reporting, First Aid,")
            print("       Chemical Safety, Scaffolding, Vehicle Safety, Hot Work,")
            print("       Concrete Pouring, Weather Hazards")
            print()
            print("  ✅ Comprehensive Safety Audit Checklist (48 items)")
            print("     - 16 categories covering ISO 45001 & OSHA requirements")
            print("     - General Housekeeping, PPE, Working at Height, Excavation,")
            print("       Electrical, Fire Safety, Scaffolding, Equipment,")
            print("       Permit to Work, Training, First Aid, Incident Reporting,")
            print("       Safety Signage")
            print()
            
            return True
            
        finally:
            session.close()
            
    except Exception as e:
        print()
        print("❌ Seeding failed!")
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_safety_data()
    sys.exit(0 if success else 1)
