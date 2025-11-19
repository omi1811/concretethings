#!/usr/bin/env python3
"""
ProSite - Deployment Fix Script
Generates all necessary configuration for production deployment
"""

import secrets
import os

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_hex(32)

def create_render_env_file():
    """Create .env file for Render deployment"""
    secret_key = generate_secret_key()
    jwt_key = generate_secret_key()
    
    env_content = f"""# ProSite Production Environment Variables
# Copy these to Render Dashboard → Environment Tab

DATABASE_URL=postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres
FLASK_ENV=production
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_key}
CORS_ORIGINS=*

# Optional - Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@prosite.com

# Optional - Supabase Storage
SUPABASE_URL=https://lsqvxfaonbvqvlwrhsby.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional - Monitoring
SENTRY_DSN=your-sentry-dsn
"""
    
    with open('.env.render', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Created .env.render")
    print("\n📋 Copy these environment variables to Render Dashboard:")
    print("=" * 70)
    print(env_content)
    print("=" * 70)
    
    return secret_key, jwt_key

def create_vercel_env_file(backend_url):
    """Create .env file for Vercel frontend deployment"""
    env_content = f"""# ProSite Frontend Environment Variables
# Add this to Vercel Dashboard → Settings → Environment Variables

NEXT_PUBLIC_API_URL={backend_url}
"""
    
    with open('frontend/.env.production', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("\n✅ Created frontend/.env.production")
    print("\n📋 Add this to Vercel:")
    print("=" * 70)
    print(env_content)
    print("=" * 70)

def create_deployment_guide():
    """Create step-by-step deployment guide"""
    guide = """
🚀 ProSite Deployment - Quick Start Guide
==========================================

STEP 1: Deploy Backend to Render (15 minutes)
----------------------------------------------
1. Open Render Dashboard: https://dashboard.render.com/
2. Click on your ProSite service
3. Go to Environment tab
4. Add all variables from .env.render file (created above)
5. Click "Save Changes"
6. Wait for automatic redeploy (~2-3 minutes)
7. Test: curl https://your-service.onrender.com/health

STEP 2: Deploy Frontend to Vercel (15 minutes)
-----------------------------------------------
1. Install Vercel CLI:
   npm i -g vercel

2. Navigate to frontend folder:
   cd frontend

3. Login to Vercel:
   vercel login

4. Deploy:
   vercel

   Answer prompts:
   - Link to existing project? No
   - Project name: prosite-frontend
   - Directory: ./
   - Build command: (auto-detected)
   - Output directory: (auto-detected)

5. Add environment variable:
   vercel env add NEXT_PUBLIC_API_URL production
   Enter: https://your-backend.onrender.com

6. Production deploy:
   vercel --prod

7. Visit the URL provided

STEP 3: Verify Supabase Database (10 minutes)
----------------------------------------------
1. Go to: https://supabase.com/dashboard/project/lsqvxfaonbvqvlwrhsby
2. Click "SQL Editor" in sidebar
3. Click "New Query"
4. Run this verification query:

   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;

5. Should return 30+ tables
6. If no tables, run the migration:
   - Open supabase_migration.sql
   - Copy all content
   - Paste in SQL Editor
   - Click "Run"

STEP 4: Test End-to-End (5 minutes)
------------------------------------
1. Open frontend URL from Step 2
2. Click "Sign In"
3. Enter credentials:
   Email: admin@demo.com
   Password: adminpass

4. Should see dashboard
5. Try creating a batch
6. Check if data saves

TROUBLESHOOTING
---------------
Backend not starting?
→ Check Render logs for errors
→ Verify DATABASE_URL is correct
→ Ensure SECRET_KEY is set

Frontend can't reach backend?
→ Check NEXT_PUBLIC_API_URL is set
→ Verify backend is running
→ Check CORS settings

Database connection failed?
→ Verify Supabase database is running
→ Check password in DATABASE_URL (March%402024)
→ Run migration scripts if tables missing

FILES CREATED:
--------------
✅ .env.render - Backend environment variables
✅ frontend/.env.production - Frontend environment variables
✅ DEPLOYMENT_QUICK_START.txt - This guide

ESTIMATED TOTAL TIME: 45 minutes
"""
    
    with open('DEPLOYMENT_QUICK_START.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("\n✅ Created DEPLOYMENT_QUICK_START.txt")

def main():
    print("🚀 ProSite Deployment Configuration Generator")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('server'):
        print("❌ Error: Must run from concretethings root directory")
        print("   Current directory:", os.getcwd())
        return
    
    print("\n📝 Generating deployment configuration files...\n")
    
    # Generate backend env vars
    secret_key, jwt_key = create_render_env_file()
    
    # Prompt for backend URL
    print("\n❓ What is your Render backend URL?")
    print("   Example: https://prosite-backend-xyz.onrender.com")
    print("   (Press Enter to use placeholder)")
    backend_url = "https://your-backend.onrender.com"
    print(f"   Using: {backend_url}")
    
    # Generate frontend env vars
    create_vercel_env_file(backend_url)
    
    # Create deployment guide
    create_deployment_guide()
    
    print("\n" + "=" * 70)
    print("✅ ALL CONFIGURATION FILES GENERATED!")
    print("=" * 70)
    print("\n📁 Files created:")
    print("   1. .env.render (backend environment variables)")
    print("   2. frontend/.env.production (frontend environment variables)")
    print("   3. DEPLOYMENT_QUICK_START.txt (step-by-step guide)")
    print("\n📖 Next: Read DEPLOYMENT_QUICK_START.txt and follow the steps")
    print("\n⏱️  Estimated deployment time: 45 minutes")
    print("\n🎯 Start with STEP 1: Deploy Backend to Render")
    print("=" * 70)

if __name__ == "__main__":
    main()
