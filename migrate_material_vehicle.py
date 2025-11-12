"""
Database Migration Script
Adds Material Vehicle Register and Project Settings tables
Run with: python migrate_material_vehicle.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.db import Base, engine, SessionLocal, init_db
from server.models import MaterialVehicleRegister, ProjectSettings
from sqlalchemy import text, inspect

def run_migration():
    """Run the migration to add new tables"""
    print("=" * 60)
    print("Material Vehicle Register Migration")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database connection...")
    init_db()
    
    # Check if tables already exist
    print("\n2. Checking existing tables...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"   Found {len(existing_tables)} existing tables")
    
    # Create new tables
    print("\n3. Creating new tables...")
    
    try:
        # This will create only the tables that don't exist
        Base.metadata.create_all(engine)
        print("   ✓ Tables created successfully")
    except Exception as e:
        print(f"   ✗ Error creating tables: {e}")
        return False
    
    # Verify new tables
    print("\n4. Verifying new tables...")
    inspector = inspect(engine)
    current_tables = inspector.get_table_names()
    
    if 'material_vehicle_register' in current_tables:
        print("   ✓ material_vehicle_register table created")
    else:
        print("   ✗ material_vehicle_register table NOT created")
        return False
    
    if 'project_settings' in current_tables:
        print("   ✓ project_settings table created")
    else:
        print("   ✗ project_settings table NOT created")
        return False
    
    # Create indexes for performance
    print("\n5. Creating indexes...")
    try:
        with engine.connect() as conn:
            # Indexes for material_vehicle_register
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_material_vehicle_project 
                ON material_vehicle_register(project_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_material_vehicle_status 
                ON material_vehicle_register(status)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_material_vehicle_material_type 
                ON material_vehicle_register(material_type)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_material_vehicle_entry_time 
                ON material_vehicle_register(entry_time)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_material_vehicle_exceeded 
                ON material_vehicle_register(exceeded_time_limit)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_material_vehicle_linked 
                ON material_vehicle_register(is_linked_to_batch)
            """))
            
            conn.commit()
        
        print("   ✓ Indexes created successfully")
    except Exception as e:
        print(f"   ✗ Error creating indexes: {e}")
        # Indexes are optional, continue anyway
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    print("\nNew tables added:")
    print("  - material_vehicle_register (for watchmen vehicle logging)")
    print("  - project_settings (for project-specific configurations)")
    print("\nYou can now:")
    print("  1. Use Material Vehicle Register API endpoints")
    print("  2. Configure project settings via API")
    print("  3. Run background jobs for time limit checks")
    print("=" * 60)
    
    return True


def rollback_migration():
    """Rollback the migration (drop new tables)"""
    print("\n" + "=" * 60)
    print("ROLLBACK: Dropping new tables")
    print("=" * 60)
    
    response = input("\nAre you sure you want to drop the new tables? (yes/no): ")
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        return
    
    try:
        with engine.connect() as conn:
            # Drop indexes first
            conn.execute(text("DROP INDEX IF EXISTS idx_material_vehicle_project"))
            conn.execute(text("DROP INDEX IF EXISTS idx_material_vehicle_status"))
            conn.execute(text("DROP INDEX IF EXISTS idx_material_vehicle_material_type"))
            conn.execute(text("DROP INDEX IF EXISTS idx_material_vehicle_entry_time"))
            conn.execute(text("DROP INDEX IF EXISTS idx_material_vehicle_exceeded"))
            conn.execute(text("DROP INDEX IF EXISTS idx_material_vehicle_linked"))
            
            # Drop tables
            conn.execute(text("DROP TABLE IF EXISTS material_vehicle_register"))
            conn.execute(text("DROP TABLE IF EXISTS project_settings"))
            
            conn.commit()
        
        print("✓ Rollback completed successfully")
    except Exception as e:
        print(f"✗ Error during rollback: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        success = run_migration()
        sys.exit(0 if success else 1)
