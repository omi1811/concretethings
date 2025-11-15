#!/usr/bin/env python3
"""Export SQLite to PostgreSQL SQL dump."""
import sqlite3
from datetime import datetime

def escape_sql_string(value):
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value) + "'"

conn = sqlite3.connect('data.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

with open('supabase_migration_dump.sql', 'w') as f:
    f.write(f"-- PostgreSQL dump for Supabase\n")
    f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
    f.write("BEGIN;\n\n")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Exporting {len(tables)} tables...")
    
    for table_name in tables:
        print(f"  - {table_name}")
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if rows:
            col_names = [col[1] for col in columns]
            
            for row in rows:
                values = [escape_sql_string(val) for val in row]
                f.write(f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({', '.join(values)});\n")
    
    f.write("\nCOMMIT;\n")

conn.close()
print("\n✅ Export completed: supabase_migration_dump.sql")
