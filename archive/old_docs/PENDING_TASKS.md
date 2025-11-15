# ProSite - Pending Configuration & Setup Tasks

## 🚨 Critical - Required for Production

### 1. **Email Configuration** (HIGH PRIORITY) ⚠️

**Status:** Not Configured  
**Impact:** Password reset, notifications, and alerts will not work

#### Setup Steps:

**Option A: Gmail (Recommended for Testing)**
1. Create/use a Gmail account for the app
2. Enable 2-Factor Authentication
3. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
4. Update `.env` file:
```bash

```

**Option B: SendGrid (Recommended for Production)**
1. Sign up at https://sendgrid.com (Free: 100 emails/day)
2. Create API Key (Settings → API Keys)
3. Update `.env` file:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey  # Literally "apikey"
SMTP_PASSWORD=your-sendgrid-api-key-here
SMTP_FROM_EMAIL=your-verified-email@yourdomain.com
SMTP_FROM_NAME=ProSite
EMAIL_ENABLED=true
```

**Option C: AWS SES (Best for Scale)**
1. Sign up for AWS SES
2. Verify domain/email
3. Get SMTP credentials
4. Update `.env` file:
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-aws-smtp-username
SMTP_PASSWORD=your-aws-smtp-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=ProSite
EMAIL_ENABLED=true
```

**Test Email Setup:**
```bash
cd /workspaces/concretethings
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from server.email_notifications import send_email
send_email(
    to_email='your-test-email@gmail.com',
    subject='ProSite Email Test',
    html_body='<h1>ProSite Email Test</h1><p>If you receive this, email is configured correctly! ✅</p>'
)
print('✅ Test email sent')
"
```

---

### 2. **Environment Variables Setup** (HIGH PRIORITY) ⚠️

**Status:** Using .env.example defaults  
**Impact:** Security risk, features disabled

#### Action Required:

1. **Create `.env` file:**
```bash
cd /workspaces/concretethings
cp .env.example .env
```

2. **Update Critical Variables:**
```bash
# MUST CHANGE IN PRODUCTION
SECRET_KEY=generate-random-64-char-string-here
JWT_SECRET_KEY=generate-different-64-char-string-here

# Optional but recommended
DEBUG=False  # Set to False in production
PORT=8000
HOST=0.0.0.0

# Email (see section 1 above)
EMAIL_ENABLED=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application URL (for email links)
APP_URL=https://yourdomain.com  # Update with your domain
```

3. **Generate Secure Keys:**
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate JWT_SECRET_KEY (different from above)
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

### 3. **WhatsApp Notifications** (MEDIUM PRIORITY) 📱

**Status:** Not Configured (Optional)  
**Impact:** WhatsApp alerts for NCs, TBT, PTW will not work

#### Setup Steps (Optional):

1. Sign up for Twilio: https://www.twilio.com/try-twilio
2. Get WhatsApp sandbox number (free for testing)
3. Get production WhatsApp Business number (paid)
4. Update `.env`:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_ENABLED=true
TEST_WHATSAPP_PHONE=+919876543210  # Your test number
```

**Cost:** ~$0.005 per message (after free credits)

**Alternative:** Can be skipped if only using email notifications

---

### 4. **Admin Password Change** (HIGH PRIORITY) 🔐

**Status:** Using default password  
**Impact:** Security vulnerability

#### Action Required:

1. Login as admin:
   - Email: `shrotrio@gmail.com`
   - Password: `Admin@123`

2. Change password immediately:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"shrotrio@gmail.com","password":"Admin@123"}'

# Get token from response, then:
curl -X PUT "http://localhost:8000/api/users/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password":"YourNewSecurePassword123!"}'
```

3. **Or use frontend after deployment**

---

### 5. **Database Backup Strategy** (HIGH PRIORITY) 💾

**Status:** No backup configured  
**Impact:** Data loss risk

#### Recommended Setup:

**Option A: Automated Daily Backup (Shell Script)**
```bash
# Create backup script
cat > /workspaces/concretethings/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/workspaces/concretethings/backups"
DATE=$(date +%Y%m%d-%H%M%S)
DB_FILE="/workspaces/concretethings/data.sqlite3"

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/data-$DATE.sqlite3"

# Keep only last 30 days
find $BACKUP_DIR -name "data-*.sqlite3" -mtime +30 -delete

echo "✅ Backup created: data-$DATE.sqlite3"
EOF

chmod +x backup_db.sh

# Test backup
./backup_db.sh
```

