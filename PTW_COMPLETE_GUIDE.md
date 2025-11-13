# Permit-to-Work (PTW) System - Complete Guide

## 📋 Overview

The Permit-to-Work (PTW) system is based on **ISO 45001:2018** Occupational Health and Safety Management Systems and industry best practices. This is a **copyright-free implementation** designed for universal applicability.

---

## 🔄 Complete PTW Workflow

```
┌────────────────────────────────────────────────────────────────┐
│ Step 1: CONTRACTOR FILLS PERMIT REQUEST                       │
│ ──────────────────────────────────────────────────────────     │
│ Contractor fills:                                              │
│ • Work description & location                                  │
│ • Hazards identified                                           │
│ • Safety measures to be taken                                  │
│ • PPE requirements                                             │
│ • Number of workers                                            │
│ • Work schedule & duration                                     │
│ • Emergency contacts                                           │
│ • Equipment checklist                                          │
│                                                                 │
│ Actions:                                                        │
│ • Save as DRAFT (can edit multiple times)                      │
│ • SUBMIT for approval when ready                               │
│ • Digital signature captured                                   │
└────────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 2: SITE ENGINEER REVIEWS                                 │
│ ──────────────────────────────────────────────────────────     │
│ Site Engineer receives notification                            │
│ • Reviews work scope                                           │
│ • Checks technical feasibility                                 │
│ • Verifies equipment/resources                                 │
│ • Reviews method statement                                     │
│                                                                 │
│ Decision:                                                       │
│ ✅ APPROVE → Adds digital signature → Sends to Safety Officer │
│ ❌ REJECT → Adds comments → Returns to Contractor             │
└────────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 3: SAFETY OFFICER FINAL APPROVAL                         │
│ ──────────────────────────────────────────────────────────     │
│ Safety Officer receives notification                           │
│ • Reviews hazard assessment                                    │
│ • Verifies safety measures adequate                            │
│ • Checks PPE compliance                                        │
│ • Ensures emergency procedures in place                        │
│                                                                 │
│ Decision:                                                       │
│ ✅ APPROVE → Final signature → Permit ACTIVE                  │
│ ❌ REJECT → Adds comments → Returns to Contractor             │
│                                                                 │
│ Once APPROVED:                                                  │
│ • Contractor receives WhatsApp/Email notification              │
│ • Permit valid for specified hours (e.g., 8 hours)            │
│ • Work authorized to proceed                                   │
│ • Signature board shows all approvers                          │
└────────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 4: WORK PROCEEDS (Permit Active)                         │
│ ──────────────────────────────────────────────────────────     │
│ • Permit displayed at work site                                │
│ • Signature board visible                                      │
│ • Valid for specified duration                                 │
│ • Can be suspended if unsafe conditions arise                  │
│ • Extension can be requested if needed                         │
└────────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 5: CONTRACTOR CLOSES PERMIT                              │
│ ──────────────────────────────────────────────────────────     │
│ When work completed:                                           │
│ • Contractor marks work as complete                            │
│ • Adds closing comments                                        │
│ • Confirms site cleaned                                        │
│ • Digital signature for closure                                │
│                                                                 │
│ Status: "Awaiting Closure Verification"                        │
└────────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 6: ENGINEER/SAFETY OFFICER VERIFIES CLOSURE             │
│ ──────────────────────────────────────────────────────────     │
│ • Inspects work site                                           │
│ • Confirms work completed satisfactorily                       │
│ • Verifies site cleaned                                        │
│ • Checks tools/equipment removed                               │
│ • Adds verification signature                                  │
│                                                                 │
│ Final Status: CLOSED ✅                                        │
│ Permit archived with full signature trail                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 📝 Permit Types (Configurable)

Each company can configure their own permit types:

### Common Permit Types:

1. **Hot Work Permit (HW)**
   - Welding, cutting, grinding
   - Risk Level: HIGH
   - Requires: Fire extinguisher, fire watch, spark shields
   - Max Validity: 4 hours

2. **Confined Space Entry (CS)**
   - Tanks, manholes, pits
   - Risk Level: CRITICAL
   - Requires: Gas testing, rescue equipment, attendant
   - Max Validity: 4 hours

3. **Working at Height (WAH)**
   - Scaffolding, ladders, elevated platforms
   - Risk Level: HIGH
   - Requires: Harness, fall arrest system, guardrails
   - Max Validity: 8 hours

4. **Electrical Work (EL)**
   - Live electrical work, installations
   - Risk Level: HIGH
   - Requires: LOTO, insulated tools, voltage tester
   - Max Validity: 6 hours

5. **Excavation Work (EX)**
   - Digging, trenching
   - Risk Level: MEDIUM
   - Requires: Shoring, barricading, utility clearance
   - Max Validity: 8 hours

6. **Lifting Operations (LO)**
   - Crane work, heavy lifting
   - Risk Level: MEDIUM
   - Requires: Certified rigger, lift plan, exclusion zone
   - Max Validity: 8 hours

---

## 🖊️ Digital Signature Board

### What is the Signature Board?

A **digital signboard** that shows **who signed** the permit and **when**. This creates a complete audit trail.

### Example Signature Board:

```
╔═══════════════════════════════════════════════════════════════╗
║           WORK PERMIT SIGNATURE BOARD                         ║
╠═══════════════════════════════════════════════════════════════╣
║  Permit Number: PTW-HW-20251113-00001                        ║
║  Work: Welding of steel beams at Block A                     ║
║  Status: APPROVED ✅                                          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1️⃣ PERMIT REQUESTED BY:                                     ║
║     Name: John Smith                                          ║
║     Role: Contractor Supervisor                               ║
║     Company: ABC Welding Contractors                          ║
║     Signature: [Digital Signature]                            ║
║     Date: 13-Nov-2025 09:15                                  ║
║     Comments: "Request for hot work permit"                   ║
║                                                               ║
║  2️⃣ REVIEWED & APPROVED BY:                                  ║
║     Name: Mike Johnson                                        ║
║     Role: Site Engineer                                       ║
║     Signature: [Digital Signature]                            ║
║     Date: 13-Nov-2025 10:30                                  ║
║     Comments: "Work scope reviewed. Approved to proceed."     ║
║                                                               ║
║  3️⃣ FINAL APPROVAL BY:                                       ║
║     Name: Sarah Williams                                      ║
║     Role: Safety Officer                                      ║
║     Signature: [Digital Signature]                            ║
║     Date: 13-Nov-2025 11:00                                  ║
║     Comments: "All safety precautions verified. Approved."    ║
║                                                               ║
║  Permit Valid: 13-Nov-2025 12:00 to 16:00 (4 hours)         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### When Work Closes:

