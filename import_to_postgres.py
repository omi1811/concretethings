#!/usr/bin/env python3
"""
Import JSON data to PostgreSQL/Supabase database
Respects foreign key constraints by importing tables in correct order
"""
import json
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import os
from datetime import datetime

# Configuration
DATA_DIR = "migration_data"
POSTGRES_URL = os.environ.get("DATABASE_URL", "")

# Table import order (respecting foreign key constraints)
TABLE_ORDER = [
    "companies",
    "users",
    "projects",
    "project_memberships",
    "batches",
    "cube_tests",
    "material_tests",
    "ncr",
    "safety_nc",
    "ptw",
    "trainings",
    "pour_activities",
    "labs",
    "handovers",
    "gate_register",
    # Add other tables as needed
]

def get_table_files():
    """Get all JSON files in migration_data directory"""
    data_dir = Path(DATA_DIR)
    if not data_dir.exists():
        print(f"❌ Error: Migration data directory '{DATA_DIR}' not found!")
        return []
    
    json_files = list(data_dir.glob("*.json"))
    # Exclude manifest
    json_files = [f for f in json_files if f.stem != "manifest"]
    
    return json_files

def sort_tables_by_dependency(json_files):
    """Sort tables by dependency order"""
    sorted_files = []
    remaining_files = json_files.copy()
    
    # First, add tables in the defined order
    for table_name in TABLE_ORDER:
        for file in remaining_files:
            if file.stem == table_name:
                sorted_files.append(file)
                remaining_files.remove(file)
                break
    
    # Add any remaining tables
    sorted_files.extend(remaining_files)
    
    return sorted_files

def import_table(cursor, table_file):
    """Import data from JSON file to PostgreSQL table"""
    with open(table_file, 'r') as f:
        table_data = json.load(f)
    
    table_name = table_data['table']
    columns = table_data['columns']
    rows = table_data['data']
    
    if not rows:
        print(f"  ⏭️  {table_name}: No data to import")
        return 0
    
    # Build INSERT query
    column_names = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    # Prepare data for batch insert
    values = []
    for row in rows:
        row_values = [row.get(col) for col in columns]
        # Convert hex strings back to bytes for BYTEA columns if needed
        values.append(tuple(row_values))
    
    try:
        # Use batch insert for better performance
        execute_batch(cursor, query, values, page_size=100)
        return len(values)
    except Exception as e:
        print(f"  ❌ Error importing {table_name}: {e}")
        # Try one by one to identify problematic rows
        success_count = 0
        for i, row_values in enumerate(values):
            try:
                cursor.execute(query, row_values)
                success_count += 1
            except Exception as row_error:
                print(f"     Row {i+1} failed: {row_error}")
        return success_count

def reset_sequences(cursor):
    """Reset PostgreSQL sequences to max ID + 1"""
    print("\n🔄 Resetting sequences...")
    
    # Get all sequences
    cursor.execute("""
        SELECT sequence_name, table_name, column_name
        FROM information_schema.sequences s
        JOIN information_schema.columns c ON c.column_default LIKE '%' || s.sequence_name || '%'
        WHERE s.sequence_schema = 'public'
    """)
    
    sequences = cursor.fetchall()
    
    for seq_name, table_name, col_name in sequences:
        try:
            cursor.execute(f"SELECT MAX({col_name}) FROM {table_name}")
            max_id = cursor.fetchone()[0]
            
            if max_id:
                cursor.execute(f"SELECT setval('{seq_name}', {max_id})")
                print(f"  ✅ {seq_name} → {max_id}")
        except Exception as e:
            print(f"  ⚠️  {seq_name}: {e}")

def main():
    """Main import function"""
    print("="*80)
    print("PostgreSQL/Supabase Data Import")
    print("="*80)
    
    # Check database URL
    if not POSTGRES_URL:
        print("\n❌ Error: DATABASE_URL environment variable not set!")
        print("\nPlease set it with:")
        print('export DATABASE_URL="postgresql://user:pass@host:5432/database"')
        return
    
    print(f"\n🔗 Connecting to database...")
    print(f"   Host: {POSTGRES_URL.split('@')[1].split('/')[0] if '@' in POSTGRES_URL else 'localhost'}")
    
    # Get table files
    json_files = get_table_files()
    if not json_files:
        return
    
    # Sort by dependency
    sorted_files = sort_tables_by_dependency(json_files)
    
    print(f"\n📊 Found {len(sorted_files)} tables to import")
    print(f"📁 Data directory: {Path(DATA_DIR).absolute()}\n")
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()
        
        # Disable foreign key checks temporarily for faster import
        cursor.execute("SET session_replication_role = 'replica';")
        
        total_rows = 0
        imported_tables = []
        
        # Import each table
        for table_file in sorted_files:
            try:
                rows_imported = import_table(cursor, table_file)
                total_rows += rows_imported
                imported_tables.append(table_file.stem)
                print(f"  ✅ {table_file.stem}: {rows_imported} rows imported")
            except Exception as e:
                print(f"  ❌ {table_file.stem}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET session_replication_role = 'origin';")
        
        # Reset sequences
        reset_sequences(cursor)
        
        # Commit transaction
        conn.commit()
        
        print("\n" + "="*80)
        print(f"✅ Import completed!")
        print(f"   Tables imported: {len(imported_tables)}")
        print(f"   Total rows: {total_rows}")
        print("="*80)
        
        cursor.close()
        conn.close()
        
        print("\n📝 Next steps:")
        print("   1. Verify data integrity")
        print("   2. Test API endpoints")
        print("   3. Run test suite")
        print("   4. Deploy to production")
        
    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        print("\nTroubleshooting:")
        print("   1. Check DATABASE_URL is correct")
        print("   2. Verify network connectivity to database")
        print("   3. Ensure database user has INSERT privileges")

if __name__ == "__main__":
    main()
