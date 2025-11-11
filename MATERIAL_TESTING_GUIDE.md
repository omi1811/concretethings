# Material Testing & Third-Party Lab Integration

## Overview

This document describes the implementation of:
1. **Email notifications** for test failures
2. **Third-party test register** for external lab testing (concrete cubes)
3. **Material testing register** for steel, glass, railing, etc. with approved brands

## ISO Standards Compliance

### ISO 9001:2015 - Quality Management System
- **Clause 7.4**: Communication (Email notifications to stakeholders)
- **Clause 8.4**: Control of externally provided processes, products and services (Approved brands)
- **Clause 8.4.1**: Evaluation and selection of suppliers (Brand approval process)
- **Clause 8.6**: Release of products and services (Material test verification)
- **Clause 8.7**: Control of nonconforming outputs (NCR generation on failures)

### ISO/IEC 17025:2017 - Testing Laboratory Requirements
- **General requirements**: Impartiality and confidentiality
- **Structural requirements**: NABL accreditation tracking
- **Resource requirements**: Laboratory competence verification
- **Process requirements**: Test certificate documentation with photos

## 1. Email Notification System

### Features
- ✅ SMTP-based email sending (Gmail, Outlook, SendGrid, AWS SES)
- ✅ Professional HTML email templates
- ✅ Plain text fallback for compatibility
- ✅ Multi-recipient broadcasting
- ✅ Test failure alerts to Quality Manager & RMC Vendor
- ✅ Graceful degradation when disabled

### Email Templates

#### Cube Test Failure Email
**Recipients:** Quality Manager, RMC Vendor Contact, Project Manager  
**Trigger:** When concrete strength test fails IS 516 criteria

**Content:**
- Project and batch identification
- Test details with color-coded results
- Individual cube strengths in table format
- Pass/fail status with visual indicators
- NCR number
- Required actions per ISO 9001:2015
- Direct link to test report

### Configuration

**Environment Variables (.env):**
```bash
# Gmail (recommended for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=ConcreteThings QMS
EMAIL_ENABLED=true
```

**Other Providers:**

**Microsoft 365/Outlook:**
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

**SendGrid (Production):**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**AWS SES (Production):**
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-iam-access-key
SMTP_PASSWORD=your-iam-secret-key
```

### Gmail Setup (Step-by-Step)

1. **Enable 2-Factor Authentication:**
   - Go to Google Account: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Click "Generate"
   - Copy the 16-character password (format: xxxx xxxx xxxx xxxx)

3. **Update .env:**
   ```bash
   SMTP_USER=yourname@gmail.com
   SMTP_PASSWORD=xxxxxxxxxxxxxx  # 16-char app password (no spaces)
   EMAIL_ENABLED=true
   ```

### Usage Example

```python
from server.email_notifications import notify_test_failure_email

# After cube test failure
if cube_test.pass_fail_status == "fail":
    result = notify_test_failure_email(
        cube_test=cube_test,
        batch_register=batch,
        mix_design=mix_design,
        vendor=vendor,
        project=project,
        quality_manager_email="qm@company.com",
        pm_email="pm@company.com"
    )
    # Result: {"success": 3, "failed": 0, "total": 3}
