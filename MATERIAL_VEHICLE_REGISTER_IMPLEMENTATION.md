# Material Vehicle Register & Role-Based Workflow Implementation

## Overview

Complete implementation of role-based access control with Material Vehicle Register for watchmen, bulk concrete entry workflow for quality engineers, and automated notifications for time limits and test reminders.

**Implementation Date:** November 12, 2025  
**Status:** ✅ Backend Complete - Ready for Frontend & Testing

---

## Business Requirements

### Two Company Types

**Company Type C1 (Material Add-on Enabled):**
- Watchman/security logs all material vehicles
- P1 person (Watchman) enters vehicle details, photos (MTC, vehicle)
- System checks vehicle time on site vs allowed limit
- Warnings sent to quality engineers if time exceeded
- Quality Jr. Engineer bulk adds concrete data linking to vehicles
- Cube testing workflow starts after bulk entry

**Company Type C2 (Standard Workflow):**
- Work starts directly from bulk entry by engineer
- No material vehicle register needed
- Direct concrete batch entry
- Standard cube testing workflow

### Automated Notifications

1. **Vehicle Time Limit Warnings**
   - Check vehicles every 15-30 minutes
   - Send warning to quality engineers if vehicle exceeds allowed time (default: 3 hours)
   - Configurable per project

2. **Daily Test Reminders**
   - Check pending cube tests daily (default: 9:00 AM)
   - Send reminders to quality engineers and/or project admins
   - Configurable recipients and time

3. **Missed Test Warnings**
   - Check daily (default: 6:00 PM) for tests not performed on scheduled date
   - Send warnings to project admins
   - Track compliance

---

## Database Models

### 1. Material Vehicle Register

**Table:** `material_vehicle_register`

```python
class MaterialVehicleRegister(Base):
    # Vehicle Entry Details
    vehicle_number: str              # Required
    vehicle_type: str               # RMC Truck, TMT Truck, etc.
    
    # Material Details
    material_type: str              # Concrete, Steel, Cement, Sand
    supplier_name: str
    challan_number: str
    
    # Driver Details
    driver_name: str
    driver_phone: str
    driver_license: str
    
    # Entry/Exit Times
    entry_time: datetime            # Required
    exit_time: datetime            # Optional (until vehicle exits)
    duration_hours: float          # Calculated
    
    # Time Limit Tracking
    allowed_time_hours: float      # From project settings
    exceeded_time_limit: bool      # Auto-set if exceeded
    time_warning_sent: bool
    time_warning_sent_at: datetime
    
    # Photos (JSON array)
    photos: str  # [{"type": "MTC", "url": "...", "uploadedBy": 123}, ...]
    
    # Status
    status: str  # on_site, exited
    purpose: str
    remarks: str
    
    # Linkage to RMC Batch
    linked_batch_id: int           # Links to BatchRegister
    is_linked_to_batch: bool
    
    # Metadata
    created_by: int                # Watchman user
    project_id: int
```

**Key Features:**
- Photos stored as JSON array with type, URL, uploaded user
- Automatic time limit calculation
- Warning flag and timestamp
- Link to concrete batch after quality engineer bulk entry

### 2. Project Settings

**Table:** `project_settings`

```python
class ProjectSettings(Base):
    project_id: int  # One settings record per project
    
    # Material Vehicle Register Settings
    enable_material_vehicle_addon: bool  # C1 vs C2 company
    vehicle_allowed_time_hours: float    # Default: 3.0
    send_time_warnings: bool            # Default: True
    
    # Notification Settings
    enable_test_reminders: bool         # Default: True
    reminder_time: str                  # HH:MM format, default "09:00"
    notify_project_admins: bool
    notify_quality_engineers: bool
    
    # Channels
    enable_whatsapp_notifications: bool
    enable_email_notifications: bool
```

**Configuration Options:**
- Enable/disable material vehicle addon per project
- Set allowed vehicle time limit
- Configure notification recipients and timing
- Toggle notification channels

### 3. Updated ProjectMembership

