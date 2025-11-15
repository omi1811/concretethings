# Supabase Migration - Step-by-Step Guide

## 🎯 Complete Migration from SQLite to Supabase PostgreSQL

**Current Setup:** SQLite (local development)  
**Target Setup:** Supabase PostgreSQL (production-ready, cloud-hosted)  
**Migration Type:** Full database migration with authentication

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Supabase Setup](#2-supabase-setup)
3. [Export SQLite Data](#3-export-sqlite-data)
4. [Schema Migration](#4-schema-migration)
5. [Data Migration](#5-data-migration)
6. [Authentication Setup](#6-authentication-setup)
7. [API Configuration](#7-api-configuration)
8. [Testing & Verification](#8-testing--verification)
9. [Production Deployment](#9-production-deployment)
10. [Rollback Plan](#10-rollback-plan)

---

## 1. Prerequisites

### **What You Need:**

✅ **Supabase Account** - Sign up at https://supabase.com  
✅ **Current SQLite Database** - `/workspaces/concretethings/data.sqlite3`  
✅ **PostgreSQL Client** - `psql` command-line tool  
✅ **Python 3.8+** - For migration scripts  
✅ **Node.js 16+** - For Supabase CLI  

### **Install Required Tools:**

```bash
# Install Supabase CLI
npm install -g supabase

# Install PostgreSQL client
sudo apt-get update
sudo apt-get install postgresql-client

# Install Python dependencies
pip install psycopg2-binary sqlalchemy python-dotenv
```

---

## 2. Supabase Setup

### **Step 2.1: Create Supabase Project**

1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Fill in details:
   - **Project Name:** `prosite-production`
   - **Database Password:** (Generate strong password - **SAVE THIS!**)
   - **Region:** Choose closest to your users (e.g., Mumbai for India)
   - **Pricing Plan:** Free tier for testing, Pro for production

4. Wait 2-3 minutes for project provisioning

---

### **Step 2.2: Get Database Credentials**

1. Go to **Settings** > **Database**
2. Copy the following:

```bash
# Supabase Database Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# PostgreSQL Connection String
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# Direct Connection (for psql)
PGHOST=db.your-project.supabase.co
PGPORT=5432
PGDATABASE=postgres
PGUSER=postgres
PGPASSWORD=your-database-password
```

3. Save these to `.env.production` file:

```bash
# Create production environment file
cat > .env.production << EOF
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Database Connection
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# App Configuration
FLASK_ENV=production
JWT_SECRET_KEY=$(openssl rand -hex 32)
FRONTEND_URL=https://prosite.vercel.app

# Email Configuration (existing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@prosite.com
SMTP_PASSWORD=your-smtp-password
EOF
```

---

### **Step 2.3: Test Connection**

```bash
# Load environment variables
source .env.production

# Test PostgreSQL connection
psql "$DATABASE_URL" -c "SELECT version();"
```

**Expected Output:**
```
                                                      version
--------------------------------------------------------------------------------------------------------------------
 PostgreSQL 15.1 on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
(1 row)
```

✅ **Connection successful!**

---

## 3. Export SQLite Data

### **Step 3.1: Backup Current SQLite Database**

```bash
# Create backup
cp data.sqlite3 data.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -lh data.sqlite3*
```

---

### **Step 3.2: Export Schema**

```bash
# Export SQLite schema to SQL
sqlite3 data.sqlite3 .schema > sqlite_schema.sql

# Review schema
cat sqlite_schema.sql
```

---

### **Step 3.3: Export Data**

Create export script:

```python
# export_sqlite_data.py
"""Export data from SQLite to JSON for PostgreSQL migration"""

import sqlite3
import json
from datetime import datetime

def serialize_value(value):
    """Convert SQLite values to JSON-serializable format"""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()  # Convert binary to hex
    return value

def export_table(conn, table_name):
    """Export a table to JSON"""
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Convert to list of dicts
    data = []
    for row in rows:
        row_dict = {}
        for col, val in zip(columns, row):
            row_dict[col] = serialize_value(val)
        data.append(row_dict)
    
    return data

def main():
    # Connect to SQLite
    conn = sqlite3.connect('data.sqlite3', detect_types=sqlite3.PARSE_DECLTYPES)
    
    # Get all table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(tables)} tables to export:")
    for table in tables:
        print(f"  - {table}")
    
    # Export each table
    export_data = {}
    for table in tables:
        print(f"\nExporting {table}...")
        data = export_table(conn, table)
        export_data[table] = data
        print(f"  ✅ Exported {len(data)} rows")
    
    # Save to JSON
    with open('sqlite_export.json', 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n✅ Export complete! Data saved to sqlite_export.json")
    
    # Print summary
    print("\n📊 Export Summary:")
    for table, data in export_data.items():
        print(f"  {table}: {len(data)} rows")
    
    conn.close()

if __name__ == "__main__":
    main()
```

Run export:

```bash
python export_sqlite_data.py
```

**Output:**
```
Found 25 tables to export:
  - users
  - companies
  - projects
  - project_memberships
  - batch_registers
  - cube_tests
  - material_tests
  ...

Exporting users...
  ✅ Exported 10 rows
...

✅ Export complete! Data saved to sqlite_export.json

📊 Export Summary:
  users: 10 rows
  companies: 3 rows
  projects: 5 rows
  batch_registers: 150 rows
  ...
```

---

## 4. Schema Migration

### **Step 4.1: Convert SQLite Schema to PostgreSQL**

Create conversion script:

```python
# convert_schema_to_postgres.py
"""Convert SQLite schema to PostgreSQL"""

import re

def convert_schema(sqlite_schema):
    """Convert SQLite SQL to PostgreSQL SQL"""
    
    # Replace SQLite types with PostgreSQL types
    postgres_schema = sqlite_schema
    
    # INTEGER PRIMARY KEY → SERIAL PRIMARY KEY
    postgres_schema = re.sub(
        r'(\w+)\s+INTEGER\s+PRIMARY KEY',
        r'\1 SERIAL PRIMARY KEY',
        postgres_schema
    )
    
    # AUTOINCREMENT → (remove, SERIAL handles this)
    postgres_schema = postgres_schema.replace('AUTOINCREMENT', '')
    
    # DATETIME → TIMESTAMP
    postgres_schema = postgres_schema.replace('DATETIME', 'TIMESTAMP')
    
    # BOOLEAN → BOOLEAN (already compatible)
    
    # TEXT → TEXT (already compatible)
    
    # BLOB → BYTEA
    postgres_schema = postgres_schema.replace('BLOB', 'BYTEA')
    
    # Remove SQLite-specific syntax
    postgres_schema = postgres_schema.replace('WITHOUT ROWID', '')
    
    # Add IF NOT EXISTS
    postgres_schema = re.sub(
        r'CREATE TABLE (\w+)',
        r'CREATE TABLE IF NOT EXISTS \1',
        postgres_schema
    )
    
    return postgres_schema

# Read SQLite schema
with open('sqlite_schema.sql', 'r') as f:
    sqlite_schema = f.read()

# Convert to PostgreSQL
postgres_schema = convert_schema(sqlite_schema)

# Save PostgreSQL schema
with open('postgres_schema.sql', 'w') as f:
    f.write(postgres_schema)

print("✅ Schema converted to PostgreSQL")
print("   Saved to: postgres_schema.sql")
```

Run conversion:

```bash
python convert_schema_to_postgres.py
```

---

### **Step 4.2: Apply Schema to Supabase**

```bash
# Load environment variables
source .env.production

# Apply schema to Supabase
psql "$DATABASE_URL" -f postgres_schema.sql
```

**Expected Output:**
```
CREATE TABLE
CREATE TABLE
CREATE TABLE
...
✅ Schema applied successfully
```

---

### **Step 4.3: Verify Schema**

```bash
# List all tables
psql "$DATABASE_URL" -c "\dt"
```

**Expected Output:**
```
               List of relations
 Schema |       Name         | Type  |  Owner
--------+--------------------+-------+----------
 public | users              | table | postgres
 public | companies          | table | postgres
 public | projects           | table | postgres
 public | batch_registers    | table | postgres
 ...
```

---

## 5. Data Migration

### **Step 5.1: Import Data to PostgreSQL**

Create import script:

```python
# import_to_postgres.py
"""Import data from JSON to PostgreSQL"""

import json
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv('.env.production')

def import_table(conn, table_name, data):
    """Import data into a PostgreSQL table"""
    if not data:
        print(f"  ⏭️  {table_name}: No data to import")
        return
    
    cursor = conn.cursor()
    
    # Get column names from first row
    columns = list(data[0].keys())
    
    # Prepare INSERT query
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Prepare data
    values = []
    for row in data:
        values.append(tuple(row[col] for col in columns))
    
    # Execute batch insert
    try:
        execute_values(cursor, query, values)
        conn.commit()
        print(f"  ✅ {table_name}: Imported {len(data)} rows")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ {table_name}: Error - {str(e)}")
        raise

def main():
    # Load exported data
    with open('sqlite_export.json', 'r') as f:
        export_data = json.load(f)
    
    print(f"Loaded data for {len(export_data)} tables")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print("✅ Connected to PostgreSQL\n")
    
    # Import order (respect foreign key constraints)
    import_order = [
        'users',
        'companies',
        'projects',
        'project_memberships',
        'rmc_vendors',
        'mix_designs',
        'batch_registers',
        'cube_tests',
        'material_tests',
        'ncr_reports',
        'safety_ncs',
        'ptw_permits',
        'training_sessions',
        'pour_activities',
        'gate_logs',
        # ... add all tables in dependency order
    ]
    
    # Import each table
    for table in import_order:
        if table in export_data:
            print(f"Importing {table}...")
            import_table(conn, table, export_data[table])
        else:
            print(f"  ⏭️  {table}: Not found in export")
    
    # Import remaining tables not in import_order
    for table in export_data:
        if table not in import_order:
            print(f"Importing {table}...")
            import_table(conn, table, export_data[table])
    
    conn.close()
    print("\n✅ Data import complete!")

if __name__ == "__main__":
    main()
```

Run import:

```bash
python import_to_postgres.py
```

**Expected Output:**
```
Loaded data for 25 tables
✅ Connected to PostgreSQL

Importing users...
  ✅ users: Imported 10 rows
Importing companies...
  ✅ companies: Imported 3 rows
Importing projects...
  ✅ projects: Imported 5 rows
...

✅ Data import complete!
```

---

### **Step 5.2: Reset Sequences**

PostgreSQL sequences need to be reset after data import:

```sql
-- reset_sequences.sql

-- Reset users sequence
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- Reset projects sequence
SELECT setval('projects_id_seq', (SELECT MAX(id) FROM projects));

-- Reset batch_registers sequence
SELECT setval('batch_registers_id_seq', (SELECT MAX(id) FROM batch_registers));

-- Add more sequences as needed...
```

Apply:

```bash
psql "$DATABASE_URL" -f reset_sequences.sql
```

---

## 6. Authentication Setup

### **Step 6.1: Enable Supabase Auth**

1. Go to Supabase Dashboard → **Authentication** → **Settings**
2. Enable **Email Auth**
3. Configure **Email Templates**:
   - **Confirmation Email** - For new signups
   - **Reset Password** - For password reset
   - **Magic Link** - For passwordless login

---

### **Step 6.2: Migrate Existing Users**

Supabase has its own auth system. You have two options:

**Option A: Keep Custom JWT Auth (Recommended for now)**
- No changes needed
- Continue using existing Flask JWT
- Use Supabase only for database

**Option B: Migrate to Supabase Auth**
- Requires password reset for all users
- More complex migration
- Better long-term solution

**Let's go with Option A for smooth migration.**

---

### **Step 6.3: Update Backend Configuration**

Update `server/db.py`:

```python
# server/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data.sqlite3')

# Create engine
if DATABASE_URL.startswith('postgresql'):
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
else:
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 7. API Configuration

### **Step 7.1: Update Environment Variables**

```bash
# .env.production

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# Supabase (optional, if using Supabase Auth later)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Flask Configuration
FLASK_ENV=production
FLASK_APP=server/app.py
SECRET_KEY=$(openssl rand -hex 32)

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Frontend URL
FRONTEND_URL=https://prosite.vercel.app

# Email (existing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@prosite.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@prosite.com
SMTP_FROM_NAME=ProSite Quality Management

# Optional: WhatsApp
WHATSAPP_API_URL=https://api.whatsapp.com
WHATSAPP_API_KEY=your-whatsapp-key
```

---

### **Step 7.2: Update Frontend Configuration**

Update `frontend/.env.local`:

```bash
# API URL (production)
NEXT_PUBLIC_API_URL=https://your-backend.render.com/api

# Supabase (if using Supabase Storage for files)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# App Configuration
NEXT_PUBLIC_APP_NAME=ProSite
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## 8. Testing & Verification

### **Step 8.1: Verify Data Integrity**

```bash
# Count records in key tables
psql "$DATABASE_URL" << EOF
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'batch_registers', COUNT(*) FROM batch_registers
UNION ALL
SELECT 'cube_tests', COUNT(*) FROM cube_tests;
EOF
```

**Expected Output:**
```
  table_name     | count
-----------------+-------
 users           |    10
 projects        |     5
 batch_registers |   150
 cube_tests      |   300
```

Compare with SQLite:

```bash
sqlite3 data.sqlite3 << EOF
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects;
EOF
```

---

### **Step 8.2: Test API Endpoints**

```bash
# Test login
curl -X POST https://your-backend.render.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@prosite.com",
    "password": "Admin@ProSite2024"
  }'

# Expected: 200 OK with access token

# Test projects list
curl -X GET https://your-backend.render.com/api/projects \
  -H "Authorization: Bearer $TOKEN"

# Expected: List of projects
```

---

### **Step 8.3: Run Test Bot**

```bash
# Run comprehensive test bot
python test_bot_comprehensive.py https://your-backend.render.com
```

Review test report for any issues.

---

## 9. Production Deployment

### **Step 9.1: Deploy Backend (Render/Railway/Heroku)**

**Using Render:**

1. Go to https://render.com
2. Click **New** → **Web Service**
3. Connect GitHub repository
4. Configure:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn server.app:app`
   - **Environment Variables:** Copy from `.env.production`

---

### **Step 9.2: Deploy Frontend (Vercel)**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
cd frontend
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend.render.com/api
```

---

### **Step 9.3: Configure Domain (Optional)**

**Custom Domain Setup:**

1. Go to Supabase → Settings → Custom Domains
2. Add your domain: `db.prosite.com`
3. Update DNS records as instructed
4. Wait for verification (15-30 minutes)

---

## 10. Rollback Plan

### **If Migration Fails:**

**Step 10.1: Restore SQLite Backup**

```bash
# Stop backend server
# Restore backup
cp data.sqlite3.backup_YYYYMMDD_HHMMSS data.sqlite3

# Restart backend with SQLite
export DATABASE_URL="sqlite:///./data.sqlite3"
python server/app.py
```

---

### **Step 10.2: Keep Both Databases (Gradual Migration)**

Run dual databases during transition:

```python
# Dual database configuration
SQLITE_URL = "sqlite:///./data.sqlite3"
POSTGRES_URL = os.getenv('DATABASE_URL')

# Route reads to PostgreSQL, writes to both
if os.getenv('MIGRATION_MODE') == 'dual':
    # Write to both databases
    # Read from PostgreSQL
    pass
```

---

## ✅ Post-Migration Checklist

- [ ] All tables migrated successfully
- [ ] Record counts match between SQLite and PostgreSQL
- [ ] All foreign key relationships intact
- [ ] Sequences reset correctly
- [ ] Authentication working (login/logout)
- [ ] API endpoints responding correctly
- [ ] File uploads working (if using Supabase Storage)
- [ ] Email notifications sending
- [ ] Frontend deployed and connected
- [ ] SSL certificates configured
- [ ] Backups configured (Supabase auto-backup enabled)
- [ ] Monitoring set up (Supabase dashboard)
- [ ] Team notified of new production URL

---

## 🎉 Migration Complete!

**Your ProSite application is now running on Supabase PostgreSQL!**

**Benefits:**
✅ Production-grade PostgreSQL database  
✅ Automatic backups  
✅ Real-time capabilities (optional)  
✅ Built-in authentication (optional)  
✅ File storage with CDN  
✅ RESTful API auto-generated  
✅ Dashboard for monitoring  
✅ Free tier: 500MB database, 2GB bandwidth  

**Next Steps:**
1. Monitor application for 24-48 hours
2. Set up alerts in Supabase dashboard
3. Configure database backups
4. Optimize queries for PostgreSQL
5. Consider Supabase Auth migration (Phase 2)
6. Set up CI/CD pipeline

---

**Migration Date:** Ready to execute  
**Estimated Duration:** 2-4 hours  
**Complexity:** Medium  
**Risk Level:** Low (with backups and rollback plan)