```

## 2. Third-Party Test Register

### Purpose
For concrete cube tests conducted by external NABL-accredited laboratories. Enables tracking of third-party test results with mandatory certificate photo upload.

### Database Models

#### ThirdPartyLab
Stores NABL-accredited laboratory information.

**Fields:**
- Lab identification (name, code, contact details)
- Address (city, state, pincode)
- NABL accreditation (number, validity, scope)
- Approval workflow (quality manager approval)
- Active status
- Soft delete (no permanent deletion)

**Key Features:**
- NABL accreditation tracking with validity dates
- Scope of accreditation (Concrete, Steel, Soil, etc.)
- Quality manager approval before lab can be used

#### ThirdPartyCubeTest
Concrete cube test results from external labs.

**Fields:**
- **Test Identification:**
  - Lab test report number (unique)
  - Test age (7, 28, 56, 90 days)
  
- **Sample Details:**
  - Collection date
  - Received at lab date
  - Testing date
  
- **Test Results:**
  - Number of cubes tested
  - Individual cube strengths (up to 3 cubes)
  - Average strength
  - Required strength
  - Pass/fail status (as per lab certificate)
  
- **MANDATORY Certificate Photo:**
  - Certificate/result sheet image
  - Stored as binary data in database
  - Supports JPEG, PNG, PDF
  
- **Verification:**
  - Internal quality team verification
  - Verification remarks
  
- **NCR Tracking:**
  - Auto-generate NCR if test fails
  - Email notifications to stakeholders
  
- **Soft Delete:**
  - No permanent deletion (audit trail)

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Sample Collection                                        │
│    Quality person collects concrete samples from batch     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Lab Testing                                              │
│    External NABL lab conducts cube compression test       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Certificate Receipt                                      │
│    Lab provides test certificate with results              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Entry in QMS (WITHOUT OCR - Direct Entry)               │
│    Quality person:                                          │
│    - Enters test results manually from certificate         │
│    - Uploads certificate photo (mandatory)                 │
│    - Links to batch register                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Automatic Processing                                     │
│    System:                                                  │
│    - Checks pass/fail based on entered results            │
│    - Generates NCR if failed                               │
│    - Sends email to QM & RMC vendor                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Verification                                             │
│    Quality Manager verifies entry against certificate      │
└─────────────────────────────────────────────────────────────┘
```

**Note:** OCR (Optical Character Recognition) for automatic data extraction from certificates will be implemented in a future phase. Currently, all data is entered manually by the quality person.

### API Endpoints (To Be Implemented)

```
# Labs
GET    /api/third-party-labs              # List approved labs
POST   /api/third-party-labs              # Add new lab
PUT    /api/third-party-labs/:id/approve  # Approve lab (QM)
GET    /api/third-party-labs/:id          # Get lab details

# Third-party tests
GET    /api/third-party-cube-tests        # List tests (filter by project/batch/lab)
POST   /api/third-party-cube-tests        # Create new test with certificate photo
GET    /api/third-party-cube-tests/:id    # Get test details
GET    /api/third-party-cube-tests/:id/certificate  # Download certificate
PUT    /api/third-party-cube-tests/:id/verify       # Verify test (QM)
```

## 3. Material Testing & Approved Brands

### Purpose
Track testing of other construction materials (steel, glass, railing, paint, etc.) with company-specific approved brand lists per ISO 9001:2015 Clause 8.4.

### Database Models

#### MaterialCategory
Material type classification.

**Examples:**
- **Steel:** Reinforcement bars, structural steel, TMT bars
- **Glass:** Float glass, toughened glass, laminated glass
- **Railing:** SS railing, MS railing, aluminum railing
- **Paint:** Primer, emulsion, enamel
- **Waterproofing:** Membrane, coating, admixture
- **Tiles:** Vitrified, ceramic, mosaic
- **Aluminum:** Windows, doors, ACP sheets

**Fields:**
- Category name and code
- Description
- Applicable standards (e.g., "IS 1786, IS 2062")
- Testing requirements (requires testing? frequency?)
- Active status

#### ApprovedBrand
Company-approved brands for each material category.

**Fields:**
- Brand name and manufacturer
- Grade/specification (e.g., "Fe 500D", "6mm Clear Glass")
- Compliance standards
- Approval details (approved by, date, validity)
- Optional type test certificate upload
- Active status

**Workflow:**
1. Quality Manager adds approved brands
2. Uploads type test certificate (if available)
3. Sets approval validity period
4. Only approved brands can be used in projects

#### MaterialTestRegister
Test records for materials with third-party lab certificates.

**Fields:**
- **Material Details:**
  - Description, grade, quantity
  - Supplier and manufacturer
  - Batch/lot number
  - Invoice details
  
- **Location:**
  - Where material is used (e.g., "Building A, 3rd Floor Column")
  
- **Test Details:**
  - Lab test report number
  - Sample collection date, testing date
  - Test parameters (JSON - flexible for different materials)
  - Test results (JSON - flexible structure)
  - Pass/fail status
  
- **MANDATORY Certificate Photo:**
  - Test certificate image
  - Stored as binary data
  
- **Verification:**
  - Entry person and verification workflow
  - Quality manager approval
  
- **NCR Tracking:**
  - Auto-generate NCR if failed
  
- **Soft Delete:**
  - No permanent deletion

### Material-Specific Test Parameters