**New Role Added:** `Watchman`

```python
# Roles:
# - ProjectAdmin: Full project control
# - QualityManager: Verify tests, approve results
# - QualityEngineer: Perform tests, enter data
# - SiteEngineer: View data, enter batch info
# - DataEntry: Basic data entry only
# - Watchman: Material vehicle register ONLY (restricted access)
# - Viewer: Read-only access
# - RMCVendor: View own batches only
```

**Watchman Permissions:**
- Can ONLY access Material Vehicle Register
- Cannot see batches, tests, reports, or other features
- Can add/edit vehicle entries
- Can upload photos (MTC, vehicle, challan)
- Can mark vehicle exit

---

## API Endpoints

### Material Vehicle Register (`/api/material-vehicles`)

#### 1. Create Vehicle Entry
```
POST /api/material-vehicles/create
Authorization: Bearer {token}

Body:
{
  "projectId": 1,
  "vehicleNumber": "MH-01-1234",
  "vehicleType": "RMC Truck",
  "materialType": "Concrete",
  "supplierName": "ABC Concrete",
  "challanNumber": "CH-2025-001",
  "driverName": "John Doe",
  "driverPhone": "+919876543210",
  "driverLicense": "MH1234567890",
  "entryTime": "2025-11-12T10:30:00Z",
  "purpose": "Slab casting delivery",
  "remarks": "Vehicle arrived on time"
}

Response: 201 Created
{
  "success": true,
  "message": "Vehicle entry created successfully",
  "vehicleEntry": { ...vehicle entry object... }
}
```

#### 2. List Vehicle Entries
```
GET /api/material-vehicles/list?projectId=1&status=on_site&dateFrom=2025-11-12
Authorization: Bearer {token}

Query Params:
- projectId (required)
- status (optional): on_site, exited
- materialType (optional)
- dateFrom, dateTo (optional)
- exceededOnly (optional): true/false
- page, perPage (optional)

Response: 200 OK
{
  "success": true,
  "vehicleEntries": [ ...array of entries... ],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "total": 150,
    "pages": 3
  }
}
```

#### 3. Get Vehicle Entry Details
```
GET /api/material-vehicles/{entry_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "vehicleEntry": { ...vehicle entry details... }
}
```

#### 4. Update Vehicle Entry
```
PUT /api/material-vehicles/{entry_id}/update
Authorization: Bearer {token}

Body:
{
  "exitTime": "2025-11-12T14:30:00Z",
  "photos": [
    {"type": "MTC", "url": "/uploads/vehicle_photos/mtc_123.jpg"},
    {"type": "vehicle", "url": "/uploads/vehicle_photos/truck_456.jpg"}
  ],
  "remarks": "Vehicle exited after unloading"
}

Response: 200 OK
{
  "success": true,
  "message": "Vehicle entry updated successfully",
  "vehicleEntry": { ...updated entry... }
}
```

#### 5. Mark Vehicle Exit
```
POST /api/material-vehicles/{entry_id}/mark-exit
Authorization: Bearer {token}

Body:
{
  "exitTime": "2025-11-12T14:30:00Z"  # Optional, defaults to now
}

Response: 200 OK
{
  "success": true,
  "message": "Vehicle MH-01-1234 marked as exited",
  "vehicleEntry": { ...entry with exit time and duration... }
}
```

#### 6. Upload Photo
```
POST /api/material-vehicles/upload-photo
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- photo: (file)
- entryId: 123
- photoType: "MTC" | "vehicle" | "challan" | "general"

Response: 201 Created
{
  "success": true,
  "message": "Photo uploaded successfully",
  "photo": {
    "type": "MTC",
    "url": "/uploads/vehicle_photos/vehicle_123_MTC_20251112_103045_mtc.jpg",
    "filename": "vehicle_123_MTC_20251112_103045_mtc.jpg"
  }
}
```

#### 7. Check Time Limits (Background Job)
```
POST /api/material-vehicles/check-time-limits
Authorization: Bearer {token}

Body:
{
  "projectId": 1
}

Response: 200 OK
{
  "success": true,
  "message": "Sent warnings for 3 vehicle(s)",
  "count": 3,
  "vehicles": [ ...exceeded vehicles... ]
}
```

