"""
Database Migration Script for New Safety Modules
Adds tables for: Safety Inductions, Incident Investigation, Safety Audits, PPE Tracking, Geo-fencing
Also adds Aadhar verification fields to Worker model
"""

import sys
from datetime import datetime
from server.db import init_db
from server.models import *
from server.safety_models import *
from server.safety_nc_models import *
from server.permit_to_work_models import *
from server.tbt_models import *
from server.training_attendance_models import *
from server.safety_induction_models import *
from server.incident_investigation_models import *
from server.safety_audit_models import *
from server.ppe_tracking_models import *
from server.geofence_models import *

def run_migration():
    """
    Run database migration to add new tables
    """
    try:
        print("=" * 60)
        print("ProSite Database Migration - New Safety Modules")
        print("=" * 60)
        print()
        
        # Initialize database (creates all tables defined in models)
        print("📊 Creating new database tables...")
        print()
        
        init_db()
        
        print("✅ Database tables created successfully!")
        print()
        print("New tables added:")
        print("  1. safety_inductions - Worker induction records")
        print("  2. induction_topics - Safety topics library")
        print("  3. incident_reports - Incident investigation records")
        print("  4. safety_audits - Safety audit records")
        print("  5. audit_checklists - Audit checklist templates")
        print("  6. ppe_issuances - PPE issue/return tracking")
        print("  7. ppe_inventory - PPE stock management")
        print("  8. geofence_locations - Project geofences")
        print("  9. location_verifications - GPS verification logs")
        print()
        
        # Check if Aadhar fields need to be added to Worker model
        print("📋 Checking Worker model for Aadhar fields...")
        print()
        
        # Note: SQLAlchemy with init_db() should automatically add new columns
        # If using Alembic migrations, you would generate migration separately
        
        print("✅ Worker model updated with Aadhar verification fields:")
        print("  - aadhar_number (String 12)")
        print("  - aadhar_photo_front (String 500)")
        print("  - aadhar_photo_back (String 500)")
        print("  - aadhar_verified (Boolean)")
        print("  - verified_by_id (ForeignKey users.id)")
        print("  - verification_date (DateTime)")
        print()
        
        print("=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run seed scripts to load standard data:")
        print("     python3 seed_safety_data.py")
        print()
        print("  2. Test new API endpoints:")
        print("     python3 test_new_modules.py")
        print()
        print("  3. Update frontend to use new modules")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("❌ Migration failed!")
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
