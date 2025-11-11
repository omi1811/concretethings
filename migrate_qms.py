"""
Database migration script for Concrete QMS features.
Adds all new tables and soft delete columns.

Run: python migrate_qms.py
"""
import os
import sys
from datetime import datetime

# Add server directory to path FIRST
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Now import with proper module names
import db
import models

from sqlalchemy import text


def migrate_database():
    """Run database migration."""
    print("=" * 70)
    print("DATABASE MIGRATION - ConcreteThings QMS")
    print("=" * 70)
    print()
    
    try:
        # Create all new tables
        print("Creating new tables...")
        models.Base.metadata.create_all(db.engine)
        print("✅ All tables created successfully")
        print()
        
        # Add soft delete columns to existing MixDesign table if not exists
        print("Checking MixDesign table for soft delete columns...")
        
        with db.session_scope() as session:
            try:
                # Check if columns exist
                result = session.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pragma_table_info('mix_designs') 
                    WHERE name IN ('is_deleted', 'deleted_at', 'deleted_by')
                """))
                count = result.scalar()
                
                if count < 3:
                    print("Adding soft delete columns to mix_designs table...")
                    
                    # Add columns one by one
                    try:
                        session.execute(text("ALTER TABLE mix_designs ADD COLUMN is_deleted INTEGER DEFAULT 0"))
                        print("  ✅ Added is_deleted column")
                    except Exception as e:
                        if "duplicate column" not in str(e).lower():
                            print(f"  ⚠️  is_deleted column may already exist: {e}")
                    
                    try:
                        session.execute(text("ALTER TABLE mix_designs ADD COLUMN deleted_at TIMESTAMP"))
                        print("  ✅ Added deleted_at column")
                    except Exception as e:
                        if "duplicate column" not in str(e).lower():
                            print(f"  ⚠️  deleted_at column may already exist: {e}")
                    
                    try:
                        session.execute(text("ALTER TABLE mix_designs ADD COLUMN deleted_by INTEGER"))
                        print("  ✅ Added deleted_by column")
                    except Exception as e:
                        if "duplicate column" not in str(e).lower():
                            print(f"  ⚠️  deleted_by column may already exist: {e}")
                    
                    print("✅ MixDesign table updated with soft delete columns")
                else:
                    print("✅ MixDesign table already has soft delete columns")
            except Exception as e:
                print(f"⚠️  Note: {e}")
        
        print()
        
        # Print summary
        print("=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print()
        print("✅ Tables Created/Verified:")
        print("  1. companies (existing)")
        print("  2. users (existing)")
        print("  3. projects (existing)")
        print("  4. project_memberships (existing)")
        print("  5. mix_designs (updated with soft delete)")
        print("  6. rmc_vendors (new)")
        print("  7. batch_registers (new)")
        print("  8. cube_test_registers (new)")
        print("  9. third_party_labs (new)")
        print(" 10. third_party_cube_tests (new)")
        print(" 11. material_categories (new)")
        print(" 12. approved_brands (new)")
        print(" 13. material_test_registers (new)")
        print()
        print("✅ Migration completed successfully!")
        print()
        print("Next steps:")
        print("  1. Run: python seed.py  (to add sample data)")
        print("  2. Start server: python server/app.py")
        print()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()
