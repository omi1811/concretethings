# Non-Conformance (NC) Management for Safety Module

## 🔄 Complete NC Workflow

This document explains how Non-Conformances (NCs) work in ProSite Safety module, specifically addressing:
1. How NCs are raised by safety officers
2. How contractors are notified
3. How contractors respond and close NCs
4. Notification channels and tracking

---

## 📋 NC Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: RAISE NC (Safety Officer)                              │
│ ────────────────────────────────────────────────────────────    │
│ • Safety officer finds issue during inspection                 │
│ • Creates NC with details (title, description, severity)       │
│ • Assigns to specific contractor                               │
│ • Sets due date for corrective action                          │
│ • Attaches evidence photos/videos                              │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: CONTRACTOR NOTIFIED (Automatic)                        │
│ ────────────────────────────────────────────────────────────    │
│ 📱 WhatsApp Notification:                                      │
│    "🔴 Non-Conformance Raised                                  │
│     NC Number: NC-20251113-00001                               │
│     Title: Unsafe scaffolding at Block A                       │
│     Severity: MAJOR                                            │
│     Due Date: 15-Nov-2025 17:00                                │
│     Please submit corrective action plan ASAP."                │
│                                                                 │
│ 📧 Email Notification:                                         │
│    Same content in email format                                │
│                                                                 │
│ 🔔 In-App Notification:                                        │
│    Dashboard shows "1 Pending NC"                              │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: CONTRACTOR VIEWS NC                                    │
│ ────────────────────────────────────────────────────────────    │
│ Contractor logs into ProSite and sees:                         │
│ • Dashboard with pending NCs count                             │
│ • List of NCs assigned to them                                 │
│ • NC details: description, photos, location, due date          │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: CONTRACTOR SUBMITS ACTION (Contractor)                 │
│ ────────────────────────────────────────────────────────────    │
│ • Contractor reviews NC                                        │
│ • Submits proposed corrective action plan                      │
│ • Uploads "before" and "after" photos                          │
│ • Marks work as completed                                      │
│ • Submits for verification                                     │
│ • Status changes: "Pending Action" → "Action Submitted"        │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: SAFETY OFFICER VERIFIES                                │
│ ────────────────────────────────────────────────────────────    │
│ Safety officer reviews:                                         │
│ • Proposed action plan                                         │
│ • Completion photos                                            │
│                                                                 │
│ Option A: APPROVE ✅                                           │
│ • Marks NC as verified and closed                              │
│ • Contractor receives approval notification                    │
│ • NC status: "Verified" → "Closed"                             │
│                                                                 │
│ Option B: REJECT ❌                                            │
│ • Provides verification notes (what's missing)                 │
│ • NC goes back to contractor                                   │
│ • Contractor receives rejection notification                   │
│ • Status: "Rejected" (loops back to Step 4)                    │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: NC CLOSED ✅                                           │
│ ────────────────────────────────────────────────────────────    │
│ • Final notification sent to contractor                        │
│ • NC record archived                                           │
│ • Analytics updated                                            │
│ • Contractor scorecard updated                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔔 How Contractors Know About NCs

### 1. **WhatsApp Notification** (Instant)
When NC is raised, contractor receives WhatsApp message:

```
🔴 *Non-Conformance Raised*

*NC Number:* NC-20251113-00001
*Title:* Unsafe scaffolding at Block A
*Severity:* MAJOR
*Category:* Safety Violation
*Location:* Block A, Level 3

*Description:*
Scaffolding installed without guardrails. 
Workers exposed to fall hazard.

*Assigned To:* ABC Scaffolding Contractors
*Due Date:* 15-Nov-2025 17:00

⚠️ Please submit your corrective action plan ASAP.

_Automated alert from ProSite Safety_
```

### 2. **Email Notification**
Same content sent to contractor's registered email.

### 3. **In-App Dashboard**
When contractor logs into ProSite:
- **Dashboard shows**: "🔴 3 Pending NCs"
- **List view**: All NCs with status, due date, severity
- **Filter by**: Pending, Overdue, Rejected, Closed

### 4. **Overdue Alerts**
If contractor doesn't respond before due date:
```
⚠️ *Non-Conformance OVERDUE*

*NC Number:* NC-20251113-00001
*Title:* Unsafe scaffolding at Block A
*Due Date:* 15-Nov-2025 17:00

This NC is now overdue. Please submit corrective actions immediately.

_Automated alert from ProSite Safety_
```

---

## 🛠️ API Endpoints for NC Management

### **1. Create NC (Safety Officer)**
```bash
POST /api/safety/nc
```

**Request:**
```json
{
  "project_id": 1,
  "nc_title": "Unsafe scaffolding at Block A",
  "nc_description": "Scaffolding installed without guardrails",
  "severity": "major",
  "category": "safety_violation",
  "assigned_to_contractor": "ABC Scaffolding Contractors",
  "assigned_to_user": 15,
  "location": "Block A, Level 3",
  "geo_location": {"lat": 12.345, "lng": 77.678},
  "evidence_photos": ["https://...", "https://..."],
  "due_date": "2025-11-15T17:00:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "NC NC-20251113-00001 created and contractor notified",
  "nc": {
    "id": 1,
    "nc_number": "NC-20251113-00001",
    "nc_title": "Unsafe scaffolding at Block A",
    "severity": "major",
    "verification_status": "pending_action",
    "is_closed": false
  }
}
```

**Auto Actions:**
- ✅ NC number auto-generated (NC-YYYYMMDD-NNNNN)
- ✅ WhatsApp sent to contractor
- ✅ Email sent to contractor
- ✅ In-app notification created

---

### **2. Get NC Dashboard (Contractor)**
```bash
GET /api/safety/nc/dashboard
```

**Response:**
```json
{
  "success": true,
  "dashboard": {
    "pending_action": 3,
    "action_submitted": 1,
    "overdue": 2,
    "closed": 15,
    "rejected": 1,
    "recent_ncs": [
      {
        "nc_number": "NC-20251113-00001",
        "nc_title": "Unsafe scaffolding",
        "severity": "major",
        "due_date": "2025-11-15T17:00:00",
        "is_overdue": false,
        "verification_status": "pending_action"
      }
    ]
  }
}
```

---

### **3. Get All NCs (Contractor)**
```bash
GET /api/safety/nc
GET /api/safety/nc?status=pending_action
GET /api/safety/nc?is_overdue=true
```

**Response:**
```json
{
  "success": true,
  "ncs": [
    {
      "id": 1,
      "nc_number": "NC-20251113-00001",
      "nc_title": "Unsafe scaffolding at Block A",
      "severity": "major",
      "assigned_to_contractor": "ABC Scaffolding",
      "verification_status": "pending_action",
      "due_date": "2025-11-15T17:00:00"
    }
  ]
}
```

**Auto Filtering:**
- If logged-in user is contractor → Shows only their NCs
- If logged-in user is safety officer → Shows all NCs

---

### **4. Submit Corrective Action (Contractor)**
```bash
POST /api/safety/nc/{nc_id}/action
```

**Request:**
```json
{
  "proposed_action": "Install guardrails on all four sides, add toe boards, ensure double handrails as per code",
  "action_taken": "Guardrails installed and inspected",
  "action_photos": [
    "https://storage.../before.jpg",
    "https://storage.../after.jpg"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Corrective action submitted for verification",
  "nc": {
    "nc_number": "NC-20251113-00001",
    "verification_status": "action_submitted",
    "action_completion_date": "2025-11-14T10:30:00"
  }
}
```

---

### **5. Verify NC (Safety Officer)**

**Approve:**
```bash
POST /api/safety/nc/{nc_id}/verify
```

```json
{
  "approved": true,
  "verification_notes": "Guardrails properly installed. Complies with safety standards.",
  "closure_remarks": "Satisfactory completion. No further action needed."
}
```

**Reject:**
```json
{
  "approved": false,
  "verification_notes": "Toe boards still missing. Handrails not at proper height (should be 1050mm)."
}
```

**Response (Approved):**
```json
{
  "success": true,
  "message": "NC NC-20251113-00001 verified and closed",
  "nc": {
    "verification_status": "verified",
    "is_closed": true,
    "closed_at": "2025-11-14T15:00:00"
  }
}
```

**Auto Actions:**
- ✅ Contractor receives WhatsApp/Email notification
- ✅ NC marked as closed in database
- ✅ Analytics updated

**Response (Rejected):**
```json
{
  "success": true,
  "message": "NC NC-20251113-00001 rejected. Contractor notified.",
  "nc": {
    "verification_status": "rejected",
    "is_closed": false
  }
}
```

**Auto Actions:**
- ✅ Contractor receives rejection notification with notes
- ✅ NC goes back to contractor for re-work
- ✅ Status: "rejected" (contractor can resubmit action)

---

### **6. Add Comments (Discussion)**
```bash
POST /api/safety/nc/{nc_id}/comments
```

```json
{
  "comment_text": "We need additional materials. Can we get 2 more days extension?",
  "attachments": ["https://storage.../material-quote.pdf"]
}
```

Allows discussion between safety officer and contractor.

---

### **7. Get Notifications**
```bash
GET /api/safety/nc/notifications
```

```json
{
  "success": true,
  "notifications": [
    {
      "notification_type": "nc_raised",
      "subject": "New NC Raised: NC-20251113-00001",
      "notification_channel": "whatsapp",
      "sent_at": "2025-11-13T09:30:00",
      "delivery_status": "sent"
    }
  ]
}
```

---

## 📊 NC Status Flow

| Status | Description | Who Can Change |
|--------|-------------|----------------|
| `pending_action` | NC raised, waiting for contractor response | Initial state |
| `action_submitted` | Contractor submitted corrective action | Contractor |
| `verified` | Safety officer approved the action | Safety Officer |
| `rejected` | Safety officer rejected (needs re-work) | Safety Officer |
| `closed` | NC fully closed | Safety Officer (after verify) |

---

## 🎯 User Roles & Permissions

### **Safety Officer**
- ✅ Create NC
- ✅ Verify/Reject NC
- ✅ View all NCs
- ✅ Add comments

### **Contractor**
- ✅ View assigned NCs
- ✅ Submit corrective actions
- ✅ Upload photos
- ✅ Add comments
- ❌ Cannot create NC
- ❌ Cannot verify/close NC

### **Admin**
- ✅ Full access to all NCs
- ✅ View analytics
- ✅ Generate reports

---

## 🔔 Notification Channels

### **WhatsApp** (Primary)
- Instant delivery
- High read rate
- Includes all NC details
- Sent via Twilio WhatsApp Business API

### **Email** (Secondary)
- Professional communication
- Includes attachments
- Good for record-keeping

### **In-App** (Always)
- Dashboard notifications
- Badge count
- Detailed view with photos

---

## 📈 Analytics & Tracking

### **Contractor Scorecard**
```bash
GET /api/safety/analytics/contractor-scorecard?contractor=ABC
```

Shows:
- Total NCs assigned
- NCs closed on time
- Overdue NCs
- Average closure time
- Rejection rate
- Safety score (0-100)

### **NC Trends**
```bash
GET /api/safety/analytics/nc-trends
```

Shows:
- NCs by severity (minor, major, critical)
- NCs by category (safety, quality, etc.)
- Monthly trends
- Most common violations

---

## 🚀 Next Steps

### 1. **Database Migration**
```bash
python3 -c "from server.db import init_db; from server.safety_nc_models import *; init_db()"
```

Creates tables:
- `safety_non_conformances`
- `safety_nc_comments`
- `safety_contractor_notifications`

### 2. **Test NC Workflow**
```bash
# 1. Safety officer creates NC
curl -X POST http://localhost:5000/api/safety/nc \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{...}'

# 2. Contractor views NCs
curl http://localhost:5000/api/safety/nc/dashboard \
  -H "Authorization: Bearer <contractor-token>"

# 3. Contractor submits action
curl -X POST http://localhost:5000/api/safety/nc/1/action \
  -H "Authorization: Bearer <contractor-token>" \
  -d '{...}'

# 4. Safety officer verifies
curl -X POST http://localhost:5000/api/safety/nc/1/verify \
  -H "Authorization: Bearer <token>" \
  -d '{"approved": true, ...}'
```

### 3. **Frontend Integration**
Build UI screens:
- NC creation form (safety officer)
- NC dashboard (contractor)
- NC details with photo viewer
- Comment/discussion thread
- Verification interface

---

## 💡 Example Scenario

**Scenario**: Safety officer finds scaffolding issue

1. **09:00 AM** - Safety officer inspects site, finds unsafe scaffolding
2. **09:15 AM** - Creates NC in ProSite app with photos
3. **09:15 AM** - Contractor "ABC Scaffolding" receives WhatsApp:
   ```
   🔴 NC Raised: NC-20251113-00001
   Unsafe scaffolding - Missing guardrails
   Due: 15-Nov-2025 17:00
   ```
4. **10:00 AM** - Contractor logs into ProSite, sees "1 Pending NC"
5. **10:30 AM** - Contractor reviews NC details, photos, location
6. **11:00 AM** - Contractor submits action plan: "Will install guardrails by 2 PM"
7. **02:00 PM** - Work completed, contractor uploads "after" photos
8. **02:30 PM** - Safety officer receives notification "Action submitted"
9. **03:00 PM** - Safety officer inspects work, approves closure
10. **03:01 PM** - Contractor receives:
    ```
    ✅ NC Closed: NC-20251113-00001
    Your corrective actions verified and approved.
    ```

---

## 🔐 Security Features

- ✅ Company data isolation (multi-tenant safe)
- ✅ Role-based access control
- ✅ JWT authentication required
- ✅ Contractors see only their NCs
- ✅ Audit trail (who raised, who verified, timestamps)
- ✅ Photo evidence with timestamps

---

## 📋 Summary

**Key Features:**
1. ✅ **Instant Notifications**: WhatsApp + Email + In-App
2. ✅ **Clear Assignment**: NC assigned to specific contractor
3. ✅ **Photo Evidence**: Before/after photos for verification
4. ✅ **Discussion Thread**: Comments for clarifications
5. ✅ **SLA Tracking**: Due dates and overdue alerts
6. ✅ **Verification Workflow**: Approve/Reject with notes
7. ✅ **Analytics**: Contractor scorecard and NC trends

**Benefits:**
- Contractors always know about NCs (multiple notification channels)
- Clear workflow from raise → action → verify → close
- Evidence-based closure (photos required)
- Accountability (who did what, when)
- Compliance tracking (ISO 9001, safety standards)

---

*This NC system ensures zero miscommunication between safety officers and contractors, with built-in notifications and tracking at every step.*
