#!/usr/bin/env python3
"""Database health check script"""

from server.db import engine
from sqlalchemy import inspect, text

def check_database():
    print("=" * 60)
    print("DATABASE HEALTH CHECK")
    print("=" * 60)
    
    try:
        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful")
            
            # Get all tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"✓ Found {len(tables)} tables in database")
            
            # List first 20 tables
            print("\nTables in database:")
            for i, table in enumerate(tables[:20], 1):
                print(f"  {i}. {table}")
            
            if len(tables) > 20:
                print(f"  ... and {len(tables) - 20} more tables")
            
            # Check for contractor/vendor tables
            print("\nChecking for contractor/vendor related tables:")
            contractor_tables = [t for t in tables if 'contractor' in t.lower() or 'vendor' in t.lower()]
            if contractor_tables:
                for table in contractor_tables:
                    print(f"  ✓ {table}")
            else:
                print("  ⚠ No contractor or vendor tables found")
                print("  ℹ Contractors are stored as text fields in handover_register")
                print("  ℹ RMC vendors are in 'rmc_vendors' table")
            
            # Check handover_register table
            if 'handover_register' in tables:
                print("\n✓ handover_register table exists")
                columns = inspector.get_columns('handover_register')
                contractor_cols = [c['name'] for c in columns if 'contractor' in c['name'].lower()]
                if contractor_cols:
                    print(f"  Contractor columns: {', '.join(contractor_cols)}")
            
            print("\n" + "=" * 60)
            print("DATABASE CHECK COMPLETE")
            print("=" * 60)
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_database()
    exit(0 if success else 1)