#### 8. Link Vehicle to Batch
```
POST /api/material-vehicles/link-to-batch
Authorization: Bearer {token}

Body:
{
  "vehicleEntryId": 123,
  "batchId": 456
}

Response: 200 OK
{
  "success": true,
  "message": "Vehicle MH-01-1234 linked to batch BATCH-2025-0045",
  "vehicleEntry": { ...linked entry... }
}
```

#### 9. Get Statistics
```
GET /api/material-vehicles/stats?projectId=1
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "stats": {
    "totalEntries": 150,
    "onSite": 8,
    "exited": 142,
    "exceededTimeLimit": 5,
    "linkedToBatches": 120,
    "todayEntries": 12
  }
}
```

---

### Project Settings (`/api/project-settings`)

#### 1. Get Project Settings
```
GET /api/project-settings/{project_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "settings": {
    "id": 1,
    "projectId": 1,
    "enableMaterialVehicleAddon": true,
    "vehicleAllowedTimeHours": 3.0,
    "sendTimeWarnings": true,
    "enableTestReminders": true,
    "reminderTime": "09:00",
    "notifyProjectAdmins": true,
    "notifyQualityEngineers": true,
    "enableWhatsappNotifications": false,
    "enableEmailNotifications": true,
    "createdAt": "2025-11-12T00:00:00Z",
    "updatedAt": "2025-11-12T10:00:00Z"
  }
}
```

#### 2. Update Project Settings (ProjectAdmin only)
```
PUT /api/project-settings/{project_id}/update
Authorization: Bearer {token}

Body:
{
  "enableMaterialVehicleAddon": true,
  "vehicleAllowedTimeHours": 4.0,
  "sendTimeWarnings": true,
  "enableTestReminders": true,
  "reminderTime": "08:30",
  "notifyProjectAdmins": true,
  "notifyQualityEngineers": true,
  "enableWhatsappNotifications": true,
  "enableEmailNotifications": true
}

Response: 200 OK
{
  "success": true,
  "message": "Project settings updated successfully",
  "settings": { ...updated settings... }
}
```

#### 3. Get All Settings (for user's projects)
```
GET /api/project-settings/all
Authorization: Bearer {token}

Response: 200 OK
{
  "success": true,
  "settings": [ ...array of settings for all projects user has access to... ]
}
```

---

### Background Jobs (`/api/background-jobs`)

**Note:** These endpoints are for manual triggering. In production, use cron jobs or schedulers.

#### 1. Run Vehicle Time Check
```
POST /api/background-jobs/run-vehicle-check
Authorization: Bearer {token}  # Admin only

Response: 200 OK
{
  "success": true,
  "message": "Vehicle time limit check complete",
  "warningsSent": 5
}
```

#### 2. Run Test Reminders
```
POST /api/background-jobs/run-test-reminders
Authorization: Bearer {token}  # Admin only

Response: 200 OK
{
  "success": true,
  "message": "Test reminder check complete",
  "remindersSent": 12
}
```

#### 3. Run Missed Test Check
```
POST /api/background-jobs/run-missed-test-check
Authorization: Bearer {token}  # Admin only

Response: 200 OK
{
  "success": true,
  "message": "Missed test check complete",
  "warningsSent": 3
}
```

#### 4. Run All Jobs
```
POST /api/background-jobs/run-all
Authorization: Bearer {token}  # Admin only

Response: 200 OK
{
  "success": true,
  "message": "All background jobs complete",
  "results": {
    "time_warnings": 5,
    "test_reminders": 12,
    "missed_tests": 3
  }
}
```

---

## Workflows

### Company Type C1 (Material Add-on) - Complete Workflow

#### Phase 1: Vehicle Entry by Watchman (P1)

