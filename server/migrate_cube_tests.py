import sqlite3
import os
from pathlib import Path

# Path to database
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data.sqlite3"

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    if not DB_PATH.exists():
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Disable foreign keys
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        # 2. Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # 3. Rename existing table
        print("Renaming existing table...")
        cursor.execute("ALTER TABLE cube_test_registers RENAME TO cube_test_registers_old")
        
        # 4. Create new table with nullable batch_id
        # We manually define the CREATE statement to ensure it matches the model exactly
        # but with batch_id as nullable
        print("Creating new table...")
        create_table_sql = """
        CREATE TABLE cube_test_registers (
            id INTEGER NOT NULL, 
            batch_id INTEGER, 
            project_id INTEGER NOT NULL, 
            set_number INTEGER NOT NULL, 
            test_age_days INTEGER NOT NULL, 
            cube_identifier VARCHAR(10), 
            pour_activity_id INTEGER, 
            third_party_lab_id INTEGER, 
            sent_to_lab_date DATETIME, 
            expected_result_date DATETIME, 
            casting_date DATETIME NOT NULL, 
            casting_time VARCHAR(10), 
            cast_by INTEGER NOT NULL, 
            structure_type VARCHAR(100), 
            structure_location TEXT, 
            concrete_grade VARCHAR(50), 
            concrete_type VARCHAR(20), 
            concrete_source VARCHAR(20), 
            number_of_cubes INTEGER, 
            sample_identification VARCHAR(100), 
            curing_method VARCHAR(50), 
            curing_temperature FLOAT, 
            testing_date DATETIME, 
            tested_by INTEGER, 
            testing_machine_id VARCHAR(100), 
            machine_calibration_date DATETIME, 
            cube_1_weight_kg FLOAT, 
            cube_1_length_mm FLOAT, 
            cube_1_width_mm FLOAT, 
            cube_1_height_mm FLOAT, 
            cube_1_load_kn FLOAT, 
            cube_1_strength_mpa FLOAT, 
            cube_2_weight_kg FLOAT, 
            cube_2_length_mm FLOAT, 
            cube_2_width_mm FLOAT, 
            cube_2_height_mm FLOAT, 
            cube_2_load_kn FLOAT, 
            cube_2_strength_mpa FLOAT, 
            cube_3_weight_kg FLOAT, 
            cube_3_length_mm FLOAT, 
            cube_3_width_mm FLOAT, 
            cube_3_height_mm FLOAT, 
            cube_3_load_kn FLOAT, 
            cube_3_strength_mpa FLOAT, 
            average_strength_mpa FLOAT, 
            required_strength_mpa FLOAT, 
            strength_ratio_percent FLOAT, 
            pass_fail_status VARCHAR(20), 
            failure_mode_cube_1 VARCHAR(50), 
            failure_mode_cube_2 VARCHAR(50), 
            failure_mode_cube_3 VARCHAR(50), 
            verified_by INTEGER, 
            verified_at DATETIME, 
            ncr_generated INTEGER, 
            ncr_number VARCHAR(100), 
            notification_sent INTEGER, 
            tester_signature_data BLOB, 
            tester_signature_timestamp DATETIME, 
            verifier_signature_data BLOB, 
            verifier_signature_timestamp DATETIME, 
            remarks TEXT, 
            is_deleted INTEGER, 
            deleted_at DATETIME, 
            deleted_by INTEGER, 
            created_at DATETIME, 
            updated_at DATETIME, 
            PRIMARY KEY (id), 
            FOREIGN KEY(batch_id) REFERENCES batch_registers (id), 
            FOREIGN KEY(project_id) REFERENCES projects (id), 
            FOREIGN KEY(pour_activity_id) REFERENCES pour_activities (id), 
            FOREIGN KEY(third_party_lab_id) REFERENCES third_party_labs (id), 
            FOREIGN KEY(cast_by) REFERENCES users (id), 
            FOREIGN KEY(tested_by) REFERENCES users (id), 
            FOREIGN KEY(verified_by) REFERENCES users (id), 
            FOREIGN KEY(deleted_by) REFERENCES users (id)
        )
        """
        cursor.execute(create_table_sql)
        
        # 5. Copy data
        print("Copying data...")
        # Get columns from old table
        cursor.execute("PRAGMA table_info(cube_test_registers_old)")
        columns = [info[1] for info in cursor.fetchall()]
        columns_str = ", ".join(columns)
        
        cursor.execute(f"INSERT INTO cube_test_registers ({columns_str}) SELECT {columns_str} FROM cube_test_registers_old")
        
        # 6. Drop old table
        print("Dropping old table...")
        cursor.execute("DROP TABLE cube_test_registers_old")
        
        # 7. Commit
        conn.commit()
        print("Migration successful!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
