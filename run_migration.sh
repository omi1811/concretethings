#!/bin/bash
# Supabase Migration Execution Script
# Run this after setting up your Supabase project

set -e  # Exit on error

echo "================================================================================================="
echo "🚀 ProSite Supabase Migration Script"
echo "================================================================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERROR: DATABASE_URL not set${NC}"
    echo ""
    echo "Please set your Supabase database URL:"
    echo ""
    echo -e "${YELLOW}export DATABASE_URL=\"postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres\"${NC}"
    echo ""
    echo "To get your credentials:"
    echo "  1. Go to https://app.supabase.com"
    echo "  2. Select your project"
    echo "  3. Click 'Settings' → 'Database'"
    echo "  4. Copy the 'Connection string' under 'Connection pooling'"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ DATABASE_URL is set${NC}"
echo ""

# Step 2: Verify data export
echo -e "${BLUE}Step 2: Verifying exported data...${NC}"
if [ ! -d "migration_data" ]; then
    echo -e "${YELLOW}⚠️  Migration data not found. Running export...${NC}"
    python export_sqlite_data.py
fi

if [ ! -f "migration_data/manifest.json" ]; then
    echo -e "${RED}❌ Export failed. Please run: python export_sqlite_data.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Data export verified${NC}"
echo ""

# Step 3: Show schema file
echo -e "${BLUE}Step 3: Schema conversion${NC}"
if [ ! -f "schema_postgres.sql" ]; then
    echo -e "${YELLOW}⚠️  Schema not converted. Running conversion...${NC}"
    python convert_schema_to_postgres.py
fi

echo -e "${GREEN}✅ PostgreSQL schema ready: schema_postgres.sql${NC}"
echo ""

# Step 4: Manual schema creation prompt
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  MANUAL STEP REQUIRED${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Before importing data, you must create the database schema in Supabase:"
echo ""
echo "  1. Open your Supabase project: https://app.supabase.com"
echo "  2. Go to 'SQL Editor'"
echo "  3. Create a new query"
echo "  4. Copy the contents of: ${BLUE}schema_postgres.sql${NC}"
echo "  5. Paste into SQL Editor and click 'RUN'"
echo "  6. Verify all tables were created successfully"
echo ""
echo -e "${YELLOW}Have you completed the schema creation in Supabase? (yes/no)${NC}"
read -r response

if [[ ! "$response" =~ ^[Yy]es$ ]]; then
    echo -e "${RED}Migration cancelled. Please create the schema first.${NC}"
    exit 0
fi

echo ""

# Step 5: Import data
echo -e "${BLUE}Step 5: Importing data to Supabase...${NC}"
echo ""
echo -e "${YELLOW}This will import all data to your Supabase database.${NC}"
echo -e "${YELLOW}Continue? (yes/no)${NC}"
read -r confirm

if [[ ! "$confirm" =~ ^[Yy]es$ ]]; then
    echo -e "${RED}Import cancelled.${NC}"
    exit 0
fi

python import_to_postgres.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Data import completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Data import failed. Check errors above.${NC}"
    exit 1
fi

echo ""

# Step 6: Verification
echo -e "${BLUE}Step 6: Verification steps${NC}"
echo ""
echo "Please verify your migration:"
echo ""
echo "  1. Check table row counts in Supabase Table Editor"
echo "  2. Verify user accounts exist"
echo "  3. Test login with existing credentials"
echo "  4. Check project data"
echo ""

# Step 7: Update environment variables
echo -e "${BLUE}Step 7: Update application configuration${NC}"
echo ""
echo "Update your environment variables:"
echo ""
echo -e "${YELLOW}For local development (.env file):${NC}"
echo "DATABASE_URL=$DATABASE_URL"
echo ""
echo -e "${YELLOW}For production (Render/Vercel):${NC}"
echo "  1. Go to your hosting dashboard"
echo "  2. Add DATABASE_URL environment variable"
echo "  3. Redeploy your application"
echo ""

# Step 8: Test connection
echo -e "${BLUE}Step 8: Testing database connection...${NC}"
python -c "
import os
try:
    import psycopg2
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    print(f'✅ Connection successful! Found {count} users.')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
"

echo ""
echo "================================================================================================="
echo -e "${GREEN}🎉 Migration completed successfully!${NC}"
echo "================================================================================================="
echo ""
echo "Next steps:"
echo "  1. Start your application with new DATABASE_URL"
echo "  2. Test all major functionalities"
echo "  3. Run test suite: python test_bot_comprehensive.py"
echo "  4. Update DNS/domain settings if deploying"
echo ""
echo -e "${YELLOW}⚠️  Keep your SQLite backup safe: data.sqlite3${NC}"
echo ""