1. **Watchman logs in** (role: Watchman)
2. **Sees only Material Vehicle Register** (all other features hidden)
3. **Vehicle arrives at gate** (e.g., MH-01-1234, RMC Truck, ABC Concrete)
4. **Watchman creates entry:**
   - Vehicle number: MH-01-1234
   - Material type: Concrete
   - Supplier: ABC Concrete
   - Driver details: Name, Phone
   - Entry time: Auto-captured (10:30 AM)
   - Purpose: Slab casting delivery
5. **Uploads photos:**
   - MTC (Material Test Certificate)
   - Vehicle photo
   - Challan/bill photo
6. **Entry saved** with status: "on_site"

#### Phase 2: Automatic Time Limit Monitoring

7. **Background job runs every 30 minutes**
8. **Checks all vehicles with status "on_site"**
9. **Project setting: allowed time = 3 hours**
10. **Vehicle MH-01-1234 entered at 10:30 AM**
11. **At 1:45 PM (3h 15min later):**
    - Exceeds 3-hour limit
    - System marks `exceeded_time_limit = True`
    - Sends WhatsApp/Email to all Quality Engineers:
      ```
      ⚠️ VEHICLE TIME LIMIT EXCEEDED
      Vehicle: MH-01-1234
      Material: Concrete
      Supplier: ABC Concrete
      Entry Time: 10:30 AM
      Hours on Site: 3.2 hours
      Allowed: 3.0 hours
      ⏰ Time exceeded by: 0.2 hours
      Please check vehicle status and take necessary action.
      ```

#### Phase 3: Slab Casting (4 vehicles total)

12. **Watchman logs 3 more vehicles:**
    - MH-02-5678 at 11:00 AM
    - MH-03-9012 at 11:30 AM
    - MH-04-3456 at 12:00 PM
13. **All 4 vehicles on site for slab casting**
14. **Concrete delivered and poured**
15. **Quality Jr. Engineer arrives after casting**

#### Phase 4: Bulk Concrete Entry by Quality Engineer

16. **Quality Jr. Engineer logs in** (role: QualityEngineer)
17. **Opens "Bulk Entry" page**
18. **Sees 4 vehicles from Material Register:**
    - MH-01-1234 (on_site)
    - MH-02-5678 (on_site)
    - MH-03-9012 (on_site)
    - MH-04-3456 (on_site)
19. **Selects all 4 vehicles**
20. **Enters single set of concrete details:**
    - Grade: M45FF
    - Total quantity: 4 m³
    - Location: A Building / 5th Slab
    - Slump: 100mm
    - Temperature: 32°C
    - Remarks: Slab casting completed
21. **System creates:**
    - 4 linked batch entries (one per vehicle)
    - Links each batch to respective vehicle entry
    - All batches tagged with same location and pour activity
22. **Batches auto-generated:**
    - BATCH-2025-0045 (MH-01-1234, 1.0m³)
    - BATCH-2025-0046 (MH-02-5678, 1.0m³)
    - BATCH-2025-0047 (MH-03-9012, 1.0m³)
    - BATCH-2025-0048 (MH-04-3456, 1.0m³)

#### Phase 5: Cube Testing Workflow

23. **Quality Engineer opens Cube Casting Modal**
24. **Selects pour activity: POUR-2025-003 (A Building / 5th Slab)**
25. **Sees all 4 linked batches**
26. **Casts cube specimens:**
    - 3 cubes for 7-day test
    - 3 cubes for 28-day test
27. **System creates cube test records:**
    - CUBE-2025-0045 (7-day, scheduled: Nov 19)
    - CUBE-2025-0046 (28-day, scheduled: Dec 10)
28. **System creates test reminders:**
    - Reminder 1: Nov 19, 2025 (7-day)
    - Reminder 2: Dec 10, 2025 (28-day)

#### Phase 6: Daily Test Reminders

