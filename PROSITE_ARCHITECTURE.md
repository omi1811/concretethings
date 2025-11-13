# ProSite - Modular Architecture

## Platform Overview

**ProSite** is a multi-module platform for professional site management across construction, safety, and quality domains. The platform provides a flexible framework where users can create and configure their own workflows, forms, and processes.

### Design Philosophy (Inspired by DigiQC)

ProSite follows DigiQC's successful approach:
- **Platform provides the framework**, not rigid workflows
- **Users create their own content** (forms, checklists, permits)
- **Highly configurable** - adapts to different industries and site conditions
- **Microservices architecture** - each module operates independently

---

## 🏗️ Available Modules

### 1. ConcreteThings (Quality Management System)

**Purpose:** Complete concrete quality management for construction projects

**Features:**
- Mix design management
- Batch tracking & cube testing
- Third-party lab integration
- Material vehicle register
- Pour activity tracking
- NCR (Non-Conformance Reports)
- Automated test reminders
- WhatsApp & Email notifications

**Use Cases:**
- Civil construction sites
- RMC (Ready-Mix Concrete) plants
- Infrastructure projects
- Commercial buildings

**API Prefix:** `/api/*` (existing endpoints)

---

### 2. SiteSafety (User-Configurable Safety Platform)

**Purpose:** Flexible safety management system that adapts to any site/industry

**Core Capabilities:**

#### ✅ Form Builder System (DigiQC-style)
- **User-created templates** for any safety form type:
  - Safety checklists
  - Incident reports
  - Permit-to-work
  - Audits & inspections
  - Risk assessments
  - Near-miss observations
  
- **Flexible field types:**
  - Text, number, date, time
  - Single/multiple choice
  - Photos/videos
  - Signatures
  - GPS location
  - Custom scoring

- **Version control:** Templates can be updated with version tracking

#### ✅ Workforce Management
- Worker registration with QR/NFC
- Attendance tracking (check-in/check-out)
- PPE verification (with photo)
- Training & certification tracking
- Contractor-wise grouping

#### ✅ Digital Permits
- User-defined permit types (hot work, confined space, working at height, etc.)
- Multi-level approvals
- Digital signatures
- Validity timers
- Risk assessment attachments

#### ✅ Actions & Follow-ups
- Action items from any submission
- SLA tracking & escalation
- Assigned responsibilities
- Completion verification

#### ✅ Analytics
- Submission trends
- Contractor scorecards
- Compliance tracking
- Overdue actions

**API Prefix:** `/api/safety/*`

**Key Endpoints:**
```
# Module Configuration
GET  /api/safety/modules
POST /api/safety/modules

# Form Templates (User-Created)
GET  /api/safety/templates
POST /api/safety/templates
PUT  /api/safety/templates/:id

# Form Submissions
GET  /api/safety/submissions
POST /api/safety/submissions
GET  /api/safety/submissions/:id

# Workers
GET  /api/safety/workers
POST /api/safety/workers

# Attendance
POST /api/safety/attendance/check-in

# Actions
GET  /api/safety/actions
POST /api/safety/actions
PUT  /api/safety/actions/:id/complete

# Analytics
GET  /api/safety/analytics/summary
```

---

## 📐 Architecture

### Database Design

#### ConcreteThings Tables (Existing)
- companies, users, projects
- material_categories, rmc_vendors, mix_designs
- batch_registers, cube_test_registers
- material_vehicle_register
- pour_activities
- training_records

#### SiteSafety Tables (New)
- **safety_modules** - Module configuration per company/project
- **safety_form_templates** - User-created form templates with version control
- **safety_form_submissions** - Actual form data submitted
- **safety_workers** - Worker database
- **safety_worker_attendance** - Daily attendance logs
- **safety_actions** - Actions arising from submissions

### Microservices Structure

```
server/
├── app.py                    # Main Flask app
├── models.py                 # ConcreteThings models
├── safety_models.py          # SiteSafety models
├── safety.py                 # SiteSafety API
├── auth.py                   # Shared authentication
├── batches.py                # ConcreteThings - Batches
├── cube_tests.py             # ConcreteThings - Testing
├── material_vehicle_register.py
├── notifications.py          # Shared notifications
└── ...
```

---

## 🚀 Getting Started

### Enable Safety Module for Your Company

1. **Create a Safety Module:**
```bash
POST /api/safety/modules
{
  "module_type": "checklist",
  "module_name": "Daily Safety Inspections",
  "description": "Morning safety checks before work starts",
  "icon": "clipboard-check"
}
```

