# 🚀 ProSite - AWS Free Tier Deployment Guide

## ✅ Perfect for Testing Before Sales

**AWS Free Tier Benefits:**
- ✅ **12 months FREE** (not just $5/month)
- ✅ **750 hours/month EC2** (enough for 1 server running 24/7)
- ✅ **20GB RDS PostgreSQL** database (free for 12 months)
- ✅ **5GB S3 storage** for file uploads
- ✅ **Usage limits & billing alerts** (won't surprise you with charges)
- ✅ **Professional infrastructure** (scalable when ready for sales)
- ✅ **Global reach** (fast worldwide)

**Perfect for:** Testing, demos, pilot customers, MVP validation

---

## 📊 AWS Architecture (Simple & Free)

```
┌─────────────────────────────────────────────────────┐
│                   AWS Free Tier                      │
│                                                      │
│  ┌──────────────┐       ┌──────────────┐           │
│  │   EC2 t2.micro│──────→│ RDS PostgreSQL│          │
│  │   (Backend)   │       │   db.t3.micro │          │
│  │   Flask API   │       │   20GB Free   │          │
│  │   750h/month  │       │   750h/month  │          │
│  └──────────────┘       └──────────────┘           │
│         │                                            │
│         │ uploads                                    │
│         ↓                                            │
│  ┌──────────────┐                                   │
│  │  S3 Bucket   │                                   │
│  │  5GB Free    │                                   │
│  └──────────────┘                                   │
│                                                      │
└─────────────────────────────────────────────────────┘
                    ↑
                    │ API calls
                    │
         ┌──────────────────┐
         │  Vercel (FREE)   │
         │  Next.js Frontend│
         └──────────────────┘
```

**Cost:** $0/month for 12 months (within free tier limits)

---

## 🎯 Step-by-Step AWS Deployment

### PHASE 1: AWS Setup (20 minutes)

#### 1.1 Create AWS Account
1. Go to: https://aws.amazon.com/free/
2. Click **"Create a Free Account"**
3. Enter email, password, account name: `ProSite-Production`
4. Choose **"Personal"** account type
5. Add payment method (won't charge unless you exceed free tier)
6. Verify phone number
7. Select **"Free - Basic Support"**

#### 1.2 Set Up Billing Alerts (IMPORTANT!)
1. Go to: https://console.aws.amazon.com/billing/
2. Click **"Billing preferences"** (left sidebar)
3. Enable:
   - ✅ "Receive Free Tier Usage Alerts"
   - ✅ "Receive Billing Alerts"
4. Enter email: `shrotrio@gmail.com`
5. Save preferences

6. Go to **CloudWatch** (search in AWS console)
7. Click **"Alarms"** → **"Billing"** → **"Create Alarm"**
8. Set threshold: `$5` (will alert if you exceed free tier)
9. Add notification email: `shrotrio@gmail.com`
10. Create alarm

**Now you're protected from unexpected charges!**

---

### PHASE 2: Database Setup (15 minutes)

#### 2.1 Create RDS PostgreSQL Database

1. Go to **RDS** service (search in AWS console)
2. Click **"Create database"**
3. Select:
   - Engine: **PostgreSQL**
   - Version: **15.4** (or latest)
   - Template: **Free tier** ⚠️ (IMPORTANT)
   - DB instance identifier: `prosite-db`
   - Master username: `postgres`
   - Master password: `ProSite2024!Secure` (save this!)
   - DB instance class: **db.t3.micro** (free tier eligible)
   - Storage: **20 GB** (max free tier)
   - Enable storage autoscaling: **No**
   - Public access: **Yes** (needed for now)
   - VPC security group: **Create new** → `prosite-db-sg`
   - Database name: `prosite`

4. Click **"Create database"**
5. Wait 5-10 minutes for database to be available

#### 2.2 Configure Security Group
1. Go to **EC2** → **Security Groups**
2. Find `prosite-db-sg`
3. Click **"Edit inbound rules"**
4. Add rule:
   - Type: **PostgreSQL**
   - Protocol: **TCP**
   - Port: **5432**
   - Source: **0.0.0.0/0** (anywhere - for testing only)
5. Save rules

#### 2.3 Get Database Connection String
1. Go back to **RDS** → **Databases** → `prosite-db`
2. Copy **Endpoint**: something like `prosite-db.xxxxx.us-east-1.rds.amazonaws.com`
3. Your connection string:
```
postgresql://postgres:ProSite2024!Secure@prosite-db.xxxxx.us-east-1.rds.amazonaws.com:5432/prosite
```

---

### PHASE 3: S3 Storage for Uploads (10 minutes)

#### 3.1 Create S3 Bucket
1. Go to **S3** service
2. Click **"Create bucket"**
3. Settings:
   - Bucket name: `prosite-uploads-2025` (must be globally unique)
   - Region: **US East (N. Virginia)** (same as RDS)
   - Block all public access: **Uncheck** (we need public URLs)
   - Acknowledge warning: ✅
   - Bucket versioning: **Disable**
   - Encryption: **Disable** (for simplicity)
4. Create bucket

#### 3.2 Configure CORS
1. Click on your bucket → **Permissions** tab
2. Scroll to **CORS configuration**
3. Click **Edit** and paste:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"]
    }
]
```
4. Save changes

#### 3.3 Make Bucket Public (for uploaded files)
1. Still in **Permissions** tab
2. **Bucket policy** → Edit
3. Paste:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::prosite-uploads-2025/*"
        }
    ]
}
```
4. Save changes

