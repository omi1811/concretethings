#!/usr/bin/env python3
"""
Migration script to update User table with phone, is_system_admin, 
failed_login_attempts, last_login, and updated_at columns.
"""
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.sqlite3"


def migrate():
    """Add new columns to users table."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("Starting user table migration...")
    
    try:
        # Check if phone column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations_needed = []
        
        if "phone" not in columns:
            migrations_needed.append(("phone", "ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
        
        if "is_system_admin" not in columns:
            migrations_needed.append(("is_system_admin", "ALTER TABLE users ADD COLUMN is_system_admin INTEGER DEFAULT 0"))
        
        if "failed_login_attempts" not in columns:
            migrations_needed.append(("failed_login_attempts", "ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
        
        if "last_login" not in columns:
            migrations_needed.append(("last_login", "ALTER TABLE users ADD COLUMN last_login DATETIME"))
        
        if "updated_at" not in columns:
            migrations_needed.append(("updated_at", "ALTER TABLE users ADD COLUMN updated_at DATETIME"))
        
        if "created_at" not in columns:
            migrations_needed.append(("created_at", "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
        
        if not migrations_needed:
            print("✓ All columns already exist. No migration needed.")
            conn.close()
            return
        
        # Execute migrations
        for col_name, sql in migrations_needed:
            print(f"  Adding column: {col_name}")
            cursor.execute(sql)
        
        conn.commit()
        print(f"✓ Successfully added {len(migrations_needed)} column(s) to users table!")
        
        # Update full_name to be NOT NULL (if there are existing records, set default)
        cursor.execute("SELECT COUNT(*) FROM users WHERE full_name IS NULL")
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"  Updating {null_count} user(s) with NULL full_name...")
            cursor.execute("UPDATE users SET full_name = 'Unknown User' WHERE full_name IS NULL")
            conn.commit()
        
        # Update phone to have default if NULL (existing users)
        cursor.execute("SELECT COUNT(*) FROM users WHERE phone IS NULL")
        null_phone_count = cursor.fetchone()[0]
        if null_phone_count > 0:
            print(f"  Warning: {null_phone_count} user(s) have NULL phone. Please update manually.")
            print("  Setting temporary phone numbers for existing users...")
            cursor.execute("UPDATE users SET phone = '+1000000' || id WHERE phone IS NULL")
            conn.commit()
        
        print("✓ Migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
