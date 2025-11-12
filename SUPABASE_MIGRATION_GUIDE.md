# 🚀 Supabase Migration Guide - Step by Step

## Overview
Due to GitHub Codespaces network restrictions (IPv6 connectivity issues), we're using a **manual SQL-based migration** approach instead of the automated Python script.

## ✅ What's Been Prepared

1. **Backup Created**: `data.sqlite3.backup-TIMESTAMP`
2. **SQL Dump**: `sqlite_dump.sql` (full SQLite export)
3. **Schema Script**: `supabase_migration.sql` (Postgres DDL)
4. **Data Script**: `supabase_data_inserts.sql` (INSERT statements)

## 📋 Migration Steps

### Step 1: Access Your Supabase Project

1. Go to https://supabase.com/dashboard
2. Select your project: `lsqvxfaonbvqvlwrhsby`
3. Navigate to **SQL Editor** (left sidebar)

### Step 2: Create the Database Schema

1. In SQL Editor, click **"New query"**
2. Copy the entire contents of `supabase_migration.sql`
3. Paste into the SQL Editor
4. Click **Run** (or press Ctrl+Enter)
5. ✅ You should see: "Migration base schema created successfully!"

**What this does:**
- Creates all 18 tables with proper Postgres data types
- Sets up foreign key relationships
- Creates indexes
- Prepares sequences for auto-increment IDs

### Step 3: Insert Your Data

1. Create another **"New query"** in SQL Editor
2. Copy the entire contents of `supabase_data_inserts.sql`
3. Paste into the SQL Editor
4. Click **Run**
5. ✅ You should see a summary table showing row counts:
   ```
   companies                    | 1
   users                        | 1
   projects                     | 1
   batch_registers              | 1
   material_vehicle_register    | 2
   ```

### Step 4: Verify Migration

Run this verification query in Supabase SQL Editor:

```sql
-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check data counts
SELECT 
    (SELECT COUNT(*) FROM companies) as companies,
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM projects) as projects,
    (SELECT COUNT(*) FROM batch_registers) as batches,
    (SELECT COUNT(*) FROM material_vehicle_register) as vehicles;

-- Verify foreign keys are working
SELECT 
    u.email,
    c.name as company,
    p.name as project
FROM users u
JOIN companies c ON u.company_id = c.id
LEFT JOIN project_memberships pm ON pm.user_id = u.id
LEFT JOIN projects p ON p.id = pm.project_id;
```

**Expected results:**
- 18 tables listed
- Row counts: 1 company, 1 user, 1 project, 1 batch, 2 vehicles
- User joined to company and project successfully

### Step 5: Test Application Connection

Once migration is complete, test the app connection:

1. **Keep DATABASE_URL in .env** (already set):
   ```
   DATABASE_URL=postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres
   ```

2. **Important**: The app won't be able to connect from Codespaces due to network restrictions, BUT you can:
   - Deploy to a server/VM that has IPv6 or proper network access
   - Use Docker locally on your machine
   - Deploy to Vercel/Netlify/Railway/Render

### Step 6: Deploy the Application

Since Codespaces can't connect to Supabase, here are your deployment options:

#### Option A: Deploy to Railway.app (Recommended - Free tier)

1. Push your code to GitHub
2. Go to https://railway.app
3. Create new project → Deploy from GitHub
4. Add environment variables:
   ```
   DATABASE_URL=postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres
   JWT_SECRET_KEY=your-secret-key-change-in-production
   FLASK_ENV=production
   ```
5. Railway will auto-detect the Python app and deploy

#### Option B: Deploy with Docker (Local Machine)

```bash
# On your local machine (not Codespaces):
git clone <your-repo>
cd concretethings

# Build
docker build -t concretethings:latest .

# Run
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres" \
  -e JWT_SECRET_KEY="your-secret-key" \
  concretethings:latest
```

#### Option C: Deploy to Render.com (Free tier)

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT 'server.app:create_app()'`
6. Add environment variables (same as above)

### Step 7: Update File Storage (Production)

After successful deployment, migrate file uploads to Supabase Storage:

1. In Supabase Dashboard → Storage
2. Create bucket: `concretethings-uploads`
3. Set bucket to **Public** (or configure auth policies)
4. Update upload endpoints to use Supabase Storage SDK

## 🔍 Troubleshooting

### If you see "table already exists" errors:
This is OK if running the schema script multiple times. The script uses `CREATE TABLE IF NOT EXISTS`.

### If you see foreign key constraint errors:
Run the schema script first, then the data script. Make sure parent tables (companies, users, projects) are populated before child tables.

### If sequences are wrong:
The data script includes sequence reset commands at the end. Run them again:
```sql
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users), true);
SELECT setval('projects_id_seq', (SELECT MAX(id) FROM projects), true);
-- etc for other tables
```

## 📊 Current Database State

**Before Migration (SQLite):**
- 18 tables
- 1 user, 1 project, 1 batch, 2 vehicles
- ~582 lines of SQL

**After Migration (Supabase):**
- Same 18 tables in Postgres
- All data preserved with proper typing
- Foreign keys enforced
- Ready for production scale

## 🎯 Next Steps After Migration

1. ✅ Verify data in Supabase SQL Editor
2. ✅ Deploy app to a platform that can reach Supabase (Railway/Render/Vercel)
3. ✅ Test API endpoints
4. ✅ Configure Supabase Storage for file uploads
5. ✅ Set up Row Level Security (RLS) policies in Supabase
6. ✅ Configure background jobs (APScheduler or platform cron)
7. ✅ Add monitoring and logging

## 📞 Support

If you encounter issues:
- Check Supabase logs: Dashboard → Logs
- Verify network connectivity from your deployment platform
- Review foreign key relationships if inserts fail
- Ensure sequences are set correctly

## ✨ Benefits of Supabase

- **Managed Postgres**: No DB maintenance
- **Built-in Auth**: Can integrate Supabase Auth later
- **Real-time**: WebSocket subscriptions available
- **Storage**: Built-in file storage
- **Auto-generated APIs**: REST and GraphQL
- **Free tier**: 500MB database, 1GB storage

---

**Migration prepared on**: November 12, 2025  
**Target Database**: Supabase (lsqvxfaonbvqvlwrhsby)  
**Migration Type**: Manual SQL execution (due to Codespaces network limitations)
