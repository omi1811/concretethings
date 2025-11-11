# 🎯 DigiQC-Style User Management & SaaS Pricing Model

## 📋 Table of Contents
1. [SaaS Pricing Model](#saas-pricing-model)
2. [User Hierarchy (DigiQC-Style)](#user-hierarchy-digiqc-style)
3. [Support Admin Dashboard](#support-admin-dashboard)
4. [Company Admin Capabilities](#company-admin-capabilities)
5. [Project-Level Permissions](#project-level-permissions)
6. [Database Schema](#database-schema)
7. [Free Tier Deployment (Supabase + Render)](#free-tier-deployment)

---

## 💰 SaaS Pricing Model

### **Business Model: Per-Project Subscription**

**Pricing Structure:**
- ₹5,000/month per active project
- Unlimited users within a project
- You control project limits for each company

### **Example Scenarios:**

#### **Scenario 1: Small Construction Company**
```
Company: ABC Builders
Subscription: Starter Plan
Active Projects: 1
Cost: ₹5,000/month
Limit set by you: 1 project
```

#### **Scenario 2: Medium Company**
```
Company: XYZ Construction
Subscription: Professional Plan
Active Projects: 5
Cost: ₹25,000/month (5 × ₹5,000)
Limit set by you: 5 projects
```

#### **Scenario 3: Enterprise**
```
Company: PQR Infrastructure
Subscription: Enterprise Plan
Active Projects: 20
Cost: ₹100,000/month (20 × ₹5,000)
Limit set by you: 20 projects
Special: Custom pricing, ₹4,500/project
```

### **What You Control (Support Admin):**

```javascript
{
  company: "ABC Builders",
  activeProjectsLimit: 1,        // ← YOU set this
  pricePerProject: 5000,          // ← YOU set this
  billingStatus: "active",        // ← YOU control this
  subscriptionPlan: "starter"     // ← YOU assign this
}
```

**Key Controls:**
- ✅ Set project limit (1, 3, 5, 10, 20, unlimited)
- ✅ Custom pricing per company (bulk discounts)
- ✅ Suspend account (if payment fails)
- ✅ Activate/deactivate companies
- ✅ View all companies' usage and billing

---

## 👥 User Hierarchy (DigiQC-Style)

### **5-Level Hierarchy:**

```
Level 1: Support Admin (YOU)
    ↓ Manages all companies
    
Level 2: Company Admin
    ↓ Creates and manages projects (within limit)
    
Level 3: Project Admin
    ↓ Manages project team and approves data
    
Level 4: Project Members (various roles)
    ↓ Quality Engineers, Site Engineers, etc.
    
Level 5: View-Only Users
    ↓ RMC vendors, auditors, clients
```

---

### **Level 1: Support Admin (YOU)** 🔑

**Role:** `is_support_admin = 1`

**Powers:**
- ✅ Access `/support` dashboard (your exclusive portal)
- ✅ View all companies globally
- ✅ Create new companies
- ✅ Set project limits per company
- ✅ Set custom pricing
- ✅ Suspend/activate companies
- ✅ Assign Company Admins
- ✅ View global analytics:
  - Total companies: 47
  - Total active projects: 184
  - Monthly revenue: ₹920,000
  - Top customers by revenue
  - Project growth trends
- ✅ Access all data (read-only) for support
- ✅ Generate invoices
- ✅ Manage subscriptions

**Use Cases:**
- Customer onboarding: "ABC Builders wants 3 projects"
- Billing management: Set limit, track payments
- Customer support: Access their data to troubleshoot
- Business analytics: Which companies are growing?

**Example Dashboard:**
```
╔══════════════════════════════════════════════╗
║       SUPPORT ADMIN DASHBOARD                ║
╠══════════════════════════════════════════════╣
║  Total Companies: 47                         ║
║  Active Projects: 184                        ║
║  Monthly Revenue: ₹920,000                   ║
║  New Signups (This Month): 5                 ║
║  Pending Payments: 2                         ║
╠══════════════════════════════════════════════╣
║  Recent Activity:                            ║
║  ✅ ABC Builders - Payment received ₹15,000  ║
║  ⚠️  XYZ Corp - Payment overdue             ║
║  🆕 PQR Infra - New signup (trial)          ║
╚══════════════════════════════════════════════╝
```

---

### **Level 2: Company Admin** 🏢

**Role:** `is_company_admin = 1`

**Powers:**
- ✅ Create projects (up to their limit)
- ✅ View project limit and usage:
  ```
  Your Plan: Professional
  Active Projects: 3 / 5 (2 remaining)
  Cost: ₹15,000/month
  ```
- ✅ Assign Project Admins
- ✅ View all company projects
- ✅ Company-wide reports
- ✅ Manage RMC vendor list
- ✅ Invite users to company
- ❌ Cannot exceed project limit
- ❌ Cannot change billing (contact support)
- ❌ Cannot see other companies

**Workflow:**
```
1. Company Admin logs in
2. Sees: "3 of 5 projects active"
3. Clicks "New Project"
4. If within limit: ✅ Project created
5. If at limit: ❌ "Upgrade plan to create more projects"
6. Contact support button shown
```

**Example View:**
```
╔══════════════════════════════════════════════╗
║  ABC Builders - Company Dashboard            ║
╠══════════════════════════════════════════════╣
║  Subscription: Professional                  ║
║  Active Projects: 3 / 5                      ║
║  💰 ₹15,000/month                            ║
║  Next Billing: Dec 1, 2025                   ║
╠══════════════════════════════════════════════╣
║  Projects:                                   ║
║  1. Skyline Tower [Active] 👥 12 users       ║
║  2. Metro Bridge [Active] 👥 8 users         ║
║  3. Mall Project [Active] 👥 15 users        ║
║                                              ║
║  [+ Create New Project] ← 2 slots available ║
╚══════════════════════════════════════════════╝
```

---

### **Level 3: Project Admin** 📊

**Role:** `ProjectMembership.role = "ProjectAdmin"`

**Powers:**
- ✅ Full control over their project
- ✅ Invite/remove team members
- ✅ Assign roles to members
- ✅ Approve all batches
- ✅ Approve all test results
- ✅ Generate reports
- ✅ Export data
- ✅ Project settings
- ❌ Cannot create new projects
- ❌ Cannot see other projects (unless assigned)

**Use Cases:**
- Project Manager of "Skyline Tower"
- Responsible for quality on that project
- Reviews and approves all QC data

---

### **Level 4: Project Members** 👷

**Roles (DigiQC-style):**

#### **4a. Quality Manager**
**Role:** `role = "QualityManager"`

**Permissions:**
```javascript
{
  canCreateBatch: true,
  canEditBatch: true,
  canDeleteBatch: false,
  canApproveBatch: true,        // ← Can approve
  canCreateTest: true,
  canEditTest: true,
  canApproveTest: true,         // ← Can approve
  canManageTeam: false,
  canGenerateReports: true,
  canExportData: true
}
```

**Use Case:** Senior QC engineer, verifies test results

---

#### **4b. Quality Engineer**
**Role:** `role = "QualityEngineer"`

**Permissions:**
```javascript
{
  canCreateBatch: true,
  canEditBatch: true,
  canDeleteBatch: false,
  canApproveBatch: false,       // ← Cannot approve
  canCreateTest: true,
  canEditTest: true,
  canApproveTest: false,        // ← Cannot approve
  canManageTeam: false,
  canGenerateReports: true,
  canExportData: false
}
```

**Use Case:** Field engineer, performs tests daily

---

#### **4c. Site Engineer**
**Role:** `role = "SiteEngineer"`

**Permissions:**
```javascript
{
  canCreateBatch: true,         // ← Can enter batch info
  canEditBatch: true,
  canDeleteBatch: false,
  canApproveBatch: false,
  canCreateTest: false,         // ← Cannot perform tests
  canEditTest: false,
  canApproveTest: false,
  canManageTeam: false,
  canGenerateReports: true,
  canExportData: false
}
```

**Use Case:** Records concrete deliveries only

---

#### **4d. Data Entry**
**Role:** `role = "DataEntry"`

**Permissions:**
```javascript
{
  canCreateBatch: true,
  canEditBatch: true,
  canDeleteBatch: false,
  canApproveBatch: false,
  canCreateTest: false,
  canEditTest: false,
  canApproveTest: false,
  canManageTeam: false,
  canGenerateReports: false,
  canExportData: false
}
```

**Use Case:** Office staff, basic data entry only

---

### **Level 5: View-Only Users** 👀

#### **5a. Viewer**
**Role:** `role = "Viewer"`

**Permissions:** All false (read-only)

**Use Cases:**
- Client representatives
- Consultants
- Audit teams
- Management review

---

#### **5b. RMC Vendor**
**Role:** `role = "RMCVendor"`

**Permissions:** Can only view their own batches

**Use Case:**
- Vendor logs in
- Sees only batches from their company
- Can check test results
- Cannot see other vendors' data

---

## 🎛️ Support Admin Dashboard

### **URL:** `/support` (protected route)

**Authentication Check:**
```javascript
if (!user.isSupportAdmin) {
  return <Redirect to="/dashboard" />
}
```

### **Dashboard Sections:**

#### **1. Overview Tab**
```
┌─────────────────────────────────────────────┐
│  📊 Business Metrics                        │
├─────────────────────────────────────────────┤
│  Total Companies: 47                        │
│  Active Companies: 45                       │
│  Suspended: 2                               │
│                                             │
│  Total Projects: 184                        │
│  Active Projects: 178                       │
│  Completed: 6                               │
│                                             │
│  💰 Monthly Revenue: ₹920,000               │
│  Average per Company: ₹19,574               │
│  Projected Annual: ₹11,040,000              │
└─────────────────────────────────────────────┘
```

#### **2. Companies Tab**
```
┌────────────────────────────────────────────────────────────┐
│  [+ Create Company]  [Search companies...]  [Filter ▾]     │
├────────────────────────────────────────────────────────────┤
│  Company Name       │ Projects │ Plan    │ Status │ Actions│
├────────────────────────────────────────────────────────────┤
│  ABC Builders       │ 5/5      │ Pro     │ ✅     │ ⚙️ 👁️  │
│  XYZ Construction   │ 3/3      │ Basic   │ ✅     │ ⚙️ 👁️  │
│  PQR Infrastructure │ 20/20    │ Ent     │ ✅     │ ⚙️ 👁️  │
│  LMN Developers     │ 1/1      │ Trial   │ ⚠️     │ ⚙️ 👁️  │
│  RST Builders       │ 0/5      │ Suspend │ ❌     │ ⚙️ 👁️  │
└────────────────────────────────────────────────────────────┘
```

**Actions:**
- ⚙️ **Settings:** Edit limits, pricing, status
- 👁️ **View:** See company dashboard
- 🔔 **Notify:** Send email/WhatsApp
- 💰 **Invoice:** Generate billing invoice

#### **3. Company Settings Modal**

When you click ⚙️ Settings:

```
╔═══════════════════════════════════════════════╗
║  Edit Company: ABC Builders                   ║
╠═══════════════════════════════════════════════╣
║  Company Name: [ABC Builders            ]     ║
║  Email: [contact@abcbuilders.com       ]     ║
║  Phone: [+91 9876543210                ]     ║
║  GSTIN: [27AABCU9603R1ZM               ]     ║
║                                               ║
║  Subscription Plan:                           ║
║  ◉ Trial (1 project, 30 days free)           ║
║  ○ Starter (1 project)                        ║
║  ○ Professional (3-5 projects)                ║
║  ○ Enterprise (10+ projects)                  ║
║  ○ Custom                                     ║
║                                               ║
║  Active Projects Limit: [5  ]                 ║
║  Price Per Project: [₹5000  ]                 ║
║  Total Monthly: ₹25,000                       ║
║                                               ║
║  Billing Status:                              ║
║  ◉ Active                                     ║
║  ○ Suspended (payment overdue)                ║
║  ○ Cancelled                                  ║
║                                               ║
║  Subscription Dates:                          ║
║  Start: [01-Nov-2025]  End: [01-Nov-2026]    ║
║  Next Billing: [01-Dec-2025]                  ║
║                                               ║
║  [Save Changes]  [Cancel]                     ║
╚═══════════════════════════════════════════════╝
```

#### **4. Analytics Tab**

**Charts:**
- Revenue trend (last 12 months)
- New signups vs churn
- Project count growth
- Top 10 customers by revenue
- Plan distribution (pie chart)

**Reports:**
- Monthly revenue report (PDF)
- Company list with billing details (Excel)
- Payment collection report
- Overdue accounts list

---

## 🏢 Company Admin Capabilities

### **What Company Admin Sees:**

**Dashboard URL:** `/dashboard/company-settings`

```
╔═══════════════════════════════════════════════╗
║  ABC Builders - Company Settings              ║
╠═══════════════════════════════════════════════╣
║  📊 Current Subscription                      ║
║  Plan: Professional                           ║
║  Active Projects: 3 / 5                       ║
║  Monthly Cost: ₹15,000                        ║
║  Next Billing: Dec 1, 2025                    ║
║  Payment Method: ████ ████ ████ 1234         ║
║                                               ║
║  [Upgrade Plan]  [Payment History]            ║
╠═══════════════════════════════════════════════╣
║  📁 Your Projects                             ║
║                                               ║
║  1. ✅ Skyline Tower (Active)                 ║
║     Created: Jan 15, 2025                     ║
║     Team: 12 members                          ║
║     [Manage] [View] [Archive]                 ║
║                                               ║
║  2. ✅ Metro Bridge (Active)                  ║
║     Created: Feb 10, 2025                     ║
║     Team: 8 members                           ║
║     [Manage] [View] [Archive]                 ║
║                                               ║
║  3. ✅ Mall Project (Active)                  ║
║     Created: Mar 5, 2025                      ║
║     Team: 15 members                          ║
║     [Manage] [View] [Archive]                 ║
║                                               ║
║  💡 2 project slots available                 ║
║  [+ Create New Project]                       ║
╠═══════════════════════════════════════════════╣
║  👥 Company Users                             ║
║                                               ║
║  [+ Invite User]  [Manage Roles]              ║
║                                               ║
║  John Doe (director@abc.com)                  ║
║  └─ Role: Company Admin                       ║
║  └─ Projects: All (3)                         ║
║                                               ║
║  Ravi Kumar (ravi@abc.com)                    ║
║  └─ Role: Quality Manager                     ║
║  └─ Projects: Skyline Tower, Metro Bridge    ║
║                                               ║
║  Priya Sharma (priya@abc.com)                 ║
║  └─ Role: Quality Engineer                    ║
║  └─ Project: Mall Project                     ║
╚═══════════════════════════════════════════════╝
```

### **Creating a New Project (Company Admin):**

**Step 1:** Click "Create New Project"

**Step 2:** Check limit
```javascript
if (company.activeProjects >= company.activeProjectsLimit) {
  showError("You've reached your project limit (3/3)");
  showUpgradeButton("Contact support to increase limit");
  return;
}
```

**Step 3:** Fill project details
```
Project Name: Industrial Warehouse
Location: Pune, Maharashtra
Client: XYZ Logistics
Start Date: Nov 15, 2025
End Date: May 15, 2026
Project Code: AUTO-GENERATED or MANUAL
```

**Step 4:** Assign Project Admin
```
Search and select user:
→ Amit Patel (amit@abc.com)
   Role: Project Admin
```

**Step 5:** Success!
```
✅ Project Created!
Active Projects: 4 / 5
Your monthly bill will increase to ₹20,000
Next billing date: Dec 1, 2025
```

---

## 🗄️ Database Schema

### **Enhanced Tables:**

```sql
-- Companies table with SaaS pricing
CREATE TABLE companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL UNIQUE,
  
  -- SaaS Pricing
  subscription_plan VARCHAR(50) DEFAULT 'trial',
  active_projects_limit INTEGER DEFAULT 1,
  price_per_project FLOAT DEFAULT 5000.0,
  
  -- Billing
  billing_status VARCHAR(50) DEFAULT 'active',
  subscription_start_date DATETIME,
  subscription_end_date DATETIME,
  last_payment_date DATETIME,
  next_billing_date DATETIME,
  
  -- Company details
  company_email VARCHAR(255),
  company_phone VARCHAR(20),
  company_address TEXT,
  gstin VARCHAR(20),
  
  is_active INTEGER DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Users with support admin role
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(20) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  
  company_id INTEGER REFERENCES companies(id),
  
  -- Roles
  is_support_admin INTEGER DEFAULT 0,  -- YOU
  is_company_admin INTEGER DEFAULT 0,
  is_system_admin INTEGER DEFAULT 0,   -- Deprecated
  
  designation VARCHAR(100),
  profile_photo VARCHAR(500),
  
  is_active INTEGER DEFAULT 1,
  is_email_verified INTEGER DEFAULT 0,
  is_phone_verified INTEGER DEFAULT 0,
  failed_login_attempts INTEGER DEFAULT 0,
  account_locked_until DATETIME,
  
  last_login DATETIME,
  last_activity DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by INTEGER REFERENCES users(id)
);

-- Projects with detailed info
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  
  name VARCHAR(255) NOT NULL,
  project_code VARCHAR(50) UNIQUE,
  description TEXT,
  location VARCHAR(255),
  client_name VARCHAR(255),
  
  start_date DATETIME,
  end_date DATETIME,
  actual_end_date DATETIME,
  
  status VARCHAR(50) DEFAULT 'active',
  is_active INTEGER DEFAULT 1,
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by INTEGER REFERENCES users(id)
);

-- Project memberships with granular permissions
CREATE TABLE project_memberships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  
  role VARCHAR(64) DEFAULT 'Viewer',
  
  -- Batch permissions
  can_create_batch INTEGER DEFAULT 1,
  can_edit_batch INTEGER DEFAULT 1,
  can_delete_batch INTEGER DEFAULT 0,
  can_approve_batch INTEGER DEFAULT 0,
  
  -- Test permissions
  can_create_test INTEGER DEFAULT 1,
  can_edit_test INTEGER DEFAULT 1,
  can_delete_test INTEGER DEFAULT 0,
  can_approve_test INTEGER DEFAULT 0,
  
  -- Admin permissions
  can_manage_team INTEGER DEFAULT 0,
  can_generate_reports INTEGER DEFAULT 1,
  can_export_data INTEGER DEFAULT 0,
  can_manage_settings INTEGER DEFAULT 0,
  
  is_active INTEGER DEFAULT 1,
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  added_by INTEGER REFERENCES users(id)
);
```

---

## 🆓 Free Tier Deployment (Supabase + Render/Netlify)

### **Architecture for Testing:**

```
Frontend (Next.js) → Netlify Free Tier
    ↓
Backend (Flask API) → Render Free Tier
    ↓
Database (PostgreSQL) → Supabase Free Tier
    ↓
File Storage → Supabase Storage Free Tier
```

### **Cost: $0/month for testing!** 🎉

---

### **Step 1: Supabase Setup (Database + Storage)**

**1. Create Supabase Project:**
```
1. Go to supabase.com
2. Sign up (GitHub account)
3. Create new project:
   Name: concretethings-qms
   Region: Mumbai (closest to you)
   Password: (generate strong password)
4. Wait 2 minutes for setup
```

**2. Get Database Connection:**
```
Dashboard → Settings → Database
Copy:
- Connection string (URI mode)
- Host: db.xxx.supabase.co
- Port: 5432
- Database: postgres
- User: postgres
- Password: your_password
```

**3. Run Migrations:**
```bash
# On your local machine
export DATABASE_URL="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
python migrate_db.py
```

**4. Set Up Storage for Photos:**
```
Dashboard → Storage → Create bucket
Bucket name: project-photos
Public: Yes (for now, restrict later)
```

**Free Tier Limits:**
- 500 MB database
- 1 GB storage
- 2 GB bandwidth
- Enough for 100+ projects in testing!

---

### **Step 2: Render Setup (Backend API)**

**1. Create Render Account:**
```
1. Go to render.com
2. Sign up with GitHub
3. Connect your repository: omi1811/concretethings
```

**2. Create Web Service:**
```
Dashboard → New → Web Service
Repository: concretethings
Name: concretethings-api
Region: Singapore (closest to India)
Branch: main
Root Directory: /
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn server.app:app
```

**3. Environment Variables:**
```
DATABASE_URL = postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
SECRET_KEY = (generate random 32-char string)
JWT_SECRET_KEY = (generate random 32-char string)
FLASK_ENV = production
SUPABASE_URL = https://xxx.supabase.co
SUPABASE_KEY = your_anon_key
```

**4. Free Tier Limits:**
- 750 hours/month (31 days × 24 hours)
- 512 MB RAM
- Sleeps after 15 min inactivity (cold starts)
- Perfect for testing!

**Your API URL:**
```
https://concretethings-api.onrender.com
```

---

### **Step 3: Netlify Setup (Frontend)**

**1. Create Netlify Account:**
```
1. Go to netlify.com
2. Sign up with GitHub
3. Import repository
```

**2. Build Settings:**
```
Repository: omi1811/concretethings
Base directory: frontend
Build command: npm run build
Publish directory: frontend/.next
```

**3. Environment Variables:**
```
NEXT_PUBLIC_API_URL = https://concretethings-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL = https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = your_anon_key
```

**4. Deploy:**
```
Click "Deploy site"
Wait 2-3 minutes
Your site: https://concretethings-qms.netlify.app
```

**5. Custom Domain (Optional):**
```
Domain Settings → Add custom domain
Example: qms.concretethings.com
Add DNS records (Netlify provides instructions)
SSL: Automatic (Let's Encrypt)
```

**Free Tier Limits:**
- 100 GB bandwidth/month
- 300 build minutes/month
- Unlimited sites
- Perfect for production too!

---

### **Step 4: Set Yourself as Support Admin**

**Method 1: Direct Database (Recommended for first time)**

```sql
-- Connect to Supabase SQL Editor
-- Dashboard → SQL Editor → New query

-- Find your user (after you register via UI)
SELECT id, email, full_name FROM users WHERE email = 'your@email.com';

-- Make yourself Support Admin
UPDATE users 
SET is_support_admin = 1,
    is_company_admin = 0,
    is_system_admin = 0
WHERE email = 'your@email.com';

-- Verify
SELECT id, email, is_support_admin FROM users WHERE id = 1;
```

**Method 2: Seed Script**

Create `seed_support_admin.py`:
```python
from server.models import User
from server.db import session_scope
from werkzeug.security import generate_password_hash

with session_scope() as session:
    # Create support admin
    support_admin = User(
        email="your@email.com",
        phone="+919876543210",
        full_name="Your Name",
        password_hash=generate_password_hash("YourStrongPassword123!"),
        is_support_admin=1,
        is_company_admin=0,
        is_active=1,
        designation="Support Admin"
    )
    session.add(support_admin)
    print("✅ Support admin created!")
```

Run:
```bash
python seed_support_admin.py
```

---

### **Step 5: Test the System**

**1. Access Frontend:**
```
https://concretethings-qms.netlify.app
```

**2. Login as Support Admin:**
```
Email: your@email.com
Password: YourStrongPassword123!
```

**3. You should see:**
```
✅ Login successful
✅ Redirects to /support (your exclusive dashboard)
✅ Shows "Support Admin Dashboard"
✅ You can create companies, set limits
```

**4. Create Test Company:**
```
Support Dashboard → Companies → Create
Name: Test Company ABC
Projects Limit: 1
Price: ₹5,000
Plan: Trial
```

**5. Invite Company Admin:**
```
Users → Invite
Email: companytest@test.com
Role: Company Admin
Company: Test Company ABC
```

**6. Login as Company Admin:**
```
Email: companytest@test.com
Password: (set during registration)
```

**7. Create Project:**
```
Projects → New Project
Name: Test Tower
Check: "1 of 1 projects"
Success: ✅ Project created
```

**8. Test Project Limit:**
```
Try creating 2nd project
Error: "You've reached your project limit (1/1)"
Shows: "Contact support to upgrade"
```

---

## 🎯 Summary

### **What You Get:**

1. **SaaS Pricing Model:**
   - ₹5,000/month per project
   - You control limits per company
   - Automatic billing tracking

2. **DigiQC-Style Roles:**
   - Support Admin (YOU) - Global control
   - Company Admin - Project creation within limit
   - Project Admin - Team management
   - Quality Engineers, Site Engineers, etc.
   - Granular permissions

3. **Free Testing Deployment:**
   - Supabase: Free PostgreSQL + Storage
   - Render: Free API hosting
   - Netlify: Free frontend hosting
   - Total: $0/month

4. **Production Ready:**
   - Enhanced database models
   - Contact Us modal (no more demo button)
   - Project limit enforcement
   - Billing status tracking

---

## 📝 Next Steps

**Immediate (This Week):**
1. Deploy to free tier (4-6 hours)
2. Set yourself as Support Admin
3. Test company creation
4. Test project limits
5. Invite test users

**Short Term (Next 2 Weeks):**
1. Build Support Admin UI (`/support` dashboard)
2. Build Company Admin UI (project management)
3. Build Project Admin UI (team management)
4. Implement permission checks in API
5. Add billing/invoice generation

**Long Term (Month 2-3):**
1. Payment gateway integration (Razorpay)
2. Automated billing emails
3. Usage analytics
4. Mobile app (if needed)
5. Custom domains per company (white-label)

---

**Ready to deploy? Let me create the deployment scripts!** 🚀