29. **Nov 19, 2025 - 9:00 AM (project reminder time):**
    - Background job runs
    - Finds reminder for CUBE-2025-0045 (7-day test)
    - Sends WhatsApp/Email to Quality Engineers:
      ```
      🔔 CUBE TEST REMINDER
      Cube ID: CUBE-2025-0045
      Test Age: 7 days
      Scheduled Date: 2025-11-19
      Batch: BATCH-2025-0045
      Grade: M45FF
      Location: A Building / 5th Slab
      Status: ⏳ PENDING
      ⚠️ Test must be performed today!
      ```

30. **Engineer performs test:**
    - Crushes 3 cubes
    - Records strengths: 35.2, 36.1, 34.8 MPa
    - Average: 35.4 MPa
    - Status: Pass
31. **System marks reminder as completed**

#### Phase 7: Missed Test Warning

32. **If test not performed by end of day:**
    - Background job runs at 6:00 PM
    - Detects reminder not completed
    - Sends warning to Project Admin:
      ```
      ❌ MISSED TESTS WARNING
      Project: A Building Construction
      Date: 2025-11-19
      
      1 test(s) were not performed on scheduled date:
        • Cube CUBE-2025-0045 - 7 days (Due: 2025-11-19)
      
      ⚠️ Please review and take necessary action.
      Delayed testing may affect quality records and compliance.
      ```

33. **Vehicle Exit:**
    - Watchman marks vehicles as exited
    - Calculates duration (e.g., 3.5 hours)
    - Status: exited

---

### Company Type C2 (Standard) - Direct Entry Workflow

1. **Project setting: `enable_material_vehicle_addon = False`**
2. **Quality Engineer logs in**
3. **No Material Vehicle Register visible**
4. **Work starts directly from bulk entry or standard batch form**
5. **Engineer creates batches:**
   - Uses Quick Entry (from previous implementation)
   - Or uses Bulk Import (from Excel)
   - Or uses Full Form
6. **Cube testing workflow same as C1 (Phase 5-7)**

---

## Background Jobs Schedule

### Production Cron Jobs (Linux/Docker)

Add to crontab or use system scheduler:

```bash
# Check vehicle time limits every 30 minutes
*/30 * * * * curl -X POST http://localhost:5000/api/background-jobs/run-vehicle-check -H "Authorization: Bearer {admin_token}"

# Send test reminders daily at 9:00 AM
0 9 * * * curl -X POST http://localhost:5000/api/background-jobs/run-test-reminders -H "Authorization: Bearer {admin_token}"

# Check missed tests daily at 6:00 PM
0 18 * * * curl -X POST http://localhost:5000/api/background-jobs/run-missed-test-check -H "Authorization: Bearer {admin_token}"
```

### Alternative: Python Scheduler

```python
# In production, add to main app or separate worker process
from apscheduler.schedulers.background import BackgroundScheduler
from server.background_jobs import check_vehicle_time_limits, check_pending_tests, check_missed_tests

scheduler = BackgroundScheduler()

# Every 30 minutes
scheduler.add_job(check_vehicle_time_limits, 'interval', minutes=30)

# Daily at 9:00 AM
scheduler.add_job(check_pending_tests, 'cron', hour=9, minute=0)

# Daily at 6:00 PM
scheduler.add_job(check_missed_tests, 'cron', hour=18, minute=0)

scheduler.start()
```

---

## Notification Messages

### 1. Vehicle Time Limit Warning
```
⚠️ *VEHICLE TIME LIMIT EXCEEDED*

Vehicle: MH-01-1234
Material: Concrete
Supplier: ABC Concrete

Entry Time: 2025-11-12 10:30
Hours on Site: 3.2 hours
Allowed: 3.0 hours

⏰ Time exceeded by: 0.2 hours

Please check vehicle status and take necessary action.

- ConcreteThings QMS
```

**Sent to:** Quality Engineers, Quality Managers, Project Admins  
**Channel:** WhatsApp + Email  
**Frequency:** Once per vehicle (when limit first exceeded)

### 2. Daily Test Reminder
```
🔔 *CUBE TEST REMINDER*

Cube ID: CUBE-2025-0045
Test Age: 7 days
Scheduled Date: 2025-11-19

Batch: BATCH-2025-0045
Grade: M45FF
Location: A Building / 5th Slab

Status: ⏳ PENDING
⚠️ Test must be performed today!

Please complete the test and record results in the system.

- ConcreteThings QMS
```