#### Steel (IS 1786:2008, IS 2062:2011)
```json
{
  "test_parameters": {
    "yieldStrength": {"required": 500, "unit": "MPa"},
    "tensileStrength": {"required": 545, "unit": "MPa"},
    "elongation": {"required": 14.5, "unit": "%"},
    "bendTest": {"required": "pass"}
  },
  "test_results": {
    "yieldStrength": {"achieved": 520, "status": "pass"},
    "tensileStrength": {"achieved": 565, "status": "pass"},
    "elongation": {"achieved": 16.2, "status": "pass"},
    "bendTest": {"result": "pass", "status": "pass"}
  }
}
```

#### Glass (IS 2553:1990)
```json
{
  "test_parameters": {
    "thickness": {"required": 6, "unit": "mm", "tolerance": 0.2},
    "breakingStrength": {"required": 45, "unit": "MPa"},
    "visualInspection": {"required": "pass"}
  },
  "test_results": {
    "thickness": {"achieved": 6.1, "status": "pass"},
    "breakingStrength": {"achieved": 52, "status": "pass"},
    "visualInspection": {"result": "pass", "status": "pass"}
  }
}
```

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Setup Approved Brands (One-time)                        │
│    Quality Manager:                                         │
│    - Creates material categories                           │
│    - Adds approved brands for each category                │
│    - Uploads type test certificates (if available)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Material Receipt on Site                                 │
│    Site engineer receives material with invoice & challan  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Sample Collection & Testing                              │
│    - Sample sent to third-party NABL lab                   │
│    - Lab conducts tests as per applicable standards        │
│    - Lab issues test certificate                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Entry in QMS (Quality Person)                           │
│    - Enters material details                               │
│    - Selects approved brand (from dropdown)                │
│    - Enters test results manually                          │
│    - Uploads certificate photo (mandatory)                 │
│    - Specifies location where material is used             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Auto-Processing                                          │
│    System:                                                  │
│    - Validates against approved brand                      │
│    - Checks pass/fail based on test results               │
│    - Generates NCR if failed or unapproved brand used      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Verification & Approval                                  │
│    Quality Manager:                                         │
│    - Verifies test entry against certificate               │
│    - Approves material for use                             │
│    - Issues release note if passed                         │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints (To Be Implemented)

```
# Material Categories
GET    /api/material-categories           # List all categories
POST   /api/material-categories           # Create category (admin)
PUT    /api/material-categories/:id       # Update category
GET    /api/material-categories/:id       # Get category details

# Approved Brands
GET    /api/approved-brands               # List approved brands (filter by category)
POST   /api/approved-brands               # Add new brand (QM)
PUT    /api/approved-brands/:id           # Update brand
GET    /api/approved-brands/:id           # Get brand details
GET    /api/approved-brands/:id/certificate  # Download type certificate

# Material Tests
GET    /api/material-tests                # List tests (filter by project/category/status)
POST   /api/material-tests                # Create test with certificate photo
GET    /api/material-tests/:id            # Get test details
GET    /api/material-tests/:id/certificate  # Download certificate
PUT    /api/material-tests/:id/verify     # Verify test (QM)
```

## Implementation Status

### ✅ Completed

1. **Email Notification Service**
   - `server/email_notifications.py` (500+ lines)
   - SMTP integration with multiple providers
   - Professional HTML email templates
   - Test failure notifications
   - Configuration in `.env.example`

2. **Database Models**
   - `ThirdPartyLab` - NABL lab tracking
   - `ThirdPartyCubeTest` - External cube tests with certificates
   - `MaterialCategory` - Material type classification
   - `ApprovedBrand` - Company-approved brands
   - `MaterialTestRegister` - Material tests with certificates
   - All models have soft delete (no permanent deletion)
   - ISO compliance documented in code comments

### ⏳ Pending

1. **Database Migration**
   - Create migration script for new tables
   - Test migration with sample data

2. **API Endpoints**
   - Third-party labs CRUD
   - Third-party cube tests CRUD with photo upload
   - Material categories CRUD
   - Approved brands CRUD with certificate upload
   - Material tests CRUD with certificate upload

3. **Frontend UI**
   - Lab management (add/approve labs)
   - Third-party test entry form
   - Material category & brand management
   - Material test entry form
   - Certificate viewer