---

### PHASE 4: Backend Deployment on EC2 (30 minutes)

#### 4.1 Launch EC2 Instance
1. Go to **EC2** service
2. Click **"Launch Instance"**
3. Settings:
   - Name: `ProSite-Backend`
   - Application and OS: **Ubuntu Server 22.04 LTS**
   - Instance type: **t2.micro** (free tier eligible)
   - Key pair: **Create new key pair**
     - Name: `prosite-key`
     - Type: **RSA**
     - Format: **.pem** (for SSH)
     - Download and save to safe location
   - Network settings:
     - Auto-assign public IP: **Enable**
     - Create security group: **Yes**
     - Security group name: `prosite-backend-sg`
     - Rules:
       - SSH (22) from **My IP**
       - HTTP (80) from **Anywhere**
       - HTTPS (443) from **Anywhere**
       - Custom TCP (8000) from **Anywhere** (for API)
   - Storage: **8 GB** (free tier)
4. Click **"Launch instance"**
5. Wait 2-3 minutes for instance to start

#### 4.2 Get Instance IP
1. Go to **EC2** → **Instances**
2. Select `ProSite-Backend`
3. Copy **Public IPv4 address**: e.g., `3.235.xxx.xxx`

#### 4.3 Connect to Server
```powershell
# Windows PowerShell
# Navigate to where you saved prosite-key.pem
cd C:\Users\shrot\Downloads

# Set permissions (Windows)
icacls prosite-key.pem /inheritance:r
icacls prosite-key.pem /grant:r "%USERNAME%:R"

# Connect via SSH
ssh -i prosite-key.pem ubuntu@3.235.xxx.xxx
```

#### 4.4 Install Dependencies on Server
```bash
# Once connected to EC2 instance:

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv nginx git postgresql-client

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install

# Verify installations
python3 --version
pip3 --version
aws --version
nginx -v
```

#### 4.5 Clone and Setup Application
```bash
# Clone your repository
cd /home/ubuntu
git clone https://github.com/omi1811/concretethings.git
cd concretethings

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
pip install gunicorn psycopg2-binary boto3

# Create production environment file
nano .env
```

