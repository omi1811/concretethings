# Multi-App Subscription Model

## Overview

ProSite supports **modular app subscriptions** allowing companies to choose which applications they need:

- **Safety App Only**: Safety management features
- **Concrete App Only**: QMS/concrete quality features
- **Both Apps**: Complete system with cross-app integration features

## Subscription Types

### 1. Safety-Only Subscription

**Companies get access to:**
- Safety Observations
- Safety Workers Register
- Non-Conformance (NC) Management
- Permit-to-Work (PTW)
- Toolbox Talks (TBT) with QR Attendance
- Safety Actions
- Safety Dashboard & Reports

**Hidden features:**
- Mix Designs
- Batches
- Cube Tests
- Pour Activities
- Material Management
- Quality Training

**Example Company:**
```json
{
  "name": "ABC Safety Consultants",
  "subscribed_apps": ["safety"]
}
```

---

### 2. Concrete-Only Subscription

**Companies get access to:**
- Mix Designs
- Batch Management
- Cube Testing (In-house & Third-party)
- Pour Activities
- Material & Vehicle Register
- Quality Training Records
- Quality Dashboard & Reports

**Hidden features:**
- Safety Observations
- Safety Workers
- Non-Conformance Management
- Permit-to-Work
- Toolbox Talks

**Example Company:**
```json
{
  "name": "XYZ Concrete Lab",
  "subscribed_apps": ["concrete"]
}
```

---

### 3. Both Apps (Complete System)

**Companies get access to:**
- **All Safety features** (from Safety app)
- **All Concrete features** (from Concrete app)
- **Cross-app integration features**:
  - **Quality Training with Worker QR Attendance** ✨ (NEW!)
  - Integrated dashboards
  - Cross-app reports
  - Worker certifications
  - Unified worker database

**Example Company:**
```json
{
  "name": "Main Construction Co.",
  "subscribed_apps": ["safety", "concrete"]
}
```

---

## Database Schema

### Company Model Update

```python
class Company(Base):
    __tablename__ = "companies"
    
    id: int
    name: str
    
    # Multi-App Subscription (NEW!)
    subscribed_apps: str  # JSON array: ["safety"], ["concrete"], or ["safety", "concrete"]
    
    # Pricing
    subscription_plan: str  # trial, basic, pro, enterprise
    active_projects_limit: int
    price_per_project: float
    
    def has_app(self, app_name: str) -> bool:
        """Check if company subscribed to specific app"""
        apps = json.loads(self.subscribed_apps)
        return app_name in apps
    
    def has_both_apps(self) -> bool:
        """Check if company has both apps"""
        apps = json.loads(self.subscribed_apps)
        return "safety" in apps and "concrete" in apps
```

---

## API Access Control

### Middleware Decorators

#### 1. `@require_app('safety')`
Restricts endpoint to users whose company has Safety app.

```python
@app.route('/api/safety/observations', methods=['GET'])
@require_app('safety')
def list_observations():
    # Only accessible if company has ["safety"] or ["safety", "concrete"]
    ...
```

#### 2. `@require_app('concrete')`
Restricts endpoint to users whose company has Concrete app.

```python
@app.route('/api/batches', methods=['GET'])
@require_app('concrete')
def list_batches():
    # Only accessible if company has ["concrete"] or ["safety", "concrete"]
    ...
```

#### 3. `@require_both_apps()`
Restricts endpoint to users whose company has BOTH apps.

```python
@app.route('/api/training/<int:training_id>/scan-worker', methods=['POST'])
@require_both_apps()
def scan_worker_for_training(training_id):
    # Only accessible if company has ["safety", "concrete"]
    # Cross-app feature: Quality training with safety workers QR attendance
    ...
```

---

## Cross-App Feature: Quality Training with QR Attendance

### **Only available when company has BOTH apps!**

This feature bridges Safety and Concrete apps:

1. **Trainer** (from Concrete app) creates quality training session
2. **Workers** (from Safety app) are registered with QR codes (helmet stickers)
3. **Trainer scans worker QR codes** to mark attendance
4. **System tracks** attendance, assessments, and certifications

### Database Schema

