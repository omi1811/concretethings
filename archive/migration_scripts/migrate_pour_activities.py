#!/usr/bin/env python3
"""
Database migration script for Pour Activity feature.
Adds:
- pour_activities table (batch consolidation)
- pour_activity_id column to batch_registers
- concrete_type column to cube_test_registers

Run this to upgrade existing database schema.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data.sqlite3"

def migrate():
    """Add Pour Activity tables and columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    migrations_applied = []
    
    # 1. Create pour_activities table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pour_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                pour_id VARCHAR(100) UNIQUE NOT NULL,
                pour_date DATETIME NOT NULL,
                
                -- Location details
                building_name VARCHAR(200),
                floor_level VARCHAR(100),
                zone VARCHAR(100),
                grid_reference VARCHAR(100),
                structural_element_type VARCHAR(100),
                element_id VARCHAR(200),
                location_description TEXT,
                
                -- Concrete details
                concrete_type VARCHAR(20) DEFAULT 'Normal',
                design_grade VARCHAR(50),
                total_quantity_planned REAL,
                total_quantity_received REAL,
                
                -- Status workflow
                status VARCHAR(50) DEFAULT 'in_progress',
                started_at DATETIME,
                completed_at DATETIME,
                
                -- Audit
                created_by INTEGER,
                completed_by INTEGER,
                remarks TEXT,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (completed_by) REFERENCES users(id)
            )
        """)
        migrations_applied.append("✓ Created pour_activities table")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("⚠ pour_activities table already exists, skipping creation")
        else:
            raise
    
    # 2. Add pour_activity_id to batch_registers
    cursor.execute("PRAGMA table_info(batch_registers)")
    batch_columns = [row[1] for row in cursor.fetchall()]
    
    if 'pour_activity_id' not in batch_columns:
        cursor.execute("""
            ALTER TABLE batch_registers 
            ADD COLUMN pour_activity_id INTEGER 
            REFERENCES pour_activities(id)
        """)
        migrations_applied.append("✓ Added pour_activity_id to batch_registers")
    else:
        print("⚠ pour_activity_id already exists in batch_registers")
    
    # 3. Add concrete_type to cube_test_registers
    cursor.execute("PRAGMA table_info(cube_test_registers)")
    cube_columns = [row[1] for row in cursor.fetchall()]
    
    if 'concrete_type' not in cube_columns:
        cursor.execute("""
            ALTER TABLE cube_test_registers 
            ADD COLUMN concrete_type VARCHAR(20) DEFAULT 'Normal'
        """)
        migrations_applied.append("✓ Added concrete_type to cube_test_registers")
    else:
        print("⚠ concrete_type already exists in cube_test_registers")
    
    # 4. Add pour_activity_id to cube_test_registers
    if 'pour_activity_id' not in cube_columns:
        cursor.execute("""
            ALTER TABLE cube_test_registers 
            ADD COLUMN pour_activity_id INTEGER 
            REFERENCES pour_activities(id)
        """)
        migrations_applied.append("✓ Added pour_activity_id to cube_test_registers")
    else:
        print("⚠ pour_activity_id already exists in cube_test_registers")
    
    # 5. Create index for performance
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pour_activities_project 
            ON pour_activities(project_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pour_activities_status 
            ON pour_activities(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_pour_activity 
            ON batch_registers(pour_activity_id)
        """)
        migrations_applied.append("✓ Created indexes for performance")
    except sqlite3.OperationalError as e:
        print(f"⚠ Index creation warning: {e}")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    if not migrations_applied:
        print("\n✓ Database is already up to date!")
        return
    
    print("\n" + "="*60)
    print("MIGRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    
    for migration in migrations_applied:
        print(migration)
    
    print("\n" + "="*60)
    print("NEW FEATURES AVAILABLE")
    print("="*60)
    print("""
✓ Pour Activity System (Batch Consolidation)
  - Group multiple batches/vehicles into one pour
  - Track location and concrete details
  - Support Normal and PT (Post-Tensioned) concrete
  
✓ PT Concrete Testing
  - Normal concrete: 3, 7, 28, 56 day tests
  - PT concrete: 5, 7, 28, 56 day tests (5 instead of 3)
  
✓ Use Case: Large Slab Pour
  Example: 4m³ slab needing 3+ vehicles
  1. Create Pour Activity: "Grid A-12, Slab, Level 5, PT, 4m³"
  2. Add Batch 1: 1.5m³ (Vehicle 1)
  3. Add Batch 2: 1.5m³ (Vehicle 2)
  4. Add Batch 3: 1.0m³ (Vehicle 3)
  5. Complete Pour → ONE set of cube tests
  
API Endpoints:
  POST   /api/pour-activities         (create)
  GET    /api/pour-activities         (list)
  GET    /api/pour-activities/:id     (details)
  PUT    /api/pour-activities/:id     (update)
  POST   /api/pour-activities/:id/complete (complete & trigger cube modal)
  POST   /api/pour-activities/:id/batches  (add batch to pour)
  DELETE /api/pour-activities/:id     (cancel)
    """)
    print("="*60)

def rollback():
    """Rollback migration (use with caution - data loss!)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n⚠ WARNING: This will remove Pour Activity tables and data!")
    response = input("Are you sure? Type 'yes' to confirm: ")
    
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        return
    
    try:
        # Remove columns (SQLite doesn't support DROP COLUMN directly)
        print("⚠ SQLite limitation: Cannot drop columns. Manual intervention needed.")
        print("To fully rollback:")
        print("1. Backup data.sqlite3")
        print("2. DROP TABLE pour_activities")
        print("3. Recreate batch_registers without pour_activity_id")
        print("4. Recreate cube_test_registers without concrete_type/pour_activity_id")
        
        # We can drop the table
        cursor.execute("DROP TABLE IF EXISTS pour_activities")
        conn.commit()
        print("✓ Dropped pour_activities table")
        
    except Exception as e:
        print(f"✗ Rollback failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
