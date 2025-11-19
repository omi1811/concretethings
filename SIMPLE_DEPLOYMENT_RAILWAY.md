# 🚀 ProSite - Simple Deployment Guide (Railway + Vercel)

## ✨ Recommended Stack (Easiest & Free to Start)

### Backend: **Railway.app** 🚂
- ✅ **Free $5 credit monthly** (renews every month)
- ✅ **Built-in PostgreSQL** (no separate database setup needed)
- ✅ **Automatic HTTPS**
- ✅ **Git-based deployment** (push code, it deploys)
- ✅ **Environment variables in dashboard**
- ✅ **File storage works** (persistent volumes)

### Frontend: **Vercel** ▲
- ✅ **Completely FREE** for hobby projects
- ✅ **Best for Next.js** (made by same company)
- ✅ **Automatic deployments** from GitHub
- ✅ **Global CDN** (super fast worldwide)
- ✅ **Automatic HTTPS**

### Total Cost: **$0/month** (Railway free tier + Vercel free tier)

---

## 🎯 Step-by-Step Deployment (30 minutes)

### STEP 1: Deploy Backend to Railway (15 minutes)

#### 1.1 Create Railway Account
1. Go to: https://railway.app/
2. Click **"Start a New Project"**
3. Sign up with GitHub (easiest)

#### 1.2 Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Connect your GitHub account
4. Select repository: `concretethings`
5. Click **"Deploy Now"**

#### 1.3 Add PostgreSQL Database
1. In your project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway automatically creates database and sets DATABASE_URL

#### 1.4 Configure Backend Service
1. Click on your backend service (the one from GitHub)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add these:

```bash
# Railway auto-provides DATABASE_URL, just add these:

FLASK_ENV=production
SECRET_KEY=943f85b632acb5769cb6a61e1549e730b9f1d3f8989750dbe1ecfc3b0250a858
JWT_SECRET_KEY=b4f0d0f60582359d66049ecc031424673e85a6b2616136053af0c0a4f5987084
CORS_ORIGINS=*
PORT=8000
```

#### 1.5 Configure Start Command
1. Go to **"Settings"** tab
2. Under **"Deploy"** section
3. Set **"Start Command"**:
```bash
gunicorn --config gunicorn.conf.py 'server.app:create_app()'
```

4. Set **"Root Directory"**: `/` (leave as root)

#### 1.6 Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Railway will give you a URL like: `https://your-app-name.up.railway.app`
4. Test it: Visit `https://your-app-name.up.railway.app/health`

---

### STEP 2: Deploy Frontend to Vercel (10 minutes)

#### 2.1 Install Vercel CLI
```powershell
# Open PowerShell
npm install -g vercel
```

#### 2.2 Deploy Frontend
```powershell
# Navigate to frontend folder
cd C:\Users\shrot\OneDrive\Desktop\ProSite\concretethings\frontend

# Login to Vercel
vercel login

# Deploy (answer prompts)
vercel

# Prompts:
# "Set up and deploy?" → Yes
# "Which scope?" → Your account
# "Link to existing project?" → No
# "Project name?" → prosite-frontend
# "Directory?" → ./ (press Enter)
# "Override settings?" → No
```

#### 2.3 Add Environment Variable
```powershell
# Add backend URL
vercel env add NEXT_PUBLIC_API_URL production

# When prompted, enter your Railway URL:
# https://your-app-name.up.railway.app
```

#### 2.4 Production Deploy
```powershell
vercel --prod
```

#### 2.5 Get Your URL
Vercel will give you a URL like: `https://prosite-frontend.vercel.app`

---

### STEP 3: Initialize Database (5 minutes)

#### 3.1 Get Database Connection String
1. Go to Railway dashboard
2. Click on **PostgreSQL** database
3. Go to **"Connect"** tab
4. Copy the **"Postgres Connection URL"**

#### 3.2 Run Migration Locally
```powershell
# In your project root
cd C:\Users\shrot\OneDrive\Desktop\ProSite\concretethings

# Create migration script for Railway
python -c "
import psycopg2
import os

# Your Railway database URL
DATABASE_URL = 'postgresql://postgres:password@containers-us-west-123.railway.app:1234/railway'

# Read and execute migration
with open('supabase_migration.sql', 'r') as f:
    sql = f.read()

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute(sql)
conn.commit()
print('✅ Database migrated!')
"
```

**OR** use Railway's SQL console:
1. Railway dashboard → PostgreSQL → **"Query"** tab
2. Copy contents of `supabase_migration.sql`
3. Paste and **"Run"**

---

## ✅ Verification Checklist

### Backend Working?
```bash
# Test health endpoint
curl https://your-app-name.up.railway.app/health

# Should return:
{"status":"healthy","service":"prosite-api"}
```

### Frontend Working?
1. Visit: `https://prosite-frontend.vercel.app`
2. Should see ProSite homepage
3. Click **"Sign In"**
4. Try login with: `admin@demo.com` / `adminpass`

### Database Working?
1. Railway dashboard → PostgreSQL → Query tab
2. Run: `SELECT COUNT(*) FROM users;`
3. Should return number of users