```
╠═══════════════════════════════════════════════════════════════╣
║  4️⃣ WORK COMPLETED BY:                                       ║
║     Name: John Smith                                          ║
║     Role: Contractor Supervisor                               ║
║     Signature: [Digital Signature]                            ║
║     Date: 13-Nov-2025 15:45                                  ║
║     Comments: "Work completed. Site cleaned and secured."     ║
║                                                               ║
║  5️⃣ CLOSURE VERIFIED BY:                                     ║
║     Name: Mike Johnson                                        ║
║     Role: Site Engineer                                       ║
║     Signature: [Digital Signature]                            ║
║     Date: 13-Nov-2025 16:00                                  ║
║     Comments: "Site inspected. All clear."                    ║
║                                                               ║
║  Status: CLOSED ✅                                            ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 📊 API Endpoints

### **Permit Types**
```
GET  /api/safety/permits/types       - Get permit types
POST /api/safety/permits/types       - Create permit type (Admin)
```

### **Contractor Workflow**
```
POST /api/safety/permits              - Create permit (draft)
POST /api/safety/permits/:id/submit   - Submit for approval
POST /api/safety/permits/:id/close    - Close permit after work
```

### **Site Engineer Workflow**
```
POST /api/safety/permits/:id/engineer-review  - Approve/Reject
```

### **Safety Officer Workflow**
```
POST /api/safety/permits/:id/safety-review    - Final Approve/Reject
POST /api/safety/permits/:id/verify-closure   - Verify closure
```

### **View Permits**
```
GET  /api/safety/permits              - Get all permits (filtered)
GET  /api/safety/permits/:id          - Get permit details
GET  /api/safety/permits/:id/signboard - Get signature board
GET  /api/safety/permits/dashboard     - Dashboard counts
```

---

## 🎯 Example: Contractor Fills Hot Work Permit

### Step 1: Create Permit (Draft)

```bash
POST /api/safety/permits
```

```json
{
  "project_id": 1,
  "permit_type_id": 1,
  "work_description": "Welding of steel beams at Block A, Level 3",
  "work_location": "Block A, Level 3, Grid D-E",
  "contractor_company": "ABC Welding Contractors",
  "work_date": "2025-11-15",
  "start_time": "12:00",
  "end_time": "16:00",
  "estimated_duration_hours": 4,
  "number_of_workers": 3,
  
  "identified_hazards": [
    "Fire/explosion from sparks",
    "Burns from hot metal",
    "Fumes inhalation",
    "Arc flash"
  ],
  
  "safety_measures": [
    "Fire extinguisher within 10m",
    "Fire watch assigned",
    "Combustibles removed from area",
    "Welding screens installed",
    "Adequate ventilation",
    "Barricading with signage"
  ],
  
  "ppe_required": [
    "Welding helmet with auto-darkening lens",
    "Leather welding gloves",
    "Leather apron",
    "Safety boots",
    "Respirator"
  ],
  
  "equipment_checklist": {
    "welding_machine": true,
    "fire_extinguisher": true,
    "welding_screens": true,
    "gas_cylinders_secured": true
  },
  
  "requires_isolation": true,
  "isolation_details": {
    "electrical_isolation": "Nearby electrical panel tagged out",
    "sprinkler_system": "Isolated with fire watch"
  },
  
  "emergency_contact_name": "John Smith",
  "emergency_contact_phone": "+1234567890",
  "nearest_hospital": "City General Hospital, 2km away",
  "first_aid_location": "Site office, Block A ground floor"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permit PTW-HW-20251113-00001 created as draft",
  "permit": {
    "id": 1,
    "permit_number": "PTW-HW-20251113-00001",
    "status": "draft",
    "workflow_stage": "contractor_request"
  }
}
```

### Step 2: Submit Permit

```bash
POST /api/safety/permits/1/submit
```

```json
{
  "designation": "Contractor Supervisor",
  "signature_type": "digital",
  "signature_data": "base64_signature_image_or_text",
  "comments": "All precautions verified. Ready for approval."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permit PTW-HW-20251113-00001 submitted for Site Engineer review",
  "permit": {
    "status": "submitted",
    "workflow_stage": "site_engineer_review",
    "submitted_at": "2025-11-13T09:15:00"
  }
}
```

**Auto-Actions:**
- ✅ Contractor signature saved
- ✅ Site Engineer notified (WhatsApp/Email)
- ✅ Audit log created

---

### Step 3: Site Engineer Approves

```bash
POST /api/safety/permits/1/engineer-review
```

```json
{
  "approved": true,
  "designation": "Site Engineer",
  "signature_type": "digital",
  "signature_data": "base64_signature",
  "comments": "Work scope reviewed. Method statement acceptable. Approved to proceed to Safety Officer."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permit PTW-HW-20251113-00001 approved by Site Engineer. Sent to Safety Officer.",
  "permit": {
    "workflow_stage": "safety_officer_review"
  }
}
```

**Auto-Actions:**
- ✅ Engineer signature saved
- ✅ Safety Officer notified
- ✅ Workflow moves forward

---

### Step 4: Safety Officer Approves

```bash
POST /api/safety/permits/1/safety-review
```

```json
{
  "approved": true,
  "designation": "Safety Officer",
  "signature_type": "digital",
  "signature_data": "base64_signature",
  "comments": "All safety precautions verified. Fire extinguisher confirmed. Fire watch assigned. Work may proceed."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permit PTW-HW-20251113-00001 APPROVED. Work authorized to proceed.",
  "permit": {
    "status": "approved",
    "workflow_stage": "approved",
    "approved_at": "2025-11-13T11:00:00",
    "valid_from": "2025-11-15T12:00:00",
    "valid_until": "2025-11-15T16:00:00"
  }
}
```

**Auto-Actions:**
- ✅ Safety Officer signature saved
- ✅ Contractor receives approval notification (WhatsApp/Email)
- ✅ Permit now ACTIVE
- ✅ Signature board complete with 3 signatures

---

### Step 5: Contractor Closes Permit

```bash
POST /api/safety/permits/1/close
```

```json
{
  "designation": "Contractor Supervisor",
  "signature_type": "digital",
  "signature_data": "base64_signature",
  "comments": "Welding completed. All equipment removed. Site cleaned. Fire watch maintained for 2 hours post-work."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permit PTW-HW-20251113-00001 closure requested. Awaiting verification.",
  "permit": {
    "status": "completed",
    "workflow_stage": "closure_verification",
    "work_completed_at": "2025-11-15T15:45:00"
  }
}
```

---

### Step 6: Engineer Verifies Closure

```bash
POST /api/safety/permits/1/verify-closure
```

```json
{
  "designation": "Site Engineer",
  "signature_type": "digital",
  "signature_data": "base64_signature",
  "comments": "Site inspected. Work completed satisfactorily. All equipment removed. Area cleaned. Permit closed."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permit PTW-HW-20251113-00001 closed successfully.",
  "permit": {
    "status": "closed",
    "workflow_stage": "closed",
    "closed_at": "2025-11-15T16:00:00"
  }
}
```

**Final State:**
- ✅ Permit fully closed
- ✅ 5 signatures captured (request, engineer approve, safety approve, close, verify)
- ✅ Complete audit trail
- ✅ Signature board shows all signers

---

## 🔒 Copyright & Compliance

### **ISO Standards Referenced:**
- **ISO 45001:2018** - Occupational Health and Safety Management Systems
- **ISO 9001:2015** - Quality Management (for documentation)

### **Copyright-Free Implementation:**
- ✅ No proprietary software copied
- ✅ Based on published ISO standards (publicly available)
- ✅ Industry best practices (common knowledge)
- ✅ Original database schema
- ✅ Original API design
- ✅ No trademarked names used

### **Industry References (Copyright-Free):**
- OSHA (Occupational Safety and Health Administration) - Public domain
- HSE UK (Health and Safety Executive) - Public guidelines
- ILO (International Labour Organization) - Open resources

---

## 📱 Notifications

### Contractor Receives:
1. **Permit Approved** (WhatsApp/Email)
   ```
   ✅ Work Permit APPROVED
   Permit: PTW-HW-20251113-00001
   Valid: 15-Nov-2025 12:00 to 16:00
   Ensure all safety precautions followed.
   ```

2. **Permit Rejected** (WhatsApp/Email)
   ```
   ❌ Work Permit REJECTED
   Permit: PTW-HW-20251113-00001
   Review rejection comments and resubmit.
   ```

3. **Permit Expiring Soon**
   ```
   ⏰ Permit Expiring in 1 hour
   Request extension if work incomplete.
   ```

### Engineer/Safety Officer Receives:
1. **Permit Submitted for Review**
2. **Closure Requested** (needs verification)

---

## 📋 Dashboard Views

### Contractor Dashboard:
```json
{
  "draft": 2,
  "submitted": 1,
  "approved": 3,
  "in_progress": 2,
  "completed": 1,
  "closed": 15,
  "rejected": 0
}
```

### Engineer/Safety Dashboard:
```json
{
  "pending_actions": {
    "engineer_review": 5,
    "safety_review": 3,
    "closure_verification": 2
  }
}
```

---

## 🚀 Next Steps

1. **Database Migration**
   ```bash
   python3 -c "from server.db import init_db; from server.permit_to_work_models import *; init_db()"
   ```

2. **Create Permit Types**
   - Hot Work, Confined Space, Working at Height, etc.

3. **Test Workflow**
   - Create permit → Submit → Engineer approve → Safety approve → Close → Verify

4. **Build Frontend**
   - Permit request form
   - Approval interfaces
   - Signature board display
   - Dashboard

---

## ✅ Summary

**How Contractor Fills Permit:**
1. Fills form with work details, hazards, safety measures
2. Saves as draft (can edit)
3. Submits with digital signature

**How Site Engineer Accepts:**
1. Receives notification
2. Reviews permit details
3. Approves/Rejects with signature

**How Safety Officer Accepts:**
1. Receives notification after engineer approval
2. Final safety review
3. Approves/Rejects with signature
4. If approved → Permit ACTIVE

**Signature Board:**
- Shows all signers (contractor, engineer, safety officer)
- Digital signatures with timestamps
- Complete audit trail
- Can be displayed on-site or printed

**All workflows ISO 45001 compliant, copyright-free, universally applicable!** 🎉
