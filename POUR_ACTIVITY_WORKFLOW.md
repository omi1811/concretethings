# Pour Activity Workflow - Batch Consolidation Feature

## Overview

**Problem:** When multiple concrete vehicles pour into a single structural element (e.g., 4m³ slab requiring 3+ vehicles), the current system creates separate cube tests for each batch, leading to wasteful testing.

**Solution:** Pour Activity system groups multiple batches into one pouring activity, enabling ONE set of cube tests for the entire pour.

## Use Case Example

### Scenario: Large Slab Pour
- **Location:** Grid A-12, Level 5, North Wing, Tower A
- **Element:** Slab (200mm thick)
- **Concrete Required:** 4.0 m³
- **Concrete Type:** PT (Post-Tensioned)
- **Design Grade:** M40
- **Vehicles Needed:** 3 transit mixers (capacity: 1.5m³ each)

### Workflow

#### 1. Create Pour Activity
```json
POST /api/pour-activities
{
  "projectId": 1,
  "pourDate": "2025-01-15T10:00:00",
  "location": {
    "buildingName": "Tower A",
    "floorLevel": "Level 5",
    "zone": "North Wing",
    "gridReference": "A-12",
    "structuralElementType": "Slab",
    "elementId": "S-A12-L5",
    "description": "Slab at Grid A-12, Level 5"
  },
  "concreteType": "PT",
  "designGrade": "M40",
  "totalQuantityPlanned": 4.0,
  "remarks": "Large slab pour requiring 3 vehicles"
}
```

**Response:**
```json
{
  "message": "Pour activity created successfully",
  "pourActivity": {
    "id": 1,
    "pourId": "POUR-2025-001",
    "status": "in_progress",
    "concreteType": "PT",
    ...
  }
}
```

#### 2. Add First Batch (Vehicle 1)
Site engineer enters batch details when first vehicle arrives:

```json
POST /api/batches
{
  "projectId": 1,
  "pourActivityId": 1,  // Link to pour
  "vehicleNumber": "MH-01-1234",
  "quantityReceived": 1.5,
  "deliveryDate": "2025-01-15T10:15:00",
  ...
}
```

#### 3. Add Second Batch (Vehicle 2)
```json
POST /api/batches
{
  "projectId": 1,
  "pourActivityId": 1,  // Same pour
  "vehicleNumber": "MH-01-5678",
  "quantityReceived": 1.5,
  "deliveryDate": "2025-01-15T10:45:00",
  ...
}
```

#### 4. Add Third Batch (Vehicle 3)
```json
POST /api/batches
{
  "projectId": 1,
  "pourActivityId": 1,  // Same pour
  "vehicleNumber": "MH-01-9012",
  "quantityReceived": 1.0,
  "deliveryDate": "2025-01-15T11:15:00",
  ...
}
```

#### 5. Complete Pour
Once all concrete is placed and pour is complete:

```json
POST /api/pour-activities/1/complete
{
  "remarks": "Pour completed successfully, all 3 vehicles delivered"
}
```

**Response:**
```json
{
  "message": "Pour activity completed successfully",
  "pourActivity": {
    "id": 1,
    "pourId": "POUR-2025-001",
    "status": "completed",
    "totalQuantityReceived": 4.0,
    "batches": [
      { "id": 101, "vehicleNumber": "MH-01-1234", "quantityReceived": 1.5 },
      { "id": 102, "vehicleNumber": "MH-01-5678", "quantityReceived": 1.5 },
      { "id": 103, "vehicleNumber": "MH-01-9012", "quantityReceived": 1.0 }
    ]
  },
  "showCubeModal": true,
  "concreteType": "PT",
  "testAges": [5, 7, 28, 56]  // PT concrete: 5 days instead of 3
}
```

#### 6. Create Cube Tests
Frontend shows cube casting modal with:
- **Pour Details:** POUR-2025-001, Grid A-12, 4.0 m³
- **Batches:** 3 vehicles linked
- **Concrete Type:** PT (Post-Tensioned)
- **Test Ages:** 5, 7, 28, 56 days (5 instead of 3 for PT)
- **Recommended:** 7-day and 28-day tests

Engineer creates cube tests:
```json
POST /api/cube-tests/cast
{
  "pourActivityId": 1,  // Links to pour (which links to all batches)
  "projectId": 1,
  "castingDate": "2025-01-15T11:30:00",
  "concreteType": "PT",
  "testSets": [
    { "testAgeDays": 7, "numberOfCubes": 3 },
    { "testAgeDays": 28, "numberOfCubes": 3 }
  ],
  ...
}
```

**Result:** 6 cubes total (2 sets × 3 cubes) linked to pour activity

## PT Concrete Testing Logic

