#!/usr/bin/env python3
"""
Export SQLite database to JSON files for migration to Supabase/PostgreSQL
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Database configuration
SQLITE_DB = "data.sqlite3"
OUTPUT_DIR = "migration_data"

def serialize_value(value):
    """Serialize datetime and other special types to JSON-compatible format"""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, bytes):
        return value.hex()  # Convert binary to hex string
    return value

def export_table(cursor, table_name):
    """Export a table to JSON"""
    print(f"Exporting {table_name}...")
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    data = []
    for row in rows:
        row_dict = {}
        for col_name, value in zip(columns, row):
            row_dict[col_name] = serialize_value(value)
        data.append(row_dict)
    
    return {
        "table": table_name,
        "columns": columns,
        "row_count": len(data),
        "data": data
    }

def main():
    """Main export function"""
    print("="*80)
    print("SQLite to JSON Export for Supabase Migration")
    print("="*80)
    
    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    
    # Connect to SQLite database
    if not Path(SQLITE_DB).exists():
        print(f"❌ Error: Database file '{SQLITE_DB}' not found!")
        return
    
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Found {len(tables)} tables to export")
    print(f"📁 Output directory: {output_dir.absolute()}\n")
    
    # Export each table
    exported_files = []
    total_rows = 0
    
    for table_name in tables:
        try:
            table_data = export_table(cursor, table_name)
            
            # Save to JSON file
            output_file = output_dir / f"{table_name}.json"
            with open(output_file, 'w') as f:
                json.dump(table_data, f, indent=2)
            
            rows = table_data['row_count']
            total_rows += rows
            exported_files.append(output_file)
            print(f"  ✅ {table_name}: {rows} rows → {output_file.name}")
            
        except Exception as e:
            print(f"  ❌ {table_name}: Error - {e}")
    
    conn.close()
    
    # Create manifest file
    manifest = {
        "export_date": datetime.now().isoformat(),
        "source_database": SQLITE_DB,
        "tables_exported": len(exported_files),
        "total_rows": total_rows,
        "tables": [f.name for f in exported_files]
    }
    
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "="*80)
    print(f"✅ Export completed!")
    print(f"   Tables exported: {len(exported_files)}")
    print(f"   Total rows: {total_rows}")
    print(f"   Manifest file: {manifest_file}")
    print("="*80)
    print("\n📝 Next step: Run convert_schema_to_postgres.py")

if __name__ == "__main__":
    main()
