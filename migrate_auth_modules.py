#!/usr/bin/env python3
"""
Migration script for:
1. Password reset tokens table
2. Module subscription system (subscribed_modules column)
3. Register admin user shrotrio@gmail.com
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def migrate_auth_and_modules(db_path='data.sqlite3'):
    """Add password reset and module subscription features."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("="*60)
        print("AUTH & MODULE SUBSCRIPTION MIGRATION")
        print("="*60)
        print(f"Database: {db_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # 1. Create password_reset_tokens table
        print("Creating password_reset_tokens table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(64) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("✓ password_reset_tokens table created")
        
        # 2. Create indexes
        print("Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_password_reset_token_hash ON password_reset_tokens(token_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_password_reset_expires ON password_reset_tokens(expires_at)')
        print("✓ Indexes created")
        
        # 3. Add subscribed_modules column to companies table
        print("\nAdding subscribed_modules column to companies...")
        try:
            cursor.execute('''
                ALTER TABLE companies 
                ADD COLUMN subscribed_modules TEXT DEFAULT '["safety", "concrete"]'
            ''')
            print("✓ subscribed_modules column added")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ subscribed_modules column already exists")
            else:
                raise
        
        # 4. Update existing companies to have all modules
        print("Updating existing companies with default modules...")
        cursor.execute('''
            UPDATE companies 
            SET subscribed_modules = '["safety", "concrete", "concrete_nc"]'
            WHERE subscribed_modules IS NULL OR subscribed_modules = ''
        ''')
        updated = cursor.rowcount
        print(f"✓ Updated {updated} companies")
        
        # 5. Register admin user shrotrio@gmail.com
        print("\nRegistering admin user...")
        
        # Check if user already exists
        cursor.execute('SELECT id, email FROM users WHERE email = ?', ('shrotrio@gmail.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠ User already exists: shrotrio@gmail.com (ID: {existing_user[0]})")
        else:
            # Get first company (or create one)
            cursor.execute('SELECT id, name FROM companies LIMIT 1')
            company = cursor.fetchone()
            
            if not company:
                print("Creating default company...")
                cursor.execute('''
                    INSERT INTO companies (name, subscription_plan, subscribed_modules)
                    VALUES (?, ?, ?)
                ''', ('Shrotri Concrete Solutions', 'enterprise', '["safety", "concrete", "concrete_nc"]'))
                company_id = cursor.lastrowid
                print(f"✓ Company created (ID: {company_id})")
            else:
                company_id = company[0]
                print(f"Using existing company: {company[1]} (ID: {company_id})")
            
            # Create admin user
            password_hash = generate_password_hash('Admin@123')  # Default password
            
            cursor.execute('''
                INSERT INTO users (
                    company_id, email, full_name, password_hash, phone,
                    is_active, is_system_admin, is_support_admin, is_company_admin,
                    is_email_verified, is_phone_verified, failed_login_attempts,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_id,
                'shrotrio@gmail.com',
                'Shrotri Admin',
                password_hash,
                '+91-9876543210',
                1,  # is_active
                1,  # is_system_admin
                1,  # is_support_admin
                1,  # is_company_admin
                1,  # is_email_verified
                0,  # is_phone_verified
                0,  # failed_login_attempts
                datetime.now(),
                datetime.now()
            ))
            
            user_id = cursor.lastrowid
            print(f"✓ Admin user created: shrotrio@gmail.com (ID: {user_id})")
            print(f"  Default password: Admin@123")
            print(f"  ⚠ IMPORTANT: Please change password after first login!")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nChanges made:")
        print("  ✓ password_reset_tokens table created")
        print("  ✓ 3 indexes created for password reset")
        print("  ✓ subscribed_modules column added to companies")
        print("  ✓ Admin user registered: shrotrio@gmail.com")
        print("\nModule Subscription System:")
        print("  - Companies can now subscribe to individual modules")
        print("  - Available modules: safety, concrete, concrete_nc")
        print("  - Module access controlled via subscribed_modules field")
        print("\nPassword Reset Flow:")
        print("  - POST /api/auth/forgot-password (email)")
        print("  - POST /api/auth/reset-password (token + new password)")
        print("  - POST /api/auth/verify-reset-token (validate token)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()


def verify_migration(db_path='data.sqlite3'):
    """Verify migration success."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("VERIFYING MIGRATION")
        print("="*60)
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='password_reset_tokens'")
        if cursor.fetchone():
            print("✓ password_reset_tokens table exists")
        else:
            print("✗ password_reset_tokens table missing")
            return False
        
        # Check column exists
        cursor.execute("PRAGMA table_info(companies)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'subscribed_modules' in columns:
            print("✓ subscribed_modules column exists in companies")
        else:
            print("✗ subscribed_modules column missing")
            return False
        
        # Check admin user
        cursor.execute('SELECT id, email, full_name, is_system_admin FROM users WHERE email = ?', ('shrotrio@gmail.com',))
        user = cursor.fetchone()
        if user:
            print(f"✓ Admin user exists: {user[1]} (Name: {user[2]}, System Admin: {user[3]})")
        else:
            print("⚠ Admin user not found (may have already existed)")
        
        # Count companies with modules
        cursor.execute('SELECT COUNT(*) FROM companies WHERE subscribed_modules IS NOT NULL')
        count = cursor.fetchone()[0]
        print(f"✓ {count} companies have module subscriptions")
        
        print("\n✅ Migration verified successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'data.sqlite3'
    
    success = migrate_auth_and_modules(db_path)
    
    if success:
        verify_migration(db_path)
    
    sys.exit(0 if success else 1)