**Sent to:** Quality Engineers, Quality Managers, Project Admins (configurable)  
**Channel:** WhatsApp + Email  
**Frequency:** Once daily at configured time (default 9:00 AM)

### 3. Missed Test Warning
```
❌ *MISSED TESTS WARNING*

Project: A Building Construction
Date: 2025-11-19

3 test(s) were not performed on scheduled date:

  • Cube CUBE-2025-0045 - 7 days (Due: 2025-11-19)
  • Cube CUBE-2025-0046 - 28 days (Due: 2025-11-19)
  • Cube CUBE-2025-0047 - 7 days (Due: 2025-11-19)

⚠️ Please review and take necessary action.
Delayed testing may affect quality records and compliance.

- ConcreteThings QMS
```

**Sent to:** Project Admins only  
**Channel:** WhatsApp + Email  
**Frequency:** Once daily at configured time (default 6:00 PM)

---

## Role-Based Access Control

### Watchman Role

**Can Access:**
- ✅ Material Vehicle Register ONLY
  - Create vehicle entries
  - Update vehicle details
  - Mark vehicle exit
  - Upload photos (MTC, vehicle, challan)
  - View own entries

**Cannot Access:**
- ❌ Batch Register
- ❌ Cube Testing
- ❌ Material Testing
- ❌ Reports
- ❌ Mix Designs
- ❌ Project Settings
- ❌ Team Management
- ❌ Any other feature

**UI Behavior:**
- Login redirects to Material Vehicle Register
- Sidebar shows ONLY "Vehicle Register" menu
- No access to dashboard, batches, tests, etc.
- Simple, focused interface for vehicle logging

### Quality Engineer Role

**Can Access:**
- ✅ Material Vehicle Register (view, link to batches)
- ✅ Batch Register (create, edit via bulk entry)
- ✅ Cube Testing (cast cubes, record results)
- ✅ Material Testing
- ✅ Reports (view, generate)
- ✅ Mix Designs (view)

**Cannot Access:**
- ❌ Project Settings (read-only)
- ❌ Team Management
- ❌ User Management

### Project Admin Role

**Can Access:**
- ✅ ALL features
- ✅ Project Settings (full control)
- ✅ Team Management
- ✅ User assignments
- ✅ All registers and testing
- ✅ Reports and analytics

---

## Files Created/Modified

### Backend Files Created

1. **`server/models.py`** (Modified)
   - Added `MaterialVehicleRegister` model
   - Added `ProjectSettings` model
   - Updated `ProjectMembership` with Watchman role

2. **`server/material_vehicle_register.py`** (NEW - 850+ lines)
   - Complete CRUD API for material vehicle register
   - Photo upload functionality
   - Time limit checking
   - Vehicle-to-batch linking
   - Statistics endpoint
   - Permission checks for Watchman role

3. **`server/project_settings.py`** (NEW - 180 lines)
   - Get/update project settings
   - Admin-only access
   - Settings for all user's projects

4. **`server/background_jobs.py`** (NEW - 450+ lines)
   - `check_vehicle_time_limits()` - Every 30 min
   - `check_pending_tests()` - Daily at reminder time
   - `check_missed_tests()` - Daily evening
   - Manual trigger endpoints for testing
   - Comprehensive logging

5. **`server/notifications.py`** (Modified)
   - Added `send_time_limit_warning()`
   - Added `send_test_reminder()`
   - Added `send_missed_test_warning()`
   - WhatsApp + Email support

6. **`server/app.py`** (Modified)
   - Registered material_vehicle_bp
   - Registered project_settings_bp
   - Registered background_jobs_bp

### Frontend Files Needed (TODO)

1. **Watchman Dashboard**
   - `frontend/app/dashboard/vehicles/page.js` - List view
   - `frontend/app/dashboard/vehicles/new/page.js` - Create entry
   - `frontend/app/dashboard/vehicles/[id]/page.js` - Entry details
   - Restricted layout showing ONLY vehicle register