```python
class TrainingAttendance(Base):
    """Cross-app table linking TrainingRecord (Concrete) + Worker (Safety)"""
    __tablename__ = "training_attendances"
    
    id: int
    training_record_id: int  # FK to training_records (Concrete app)
    worker_id: int          # FK to safety_workers (Safety app)
    worker_code: str        # W12345
    worker_name: str
    worker_company: str
    worker_trade: str
    
    check_in_method: str    # 'qr' or 'manual'
    check_in_time: datetime
    qr_code_scanned: str    # WORKER-W12345
    device_info: str
    
    # Assessment (optional)
    assessment_score: float  # 0-100
    passed_assessment: bool
    certificate_issued: bool
    certificate_number: str  # CERT-{training_id}-{attendance_id}-{date}
```

### API Endpoints (Cross-App)

All require `@require_both_apps()`:

```
POST   /api/training/<training_id>/scan-worker
       Trainer scans worker QR (helmet sticker) to mark attendance

POST   /api/training/<training_id>/attendance-manual
       Manual attendance fallback

GET    /api/training/<training_id>/attendance
       Get all attendees for training session

POST   /api/training/<training_id>/assessment
       Record worker assessment score

GET    /api/training/reports/worker-certifications
       Get worker certification report
```

### Workflow Example

**Scenario**: Main Construction Co. has BOTH apps subscribed.

1. **Quality Engineer** creates training:
   ```
   POST /api/training-register
   {
     "training_topic": "Mix Design Procedures",
     "building": "Block A",
     "activity": "Concreting",
     "trainer_id": 5
   }
   ```

2. **Trainer** starts QR attendance:
   ```
   POST /api/training/123/scan-worker
   {
     "worker_code": "W12345"
   }
   ```

3. **System** looks up worker from Safety app:
   ```
   Worker W12345:
     Name: Mohammed Ali
     Company: ABC Contractors
     Trade: Mason
   ```

4. **System** creates attendance record:
   ```json
   {
     "training_record_id": 123,
     "worker_id": 456,
     "worker_code": "W12345",
     "worker_name": "Mohammed Ali",
     "check_in_method": "qr",
     "check_in_time": "2025-11-13T08:15:30"
   }
   ```

5. **After training**, trainer records assessment:
   ```
   POST /api/training/123/assessment
   {
     "attendance_id": 789,
     "score": 92.5,
     "passed": true,
     "issue_certificate": true
   }
   ```

6. **System** issues certificate:
   ```
   Certificate: CERT-123-789-20251113
   Worker: Mohammed Ali (W12345)
   Training: Mix Design Procedures
   Score: 92.5/100
   Date: 13-Nov-2025
   ```

---

## Frontend Implementation

### 1. Login Response

When user logs in, API returns subscribed apps:

```json
{
  "user": {...},
  "company": {
    "id": 1,
    "name": "Main Construction Co.",
    "subscribedApps": ["safety", "concrete"]
  },
  "token": "..."
}
```

### 2. Get App Access

```
GET /api/user/app-access
Authorization: Bearer {token}
```

**Response:**
```json
{
  "subscribedApps": ["safety", "concrete"],
  "hasSafety": true,
  "hasConcrete": true,
  "hasBoth": true,
  "availableFeatures": {
    "safety": [
      "safety_observations",
      "safety_workers",
      "safety_nc",
      "permit_to_work",
      "toolbox_talks"
    ],
    "concrete": [
      "mix_designs",
      "batches",
      "cube_tests",
      "pour_activities",
      "material_vehicle_register",
      "quality_training"
    ],
    "crossApp": [
      "training_qr_attendance",
      "integrated_dashboards",
      "cross_app_reports"
    ]
  }
}
```

### 3. Menu Filtering (Frontend Logic)

```typescript
// React/Next.js example
const menuItems = [
  { 
    label: "Safety", 
    icon: "shield",
    requiredApp: "safety",
    children: [
      { label: "Observations", path: "/safety/observations" },
      { label: "Workers", path: "/safety/workers" },
      { label: "Non-Conformance", path: "/safety/nc" },
      { label: "Permit-to-Work", path: "/safety/ptw" },
      { label: "Toolbox Talks", path: "/safety/tbt" }
    ]
  },
  { 
    label: "Concrete", 
    icon: "cube",
    requiredApp: "concrete",
    children: [
      { label: "Mix Designs", path: "/concrete/mix-designs" },
      { label: "Batches", path: "/concrete/batches" },
      { label: "Cube Tests", path: "/concrete/cube-tests" },
      { label: "Pour Activities", path: "/concrete/pour" },
      { label: "Training", path: "/concrete/training" }
    ]
  },
  { 
    label: "Training QR Attendance", 
    icon: "qrcode",
    requiredApps: ["safety", "concrete"],  // Requires BOTH!
    path: "/training-qr"
  }
];

// Filter menu based on subscribed apps
const filteredMenu = menuItems.filter(item => {
  if (item.requiredApps) {
    // Requires multiple apps
    return item.requiredApps.every(app => subscribedApps.includes(app));
  } else if (item.requiredApp) {
    // Requires single app
    return subscribedApps.includes(item.requiredApp);
  }
  return true;  // No requirement
});
```