2. **Create a Form Template:**
```bash
POST /api/safety/templates
{
  "module_id": 1,
  "template_name": "Excavation Safety Checklist",
  "category": "Civil Safety",
  "form_fields": [
    {
      "type": "text",
      "label": "Site Location",
      "required": true
    },
    {
      "type": "choice",
      "label": "Barricading in place?",
      "options": ["Yes", "No", "N/A"],
      "required": true
    },
    {
      "type": "photo",
      "label": "Site Photo",
      "required": true
    },
    {
      "type": "signature",
      "label": "Inspector Signature",
      "required": true
    }
  ],
  "has_scoring": true,
  "scoring_config": {
    "max_score": 100,
    "scoring_fields": ["field_1", "field_2"]
  }
}
```

3. **Submit a Form:**
```bash
POST /api/safety/submissions
{
  "project_id": 1,
  "template_id": 1,
  "form_data": {
    "site_location": "Block A - Level 3",
    "barricading": "Yes",
    "site_photo": "https://cdn.example.com/photo123.jpg",
    "inspector_signature": "data:image/png;base64,..."
  },
  "geo_location": {
    "lat": 12.9716,
    "lon": 77.5946
  },
  "priority": "high"
}
```

---

## 🎯 Use Cases

### Civil Construction Site
- **Modules:** Checklists, Incidents, Permits, Audits
- **Templates:**  
  - Daily safety inspection
  - Excavation permit
  - Scaffolding checklist
  - PPE compliance audit

### Port & Dock Operations
- **Modules:** Checklists, Observations, Training
- **Templates:**
  - Vessel arrival checklist
  - Lifting operation permit
  - Dockside handling inspection
  - Confined space entry

### Mechanical Plant
- **Modules:** Permits, Audits, Maintenance
- **Templates:**
  - Hot work permit
  - Equipment isolation
  - Safety valve inspection
  - Emergency drill checklist

### Electrical Installation
- **Modules:** Permits, Testing, Certification
- **Templates:**
  - Electrical isolation permit
  - Circuit testing checklist
  - LOTO (Lockout-Tagout) verification
  - Energization approval

---

## 🔐 Access Control

### Module-Level Permissions
- **Company Admin:** Can create/modify modules and templates
- **Project Admin:** Can create templates for their projects
- **Supervisor:** Can submit forms and manage workers
- **Worker:** Can view assigned checklists and submit

---

## 📊 Analytics & Reporting

### Safety Dashboard
- Total submissions by module
- Pending approvals
- Overdue actions
- Contractor compliance scorecard
- Incident trends
- Training completion rates

### ConcreteThings Dashboard
- Batch acceptance rate
- Cube test results
- NCR trends
- Material consumption
- Testing compliance

---

## 🔄 Migration Path

### From ConcreteThings to ProSite
1. **Database:** All existing ConcreteThings data remains intact
2. **APIs:** All existing endpoints continue to work
3. **New Feature:** Safety module is additive, not replacement
4. **Users:** Existing users get access to both modules

### Adding Safety Module
```sql
-- Safety tables are created alongside existing tables
-- No migration of ConcreteThings data required
```

---

## 🌐 Deployment

### Environment Variables
```bash
# Existing
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
SECRET_KEY=...

# Safety Module (Optional)
ENABLE_SAFETY_MODULE=true
```

### Database Migration
```bash
# Create safety tables
python3 -c "from server.db import init_db; from server.safety_models import *; init_db()"
```

---

## 📱 Mobile App Considerations

### Offline-First Design
- Form templates cached locally
- Submit when online
- Photo/video queued for upload
- Worker QR codes work offline

### Progressive Web App (PWA)
- Install on home screen
- Camera access for PPE verification
- GPS for geo-tagging
- Push notifications for actions

---

## 🛣️ Roadmap

### Phase 1 (Current)
- ✅ ConcreteThings (complete)
- ✅ SiteSafety (framework ready)

### Phase 2 (Future)
- Environmental monitoring
- Equipment management
- Inventory & stores
- Financial tracking

### Phase 3
- AI-based PPE detection
- Predictive safety analytics
- IoT sensor integration
- BIM integration

---

## 🤝 Contributing

This platform is designed to be extensible. New modules can be added following the same pattern:

1. Create `{module}_models.py` with SQLAlchemy models
2. Create `{module}.py` with Flask blueprint
3. Register blueprint in `app.py`
4. Add documentation to this README

---

## 📞 Support

- **ConcreteThings Issues:** Existing QMS workflows
- **SiteSafety Issues:** Form builder, workers, permits
- **Platform Issues:** Authentication, database, deployment

---

**ProSite** - Professional Site Management Platform
Built for flexibility, configured for your needs.
