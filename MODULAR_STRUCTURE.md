# ProSite - Modular Architecture

## New Directory Structure

```
server/
├── __init__.py
├── app.py                          # Main Flask app with module registration
├── config.py                       # Global configuration
├── db.py                          # Database connection
│
├── core/                          # Core/Shared functionality
│   ├── __init__.py
│   ├── auth.py                    # JWT authentication
│   ├── models.py                  # Base models (User, Company, Project)
│   ├── notifications.py           # Notification system
│   ├── email_notifications.py     # Email service
│   ├── module_access.py           # Module subscription control
│   ├── password_reset.py          # Password reset
│   └── subscription_middleware.py # Subscription middleware
│
├── modules/
│   │
│   ├── safety/                    # Safety Module
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── safety_api.py      # Main safety operations
│   │   │   ├── tbt_api.py         # Toolbox talks
│   │   │   ├── ptw_api.py         # Permit to work
│   │   │   ├── nc_api.py          # Safety NC
│   │   │   ├── audits_api.py      # Safety audits
│   │   │   ├── induction_api.py   # Safety inductions
│   │   │   ├── incidents_api.py   # Incident investigations
│   │   │   └── ppe_api.py         # PPE tracking
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── safety_models.py
│   │   │   ├── tbt_models.py
│   │   │   ├── ptw_models.py
│   │   │   ├── nc_models.py
│   │   │   ├── audit_models.py
│   │   │   ├── induction_models.py
│   │   │   ├── incident_models.py
│   │   │   └── ppe_models.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── nc_scoring.py      # NC scoring logic
│   │
│   ├── concrete/                  # Concrete Quality Module
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── batches_api.py     # Batch management
│   │   │   ├── tests_api.py       # Cube tests
│   │   │   ├── nc_api.py          # Concrete NC
│   │   │   ├── vendors_api.py     # Vendor management
│   │   │   ├── labs_api.py        # Third-party labs
│   │   │   ├── materials_api.py   # Material tests
│   │   │   └── pour_api.py        # Pour activities
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── batch_models.py
│   │   │   ├── test_models.py
│   │   │   ├── nc_models.py
│   │   │   └── pour_models.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── batch_import.py    # Batch import logic
│   │       ├── bulk_entry.py      # Bulk entry
│   │       └── nc_scoring.py      # NC scoring logic
│   │
│   ├── materials/                 # Materials Management Module
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── materials_api.py
│   │   │   ├── vehicles_api.py
│   │   │   └── handover_api.py
│   │   └── models/
│   │       ├── __init__.py
│   │       └── material_models.py
│   │
│   ├── training/                  # Training Module
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── training_api.py
│   │   │   └── qr_attendance_api.py
│   │   └── models/
│   │       ├── __init__.py
│   │       └── training_models.py
│   │
│   ├── geofence/                  # Geofencing Module
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── geofence_api.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── geofence_models.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── geofence_middleware.py
│   │
│   └── admin/                     # Admin/Support Module
│       ├── __init__.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── support_api.py
│       │   └── projects_api.py
│       └── services/
│           ├── __init__.py
│           ├── background_jobs.py
│           └── project_settings.py
│
└── migrations/                    # Database migrations
    ├── __init__.py
    ├── migrate_auth_modules.py
    ├── migrate_safety_nc_scoring.py
    └── ...
```

## Module Responsibilities

### Core Module
- Authentication & Authorization
- User & Company Management
- Module Subscription Control
- Notifications (Email, WhatsApp, In-app)
- Password Reset

### Safety Module
- Toolbox Talks (TBT)
- Permit to Work (PTW)
- Safety Non-Conformance (NC) with scoring
- Safety Audits & Inspections
- Safety Inductions
- Incident Investigations
- PPE Tracking

### Concrete Module
- Batch Management
- Cube Testing
- Concrete NC with scoring
- Vendor Management
- Third-party Lab Integration
- Material Testing
- Pour Activities

### Materials Module
- Material Management
- Vehicle Register
- Handover Register

### Training Module
- Training Register
- QR-based Attendance
- Certification Tracking

### Geofence Module
- Geofence Management
- Location-based Access Control
- Geofence Middleware

### Admin Module
- Support Admin Functions
- Project Management
- Background Jobs
- System Settings

## Benefits

1. **Clear Separation**: Each module is self-contained
2. **Scalability**: Easy to add new modules
3. **Maintainability**: Changes isolated to specific modules
4. **Testing**: Each module can be tested independently
5. **Team Collaboration**: Different teams can work on different modules
6. **Billing**: Modules align with billing/subscription model

