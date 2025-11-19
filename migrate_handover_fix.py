#!/usr/bin/env python3
"""
Migration: Fix handover_register contractor references
Change contractor_id foreign keys to contractor_company text fields
"""

from server.db import engine
from sqlalchemy import text

def migrate():
    print("=" * 70)
    print("MIGRATION: Fix handover_register contractor references")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            print("\n1. Creating backup table...")
            conn.execute(text("""
                CREATE TABLE handover_register_backup AS 
                SELECT * FROM handover_register
            """))
            print("   ✓ Backup created")
            
            print("\n2. Dropping old table...")
            conn.execute(text("DROP TABLE handover_register"))
            print("   ✓ Old table dropped")
            
            print("\n3. Creating new table with correct schema...")
            conn.execute(text("""
                CREATE TABLE handover_register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    handover_number VARCHAR(50) UNIQUE NOT NULL,
                    work_description TEXT NOT NULL,
                    work_location VARCHAR(255) NOT NULL,
                    work_category VARCHAR(100) NOT NULL,
                    floor_level VARCHAR(50),
                    zone_area VARCHAR(100),
                    
                    -- Contractor fields (NO foreign keys - separate from RMC vendors)
                    outgoing_contractor_name VARCHAR(255) NOT NULL,
                    outgoing_contractor_company VARCHAR(255),
                    outgoing_supervisor_name VARCHAR(255) NOT NULL,
                    outgoing_supervisor_phone VARCHAR(20),
                    outgoing_supervisor_signature TEXT,
                    outgoing_signed_date DATETIME,
                    
                    incoming_contractor_name VARCHAR(255),
                    incoming_contractor_company VARCHAR(255),
                    incoming_supervisor_name VARCHAR(255),
                    incoming_supervisor_phone VARCHAR(20),
                    incoming_supervisor_signature TEXT,
                    incoming_signed_date DATETIME,
                    
                    -- Engineer/Project Manager
                    engineer_name VARCHAR(255) NOT NULL,
                    engineer_designation VARCHAR(100),
                    engineer_signature TEXT,
                    engineer_signed_date DATETIME,
                    
                    -- Handover Details
                    handover_date DATE NOT NULL,
                    scheduled_date DATE,
                    completion_percentage FLOAT DEFAULT 100.0,
                    
                    -- Defects/Snag List
                    defects_identified INTEGER DEFAULT 0,
                    defects_list TEXT,
                    remedial_work_required TEXT,
                    
                    -- Status & Workflow
                    status VARCHAR(50) DEFAULT 'draft',
                    remarks TEXT,
                    
                    -- Timestamps
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """))
            print("   ✓ New table created")
            
            print("\n4. Migrating data...")
            # Get count of records to migrate
            count_result = conn.execute(text("SELECT COUNT(*) FROM handover_register_backup"))
            record_count = count_result.scalar()
            
            if record_count > 0:
                conn.execute(text("""
                    INSERT INTO handover_register (
                        id, project_id, handover_number, work_description, work_location,
                        work_category, floor_level, zone_area,
                        outgoing_contractor_name, outgoing_contractor_company,
                        outgoing_supervisor_name, outgoing_supervisor_phone,
                        outgoing_supervisor_signature, outgoing_signed_date,
                        incoming_contractor_name, incoming_contractor_company,
                        incoming_supervisor_name, incoming_supervisor_phone,
                        incoming_supervisor_signature, incoming_signed_date,
                        engineer_name, engineer_designation, engineer_signature,
                        engineer_signed_date, handover_date, scheduled_date,
                        completion_percentage, defects_identified, defects_list,
                        remedial_work_required, status, remarks,
                        created_at, updated_at, created_by
                    )
                    SELECT 
                        id, project_id, handover_number, work_description, work_location,
                        work_category, floor_level, zone_area,
                        outgoing_contractor_name, 
                        CASE 
                            WHEN outgoing_contractor_id IS NOT NULL 
                            THEN (SELECT name FROM rmc_vendors WHERE id = outgoing_contractor_id)
                            ELSE NULL 
                        END,
                        outgoing_supervisor_name, outgoing_supervisor_phone,
                        outgoing_supervisor_signature, outgoing_signed_date,
                        incoming_contractor_name,
                        CASE 
                            WHEN incoming_contractor_id IS NOT NULL 
                            THEN (SELECT name FROM rmc_vendors WHERE id = incoming_contractor_id)
                            ELSE NULL 
                        END,
                        incoming_supervisor_name, incoming_supervisor_phone,
                        incoming_supervisor_signature, incoming_signed_date,
                        engineer_name, engineer_designation, engineer_signature,
                        engineer_signed_date, handover_date, scheduled_date,
                        completion_percentage, defects_identified, defects_list,
                        remedial_work_required, status, remarks,
                        created_at, updated_at, created_by
                    FROM handover_register_backup
                """))
                print(f"   ✓ Migrated {record_count} records")
            else:
                print("   ℹ No records to migrate")
            
            print("\n5. Dropping backup table...")
            conn.execute(text("DROP TABLE handover_register_backup"))
            print("   ✓ Backup table dropped")
            
            # Commit transaction
            trans.commit()
            
            print("\n" + "=" * 70)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print("\nChanges:")
            print("  - Removed foreign keys to rmc_vendors table")
            print("  - Changed outgoing_contractor_id → outgoing_contractor_company (text)")
            print("  - Changed incoming_contractor_id → incoming_contractor_company (text)")
            print("  - Contractors are now separate from RMC vendors")
            
            return True
            
        except Exception as e:
            trans.rollback()
            print(f"\n✗ Migration failed: {e}")
            print("Rolling back changes...")
            
            # Try to restore from backup if it exists
            try:
                conn.execute(text("DROP TABLE IF EXISTS handover_register"))
                conn.execute(text("""
                    CREATE TABLE handover_register AS 
                    SELECT * FROM handover_register_backup
                """))
                conn.execute(text("DROP TABLE handover_register_backup"))
                print("✓ Restored from backup")
            except:
                print("✗ Could not restore from backup")
            
            return False

if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