2. **Bulk Entry Page**
   - `frontend/app/dashboard/batches/bulk-entry/page.js`
   - Select multiple vehicles from material register
   - Single form for concrete details (grade, quantity, location)
   - Creates linked batches for all vehicles

3. **Project Settings Page**
   - `frontend/app/dashboard/settings/page.js`
   - Material addon toggle
   - Time limit configuration
   - Notification settings
   - Test reminder configuration

4. **Role-Based Layout**
   - Update `frontend/components/layout/Sidebar.js`
   - Show/hide menu items based on user role
   - Watchman sees ONLY "Vehicle Register"
   - Engineers see full menu minus settings

---

## Database Migration

```sql
-- Create material_vehicle_register table
CREATE TABLE material_vehicle_register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    vehicle_number VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(100),
    material_type VARCHAR(100) NOT NULL,
    supplier_name VARCHAR(255),
    challan_number VARCHAR(100),
    driver_name VARCHAR(255),
    driver_phone VARCHAR(20),
    driver_license VARCHAR(50),
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    duration_hours FLOAT,
    allowed_time_hours FLOAT,
    exceeded_time_limit INTEGER DEFAULT 0,
    time_warning_sent INTEGER DEFAULT 0,
    time_warning_sent_at DATETIME,
    photos TEXT,
    status VARCHAR(50) DEFAULT 'on_site',
    purpose VARCHAR(255),
    remarks TEXT,
    linked_batch_id INTEGER,
    is_linked_to_batch INTEGER DEFAULT 0,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (linked_batch_id) REFERENCES batch_registers(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Create project_settings table
CREATE TABLE project_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL UNIQUE,
    enable_material_vehicle_addon INTEGER DEFAULT 0,
    vehicle_allowed_time_hours FLOAT DEFAULT 3.0,
    send_time_warnings INTEGER DEFAULT 1,
    enable_test_reminders INTEGER DEFAULT 1,
    reminder_time VARCHAR(10) DEFAULT '09:00',
    notify_project_admins INTEGER DEFAULT 1,
    notify_quality_engineers INTEGER DEFAULT 1,
    enable_whatsapp_notifications INTEGER DEFAULT 0,
    enable_email_notifications INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_material_vehicle_project ON material_vehicle_register(project_id);
CREATE INDEX idx_material_vehicle_status ON material_vehicle_register(status);
CREATE INDEX idx_material_vehicle_entry_time ON material_vehicle_register(entry_time);
CREATE INDEX idx_material_vehicle_exceeded ON material_vehicle_register(exceeded_time_limit);
```

---

## Testing Checklist

### Backend API Tests

- [ ] Create material vehicle entry (Watchman role)
- [ ] Upload photos (MTC, vehicle, challan)
- [ ] List vehicle entries with filters
- [ ] Mark vehicle exit and calculate duration
- [ ] Check time limit warning trigger
- [ ] Link vehicle to batch (Quality Engineer)
- [ ] Get project settings
- [ ] Update project settings (Admin only)
- [ ] Manually trigger vehicle check job
- [ ] Manually trigger test reminder job
- [ ] Manually trigger missed test job
- [ ] Verify Watchman cannot access other endpoints
- [ ] Verify Quality Engineer can access bulk entry

### Workflow Tests

- [ ] **C1 Workflow:**
  1. Watchman creates 4 vehicle entries
  2. Upload photos for each vehicle
  3. Background job detects 1 vehicle exceeded time
  4. Warning sent to Quality Engineers
  5. Quality Engineer bulk adds concrete data
  6. System creates 4 linked batches
  7. Cube testing modal shows all 4 batches
  8. Cast cubes for 7-day and 28-day tests
  9. Test reminders sent on scheduled dates
  10. Perform tests and record results
  11. Verify missed test warning if not completed

- [ ] **C2 Workflow:**
  1. Settings: `enable_material_vehicle_addon = false`
  2. Quality Engineer uses quick entry or import
  3. Creates batches directly
  4. Cube testing workflow proceeds normally
  5. Test reminders work as expected

