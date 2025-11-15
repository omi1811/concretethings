#!/usr/bin/env python3
"""
Database migration script to add image storage columns.
Run this to upgrade existing database schema.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.sqlite3"

def migrate():
    """Add image storage columns to existing database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(mix_designs)")
    columns = [row[1] for row in cursor.fetchall()]
    
    migrations_needed = []
    
    if 'image_name' not in columns:
        migrations_needed.append("ALTER TABLE mix_designs ADD COLUMN image_name VARCHAR(512)")
    
    if 'image_data' not in columns:
        migrations_needed.append("ALTER TABLE mix_designs ADD COLUMN image_data BLOB")
    
    if 'image_mimetype' not in columns:
        migrations_needed.append("ALTER TABLE mix_designs ADD COLUMN image_mimetype VARCHAR(100)")
    
    if not migrations_needed:
        print("✓ Database is already up to date!")
        return
    
    print(f"Running {len(migrations_needed)} migration(s)...")
    
    for migration in migrations_needed:
        print(f"  - {migration}")
        cursor.execute(migration)
    
    conn.commit()
    conn.close()
    
    print("✓ Database migration completed successfully!")
    print("\nNew features available:")
    print("  - Upload and store mix design images")
    print("  - Images are optimized and stored in database")
    print("  - View images in the UI table and fullscreen")

if __name__ == "__main__":
    migrate()
