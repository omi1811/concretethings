"""
Verify Supabase Migration
Run this AFTER executing the SQL scripts in Supabase SQL Editor
to confirm the migration was successful.

NOTE: This will only work if you can connect to Supabase
(not from Codespaces due to network restrictions)
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def verify_migration():
    """Verify Supabase migration was successful"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print(f"{RED}❌ DATABASE_URL not set{RESET}")
        return False
    
    if 'sqlite' in database_url.lower():
        print(f"{YELLOW}⚠️  DATABASE_URL points to SQLite, not Supabase{RESET}")
        return False
    
    print(f"{BLUE}🔍 Connecting to Supabase...{RESET}")
    print(f"URL: {database_url.split('@')[1] if '@' in database_url else 'hidden'}")
    
    try:
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"{GREEN}✓ Connected to PostgreSQL{RESET}")
            print(f"  Version: {version[:50]}...")
            
            # Check tables
            print(f"\n{BLUE}📊 Checking tables...{RESET}")
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'companies', 'users', 'projects', 'project_memberships',
                'material_categories', 'rmc_vendors', 'mix_designs', 'approved_brands',
                'project_settings', 'material_vehicle_register', 'pour_activities',
                'batch_registers', 'cube_test_registers', 'test_reminders',
                'third_party_labs', 'third_party_cube_tests',
                'material_test_registers', 'training_records'
            ]
            
            missing = [t for t in expected_tables if t not in tables]
            if missing:
                print(f"{RED}❌ Missing tables: {', '.join(missing)}{RESET}")
                return False
            
            print(f"{GREEN}✓ All {len(expected_tables)} tables exist{RESET}")
            
            # Check row counts
            print(f"\n{BLUE}📈 Checking data...{RESET}")
            counts = {
                'companies': 0,
                'users': 0,
                'projects': 0,
                'project_memberships': 0,
                'batch_registers': 0,
                'material_vehicle_register': 0
            }
            
            for table in counts.keys():
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = result.scalar()
                
                icon = "✓" if counts[table] > 0 else "⚠️"
                color = GREEN if counts[table] > 0 else YELLOW
                print(f"{color}{icon} {table:30} {counts[table]:>5} rows{RESET}")
            
            # Check foreign keys
            print(f"\n{BLUE}🔗 Verifying relationships...{RESET}")
            
            fk_query = text("""
                SELECT 
                    u.email,
                    c.name as company,
                    COUNT(pm.id) as memberships
                FROM users u
                JOIN companies c ON u.company_id = c.id
                LEFT JOIN project_memberships pm ON pm.user_id = u.id
                GROUP BY u.email, c.name
            """)
            
            result = conn.execute(fk_query).fetchall()
            if result:
                for row in result:
                    print(f"{GREEN}✓ User: {row[0]}{RESET}")
                    print(f"  Company: {row[1]}")
                    print(f"  Project memberships: {row[2]}")
            else:
                print(f"{YELLOW}⚠️  No users found{RESET}")
            
            # Check sequences
            print(f"\n{BLUE}🔢 Checking sequences...{RESET}")
            seq_query = text("""
                SELECT 
                    schemaname,
                    sequencename,
                    last_value
                FROM pg_sequences
                WHERE schemaname = 'public'
                ORDER BY sequencename
                LIMIT 5
            """)
            
            result = conn.execute(seq_query).fetchall()
            for row in result:
                print(f"{GREEN}✓ {row[1]:40} → {row[2]}{RESET}")
            
            print(f"\n{GREEN}{'='*60}{RESET}")
            print(f"{GREEN}✅ Migration verification PASSED!{RESET}")
            print(f"{GREEN}{'='*60}{RESET}")
            print(f"\n{BLUE}Next steps:{RESET}")
            print("  1. Deploy your app to a platform that can reach Supabase")
            print("  2. Run your test suite against the Supabase DB")
            print("  3. Configure Supabase Storage for file uploads")
            print("  4. Set up Row Level Security (RLS) policies")
            
            return True
            
    except Exception as e:
        print(f"\n{RED}❌ Connection failed: {str(e)}{RESET}")
        print(f"\n{YELLOW}This is expected in Codespaces due to network restrictions.{RESET}")
        print(f"{YELLOW}Run this script from a deployed environment instead.{RESET}")
        return False

if __name__ == "__main__":
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Supabase Migration Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    success = verify_migration()
    sys.exit(0 if success else 1)