### Normal Concrete
- **Test Ages:** 3, 7, 28, 56 days
- **Standard Schedule:** 3-day and 28-day tests
- **Use Case:** Regular RCC construction

### PT (Post-Tensioned) Concrete
- **Test Ages:** 5, 7, 28, 56 days (5 instead of 3)
- **Reason:** PT concrete is stressed at 5 days, so strength must be verified at 5 days minimum
- **Standard Schedule:** 7-day and 28-day tests
- **Use Case:** Post-tensioned slabs, special structures

### Database Implementation
```python
# In CubeTestRegister model
concrete_type: Mapped[str] = mapped_column(String(20), default="Normal")

# API logic
if pour_activity.concrete_type == "PT":
    available_ages = [5, 7, 28, 56]  # 5 instead of 3
    recommended_ages = [7, 28]
else:
    available_ages = [3, 7, 28, 56]
    recommended_ages = [3, 28]
```

## API Endpoints

### Create Pour Activity
```
POST /api/pour-activities
Authorization: Bearer <token>
```

### List Pour Activities
```
GET /api/pour-activities?projectId=1&status=in_progress
Authorization: Bearer <token>
```

### Get Pour Details
```
GET /api/pour-activities/1
Authorization: Bearer <token>
```

### Update Pour
```
PUT /api/pour-activities/1
Authorization: Bearer <token>
```

### Complete Pour
```
POST /api/pour-activities/1/complete
Authorization: Bearer <token>
```

### Add Batch to Pour
```
POST /api/pour-activities/1/batches
Authorization: Bearer <token>
Body: { "batchId": 123 }
```

### Cancel Pour
```
DELETE /api/pour-activities/1
Authorization: Bearer <token>
```

## Database Schema

### pour_activities Table
```sql
CREATE TABLE pour_activities (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    pour_id VARCHAR(100) UNIQUE NOT NULL,
    pour_date DATETIME NOT NULL,
    
    -- Location
    building_name VARCHAR(200),
    floor_level VARCHAR(100),
    zone VARCHAR(100),
    grid_reference VARCHAR(100),
    structural_element_type VARCHAR(100),
    element_id VARCHAR(200),
    location_description TEXT,
    
    -- Concrete
    concrete_type VARCHAR(20) DEFAULT 'Normal',
    design_grade VARCHAR(50),
    total_quantity_planned REAL,
    total_quantity_received REAL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'in_progress',
    started_at DATETIME,
    completed_at DATETIME,
    
    -- Audit
    created_by INTEGER,
    completed_by INTEGER,
    remarks TEXT,
    
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### batch_registers Updates
```sql
ALTER TABLE batch_registers 
ADD COLUMN pour_activity_id INTEGER 
REFERENCES pour_activities(id);
```

### cube_test_registers Updates
```sql
ALTER TABLE cube_test_registers 
ADD COLUMN concrete_type VARCHAR(20) DEFAULT 'Normal';

ALTER TABLE cube_test_registers 
ADD COLUMN pour_activity_id INTEGER 
REFERENCES pour_activities(id);
```

## Benefits

### 1. Accurate Testing
- ONE set of cube tests per pour (not per batch)
- Represents actual structural element
- Follows ISO compliance

### 2. Cost Savings
- **Before:** 3 batches × 2 test sets = 6 sets × 3 cubes = 18 cubes
- **After:** 1 pour × 2 test sets = 2 sets × 3 cubes = 6 cubes
- **Savings:** 12 cubes × ₹100/cube = ₹1,200 saved per pour

### 3. Better Traceability
- Track entire pour activity (not just batches)
- Link all batches to structural element
- Easier reporting and compliance

### 4. Real-World Workflow
- Matches site engineer's mental model
- "Today we're pouring Grid A-12"
- Natural grouping of related work

### 5. PT Concrete Support
- Automatic 5-day testing for PT concrete
- Prevents premature stressing
- Ensures structural safety

## Next Steps

1. **Frontend Implementation**
   - Create `/dashboard/pour-activities` pages
   - Update batch form to link to pours
   - Update cube casting modal for pour support

2. **Testing**
   - Test complete workflow with 3+ batches
   - Verify PT concrete testing logic
   - Test cube test linkage

3. **Documentation**
   - Update user guide with pour workflow
   - Create video/screenshots
   - ISO compliance documentation

## Migration

Run the migration script:
```bash
python migrate_pour_activities.py
```

To rollback (with data loss warning):
```bash
python migrate_pour_activities.py rollback
```

## Status

✅ **Completed (Backend)**
- Database models created
- API endpoints implemented
- Database migration successful
- Pour activity system functional

⏳ **Pending (Frontend)**
- Pour activity UI pages
- Batch form updates
- Cube modal updates

---

**Last Updated:** January 2025  
**Feature Status:** Backend Complete, Frontend Pending  
**Database Migration:** Applied ✅