---

## Migration Guide

### For Existing Companies

**Default behavior**: All existing companies get BOTH apps automatically.

```sql
-- Migration script
UPDATE companies 
SET subscribed_apps = '["safety", "concrete"]'
WHERE subscribed_apps IS NULL;
```

### For New Companies

Support admin sets subscriptions during company creation:

```
POST /api/support/companies
{
  "name": "New Company Ltd.",
  "subscribed_apps": ["safety"],  // Safety-only
  "subscription_plan": "basic",
  "active_projects_limit": 1
}
```

### Changing Subscriptions

Support admin can update subscriptions:

```
PUT /api/support/companies/123
{
  "subscribed_apps": ["safety", "concrete"]  // Upgrade to both
}
```

---

## Pricing Model Examples

### Option 1: Separate Pricing

- **Safety App**: ₹3,000/month per project
- **Concrete App**: ₹4,000/month per project
- **Both Apps**: ₹6,000/month per project (bundle discount)

### Option 2: Module-based

- **Base Price**: ₹2,000/month per project
- **Safety Module**: +₹2,000/month
- **Concrete Module**: +₹3,000/month
- **Cross-App Features**: +₹1,000/month (only with both modules)

### Option 3: Tiered

- **Basic (Safety-only)**: ₹3,000/month, 1 project
- **Standard (Concrete-only)**: ₹4,000/month, 1 project
- **Professional (Both)**: ₹6,000/month, 2 projects
- **Enterprise (Both + Multi-project)**: ₹25,000/month, 10 projects

---

## Access Denied Response

When user tries to access feature not in their subscription:

```json
{
  "error": "Access denied. Your company has not subscribed to the concrete app.",
  "subscribedApps": ["safety"],
  "requiredApps": ["concrete"]
}
```

**Frontend should:**
1. Hide menu items not in subscription
2. Redirect to subscription upgrade page if accessed via URL
3. Show "Upgrade to unlock this feature" message

---

## Testing Scenarios

### Test Case 1: Safety-Only Company

```
Company: ABC Safety
Subscribed Apps: ["safety"]

✅ Can access: /api/safety/observations
✅ Can access: /api/safety/tbt/sessions
❌ Cannot access: /api/batches (403 error)
❌ Cannot access: /api/training/123/scan-worker (403 error - requires both)
```

### Test Case 2: Concrete-Only Company

```
Company: XYZ Concrete Lab
Subscribed Apps: ["concrete"]

✅ Can access: /api/batches
✅ Can access: /api/cube-tests
❌ Cannot access: /api/safety/nc (403 error)
❌ Cannot access: /api/training/123/scan-worker (403 error - requires both)
```

### Test Case 3: Both Apps Company

```
Company: Main Construction
Subscribed Apps: ["safety", "concrete"]

✅ Can access: /api/safety/observations
✅ Can access: /api/batches
✅ Can access: /api/training/123/scan-worker (cross-app feature)
✅ Can access: ALL features
```

---

## Summary

| Feature | Safety-Only | Concrete-Only | Both Apps |
|---------|-------------|---------------|-----------|
| Safety Observations | ✅ | ❌ | ✅ |
| Safety Workers | ✅ | ❌ | ✅ |
| Non-Conformance | ✅ | ❌ | ✅ |
| Permit-to-Work | ✅ | ❌ | ✅ |
| Toolbox Talks | ✅ | ❌ | ✅ |
| Mix Designs | ❌ | ✅ | ✅ |
| Batches | ❌ | ✅ | ✅ |
| Cube Tests | ❌ | ✅ | ✅ |
| Pour Activities | ❌ | ✅ | ✅ |
| Quality Training | ❌ | ✅ | ✅ |
| **Training QR Attendance** | ❌ | ❌ | **✅ Only!** |
| Integrated Dashboards | ❌ | ❌ | ✅ |
| Cross-App Reports | ❌ | ❌ | ✅ |