---

## 🔧 Common Issues & Fixes

### Issue 1: Backend won't start
**Error:** "Module not found"

**Fix:**
1. Railway dashboard → Backend service → Settings
2. Check **"Root Directory"** is `/` (not `/server`)
3. Check **"Start Command"** is correct
4. Redeploy

### Issue 2: Database connection failed
**Error:** "could not connect to server"

**Fix:**
1. Railway auto-sets DATABASE_URL
2. Don't manually set DATABASE_URL in variables
3. Just let Railway handle it automatically

### Issue 3: Frontend can't reach backend
**Error:** "Network request failed"

**Fix:**
```powershell
# Make sure environment variable is set
vercel env ls

# If not there, add it:
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-app-name.up.railway.app

# Redeploy
vercel --prod
```

### Issue 4: CORS errors
**Fix:** Make sure `CORS_ORIGINS=*` is set in Railway variables

---

## 💰 Cost Breakdown

### Free Tier Limits:
- **Railway**: $5 credit/month (enough for ~500 hours runtime)
- **Vercel**: Unlimited deployments, 100GB bandwidth
- **Total**: $0 if you stay within free tier

### When to Upgrade:
- Railway: When you need >500 hours/month ($5/month = 500 hours)
- Vercel: Only if >100GB bandwidth/month ($20/month)

### Recommended Paid Plan (if needed):
- Railway: $5/month (goes far for small apps)
- Vercel: Stay on free tier (usually sufficient)
- **Total**: $5/month

---

## 🎯 Why Railway > Supabase/Render?

| Feature | Railway | Supabase | Render |
|---------|---------|----------|--------|
| **Setup Time** | 10 min | 30 min | 30 min |
| **Database Included** | ✅ Auto | ❌ Separate | ❌ Separate |
| **Free Tier** | $5 credit | $0 (limited) | $0 (sleeps) |
| **Learning Curve** | Easy | Medium | Medium |
| **File Storage** | ✅ Persistent | Need S3 | ❌ Ephemeral |
| **Deployment** | Git push | Manual config | Manual config |
| **Logs** | ✅ Real-time | ✅ Yes | ✅ Yes |
| **Auto HTTPS** | ✅ Yes | ✅ Yes | ✅ Yes |

**Winner:** 🏆 Railway (easiest for beginners + everything included)

---

## 📱 What About Mobile App?

### Flutter App Status:
- ❌ **NOT READY** - Only structure exists, no actual code
- ⏳ **Estimated time to complete**: 3-4 weeks full development
- 💡 **Recommendation**: Deploy web app first, build mobile later

### Flutter Development Plan:
1. **Week 1**: Authentication, Dashboard, API integration
2. **Week 2**: Batch entry, Cube tests, Camera integration
3. **Week 3**: Offline sync, Local database, Testing
4. **Week 4**: Polish, Bug fixes, Play Store/App Store submission

### Can deploy mobile app?
**No** - Need to write ~10,000 lines of Dart code first.

---

## 🚀 Quick Commands Reference

### Deploy Backend to Railway:
```bash
# Railway auto-deploys from GitHub
# Just push to main branch:
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### Deploy Frontend to Vercel:
```bash
cd frontend
vercel --prod
```

### View Logs:
```bash
# Railway: Dashboard → Service → Logs tab
# Vercel: Dashboard → Deployments → Click deployment → Logs
```

### Rollback:
```bash
# Railway: Dashboard → Deployments → Click previous → Redeploy
# Vercel: Dashboard → Deployments → Click previous → Promote to Production
```

---

## 📞 Next Steps

### Immediate (Today):
1. ✅ Sign up for Railway.app
2. ✅ Deploy backend to Railway (follow STEP 1)
3. ✅ Deploy frontend to Vercel (follow STEP 2)
4. ✅ Test login and basic features

### Tomorrow:
1. Add real data to database
2. Test all features end-to-end
3. Fix any bugs
4. Share with users for testing

### Next Week:
1. Monitor usage and errors
2. Add analytics (Google Analytics)
3. Start Flutter app development (if needed)
4. User feedback and improvements

---

## 🎓 Learning Resources

### Railway Docs:
- https://docs.railway.app/
- Video: "Deploy Flask App to Railway" (YouTube)

### Vercel Docs:
- https://vercel.com/docs
- Video: "Deploy Next.js to Vercel" (YouTube)

### PostgreSQL Basics:
- https://www.postgresql.org/docs/
- Railway has built-in query editor (no need to install locally)

---

## ✅ Success Criteria

Your deployment is successful when:
- [ ] Backend health endpoint returns 200 OK
- [ ] Frontend homepage loads
- [ ] Login works with demo credentials
- [ ] Can create a batch
- [ ] Data persists after page reload
- [ ] No CORS errors in browser console
- [ ] Database has tables (check Railway PostgreSQL)

---

**Ready to deploy? Start with STEP 1 above! 🚀**

**Questions?** Check Railway's excellent docs or Discord community.
