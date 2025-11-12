# 🚀 Deployment Checklist

## Pre-Deployment (In Supabase SQL Editor)

- [ ] **Execute Schema Migration**
  - Open `supabase_migration.sql` in Supabase SQL Editor
  - Run the entire script
  - Verify: "Migration base schema created successfully!"

- [ ] **Execute Data Migration**
  - Open `supabase_data_inserts.sql` in Supabase SQL Editor
  - Run the entire script
  - Verify row counts match expectations

- [ ] **Verify Migration**
  - Run verification queries (see SUPABASE_MIGRATION_GUIDE.md)
  - Check all 18 tables exist
  - Confirm foreign keys are working

## Deployment Options

### Option 1: Railway.app (⭐ Recommended - Easiest)

**Why Railway?**
- Free tier available
- Auto-detects Python/Flask
- Easy GitHub integration
- Good for hobby/MVP projects

**Steps:**
1. [ ] Push code to GitHub
2. [ ] Sign up at https://railway.app
3. [ ] New Project → Deploy from GitHub
4. [ ] Select your repo
5. [ ] Add environment variables:
   ```
   DATABASE_URL=postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres
   JWT_SECRET_KEY=<generate-strong-secret>
   FLASK_ENV=production
   PORT=8001
   ```
6. [ ] Deploy!
7. [ ] Test endpoints using Railway domain

**Pros:** Zero config, automatic HTTPS, easy rollbacks  
**Cons:** Free tier has limits (500 hours/month)

---

### Option 2: Render.com (Good Alternative)

**Steps:**
1. [ ] Push code to GitHub
2. [ ] Sign up at https://render.com
3. [ ] New → Web Service
4. [ ] Connect GitHub repo
5. [ ] Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT 'server.app:create_app()'`
6. [ ] Add environment variables (same as Railway)
7. [ ] Create Web Service
8. [ ] Wait for deployment (~3-5 min)

**Pros:** More generous free tier, good for production  
**Cons:** Slower cold starts on free tier

---

### Option 3: Docker on Local Machine / VPS

**Steps:**
1. [ ] Clone repo to your local machine
2. [ ] Build Docker image:
   ```bash
   docker build -t concretethings:latest .
   ```
3. [ ] Run container:
   ```bash
   docker run -d -p 8001:8001 \
     -e DATABASE_URL="postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres" \
     -e JWT_SECRET_KEY="your-secret-key" \
     -e FLASK_ENV="production" \
     --name concretethings \
     concretethings:latest
   ```
4. [ ] Test: `curl http://localhost:8001/health`

**For VPS (DigitalOcean, AWS EC2, etc.):**
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure SSL with Let's Encrypt
- [ ] Set up systemd service for auto-restart

**Pros:** Full control, predictable costs  
**Cons:** More setup, you manage everything

---

### Option 4: Vercel (For Next.js Frontend + API Routes)

**Note:** Vercel is primarily for Next.js. For Flask backend:
- Deploy Flask API to Railway/Render
- Deploy Next.js frontend to Vercel
- Connect via API URL

---

## Post-Deployment Verification

- [ ] **Health Check**
  ```bash
  curl https://your-app-url.com/health
  # Expected: {"status":"healthy","service":"concretethings-api"}
  ```

- [ ] **Test Authentication**
  ```bash
  curl -X POST https://your-app-url.com/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test123"}'
  ```

- [ ] **Test Database Connection**
  ```bash
  curl https://your-app-url.com/companies/1 \
    -H "Authorization: Bearer <your-jwt-token>"
  ```

- [ ] **Run Verification Script** (if possible from deployed env):
  ```bash
  python verify_supabase_migration.py
  ```

## Security Hardening

- [ ] **Change JWT Secret**
  - Generate new secret: `python -c "import secrets; print(secrets.token_hex(32))"`
  - Update in deployment platform environment variables

- [ ] **Change Database Password**
  - Go to Supabase → Settings → Database
  - Reset password
  - Update DATABASE_URL everywhere

- [ ] **Enable Supabase RLS (Row Level Security)**
  - In Supabase Dashboard → Authentication
  - Create policies for tables
  - Example: Only allow users to see their company's data

- [ ] **Configure CORS**
  - Update `CORS(app, origins=[...])` in server/app.py
  - Add your frontend domain

- [ ] **Set up Rate Limiting**
  - Add Flask-Limiter or use platform rate limiting

## Production Configuration

- [ ] **Environment Variables Set:**
  - DATABASE_URL ✓
  - JWT_SECRET_KEY (new, strong)
  - FLASK_ENV=production
  - DEBUG=False (or remove)
  - TWILIO_* (for WhatsApp)
  - SMTP_* (for email)

- [ ] **Configure File Storage:**
  - Create Supabase Storage bucket: `concretethings-uploads`
  - Update upload endpoints to use Supabase Storage SDK
  - Example:
    ```python
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    supabase.storage.from_('concretethings-uploads').upload(...)
    ```

- [ ] **Background Jobs:**
  - Add APScheduler or use platform cron
  - Schedule: check_vehicle_time_limits (every 30 min)
  - Schedule: check_pending_tests (daily at 8 AM)

- [ ] **Monitoring & Logging:**
  - Set up error tracking (Sentry, Rollbar)
  - Configure log aggregation
  - Set up uptime monitoring

## Testing in Production

- [ ] Create test user
- [ ] Create test project
- [ ] Test vehicle registration
- [ ] Test batch entry
- [ ] Test bulk entry
- [ ] Test notifications
- [ ] Test file uploads

## Rollback Plan

If something goes wrong:

1. [ ] Keep SQLite backup: `data.sqlite3.backup-*`
2. [ ] Keep SQL dumps: `sqlite_dump.sql`
3. [ ] Document current DATABASE_URL
4. [ ] Can switch back by changing .env to SQLite
5. [ ] Re-deploy to roll back code

## Cost Estimates

**Supabase:**
- Free tier: 500MB DB, 1GB storage, 2GB bandwidth
- Pro: $25/month (8GB DB, 100GB storage)

**Railway:**
- Free: 500 hours/month, $5 credit
- Hobby: ~$5-10/month for small app

**Render:**
- Free: With limitations (spins down after inactivity)
- Starter: $7/month (always on)

**Total for hobby/MVP:** $0-15/month  
**Total for production:** $25-50/month

---

## 🎉 Ready to Deploy?

**Recommended path for beginners:**
1. ✅ Execute SQL scripts in Supabase (30 seconds)
2. ✅ Deploy to Railway.app (5 minutes)
3. ✅ Test endpoints (5 minutes)
4. ✅ Configure Supabase Storage (10 minutes)
5. ✅ Invite team members (2 minutes)

**Total time:** ~23 minutes from zero to production! 🚀

---

Need help? Check:
- Railway docs: https://docs.railway.app
- Supabase docs: https://supabase.com/docs
- Flask deployment: https://flask.palletsprojects.com/en/latest/deploying/
