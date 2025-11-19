# Quick Fix Checklist - ProSite

## ✅ Completed (Just Now)

- [x] **Created `.env` file** with secure random keys
- [x] **Created `frontend/lib/api-optimized.js`** - API client with auth
- [x] **Created `frontend/lib/db.js`** - IndexedDB utilities
- [x] **Tested servers** - Both backend and frontend running successfully
- [x] **Generated comprehensive report** - TESTING_AND_IMPROVEMENTS_REPORT.md

---

## 🔥 High Priority (Do Next)

### 1. Remove Production Console.logs (5 minutes)
**File**: `frontend/app/page.js` line 39
```javascript
// REMOVE THIS:
console.log('Contact form submitted:', contactForm);
```

**File**: `frontend/app/providers.js` line 25
```javascript
// REMOVE THIS:
console.log('App is online');
```

**Fix**: Delete these lines or wrap in development check:
```javascript
if (process.env.NODE_ENV === 'development') {
  console.log(...);
}
```

---

### 2. Test Login Functionality (10 minutes)
```powershell
# 1. Ensure servers are running
# Backend: http://localhost:8000
# Frontend: http://localhost:3000

# 2. Navigate to login
# http://localhost:3000/login

# 3. Test credentials
# Email: admin@demo.com
# Password: adminpass

# 4. Check browser console for errors
# 5. Verify redirect to dashboard
```

---

### 3. Configure Email (if needed) (15 minutes)
**Edit `.env` file**:
```bash
# For Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # From https://myaccount.google.com/apppasswords
SMTP_FROM_EMAIL=your-email@gmail.com
EMAIL_ENABLED=true
```

**Test**:
```python
python -c "from server.email_notifications import send_email; send_email('test@example.com', 'Test', 'Test email')"
```

---

### 4. Update .gitignore (2 minutes)
**Ensure these are ignored**:
```gitignore
# Environment
.env

# Dependencies
node_modules/
.venv/
__pycache__/

# Database
*.sqlite3
data.sqlite3

# Uploads
uploads/

# Logs
*.log
logs/

# Build
.next/
dist/
build/

# OS
.DS_Store
Thumbs.db
```

---

## 🎯 Medium Priority (This Week)

### 5. Enable Disabled Features
**Refactor these modules** (in `server/app.py`):
- [ ] `incident_investigation` - Line 43
- [ ] `safety_audits` - Line 44
- [ ] `ppe_tracking` - Line 45
- [ ] `geofence_api` - Line 46
- [ ] `handover_register` - Line 48

**Pattern**: Change from `db.session` to `session_scope()`:
```python
# OLD
from flask_sqlalchemy import SQLAlchemy
user = User.query.get(id)

# NEW
from .db import session_scope
with session_scope() as session:
    user = session.get(User, id)
```

---

### 6. Add Rate Limiting (30 minutes)
**Install**:
```powershell
pip install Flask-Limiter
```

**Add to `server/app.py`**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Apply to login
@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    pass
```

---

### 7. Setup Logging (20 minutes)
**Create `logs/` directory**:
```powershell
New-Item -ItemType Directory -Path logs -Force
```

**Add to `server/app.py`**:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
```

---

### 8. Add API Documentation (1 hour)
**Install Swagger**:
```powershell
pip install flask-restx
```

**Setup**:
```python
from flask_restx import Api

api = Api(app, 
    version='1.0',
    title='ProSite API',
    description='Professional Site Management API',
    doc='/api/docs'
)
```

**Access**: http://localhost:8000/api/docs

---

## 📚 Documentation Review

### Must Read:
1. **TESTING_AND_IMPROVEMENTS_REPORT.md** - Full analysis of 25 issues
2. **WINDOWS_SETUP.md** - Windows-specific setup guide
3. **WINDOWS_FIXES_SUMMARY.md** - What was fixed for Windows

### Reference:
- **AUTHENTICATION.md** - Auth system details
- **DEPLOYMENT.md** - Production deployment guide
- **QUICK_START.md** - Getting started guide

---

## 🧪 Testing Checklist

### Backend Tests
```powershell
# Test health endpoint
Invoke-WebRequest http://localhost:8000/health

# Test login
$body = @{email="admin@demo.com"; password="adminpass"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/api/auth/login -Method POST -Body $body -ContentType "application/json"
```

### Frontend Tests
```javascript
// In browser console (http://localhost:3000)

// Test auth utilities
import { isAuthenticated, getUserData } from '@/lib/db';
console.log('Authenticated:', isAuthenticated());
console.log('User:', getUserData());

// Test API client
import { authAPI } from '@/lib/api-optimized';
authAPI.getCurrentUser().then(console.log);
```

---

## 🚀 Production Readiness

### Before Going Live:
- [ ] All High Priority fixes completed
- [ ] `.env` file has production secrets
- [ ] SQLite replaced with PostgreSQL
- [ ] HTTPS/SSL configured
- [ ] Email notifications working
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Error monitoring setup (Sentry)
- [ ] Backup strategy implemented
- [ ] Security audit completed

### Production Checklist:
```bash
# 1. Update .env
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://...

# 2. Build frontend
cd frontend
npm run build

# 3. Use production server (not Flask dev server)
# For Windows: Use waitress
pip install waitress
waitress-serve --port=8000 server.app:create_app()

# For Linux: Use gunicorn (already configured)
gunicorn --config gunicorn.conf.py server.app:create_app()
```

---

## 📞 Support

### Getting Help:
1. **Check Logs**: `logs/app.log`
2. **Browser Console**: F12 → Console tab
3. **Backend Terminal**: Check Flask output
4. **Frontend Terminal**: Check Next.js output

### Common Issues:
| Issue | Solution |
|-------|----------|
| "Module not found" | `npm install` in frontend/ |
| "Connection refused" | Check if backend is running on port 8000 |
| "401 Unauthorized" | Check `.env` has correct JWT_SECRET_KEY |
| "Cannot import name" | Run `pip install -r requirements.txt` |

---

## ✨ Quick Commands

```powershell
# Start everything
.\start.ps1

# Backend only
$env:FLASK_APP = "server.app:create_app()"
.\.venv\Scripts\flask.exe run --port=8000

# Frontend only
cd frontend
npm run dev

# Check health
Invoke-WebRequest http://localhost:8000/health

# View logs
Get-Content -Path logs\app.log -Tail 50 -Wait

# Database backup
Copy-Item data.sqlite3 "backups\data-$(Get-Date -Format 'yyyyMMdd-HHmmss').sqlite3"
```

---

**Last Updated**: November 15, 2025  
**Status**: ✅ Application functional with minor improvements needed
