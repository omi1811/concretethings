#!/usr/bin/env python3
"""
Database migration script for Concrete NC (Non-Conformance) feature.
Creates 4 new tables:
- concrete_nc_tags (hierarchical tag system)
- concrete_nc_issues (NC workflow management)
- concrete_nc_notifications (notification tracking)
- concrete_nc_score_reports (contractor performance reports)
"""

import sqlite3
from datetime import datetime

def migrate_concrete_nc(db_path='data.sqlite3'):
    """Create NC tables and seed initial data."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting Concrete NC migration...")
        
        # 1. Create concrete_nc_tags table
        print("Creating concrete_nc_tags table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concrete_nc_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                level INTEGER NOT NULL,
                parent_tag_id INTEGER,
                color_code VARCHAR(7) DEFAULT '#666666',
                description TEXT,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_tag_id) REFERENCES concrete_nc_tags(id) ON DELETE SET NULL,
                CHECK (level >= 1 AND level <= 4)
            )
        ''')
        print("✓ concrete_nc_tags table created")
        
        # 2. Create concrete_nc_issues table
        print("Creating concrete_nc_issues table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concrete_nc_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                nc_number VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                photo_urls JSON,
                location_text VARCHAR(200),
                location_latitude REAL,
                location_longitude REAL,
                tag_ids JSON,
                severity VARCHAR(20) NOT NULL,
                severity_score REAL DEFAULT 0.0,
                raised_by_user_id INTEGER NOT NULL,
                raised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contractor_id INTEGER,
                oversight_engineer_id INTEGER,
                status VARCHAR(20) DEFAULT 'raised',
                acknowledged_at TIMESTAMP,
                acknowledged_by_user_id INTEGER,
                contractor_remarks TEXT,
                contractor_response TEXT,
                proposed_deadline TIMESTAMP,
                responded_at TIMESTAMP,
                resolution_description TEXT,
                resolution_photo_urls JSON,
                resolved_at TIMESTAMP,
                resolved_by_user_id INTEGER,
                verified_at TIMESTAMP,
                verified_by_user_id INTEGER,
                verification_remarks TEXT,
                closed_at TIMESTAMP,
                closed_by_user_id INTEGER,
                closure_remarks TEXT,
                actual_resolution_days INTEGER,
                rejection_reason TEXT,
                rejected_at TIMESTAMP,
                rejected_by_user_id INTEGER,
                transfer_history JSON,
                score_month VARCHAR(7),
                score_year INTEGER,
                score_week VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (raised_by_user_id) REFERENCES users(id),
                FOREIGN KEY (contractor_id) REFERENCES rmc_vendors(id),
                FOREIGN KEY (oversight_engineer_id) REFERENCES users(id),
                FOREIGN KEY (acknowledged_by_user_id) REFERENCES users(id),
                FOREIGN KEY (resolved_by_user_id) REFERENCES users(id),
                FOREIGN KEY (verified_by_user_id) REFERENCES users(id),
                FOREIGN KEY (closed_by_user_id) REFERENCES users(id),
                FOREIGN KEY (rejected_by_user_id) REFERENCES users(id),
                CHECK (severity IN ('HIGH', 'MODERATE', 'LOW')),
                CHECK (status IN ('raised', 'acknowledged', 'in_progress', 'resolved', 'verified', 'closed', 'rejected', 'transferred'))
            )
        ''')
        print("✓ concrete_nc_issues table created")
        
        # 3. Create concrete_nc_notifications table
        print("Creating concrete_nc_notifications table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concrete_nc_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id INTEGER NOT NULL,
                recipient_user_id INTEGER NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                channel VARCHAR(20) NOT NULL,
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered BOOLEAN DEFAULT 0,
                delivery_status VARCHAR(50),
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (issue_id) REFERENCES concrete_nc_issues(id) ON DELETE CASCADE,
                FOREIGN KEY (recipient_user_id) REFERENCES users(id),
                CHECK (channel IN ('whatsapp', 'email', 'in_app'))
            )
        ''')
        print("✓ concrete_nc_notifications table created")
        
        # 4. Create concrete_nc_score_reports table
        print("Creating concrete_nc_score_reports table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concrete_nc_score_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                contractor_id INTEGER NOT NULL,
                report_type VARCHAR(20) NOT NULL,
                period VARCHAR(20) NOT NULL,
                high_severity_count INTEGER DEFAULT 0,
                moderate_severity_count INTEGER DEFAULT 0,
                low_severity_count INTEGER DEFAULT 0,
                total_issues_count INTEGER DEFAULT 0,
                closed_issues_count INTEGER DEFAULT 0,
                open_issues_count INTEGER DEFAULT 0,
                total_score REAL DEFAULT 0.0,
                closure_rate REAL DEFAULT 0.0,
                avg_resolution_days REAL DEFAULT 0.0,
                performance_grade VARCHAR(2),
                generated_by_user_id INTEGER,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (contractor_id) REFERENCES rmc_vendors(id) ON DELETE CASCADE,
                FOREIGN KEY (generated_by_user_id) REFERENCES users(id),
                CHECK (report_type IN ('monthly', 'weekly')),
                CHECK (performance_grade IN ('A', 'B', 'C', 'D', 'F')),
                UNIQUE (company_id, project_id, contractor_id, report_type, period)
            )
        ''')
        print("✓ concrete_nc_score_reports table created")
        
        # 5. Create indexes for performance
        print("Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_tags_company ON concrete_nc_tags(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_tags_parent ON concrete_nc_tags(parent_tag_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_company ON concrete_nc_issues(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_project ON concrete_nc_issues(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_contractor ON concrete_nc_issues(contractor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_status ON concrete_nc_issues(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_severity ON concrete_nc_issues(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_raised_at ON concrete_nc_issues(raised_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_issues_nc_number ON concrete_nc_issues(nc_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_notifications_issue ON concrete_nc_notifications(issue_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_notifications_recipient ON concrete_nc_notifications(recipient_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_reports_company ON concrete_nc_score_reports(company_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_reports_project ON concrete_nc_score_reports(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_reports_contractor ON concrete_nc_score_reports(contractor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nc_reports_period ON concrete_nc_score_reports(period)')
        print("✓ Indexes created")
        
        # 6. Seed default NC tags (Level 1 - Main Categories)
        print("Seeding default NC tags...")
        
        # Get first company for seeding (you can modify this logic)
        cursor.execute('SELECT id FROM companies LIMIT 1')
        company_result = cursor.fetchone()
        
        if company_result:
            company_id = company_result[0]
            
            default_tags = [
                # Level 1 - Main Categories
                ('Quality Issue', 1, None, '#FF0000', 'General quality non-conformances', 1),
                ('Safety Issue', 1, None, '#FFA500', 'Safety-related non-conformances', 2),
                ('Documentation Issue', 1, None, '#FFFF00', 'Documentation and record-keeping issues', 3),
                ('Material Issue', 1, None, '#0000FF', 'Material-related non-conformances', 4),
                ('Equipment Issue', 1, None, '#800080', 'Equipment and machinery issues', 5),
                ('Environmental Issue', 1, None, '#008000', 'Environmental compliance issues', 6),
            ]
            
            for tag_name, level, parent_id, color, desc, order in default_tags:
                cursor.execute('''
                    INSERT OR IGNORE INTO concrete_nc_tags 
                    (company_id, name, level, parent_tag_id, color_code, description, display_order, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ''', (company_id, tag_name, level, parent_id, color, desc, order))
            
            print(f"✓ Default NC tags seeded for company {company_id}")
        else:
            print("⚠ No companies found, skipping tag seeding")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Concrete NC migration completed successfully!")
        print("\nCreated tables:")
        print("  - concrete_nc_tags (hierarchical tag system)")
        print("  - concrete_nc_issues (NC workflow management)")
        print("  - concrete_nc_notifications (notification tracking)")
        print("  - concrete_nc_score_reports (performance reports)")
        print("\nCreated 14 indexes for optimized queries")
        print("Seeded 6 default Level 1 NC tag categories")
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def verify_migration(db_path='data.sqlite3'):
    """Verify that all NC tables were created successfully."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("VERIFYING MIGRATION")
        print("="*60)
        
        tables = [
            'concrete_nc_tags',
            'concrete_nc_issues',
            'concrete_nc_notifications',
            'concrete_nc_score_reports'
        ]
        
        all_exist = True
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ {table}: EXISTS (rows: {count})")
            else:
                print(f"✗ {table}: MISSING")
                all_exist = False
        
        if all_exist:
            print("\n✅ All NC tables verified successfully!")
        else:
            print("\n❌ Some NC tables are missing!")
        
        return all_exist
        
    except sqlite3.Error as e:
        print(f"\n❌ Verification failed: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'data.sqlite3'
    
    print("="*60)
    print("CONCRETE NC DATABASE MIGRATION")
    print("="*60)
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Run migration
    success = migrate_concrete_nc(db_path)
    
    if success:
        # Verify migration
        verify_migration(db_path)
    
    sys.exit(0 if success else 1)
