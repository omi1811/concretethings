#!/usr/bin/env python3
"""
Migration script to add scoring system to Safety NC module.
Adds severity scores, contractor performance tracking, and reports.
"""

import sqlite3
from datetime import datetime

def migrate_safety_nc_scoring(db_path='data.sqlite3'):
    """Add scoring system to Safety NC."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("="*60)
        print("SAFETY NC SCORING SYSTEM MIGRATION")
        print("="*60)
        print(f"Database: {db_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # 1. Add scoring columns to safety_non_conformances table
        print("Adding scoring columns to safety_non_conformances...")
        
        columns_to_add = [
            ("severity_score", "REAL DEFAULT 0.0"),
            ("score_month", "VARCHAR(7)"),  # YYYY-MM
            ("score_year", "INTEGER"),
            ("score_week", "VARCHAR(10)"),  # YYYY-Wnn
            ("actual_resolution_days", "INTEGER"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f'ALTER TABLE safety_non_conformances ADD COLUMN {col_name} {col_type}')
                print(f"  ✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"  ⚠ Column already exists: {col_name}")
                else:
                    raise
        
        # 2. Create Safety NC Score Reports table
        print("\nCreating safety_nc_score_reports table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safety_nc_score_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                contractor_name VARCHAR(255),
                report_type VARCHAR(20) NOT NULL,
                period VARCHAR(20) NOT NULL,
                
                -- Severity counts
                critical_count INTEGER DEFAULT 0,
                major_count INTEGER DEFAULT 0,
                minor_count INTEGER DEFAULT 0,
                
                -- Status counts
                total_issues_count INTEGER DEFAULT 0,
                closed_issues_count INTEGER DEFAULT 0,
                open_issues_count INTEGER DEFAULT 0,
                
                -- Scoring
                total_score REAL DEFAULT 0.0,
                closure_rate REAL DEFAULT 0.0,
                avg_resolution_days REAL DEFAULT 0.0,
                performance_grade VARCHAR(2),
                
                -- Metadata
                generated_by_user_id INTEGER,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (generated_by_user_id) REFERENCES users(id),
                CHECK (report_type IN ('monthly', 'weekly')),
                CHECK (performance_grade IN ('A', 'B', 'C', 'D', 'F')),
                UNIQUE (company_id, project_id, contractor_name, report_type, period)
            )
        ''')
        print("✓ safety_nc_score_reports table created")
        
        # 3. Create indexes
        print("\nCreating indexes...")
        indexes = [
            ('idx_safety_nc_score_month', 'safety_non_conformances', 'score_month'),
            ('idx_safety_nc_score_year', 'safety_non_conformances', 'score_year'),
            ('idx_safety_nc_contractor', 'safety_non_conformances', 'assigned_to_contractor'),
            ('idx_safety_nc_severity', 'safety_non_conformances', 'severity'),
            ('idx_safety_nc_reports_company', 'safety_nc_score_reports', 'company_id'),
            ('idx_safety_nc_reports_project', 'safety_nc_score_reports', 'project_id'),
            ('idx_safety_nc_reports_contractor', 'safety_nc_score_reports', 'contractor_name'),
            ('idx_safety_nc_reports_period', 'safety_nc_score_reports', 'period'),
        ]
        
        for idx_name, table_name, column_name in indexes:
            cursor.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})')
            print(f"  ✓ {idx_name}")
        
        # 4. Update existing NCs with severity scores
        print("\nCalculating severity scores for existing NCs...")
        
        # Score mapping: critical=1.5, major=1.0, minor=0.5
        cursor.execute('''
            UPDATE safety_non_conformances 
            SET severity_score = CASE
                WHEN LOWER(severity) = 'critical' THEN 1.5
                WHEN LOWER(severity) = 'major' THEN 1.0
                WHEN LOWER(severity) = 'minor' THEN 0.5
                ELSE 0.5
            END
            WHERE severity_score IS NULL OR severity_score = 0
        ''')
        updated = cursor.rowcount
        print(f"  ✓ Updated {updated} existing NCs with severity scores")
        
        # 5. Update score tracking fields
        print("\nUpdating score tracking fields...")
        cursor.execute('''
            UPDATE safety_non_conformances 
            SET 
                score_month = strftime('%Y-%m', raised_at),
                score_year = CAST(strftime('%Y', raised_at) AS INTEGER),
                score_week = strftime('%Y-W%W', raised_at)
            WHERE raised_at IS NOT NULL
                AND (score_month IS NULL OR score_year IS NULL)
        ''')
        updated = cursor.rowcount
        print(f"  ✓ Updated {updated} NCs with tracking fields")
        
        # 6. Calculate resolution days for closed NCs
        print("\nCalculating resolution days...")
        cursor.execute('''
            UPDATE safety_non_conformances 
            SET actual_resolution_days = CAST(
                (julianday(closed_at) - julianday(raised_at)) AS INTEGER
            )
            WHERE closed_at IS NOT NULL 
                AND raised_at IS NOT NULL
                AND actual_resolution_days IS NULL
        ''')
        updated = cursor.rowcount
        print(f"  ✓ Calculated resolution days for {updated} closed NCs")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nChanges made:")
        print("  ✓ Added 5 scoring columns to safety_non_conformances")
        print("  ✓ Created safety_nc_score_reports table")
        print("  ✓ Created 8 indexes for performance")
        print("  ✓ Updated existing NCs with scores")
        print("\nScoring System:")
        print("  - Critical: 1.5 points per open issue")
        print("  - Major: 1.0 point per open issue")
        print("  - Minor: 0.5 points per open issue")
        print("\nPerformance Grades:")
        print("  - A: Score = 0 (Perfect)")
        print("  - B: Score ≤ 2.0 (Good)")
        print("  - C: Score ≤ 5.0 (Acceptable)")
        print("  - D: Score ≤ 10.0 (Poor)")
        print("  - F: Score > 10.0 (Failing)")
        
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
        
        # Check new columns
        cursor.execute("PRAGMA table_info(safety_non_conformances)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = ['severity_score', 'score_month', 'score_year', 'score_week', 'actual_resolution_days']
        for col in new_columns:
            if col in columns:
                print(f"✓ Column exists: {col}")
            else:
                print(f"✗ Column missing: {col}")
                return False
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='safety_nc_score_reports'")
        if cursor.fetchone():
            print("✓ safety_nc_score_reports table exists")
        else:
            print("✗ safety_nc_score_reports table missing")
            return False
        
        # Count NCs with scores
        cursor.execute('SELECT COUNT(*) FROM safety_non_conformances WHERE severity_score > 0')
        count = cursor.fetchone()[0]
        print(f"✓ {count} NCs have severity scores")
        
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
    
    success = migrate_safety_nc_scoring(db_path)
    
    if success:
        verify_migration(db_path)
    
    sys.exit(0 if success else 1)
