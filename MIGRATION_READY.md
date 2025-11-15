# 🚀 Supabase Migration - Ready to Execute

## ✅ Migration Prepared

Your database has been exported and is ready for migration to Supabase PostgreSQL.

**Exported:**
- ✅ 52 tables
- ✅ 42 rows of data
- ✅ PostgreSQL schema generated
- ✅ Migration scripts ready

---

## 📋 Pre-Migration Checklist

### 1. Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Choose:
   - **Name:** ProSite Production
   - **Database Password:** (generate a strong password)
   - **Region:** Choose closest to your users (e.g., Mumbai, Singapore)
   - **Pricing Plan:** Free tier for testing, Pro for production

### 2. Get Database Credentials

Once project is created:

1. Click **Settings** → **Database**
2. Scroll to **Connection string**
3. Copy the **Connection pooling** string (not Direct connection)
4. It looks like: `postgresql://postgres.xxx:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres`

### 3. Install PostgreSQL Client (if needed)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y postgresql-client libpq-dev

# Or just install Python package
pip install psycopg2-binary
```

---

## 🎯 Migration Steps

### Quick Migration (Automated)

```bash
# Set your Supabase credentials
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres"

# Run the migration script
./run_migration.sh
```

The script will:
1. ✅ Verify data export
2. ✅ Check schema conversion
3. ⚠️  Prompt you to create schema in Supabase (manual step)
4. ✅ Import all data
5. ✅ Reset sequences
6. ✅ Verify connection

---

### Manual Migration (Step-by-Step)

#### Step 1: Export Data (✅ DONE)
```bash
python export_sqlite_data.py
```

#### Step 2: Convert Schema (✅ DONE)
```bash
python convert_schema_to_postgres.py
```

#### Step 3: Create Schema in Supabase

1. Open Supabase project → **SQL Editor**
2. Open the file: `schema_postgres.sql`
3. Copy ALL contents
4. Paste into SQL Editor
5. Click **RUN**
6. Verify success (should see "Success" messages)

#### Step 4: Set Database URL

```bash
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"
```

#### Step 5: Import Data

```bash
python import_to_postgres.py
```

Expected output:
```
✅ companies: 1 rows imported
✅ users: 3 rows imported
✅ projects: 1 rows imported
...
✅ Import completed!
   Tables imported: 52
   Total rows: 42
```

---

## 🔍 Verification

### 1. Check Supabase Dashboard

1. Go to **Table Editor** in Supabase
2. Verify tables exist:
   - `companies` (1 row)
   - `users` (3 rows)
   - `projects` (1 row)

### 2. Test Database Connection

```bash
python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()
cursor.execute('SELECT email, full_name FROM users')
for row in cursor.fetchall():
    print(f'User: {row[0]} - {row[1]}')
conn.close()
"
```

Expected output:
```
User: test@example.com - Test User
User: shrotrio@gmail.com - Shrotri Admin
User: admin@testprosite.com - Test System Admin
```

### 3. Test Application Login

```bash
# Start server with new database
DATABASE_URL="postgresql://..." python -m server.app

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@testprosite.com","password":"Admin@Test123"}'
```

Should return access token.

---

## 🔧 Update Application Configuration

### Local Development

Create/update `.env` file:
```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Production Deployment (Render)

1. Go to Render dashboard
2. Select your service
3. Go to **Environment** tab
4. Add/Update:
   - `DATABASE_URL` = `postgresql://...`
5. Click **Save Changes**
6. Redeploy

### Frontend (Vercel/Next.js)

Update API base URL to point to new backend with Supabase.

---

## 🎯 Post-Migration Tasks

### 1. Test Core Features

- [ ] User login/registration
- [ ] Project creation
- [ ] Batch entry
- [ ] NCR workflow
- [ ] Safety NC workflow
- [ ] Reports generation

### 2. Performance Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_projects_company_id ON projects(company_id);
CREATE INDEX idx_project_memberships_user ON project_memberships(user_id);
CREATE INDEX idx_project_memberships_project ON project_memberships(project_id);
CREATE INDEX idx_batch_registers_project ON batch_registers(project_id);
```

### 3. Enable Row Level Security (Optional)

Supabase supports RLS for additional security:

```sql
-- Example: Users can only see their company's data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_company_isolation ON users
    FOR ALL
    USING (company_id = current_setting('app.current_company_id')::integer);
```

### 4. Setup Backups

In Supabase dashboard:
1. Go to **Settings** → **Database**
2. Under **Backups**, enable automated backups
3. Set backup schedule (daily recommended)

---

## 🚨 Troubleshooting

### Error: "relation does not exist"

**Cause:** Schema not created or table name mismatch

**Fix:**
```bash
# Re-run schema creation in Supabase SQL Editor
# Check table names match exactly
```

### Error: "duplicate key value violates unique constraint"

**Cause:** Data already imported or ID conflicts

**Fix:**
```sql
-- In Supabase SQL Editor, truncate tables:
TRUNCATE TABLE companies, users, projects CASCADE;

-- Then re-run import
python import_to_postgres.py
```

### Error: "password authentication failed"

**Cause:** Wrong password in DATABASE_URL

**Fix:**
```bash
# Get password from Supabase dashboard
# Settings → Database → Reset database password
# Update DATABASE_URL with new password
```

### Error: "connection refused"

**Cause:** Network/firewall issue or wrong host

**Fix:**
```bash
# Use connection pooling URL (port 6543), not direct connection (port 5432)
# Format: postgresql://postgres.xxx:[PASSWORD]@aws-0-region.pooler.supabase.com:6543/postgres
```

---

## 🔙 Rollback Plan

If migration fails:

### 1. Keep SQLite Backup
```bash
# Your original database is safe
ls -lh data.sqlite3

# Can always revert to SQLite
export DATABASE_URL="sqlite:///./data.sqlite3"
python -m server.app
```

### 2. Export from Supabase
```bash
# Use pg_dump to backup Supabase
pg_dump "$DATABASE_URL" > supabase_backup.sql
```

### 3. Dual Database Mode
```python
# In server/db.py, you can support both:
SQLITE_URL = "sqlite:///./data.sqlite3"
POSTGRES_URL = os.environ.get("DATABASE_URL")

# Use POSTGRES_URL if set, otherwise SQLite
DATABASE_URL = POSTGRES_URL if POSTGRES_URL else SQLITE_URL
```

---

## 📊 Migration Summary

**Current Status:**
- ✅ SQLite data exported to JSON
- ✅ PostgreSQL schema generated
- ✅ Migration scripts ready
- ⏳ Waiting for Supabase project setup

**Next Action:**
1. Create Supabase project
2. Get DATABASE_URL credentials
3. Run: `./run_migration.sh`

**Estimated Time:** 15-30 minutes

**Risk Level:** 🟢 Low (backups in place)

---

## 📞 Support

If you encounter issues:

1. **Check Logs:** Look at import script output for specific errors
2. **Supabase Docs:** https://supabase.com/docs/guides/database
3. **Test Connection:** Use psql or DB client to verify connectivity
4. **Schema Issues:** Review `schema_postgres.sql` for syntax errors

---

## ✅ Success Criteria

Migration is successful when:

1. ✅ All 52 tables created in Supabase
2. ✅ All 42 rows imported correctly
3. ✅ Application connects to Supabase
4. ✅ Users can login with existing credentials
5. ✅ Projects and data visible in application
6. ✅ New data can be created

**Ready to proceed? Run: `./run_migration.sh`**
