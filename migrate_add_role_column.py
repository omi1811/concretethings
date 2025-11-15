"""
Database Migration: Add Role Column to Users Table
Adds RBAC role field for comprehensive user role management
"""

from server.db import engine, SessionLocal
from sqlalchemy import text, inspect
import sys

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_role_column():
    """Add role column to users table if it doesn't exist"""
    with SessionLocal() as session:
        try:
            # Check if role column already exists
            if check_column_exists('users', 'role'):
                print("✅ 'role' column already exists in users table")
                return True
            
            print("📝 Adding 'role' column to users table...")
            
            # Add role column with default value
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(50) DEFAULT 'building_engineer' NOT NULL
            """))
            session.commit()
            
            print("✅ 'role' column added successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error adding role column: {str(e)}")
            session.rollback()
            return False

def update_existing_roles():
    """Update existing users with appropriate roles based on old flags"""
    with SessionLocal() as session:
        try:
            print("📝 Updating existing user roles...")
            
            # Update roles based on old permission flags
            result = session.execute(text("""
                UPDATE users 
                SET role = CASE 
                    WHEN is_system_admin = 1 OR is_support_admin = 1 THEN 'system_admin'
                    WHEN is_company_admin = 1 THEN 'project_manager'
                    ELSE 'building_engineer'
                END
                WHERE role = 'building_engineer' OR role IS NULL OR role = ''
            """))
            session.commit()
            
            updated_count = result.rowcount
            print(f"✅ Updated {updated_count} user roles")
            
            # Display role distribution
            result = session.execute(text("""
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role
                ORDER BY count DESC
            """))
            
            print("\n📊 Current Role Distribution:")
            for row in result:
                print(f"  • {row[0]}: {row[1]} users")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating roles: {str(e)}")
            session.rollback()
            return False

def verify_migration():
    """Verify the migration was successful"""
    with SessionLocal() as session:
        try:
            # Check if all users have valid roles
            result = session.execute(text("""
                SELECT COUNT(*) as count 
                FROM users 
                WHERE role IS NULL OR role = ''
            """))
            null_count = result.fetchone()[0]
            
            if null_count > 0:
                print(f"⚠️ Warning: {null_count} users have NULL or empty roles")
                return False
            
            print("✅ All users have valid roles assigned")
            return True
            
        except Exception as e:
            print(f"❌ Error verifying migration: {str(e)}")
            return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("ProSite RBAC Migration: Adding Role Column")
    print("=" * 60)
    print()
    
    # Step 1: Add role column
    if not add_role_column():
        print("\n❌ Migration failed at step 1: Adding role column")
        sys.exit(1)
    
    print()
    
    # Step 2: Update existing roles
    if not update_existing_roles():
        print("\n❌ Migration failed at step 2: Updating existing roles")
        sys.exit(1)
    
    print()
    
    # Step 3: Verify migration
    if not verify_migration():
        print("\n⚠️ Migration completed with warnings")
        sys.exit(0)
    
    print()
    print("=" * 60)
    print("✅ RBAC Migration Completed Successfully!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("  1. Update auth.py to use role field in login/register")
    print("  2. Add role-based middleware to API routes")
    print("  3. Update frontend to show role-appropriate menus")
    print("  4. Test all 12 role permissions")
    print()

if __name__ == "__main__":
    main()