Paste this in `.env`:
```bash
# Database (use your RDS endpoint)
DATABASE_URL=postgresql://postgres:ProSite2024!Secure@prosite-db.xxxxx.us-east-1.rds.amazonaws.com:5432/prosite

# Flask
FLASK_ENV=production
SECRET_KEY=943f85b632acb5769cb6a61e1549e730b9f1d3f8989750dbe1ecfc3b0250a858
JWT_SECRET_KEY=b4f0d0f60582359d66049ecc031424673e85a6b2616136053af0c0a4f5987084

# CORS
CORS_ORIGINS=*

# AWS S3 (for file uploads)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=prosite-uploads-2025

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

#### 4.6 Get AWS Access Keys
1. Go to **IAM** service in AWS console
2. Click **"Users"** → **"Add users"**
3. Username: `prosite-app`
4. Permissions: **Attach policies directly**
   - Select: **AmazonS3FullAccess**
5. Create user
6. Click on user → **Security credentials** tab
7. Click **"Create access key"**
8. Use case: **Application running on AWS compute service**
9. Copy **Access key ID** and **Secret access key**
10. Update `.env` file on EC2 with these keys

#### 4.7 Initialize Database
```bash
# Connect to RDS and run migration
psql "$DATABASE_URL"

# In PostgreSQL prompt:
\i supabase_migration.sql
\q

# Or run Python migration:
python3 -c "
from server.db import init_db
init_db()
print('Database initialized!')
"
```

#### 4.8 Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/prosite.service
```

Paste:
```ini
[Unit]
Description=ProSite Flask API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/concretethings
Environment="PATH=/home/ubuntu/concretethings/venv/bin"
ExecStart=/home/ubuntu/concretethings/venv/bin/gunicorn --config gunicorn.conf.py 'server.app:create_app()'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable prosite
sudo systemctl start prosite

# Check status
sudo systemctl status prosite

# View logs
sudo journalctl -u prosite -f
```

#### 4.9 Configure Nginx
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/prosite
```

Paste:
```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/prosite /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Test
curl http://localhost/health
```

---

### PHASE 5: Frontend Deployment (Vercel - Still FREE)

```powershell
# On your local machine
cd C:\Users\shrot\OneDrive\Desktop\ProSite\concretethings\frontend

# Install Vercel
npm install -g vercel

# Deploy
vercel login
vercel

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter: http://3.235.xxx.xxx (your EC2 IP)

# Production deploy
vercel --prod
```

---

## 🔧 AWS S3 File Upload Integration

You need to modify backend to use S3 instead of local storage:

```python
# server/utils/s3_upload.py (create this file)
import boto3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def upload_to_s3(file, folder='uploads'):
    """Upload file to S3 and return public URL"""
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    key = f"{folder}/{timestamp}_{filename}"
    
    try:
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            key,
            ExtraArgs={'ContentType': file.content_type}
        )
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
        return url
    except Exception as e:
        print(f"S3 upload error: {e}")
        return None

def delete_from_s3(url):
    """Delete file from S3"""
    key = url.split(f'{BUCKET_NAME}.s3.amazonaws.com/')[-1]
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except:
        return False
```

Update your routes to use S3:
```python
# Example: In batch creation
from utils.s3_upload import upload_to_s3

@batches_bp.route('/api/batches', methods=['POST'])
def create_batch():
    # ... existing code ...
    
    if 'photo' in request.files:
        photo = request.files['photo']
        photo_url = upload_to_s3(photo, folder='batches')
        batch.photo_url = photo_url  # Store URL instead of binary data
    
    # ... rest of code ...