**Option B: Git-based Backup**
```bash
# Add to .gitignore exceptions
echo "!backups/*.sql" >> .gitignore

# Create SQL dump
sqlite3 data.sqlite3 .dump > backups/backup-$(date +%Y%m%d).sql

# Commit to git
git add backups/
git commit -m "Database backup $(date +%Y%m%d)"
```

**Option C: Cloud Backup (AWS S3, Google Drive, Dropbox)**
- Upload daily backups to cloud storage
- Use `rclone` or provider's CLI

---

## 📋 Important - Recommended for Production

### 6. **Frontend Configuration**

**Status:** Not started  
**Impact:** Users can't access system

#### Tasks:

- [ ] Create React/Next.js frontend (or use existing)
- [ ] Add "Forgot Password" link to login page
- [ ] Create password reset pages (`/forgot-password`, `/reset-password`)
- [ ] Add module subscription UI
- [ ] Hide menu items for unsubscribed modules
- [ ] Display score dashboards

**Estimated Time:** 40-60 hours

---

### 7. **SSL/HTTPS Certificate** (Production Deployment)

**Status:** HTTP only (localhost)  
**Impact:** Insecure in production

#### Options:

**Option A: Let's Encrypt (Free)**
```bash
# Using Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

**Option B: Cloudflare (Free)**
- Add domain to Cloudflare
- Enable SSL/TLS
- Set encryption mode to "Full"

**Option C: Load Balancer SSL (AWS, Azure, GCP)**
- Use cloud provider's certificate manager
- Attach to load balancer

---

### 8. **Production Server Setup**

**Status:** Development mode  
**Impact:** Not production-ready

#### Deployment Options:

**Option A: Docker (Recommended)**
```bash
# Already has Dockerfile
docker build -t prosite .
docker run -p 8000:8000 --env-file .env prosite
```

**Option B: Render.com (Easy)**
- Connect GitHub repo
- Auto-deploy on push
- Free tier available

**Option C: AWS/Azure/GCP**
- Deploy to EC2/App Service/Compute Engine
- Use managed database (RDS/Azure SQL)
- Setup load balancer

---

### 9. **Logging & Monitoring**

**Status:** Console logging only  
**Impact:** Difficult to debug production issues

#### Setup:

1. **Structured Logging:**
```python
# Already configured in app.py
# Set LOG_LEVEL in .env
LOG_LEVEL=INFO  # or DEBUG, WARNING, ERROR
```

2. **Error Tracking (Optional):**
   - Sentry: https://sentry.io (Free tier)
   - Rollbar: https://rollbar.com
   - Add to `requirements.txt` and configure

3. **Performance Monitoring:**
   - New Relic (free tier)
   - DataDog (free trial)

---

### 10. **Email Verification Flow**

**Status:** User registration exists, verification pending  
**Impact:** Users not verified

#### Implementation Needed:

- [ ] Generate verification token on registration
- [ ] Send verification email
- [ ] Create verification endpoint
- [ ] Update `is_email_verified` on confirmation

**Estimated Time:** 4-6 hours

---

## 🔧 Optional - Nice to Have

### 11. **Rate Limiting**

**Status:** Not implemented  
**Impact:** Vulnerable to brute force

#### Setup with Redis:

```bash
# Install Redis
sudo apt install redis-server

# Add to requirements.txt
flask-limiter==3.5.0
redis==5.0.1

# Configure in app.py
from flask_limiter import Limiter
limiter = Limiter(app, storage_uri="redis://localhost:6379")

# Add to login endpoint
@limiter.limit("5 per minute")
@auth_bp.route("/login", methods=["POST"])
```

**Estimated Time:** 2-3 hours

---

### 12. **2FA (Two-Factor Authentication)**

**Status:** Not implemented  
**Impact:** Lower security for admin accounts

#### Implementation:

- [ ] Install `pyotp` library
- [ ] Generate TOTP secret per user
- [ ] Create QR code endpoint
- [ ] Validate TOTP on login
- [ ] Generate backup codes

**Estimated Time:** 8-12 hours

---

### 13. **Social Login (OAuth)**

**Status:** Not implemented  
**Impact:** Manual registration only

#### Options:

- [ ] Google OAuth
- [ ] Microsoft/Azure AD
- [ ] GitHub OAuth

**Estimated Time:** 12-16 hours per provider

---

### 14. **API Documentation (Swagger/OpenAPI)**

**Status:** Markdown docs only  
**Impact:** Harder for frontend developers

#### Setup:

```bash
# Add to requirements.txt
flask-swagger-ui==4.11.1
flasgger==0.9.7.1