4. **Future Enhancements**
   - **OCR Integration** (Phase 2):
     - Automatic data extraction from certificates
     - AI-based text recognition
     - Pre-fill form fields from uploaded certificate
     - Manual verification/correction still required
   - **Barcode/QR Code:**
     - Generate QR codes for material tracking
     - Link QR code to test certificates
   - **Mobile App:**
     - Capture certificate photos on-site
     - Offline entry capability

## Testing

### Email Notification Test

```python
# test_email.py
from server.email_notifications import get_email_service

email = get_email_service()

# Test single email
result = email.send_email(
    "test@example.com",
    "Test Email from ConcreteThings QMS",
    "<h1>Test Successful!</h1><p>If you receive this, email is working.</p>",
    "Test Successful! If you receive this, email is working."
)

print(f"Email sent: {result}")
```

### Database Model Test

```python
# After migration
from server.models import ThirdPartyLab, MaterialCategory
from server.db import get_db

db = get_db()

# Create third-party lab
lab = ThirdPartyLab(
    company_id=1,
    lab_name="ABC Testing Services",
    lab_code="LAB-001",
    contact_person_name="Dr. Smith",
    contact_phone="+919876543210",
    contact_email="lab@example.com",
    nabl_accreditation_number="NABL-TC-1234",
    scope_of_accreditation="Concrete, Steel, Soil"
)
db.add(lab)
db.commit()

print(f"Lab created: {lab.to_dict()}")

# Create material category
category = MaterialCategory(
    company_id=1,
    category_name="Steel Reinforcement",
    category_code="STL",
    applicable_standards="IS 1786:2008, IS 2062:2011",
    requires_testing=True,
    test_frequency="Per batch"
)
db.add(category)
db.commit()

print(f"Category created: {category.to_dict()}")
```

## Benefits

### For Quality Managers
- ✅ Centralized tracking of all material tests
- ✅ Automatic NCR generation on failures
- ✅ Email alerts for immediate action
- ✅ Approved brand compliance enforcement
- ✅ Complete audit trail (no data deletion)
- ✅ ISO 9001:2015 compliance

### For Site Engineers
- ✅ Easy material test entry with photo upload
- ✅ Approved brand dropdown (no unapproved materials)
- ✅ Quick verification status check
- ✅ Historical test data access

### For Management
- ✅ Real-time test failure notifications
- ✅ Third-party lab performance tracking
- ✅ Material supplier quality trends
- ✅ Compliance reporting for audits
- ✅ Risk mitigation (NCR tracking)

## Future: OCR Integration (Phase 2)

### Planned Features

1. **Certificate Photo → Auto-Fill:**
   - Upload certificate photo
   - OCR extracts text (lab name, test results, date, etc.)
   - Pre-fills form fields
   - User verifies and corrects if needed

2. **Supported Documents:**
   - PDF certificates
   - Scanned images (JPEG, PNG)
   - Multi-page documents

3. **OCR Technology Options:**
   - **Tesseract OCR** (Open source, free)
   - **Google Cloud Vision API** (Paid, high accuracy)
   - **AWS Textract** (Paid, table extraction)
   - **Azure Form Recognizer** (Paid, structured data)

4. **Implementation:**
   ```python
   # Future implementation
   from server.ocr_service import extract_certificate_data
   
   # Upload certificate
   certificate_image = request.files['certificate']
   
   # OCR extraction
   extracted_data = extract_certificate_data(certificate_image)
   # Returns: {
   #   "lab_name": "ABC Testing Lab",
   #   "report_number": "TR/2024/001",
   #   "testing_date": "2024-01-15",
   #   "cube_1_strength": 23.5,
   #   "cube_2_strength": 22.0,
   #   "cube_3_strength": 22.0,
   #   "average_strength": 22.5,
   #   "confidence": 0.95
   # }
   
   # Pre-fill form (user can edit)
   form_data = extracted_data
   ```

5. **Benefits:**
   - 80% faster data entry
   - Reduced human errors
   - Still maintains human verification
   - Audit trail with original certificate

---

**Status:** Models and email service implemented. API endpoints and UI pending.  
**Next Steps:** Create migration script, implement API endpoints, build frontend UI.  
**Future:** OCR integration for automatic certificate data extraction.