```

---

## 💰 AWS Free Tier Limits & Monitoring

### What's Free (12 months):
| Service | Free Tier Allowance | Equivalent |
|---------|---------------------|------------|
| **EC2 t2.micro** | 750 hours/month | 1 server 24/7 |
| **RDS db.t3.micro** | 750 hours/month | 1 database 24/7 |
| **RDS Storage** | 20 GB | Plenty for testing |
| **S3 Storage** | 5 GB | ~5,000 images |
| **S3 Requests** | 20,000 GET, 2,000 PUT | ~600 uploads/day |
| **Data Transfer** | 15 GB/month | ~500 users/month |

### Monthly Cost Estimate:
- **Months 1-12:** $0 (free tier)
- **After 12 months:** ~$15-25/month
  - EC2: $8.50/month
  - RDS: $12/month
  - S3: $0.50/month
  - Data transfer: $2/month

### Setting Up Cost Alerts:
1. AWS Console → **Billing** → **Budgets**
2. **Create budget** → **Cost budget**
3. Name: `ProSite-Monthly-Limit`
4. Amount: `$5`
5. Alert threshold: `100%` of budget
6. Email: `shrotrio@gmail.com`
7. Create budget

---

## 📱 Flutter App Compatibility Assessment

### Current Status: ❌ NOT COMPATIBLE - Need Major Updates

#### What Exists:
- ✅ `pubspec.yaml` with dependencies
- ✅ `README.md` documentation
- ❌ **ZERO Dart code** (only proposed structure)
- ❌ No API integration
- ❌ No screens
- ❌ No database

#### What's Needed for Flutter App:

### 1. **API Compatibility** ⚠️ Partially Ready

**Current Backend APIs:**
- ✅ Authentication (JWT) - Compatible
- ✅ Batch management - Compatible
- ✅ Cube tests - Compatible
- ⚠️ File uploads - Need S3 URLs (will fix above)
- ⚠️ Offline sync - Need versioning/timestamps

**Required Changes:**
```python
# Add timestamps to all models for sync
class Batch(Base):
    # ... existing fields ...
    synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)

# Add sync endpoint
@app.route('/api/sync/batches', methods=['POST'])
def sync_batches():
    """
    Accept offline data from mobile app
    Handle conflicts using timestamps
    """
    # Implementation needed
```

### 2. **Mobile-Specific Features** ❌ NOT IMPLEMENTED

**Need to Add:**
- [ ] Device registration endpoint
- [ ] Push notification tokens
- [ ] Batch sync with conflict resolution
- [ ] Incremental data sync (don't re-download everything)
- [ ] Image compression endpoint (mobile uploads large files)
- [ ] QR code generation for batches
- [ ] Offline-first data structure

**Estimated Backend Work:** 2-3 days

### 3. **Flutter App Development** ❌ NOT STARTED

**Required Work:**

#### Week 1: Foundation (40 hours)
- [ ] Create actual Flutter project structure
- [ ] Setup navigation and routing
- [ ] Implement authentication screens
- [ ] API service layer with Dio
- [ ] Local SQLite database with sqflite
- [ ] State management with Provider
- **Deliverable:** Can login and see empty dashboard

#### Week 2: Core Features (40 hours)
- [ ] Dashboard with KPIs
- [ ] Batch list and entry screens
- [ ] Camera integration for batch photos
- [ ] Cube test entry forms
- [ ] Material vehicle register
- **Deliverable:** Can create batches and tests

#### Week 3: Offline & Polish (40 hours)
- [ ] Offline data storage
- [ ] Background sync service
- [ ] Conflict resolution
- [ ] Push notifications setup
- [ ] Error handling and validation
- **Deliverable:** Works offline, syncs when online

#### Week 4: Testing & Deployment (40 hours)
- [ ] Unit tests
- [ ] Integration tests
- [ ] UI/UX polish
- [ ] Performance optimization
- [ ] Android APK build
- [ ] iOS build (if you have Mac)
- [ ] Play Store/App Store submission
- **Deliverable:** Published apps

**Total Effort:** 160 hours = 4 weeks full-time or 2-3 months part-time

### 4. **Backend Readiness for Mobile** 📊

| Feature | Status | Mobile Compatible | Action Needed |
|---------|--------|-------------------|---------------|
| Authentication | ✅ Working | ✅ Yes | None |
| JWT Tokens | ✅ Working | ✅ Yes | None |
| CRUD APIs | ✅ Working | ✅ Yes | None |
| File Uploads | ⚠️ Local | ❌ No | Migrate to S3 |
| Offline Sync | ❌ Missing | ❌ No | Add sync endpoints |
| Push Notifications | ❌ Missing | ❌ No | Add FCM integration |
| Image Compression | ❌ Missing | ❌ No | Add compression |
| Versioning | ❌ Missing | ❌ No | Add to all models |
| Pagination | ⚠️ Partial | ⚠️ Limited | Add to all lists |
| Search/Filter | ⚠️ Partial | ⚠️ Limited | Add mobile-optimized |

**Backend Mobile Readiness:** 40% (needs 2-3 days work)

### 5. **Realistic Mobile App Timeline**

**If starting TODAY with Flutter developer:**

```
Phase 1: Backend Updates (2-3 days)
├── Day 1: S3 migration, sync endpoints
├── Day 2: Versioning, conflict resolution
└── Day 3: Testing, documentation