# Auto-generate from docstrings
```

**Estimated Time:** 4-6 hours

---

### 15. **Automated Testing**

**Status:** Manual testing only  
**Impact:** Regressions possible

#### Setup:

```bash
# Add to requirements.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0

# Create tests/
mkdir tests
# Write unit tests, integration tests
```

**Estimated Time:** 20-40 hours

---

### 16. **CI/CD Pipeline**

**Status:** Manual deployment  
**Impact:** Slower deployments

#### Options:

- GitHub Actions (free)
- GitLab CI/CD (free)
- CircleCI (free tier)

**Estimated Time:** 4-8 hours

---

## 📊 Priority Summary

### **MUST DO NOW (Before Production):**
1. ✅ Email Configuration - **15 minutes**
2. ✅ Environment Variables Setup - **10 minutes**
3. ✅ Admin Password Change - **5 minutes**
4. ✅ Database Backup Strategy - **30 minutes**

**Total: ~1 hour to production-ready backend**

---

### **SHOULD DO SOON (Week 1):**
5. Frontend Password Reset Pages - **8 hours**
6. SSL/HTTPS Setup - **1-2 hours**
7. Production Server Deployment - **4-8 hours**

**Total: ~13-18 hours**

---

### **NICE TO HAVE (Week 2-4):**
8. Email Verification Flow - **4-6 hours**
9. Rate Limiting - **2-3 hours**
10. Logging/Monitoring - **4-6 hours**
11. API Documentation - **4-6 hours**

**Total: ~14-21 hours**

---

### **FUTURE ENHANCEMENTS (Month 2+):**
12. 2FA Implementation - **8-12 hours**
13. Social Login - **12-16 hours**
14. Automated Testing - **20-40 hours**
15. CI/CD Pipeline - **4-8 hours**

---

## ✅ Quick Start Checklist

Copy this checklist and start working through it:

```bash
# 1. Email Setup (15 min)
[ ] Create Gmail account or SendGrid account
[ ] Generate app password / API key
[ ] Update .env file with SMTP credentials
[ ] Set EMAIL_ENABLED=true
[ ] Test email: python3 -c "from server.email_notifications import send_email; send_email('test@email.com', 'Test', 'Works!')"

# 2. Environment Variables (10 min)
[ ] Copy .env.example to .env
[ ] Generate SECRET_KEY: python3 -c "import secrets; print(secrets.token_urlsafe(64))"
[ ] Generate JWT_SECRET_KEY: python3 -c "import secrets; print(secrets.token_urlsafe(64))"
[ ] Update APP_URL with your domain
[ ] Set DEBUG=False

# 3. Admin Password (5 min)
[ ] Login as shrotrio@gmail.com / Admin@123
[ ] Change password to secure password
[ ] Test new login

# 4. Database Backup (30 min)
[ ] Create backup_db.sh script
[ ] Test backup creation
[ ] Setup cron job for daily backups
[ ] Test restore process

# 5. Test Everything
[ ] Run: python3 test_auth_system.py
[ ] Test password reset flow
[ ] Test NC dashboard
[ ] Test module access control
```

---

## 🆘 Support & Documentation

**Configuration Files:**
- `.env.example` - Environment variable template
- `server/config.py` - Configuration loader
- `server/email_notifications.py` - Email service

**Documentation:**
- `SUPABASE_VS_CUSTOM_AUTH.md` - Auth comparison
- `MODULE_SYSTEM_AND_AUTH_COMPLETE.md` - Auth implementation
- `SCORING_AND_MODULAR_UPDATE.md` - Scoring system
- `COMPLETE_USER_GUIDE.md` - Full system guide

**Test Scripts:**
- `test_auth_system.py` - Verify auth system
- `test_safety_nc_scoring.py` - Test scoring

---

**Date:** November 14, 2025  
**Status:** Ready for configuration  
**Next Step:** Start with Email Configuration (15 minutes)
