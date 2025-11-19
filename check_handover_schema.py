#!/usr/bin/env python3
"""Check handover_register schema"""

from server.db import engine
from sqlalchemy import text, inspect

with engine.connect() as conn:
    result = conn.execute(text('PRAGMA table_info(handover_register)'))
    cols = result.fetchall()
    
    print("handover_register contractor-related columns:")
    print("=" * 60)
    for col in cols:
        if 'contractor' in col[1].lower():
            print(f"  {col[1]:<35} {col[2]:<15} {'NOT NULL' if col[3] else 'NULL'}")
    
    print("\nChecking for foreign keys:")
    fk_result = conn.execute(text('PRAGMA foreign_key_list(handover_register)'))
    fks = fk_result.fetchall()
    for fk in fks:
        if 'contractor' in str(fk).lower():
            print(f"  {fk}")
