#!/usr/bin/env python3
"""
Alternative Migration: Generate SQL INSERT statements for Supabase SQL Editor
Works around network restrictions by creating SQL file you can paste directly
"""
import json
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = "migration_data"
OUTPUT_FILE = "supabase_migration_inserts.sql"

def escape_sql_string(value):
    """Escape string for SQL"""
    if value is None:
        return "NULL"
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Escape single quotes
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    else:
        return f"'{str(value)}'"

def generate_insert_statements(table_file):
    """Generate INSERT statements for a table"""
    with open(table_file, 'r') as f:
        table_data = json.load(f)
    
    table_name = table_data['table']
    columns = table_data['columns']
    rows = table_data['data']
    
    if not rows:
        return f"-- {table_name}: No data to insert\n"
    
    statements = [f"\n-- Table: {table_name} ({len(rows)} rows)"]
    
    for row in rows:
        values = []
        for col in columns:
            value = row.get(col)
            values.append(escape_sql_string(value))
        
        column_list = ', '.join(columns)
        value_list = ', '.join(values)
        statements.append(f"INSERT INTO {table_name} ({column_list}) VALUES ({value_list});")
    
    return '\n'.join(statements) + '\n'

def main():
    """Generate SQL file with all INSERT statements"""
    print("="*80)
    print("🚀 Generating SQL INSERT Statements for Supabase")
    print("="*80)
    print()
    print("⚠️  Network limitation detected in Codespaces")
    print("   Creating SQL file you can run directly in Supabase SQL Editor")
    print()
    
    data_dir = Path(DATA_DIR)
    if not data_dir.exists():
        print(f"❌ Error: {DATA_DIR} not found. Run export_sqlite_data.py first")
        return
    
    # Table order (respecting foreign keys)
    table_order = [
        "companies",
        "users",
        "material_categories",
        "projects",
        "third_party_labs",
        "approved_brands",
        "project_memberships",
        "rmc_vendors",
        "project_settings",
        "mix_designs",
        "batch_registers",
        "cube_test_registers",
        "third_party_cube_tests",
        "material_vehicle_register",
        "material_test_registers",
        "pour_activities",
        "test_reminders",
        "safety_modules",
        "safety_workers",
        "permit_types",
        "tbt_sessions",
        "tbt_topics",
        "induction_topics",
        "incident_reports",
        "audit_checklists",
        "ppe_inventory",
        "geofence_locations",
        "location_verifications",
        "safety_form_templates",
        "safety_worker_attendance",
        "work_permits",
        "tbt_attendances",
        "training_records",
        "training_attendances",
        "safety_inductions",
        "safety_audits",
        "ppe_issuances",
        "safety_form_submissions",
        "permit_signatures",
        "permit_extensions",
        "permit_checklists",
        "permit_audit_logs",
        "safety_actions",
        "safety_non_conformances",
        "safety_nc_comments",
        "safety_contractor_notifications",
        "concrete_nc_tags",
        "concrete_nc_issues",
        "concrete_nc_notifications",
        "concrete_nc_score_reports",
        "password_reset_tokens",
        "safety_nc_score_reports",
    ]
    
    # Get all JSON files
    json_files = {f.stem: f for f in data_dir.glob("*.json") if f.stem != "manifest"}
    
    print(f"📊 Found {len(json_files)} tables")
    print(f"📝 Generating SQL INSERT statements...\n")
    
    with open(OUTPUT_FILE, 'w') as output:
        # Header
        output.write("-- Supabase Migration: Data Import\n")
        output.write(f"-- Generated: {datetime.now().isoformat()}\n")
        output.write("-- Source: SQLite export\n")
        output.write("-- \n")
        output.write("-- INSTRUCTIONS:\n")
        output.write("--   1. First run schema_postgres.sql in Supabase SQL Editor\n")
        output.write("--   2. Then run this file in Supabase SQL Editor\n")
        output.write("--   3. Verify data was imported successfully\n")
        output.write("-- \n\n")
        
        output.write("-- Disable triggers for faster import\n")
        output.write("SET session_replication_role = 'replica';\n\n")
        
        output.write("BEGIN;\n\n")
        
        total_rows = 0
        
        # Process tables in order
        for table_name in table_order:
            if table_name in json_files:
                print(f"  ✅ {table_name}")
                sql = generate_insert_statements(json_files[table_name])
                output.write(sql)
                
                # Count rows
                with open(json_files[table_name]) as f:
                    data = json.load(f)
                    total_rows += len(data['data'])
        
        # Process any remaining tables not in order
        for table_name, file_path in json_files.items():
            if table_name not in table_order:
                print(f"  ✅ {table_name} (extra)")
                sql = generate_insert_statements(file_path)
                output.write(sql)
                
                with open(file_path) as f:
                    data = json.load(f)
                    total_rows += len(data['data'])
        
        # Reset sequences
        output.write("\n-- Reset sequences to prevent ID conflicts\n")
        for table_name in table_order:
            if table_name in json_files:
                output.write(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1), true) FROM {table_name};\n")
        
        output.write("\n-- Re-enable triggers\n")
        output.write("SET session_replication_role = 'origin';\n\n")
        
        output.write("COMMIT;\n\n")
        output.write(f"-- Import complete: {total_rows} rows inserted\n")
    
    print("\n" + "="*80)
    print("✅ SQL INSERT statements generated!")
    print(f"   Output file: {OUTPUT_FILE}")
    print(f"   Total rows: {total_rows}")
    print("="*80)
    print()
    print("📝 Next Steps:")
    print()
    print("   1. Open Supabase project: https://app.supabase.com")
    print("   2. Go to SQL Editor")
    print("   3. Create new query")
    print("   4. Copy contents of: schema_postgres.sql")
    print("   5. Run the schema query")
    print("   6. Create another new query")
    print(f"   7. Copy contents of: {OUTPUT_FILE}")
    print("   8. Run the data import query")
    print("   9. Verify tables have data in Table Editor")
    print()
    print("✅ Migration complete!")

if __name__ == "__main__":
    main()
