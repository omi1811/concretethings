#!/usr/bin/env python3
"""
Convert SQLite schema to PostgreSQL-compatible schema
"""
import sqlite3
import re
from pathlib import Path

SQLITE_DB = "data.sqlite3"
OUTPUT_FILE = "schema_postgres.sql"

def convert_type(sqlite_type):
    """Convert SQLite types to PostgreSQL types"""
    type_map = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'REAL',
        'BLOB': 'BYTEA',
        'NUMERIC': 'NUMERIC',
        'BOOLEAN': 'BOOLEAN',
        'DATETIME': 'TIMESTAMP',
        'DATE': 'DATE',
        'TIME': 'TIME'
    }
    
    sqlite_type_upper = sqlite_type.upper().strip()
    
    # Handle VARCHAR(n)
    if 'VARCHAR' in sqlite_type_upper:
        return sqlite_type
    
    # Handle special cases
    for key, value in type_map.items():
        if key in sqlite_type_upper:
            return value
    
    return 'TEXT'  # Default to TEXT

def convert_schema(sqlite_schema):
    """Convert SQLite CREATE TABLE statement to PostgreSQL"""
    
    # Replace AUTOINCREMENT with PostgreSQL SERIAL
    schema = re.sub(
        r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
        'SERIAL PRIMARY KEY',
        sqlite_schema,
        flags=re.IGNORECASE
    )
    
    # Replace INTEGER PRIMARY KEY with SERIAL PRIMARY KEY
    schema = re.sub(
        r'INTEGER\s+PRIMARY\s+KEY',
        'SERIAL PRIMARY KEY',
        schema,
        flags=re.IGNORECASE
    )
    
    # Convert DATETIME to TIMESTAMP
    schema = re.sub(r'\bDATETIME\b', 'TIMESTAMP', schema, flags=re.IGNORECASE)
    
    # Convert BLOB to BYTEA
    schema = re.sub(r'\bBLOB\b', 'BYTEA', schema, flags=re.IGNORECASE)
    
    # Remove IF NOT EXISTS for cleaner output (optional)
    # schema = re.sub(r'IF NOT EXISTS\s+', '', schema, flags=re.IGNORECASE)
    
    return schema

def main():
    """Main conversion function"""
    print("="*80)
    print("SQLite Schema Conversion to PostgreSQL")
    print("="*80)
    
    if not Path(SQLITE_DB).exists():
        print(f"❌ Error: Database file '{SQLITE_DB}' not found!")
        return
    
    # Connect to SQLite database
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    # Get all table schemas
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📊 Converting {len(tables)} table schemas\n")
    
    # Open output file
    with open(OUTPUT_FILE, 'w') as f:
        f.write("-- PostgreSQL Schema converted from SQLite\n")
        f.write(f"-- Generated: {Path(SQLITE_DB).name}\n")
        f.write("-- \n\n")
        
        f.write("-- Drop existing tables if needed (uncomment to use)\n")
        for table_name, _ in tables:
            f.write(f"-- DROP TABLE IF EXISTS {table_name} CASCADE;\n")
        f.write("\n\n")
        
        # Convert and write each table schema
        for table_name, schema_sql in tables:
            if schema_sql:  # Some system tables might not have SQL
                print(f"  ✅ Converting {table_name}")
                converted = convert_schema(schema_sql)
                f.write(f"-- Table: {table_name}\n")
                f.write(converted + ";\n\n")
        
        # Add indexes hint
        f.write("\n-- Don't forget to add indexes for foreign keys and frequently queried columns\n")
        f.write("-- Example:\n")
        f.write("-- CREATE INDEX idx_users_company_id ON users(company_id);\n")
        f.write("-- CREATE INDEX idx_projects_company_id ON projects(company_id);\n")
    
    conn.close()
    
    print("\n" + "="*80)
    print(f"✅ Schema conversion completed!")
    print(f"   Output file: {OUTPUT_FILE}")
    print(f"   Tables converted: {len(tables)}")
    print("="*80)
    print("\n📝 Next steps:")
    print("   1. Review the generated schema file")
    print("   2. Create Supabase project and get credentials")
    print("   3. Run the schema in Supabase SQL Editor")
    print("   4. Run import_to_postgres.py to import data")

if __name__ == "__main__":
    main()