Phase 2: Flutter Core (2-3 weeks)
├── Week 1: Authentication, navigation, API layer
├── Week 2: Main features (batches, tests, safety)
└── Week 3: Offline sync, camera, QR codes

Phase 3: Polish & Deploy (1 week)
├── Days 1-3: Testing, bug fixes
├── Days 4-5: Play Store submission
└── Days 6-7: App Store submission (if iOS needed)

Total: 4-5 weeks with dedicated Flutter developer
```

**Without Flutter developer:** 8-12 weeks (learning + building)

---

## ✅ Deployment Readiness Summary

### Web Application: ✅ READY FOR AWS
- Backend code: Ready
- Frontend code: Ready
- Database migrations: Ready
- Just needs deployment (1 day)

### Mobile Application: ❌ NOT READY
- Backend APIs: 60% ready (need sync features)
- Flutter app: 0% ready (only documentation)
- Estimated time: 4-5 weeks minimum

---

## 🎯 Recommended Approach

### Phase 1: Deploy Web App on AWS (This Week)
**Day 1:** Setup AWS (RDS, S3, EC2) - Follow guide above
**Day 2:** Deploy backend, configure S3 uploads
**Day 3:** Deploy frontend, end-to-end testing
**Day 4:** Add demo data, prepare for user testing
**Day 5:** User testing, bug fixes

**Outcome:** Live web application on AWS free tier

### Phase 2: User Testing (2-4 weeks)
- Get 5-10 pilot users
- Collect feedback
- Fix bugs and issues
- Validate product-market fit

### Phase 3: Mobile App (If Users Request It)
**Only build mobile app if:**
- ✅ Users specifically ask for it
- ✅ Web app is stable and working
- ✅ You have budget for Flutter developer
- ✅ Users willing to wait 4-5 weeks

**Most users can use mobile browser for now!**

---

## 📞 Next Steps

### Immediate (Today):
1. ✅ Create AWS account
2. ✅ Set up billing alerts
3. ✅ Create RDS database
4. ✅ Create S3 bucket

### Tomorrow:
1. ✅ Launch EC2 instance
2. ✅ Deploy backend
3. ✅ Migrate to S3 uploads

### This Week:
1. ✅ Deploy frontend to Vercel
2. ✅ End-to-end testing
3. ✅ Add demo data

### Next Month:
1. User testing and feedback
2. Bug fixes and improvements
3. **Decide if mobile app is needed**

---

## 💡 Pro Tips

1. **Start with web app only** - Don't build mobile until users ask for it
2. **Use billing alerts** - AWS free tier is generous, but set alerts anyway
3. **Monitor usage** - Check AWS CloudWatch for usage metrics
4. **Backup database** - Enable RDS automatic backups
5. **Version control** - Push code to GitHub before deploying
6. **Document everything** - Keep track of AWS configurations

---

**Ready to start? Begin with AWS account creation and follow Phase 1 above!**

**Estimated time to live web app:** 1-2 days active work

**Mobile app:** Only if truly needed (4-5 weeks additional work)