### Permission Tests

- [ ] Watchman cannot access batches API
- [ ] Watchman cannot access cube tests API
- [ ] Watchman cannot access reports
- [ ] Watchman can only see vehicle register in UI
- [ ] Quality Engineer can access vehicle register (read-only)
- [ ] Quality Engineer can link vehicles to batches
- [ ] Only Project Admin can update settings

### Notification Tests

- [ ] Time limit warning sent via WhatsApp
- [ ] Time limit warning sent via Email
- [ ] Test reminder sent at configured time
- [ ] Missed test warning sent to admins
- [ ] Notification settings respected (enable/disable)
- [ ] Recipient configuration works (admins vs engineers)

---

## Next Steps

### High Priority (This Week)

1. **Create Database Migration Script**
   - Generate Alembic migration for new tables
   - Test migration up/down
   - Update seed.py with sample data

2. **Frontend - Watchman Dashboard**
   - Vehicle register list page
   - Create vehicle entry form
   - Photo upload component
   - Exit marking functionality
   - Restricted sidebar/layout

3. **Frontend - Bulk Entry Page**
   - Select vehicles from material register
   - Single form for concrete details
   - Batch creation with linking
   - Success confirmation

4. **Frontend - Project Settings**
   - Settings page for Project Admins
   - Material addon toggle
   - Time limit configuration
   - Notification settings

5. **Role-Based UI**
   - Update sidebar to hide/show based on role
   - Redirect Watchman to vehicle register
   - Test permission restrictions

### Medium Priority (Next Week)

6. **Background Job Scheduler**
   - Add APScheduler or use cron
   - Configure job timing
   - Monitor job execution
   - Error handling and logging

7. **Notification Enhancement**
   - Email template design
   - WhatsApp template approval (if using Business API)
   - Notification history tracking
   - User notification preferences

8. **Testing & QA**
   - API integration tests
   - Frontend E2E tests
   - Load testing for background jobs
   - Permission boundary tests

9. **Documentation**
   - User guide for Watchman role
   - Admin guide for settings
   - Bulk entry workflow guide
   - API documentation update

### Low Priority (Future)

10. **Analytics & Reports**
    - Vehicle time analytics
    - Material supplier performance
    - Test completion compliance
    - Notification delivery reports

11. **Mobile Optimization**
    - Responsive watchman interface
    - Photo capture from mobile camera
    - Push notifications
    - Offline support

---

## Success Metrics

### Efficiency Gains
- **Watchman data entry:** ~2 minutes per vehicle vs 0 minutes (no entry before)
- **Quality Engineer bulk entry:** ~5 minutes for 4 vehicles vs 20 minutes (individual entry)
- **Time saved:** 75% reduction in concrete data entry time for C1 companies
- **Automation:** 100% automated time limit monitoring and test reminders

### Compliance
- **Time limit compliance:** Track and enforce vehicle time on site
- **Test completion rate:** Monitor and improve with daily reminders
- **Missed test reduction:** Target 90%+ test completion on scheduled date

### User Satisfaction
- ✅ Watchman: Simple, focused interface (only vehicle register)
- ✅ Quality Engineer: Bulk entry reduces repetitive work
- ✅ Project Admin: Automated notifications improve oversight
- ✅ All users: Clear role-based access improves security

---

## Conclusion

✅ **Complete backend implementation for:**
1. Material Vehicle Register with photo upload
2. Role-based access control (Watchman role)
3. Project-specific settings
4. Automated time limit warnings
5. Daily test reminders
6. Missed test warnings to admins
7. Background jobs for monitoring

🔄 **Pending:**
1. Frontend implementation (Watchman dashboard, bulk entry, settings)
2. Database migration script
3. Background job scheduler setup
4. Comprehensive testing

**Status:** Ready for frontend development and testing phase.

---

**Document Version:** 1.0  
**Last Updated:** November 12, 2025  
**Next Review:** After frontend implementation
