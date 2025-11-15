#!/usr/bin/env python3
"""
Add training_records table to the database.
Run this migration to add the Site Training Register feature.
"""

from server.db import init_db, engine
from server.models import Base, TrainingRecord
from sqlalchemy import text

def migrate():
    """Add training_records table."""
    print("🔄 Adding training_records table...")
    
    # Create the table
    Base.metadata.create_all(engine, tables=[TrainingRecord.__table__])
    
    # Verify table was created
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='training_records'"))
        if result.fetchone():
            print("✅ training_records table created successfully!")
        else:
            print("❌ Failed to create training_records table")
            return False
    
    print("\n✅ Migration completed successfully!")
    print("\n📋 Training Register Features:")
    print("   • Photo upload (click or upload)")
    print("   • Timestamp tracking")
    print("   • Multiple trainee names")
    print("   • Location (building-wise)")
    print("   • Activity types (Blockwork, Gypsum, Plastering, etc.)")
    print("   • Training statistics")
    print("   • Soft delete (QM only)")
    
    return True

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
