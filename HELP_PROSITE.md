# 📖 ProSite Help Center - Complete User Guide

**Welcome to ProSite** - Your Complete Construction Safety & Quality Management System

---

## 🎯 Table of Contents

1. [Getting Started](#getting-started)
2. [Safety Workers Register](#safety-workers-register)
3. [Toolbox Talks (TBT) with QR Attendance](#toolbox-talks-tbt)
4. [Permit-to-Work (PTW)](#permit-to-work-ptw)
5. [Non-Conformance (NC) Management](#non-conformance-nc)
6. [Safety Observations](#safety-observations)
7. [Quality Training with QR Attendance](#quality-training)
8. [Troubleshooting](#troubleshooting)
9. [FAQs](#faqs)

---

## 🚀 Getting Started

### First Login

1. **Open ProSite** in your web browser: `https://prosite.app`
2. **Enter credentials** provided by your admin:
   - Email: `your.email@company.com`
   - Password: Your initial password
3. **Change password** on first login (mandatory)
4. **Select your project** from the dashboard

### Your Dashboard

Based on your role, you'll see different modules:

| Role | What You See |
|------|-------------|
| **Safety Officer** | Safety Workers, TBT, PTW, NC, Observations |
| **Site Engineer** | TBT (as conductor), PTW review, Observations |
| **Quality Engineer** | Quality Training, Material Tests, Cube Tests |
| **Contractor** | NC assigned to you, PTW submissions |
| **Worker** | Your profile, attendance history |

### Understanding Your Subscription

Your company's subscription determines which features you see:

- **Safety Only**: Safety Workers, TBT, PTW, NC, Observations
- **Concrete Only**: Mix Designs, Batches, Cube Tests, Quality Training
- **Both Apps**: All features + Cross-app Training QR Attendance

Check: Top-right menu → **"My Subscription"**

---

## 👷 Safety Workers Register

### Adding a New Worker (Safety Officer)

**Step 1**: Navigate to **Safety → Workers → Add Worker**

**Step 2**: Fill in worker details:
```
• Full Name: Mohammed Ali
• Worker Code: W12345 (unique, alphanumeric)
• Company: ABC Contractors
• Trade: Mason / Steel Fixer / Carpenter / etc.
• Phone: +91-XXXXXXXXXX
• Email: (optional)
• Photo: Upload clear face photo
```

**Step 3**: Click **"Generate QR Code"**
- System creates unique QR for this worker
- QR contains worker code (W12345)
- QR never expires (lifetime use)

**Step 4**: Print QR code:
- **Option 1**: Helmet sticker (30mm x 30mm, laminated)
- **Option 2**: ID card (credit card size, laminated)
- **Recommended**: Both (sticker as primary, card as backup)

**Step 5**: Save worker profile

### Printing Worker QR Codes

**Individual QR**:
1. Go to **Safety → Workers**
2. Click worker name
3. Click **"Download QR Code"**
4. Print on sticker paper (weatherproof recommended)

**Bulk QR Printing**:
1. Go to **Safety → Workers → Bulk Actions**
2. Select workers (or "Select All")
3. Click **"Print All QR Codes"**
4. Downloads PDF with all QR codes (A4 sheet, 12 stickers per page)

### QR Code Best Practices

✅ **DO**:
- Use weatherproof laminated stickers
- Place on front of helmet (clearly visible)
- Keep backup card in worker's pocket
- Re-print if QR damaged or faded

❌ **DON'T**:
- Use paper stickers (not weatherproof)
- Place QR on back of helmet (conductor can't scan)
- Share QR codes between workers (security risk)

---

## 📋 Toolbox Talks (TBT)

### For Conductors (Site Engineer / Safety Officer)

#### Creating a TBT Session

**Step 1**: Open **Safety → Toolbox Talks → New TBT**

**Step 2**: Fill session details:
```
• Topic: Select from library (22 topics) or create custom
  Examples: "Concrete Pouring Safety", "Working at Height"
  
• Location: Block A, Floor 5 / Ground Level / etc.

• Activity: Concreting / Blockwork / Steel Fixing / etc.

• Duration: 30 minutes (typical)

• Key Points: (Auto-filled from topic, editable)
  - Check formwork before pouring
  - Use proper PPE (helmet, boots, gloves)
  - Keep work area clean
  
• Hazards Discussed: (Auto-filled, editable)
  - Risk of falls from height
  - Concrete chemical burns
  - Slips on wet surfaces
  
• PPE Required: (Auto-filled, editable)
  - Safety helmet
  - Steel-toe boots
  - Rubber gloves
  - Safety goggles
```

**Step 3**: Click **"Create TBT"**
- System records YOU as conductor (auto-captured)
- Your name, role saved automatically
- Session status: "Active"

#### Conducting the TBT Briefing

**Before Workers Arrive** (7:00 AM):
1. Review key points, hazards, PPE requirements
2. Prepare any visual aids (photos of hazards)
3. Have tablet/phone ready for QR scanning

**During TBT** (7:30 AM - 8:00 AM):

**Phase 1: Briefing (25 minutes)**
1. Welcome workers, take roll call
2. Explain today's work scope
3. Discuss hazards specific to today's work
4. Demonstrate proper PPE usage
5. Explain emergency procedures (evacuation routes, first aid location)
6. Q&A session (encourage worker participation)

**Phase 2: Attendance via QR Scanning (5 minutes)**

⚠️ **IMPORTANT**: **Workers DON'T scan anything!** **YOU (conductor) scan worker QR codes!**

1. Click **"Mark Attendance"** in the app
2. Enable camera on your tablet/phone
3. **For each worker**:
   - Worker stands in front of you
   - Point camera at QR on worker's helmet
   - App scans QR → Reads worker code (W12345)
   - App shows worker details:
     ```
     ✅ Mohammed Ali
     ABC Contractors - Mason
     Mark Attendance?
     ```
   - Tap **"Yes"** → Attendance marked (07:52:13)
   - **Time taken**: 5 seconds per worker
   
4. **If QR damaged/missing**:
   - Tap **"Manual Entry"**
   - Type worker code: W12345
   - Or type name: Mohammed Ali
   - Select company from dropdown
   - Tap **"Add"**

**Real-time Attendance View**:
```
TBT Session #1234 - Concrete Pouring Safety
Conductor: Ahmed Hassan (Site Engineer)

Attendance (12 workers):
✅ M. Ali (W12345) - 07:52:13 - QR
✅ S. Patel (W12346) - 07:52:18 - QR
✅ V. Singh (W12347) - 07:52:23 - QR
✅ A. Hassan (W12348) - 07:52:28 - Manual (QR damaged)
... 8 more workers ...

Total: 12 workers in 60 seconds!
```

**Phase 3: Photo Evidence**
1. Tap **"Take Group Photo"**
2. Capture all workers in PPE
3. Photo auto-saved with session

**Phase 4: Complete Session**
1. Review attendance list (12/12 workers marked)
2. Tap **"Complete Session"**
3. Session locked (no further edits)
4. Status: "Completed"

#### After TBT

**Automatic Actions**:
- ✅ Session saved with timestamp
- ✅ Attendance records stored
- ✅ Your conductor performance updated
- ✅ Compliance report generated

**View Reports**:
- **Your Performance**: Safety → TBT → My Sessions
  - Sessions conducted: 67
  - Workers trained: 951
  - Average attendance: 14.2 per session
  
- **Monthly Compliance**: Safety → TBT → Reports
  - Days with TBT: 22/22 (100%)
  - Top conductors leaderboard

### For Workers

**What You Need**:
- ✅ QR code sticker on helmet (or backup card)
- ❌ **NO smartphone needed!**
- ❌ **NO app to download!**

**On TBT Day**:
1. Arrive at TBT location (7:30 AM)
2. Listen to conductor's safety briefing (25 minutes)
3. When conductor says "QR scanning time":
   - Stand in front of conductor
   - Conductor points tablet at your helmet QR
   - Wait for "beep" sound (2 seconds)
   - ✅ You're marked present!
4. That's it! Go to work safely.

**If QR Damaged**:
- Show your backup QR card to conductor, OR
- Tell conductor your worker code (W12345), OR
- Tell conductor your name (Mohammed Ali)
- Conductor will mark you manually

---

## 🔐 Permit-to-Work (PTW)

### For Contractors (Submitting PTW)

#### Creating a Permit

**Step 1**: Navigate to **Safety → Permit-to-Work → New Permit**

**Step 2**: Select permit type:
- Hot Work (welding, cutting, grinding)
- Confined Space Entry
- Work at Height (above 1.8 meters)
- Excavation
- Electrical Work
- Lifting Operations

**Step 3**: Fill permit details:
```
• Work Description: "Welding structural steel at Floor 5"
• Location: Block A, Floor 5, Grid E3
• Start Date/Time: 14-Nov-2025, 09:00 AM
• End Date/Time: 14-Nov-2025, 05:00 PM
• Validity Period: 8 hours
• Workers Involved: 4 (names: Ali, Patel, Singh, Kumar)
• Equipment: Welding machine, angle grinder, fire extinguisher
```

**Step 4**: Complete safety checklist:
```
Hot Work Checklist:
☑ Fire extinguisher available at work location
☑ Flammable materials removed (10-meter radius)
☑ Fire watch person assigned
☑ Welding machine inspected (cables, earth connection)
☑ Welders have valid competency certificates
☑ Emergency evacuation route clear
☑ First aid kit available
```

**Step 5**: Upload supporting documents:
- Risk assessment (PDF)
- Method statement (PDF)
- Worker competency certificates (if required)

**Step 6**: Add your signature:
- Type full name: "Ahmed Hassan"
- Tap **"Sign & Submit"**
- Status: "Pending Approval"

**What Happens Next**:
1. **Site Engineer** receives notification → Reviews → Approves/Rejects
2. **Safety Officer** receives notification → Final approval
3. You receive WhatsApp + Email notification when approved
4. Permit becomes "Active" → Work can start

#### Checking Permit Status

**Real-time Status**:
```
Permit #PTW-2025-0123
Status: 🟡 Pending Approval (Step 2/3)

Approval Chain:
✅ Ahmed Hassan (Contractor) - Submitted at 08:30 AM
✅ John David (Site Engineer) - Approved at 09:15 AM
⏳ Ravi Kumar (Safety Officer) - Pending

Estimated approval: 10:00 AM
```

### For Site Engineers (Reviewing PTW)

**Step 1**: Receive notification:
- 📧 Email: "PTW-2025-0123 awaits your review"
- 📱 WhatsApp: "New PTW from Ahmed Hassan"
- 🔔 In-app: Red badge on PTW icon

**Step 2**: Navigate to **Safety → Permit-to-Work → Pending Review**

**Step 3**: Click permit to review:
```
Permit Details:
• Type: Hot Work
• Contractor: ABC Contractors
• Work: Welding at Floor 5
• Duration: 8 hours
• Workers: 4 persons
```

**Step 4**: Verify checklist:
- ✅ All safety items checked
- ✅ Fire extinguisher confirmed
- ✅ Risk assessment attached
- ✅ Method statement approved

**Step 5**: Inspect work location (if required):
- Go to site
- Verify actual conditions match permit
- Check equipment availability
- Confirm workers competency

**Step 6**: Make decision:

**To Approve**:
1. Tap **"Approve"**
2. Add comments (optional): "Approved. Ensure fire watch throughout."
3. Sign digitally
4. Tap **"Submit Approval"**
5. Status: Forwarded to Safety Officer

**To Reject**:
1. Tap **"Reject"**
2. Add mandatory reason: "Fire extinguisher not available at location"
3. Tap **"Submit Rejection"**
4. Contractor receives notification to fix issues

### For Safety Officers (Final Approval)

Same process as Site Engineer, but you have final authority:
- If you approve → Permit becomes "Active"
- If you reject → Permit goes back to contractor

### Viewing Signature Board

**Real-time Approval Status**:
```
╔════════════════════════════════════════════════╗
║  PERMIT SIGNATURE BOARD - PTW-2025-0123       ║
╠════════════════════════════════════════════════╣
║                                                ║
║  1️⃣  Ahmed Hassan                             ║
║      Contractor - ABC Contractors              ║
║      ✍️ Signed: 14-Nov-2025 08:30:15 AM       ║
║      Status: ✅ Submitted                     ║
║                                                ║
║  2️⃣  John David                               ║
║      Site Engineer - Main Contractor           ║
║      ✍️ Signed: 14-Nov-2025 09:15:42 AM       ║
║      Status: ✅ Approved                      ║
║      Comment: "Approved. Ensure fire watch."  ║
║                                                ║
║  3️⃣  Ravi Kumar                               ║
║      Safety Officer - Main Contractor          ║
║      ✍️ Signed: 14-Nov-2025 09:45:18 AM       ║
║      Status: ✅ FINAL APPROVAL                ║
║      Comment: "Approved for 8 hours."         ║
║                                                ║
╠════════════════════════════════════════════════╣
║  PERMIT STATUS: 🟢 ACTIVE                     ║
║  Valid Until: 14-Nov-2025 05:00 PM            ║
╚════════════════════════════════════════════════╝
```

### During Work (Active Permit)

**Contractor Responsibilities**:
- Display permit at work location
- Ensure all workers have copy
- Follow safety checklist strictly
- Report any incidents immediately

**Auto-Expiry**:
- System automatically expires permit at end time
- WhatsApp notification sent 30 minutes before expiry
- Cannot continue work after expiry (need extension or new permit)

### Permit Extension

**If work not complete**:
1. Go to **Safety → PTW → My Permits**
2. Click active permit
3. Tap **"Request Extension"**
4. New end time: 14-Nov-2025 07:00 PM (+2 hours)
5. Reason: "Welding taking longer than expected"
6. Tap **"Submit Extension Request"**
7. Safety Officer approves/rejects

### Closing Permit

**After work complete**:
1. Contractor taps **"Close Permit"**
2. Upload completion photo (work area cleaned)
3. Confirm: "All tools removed, fire watch completed, area safe"
4. Safety Officer verifies and closes
5. Permit archived

---

## ⚠️ Non-Conformance (NC) Management

### For Safety Officers (Raising NC)

#### When to Raise NC

Raise NC when you observe:
- Workers without proper PPE
- Unsafe working conditions
- Violation of safety procedures
- Quality defects (concrete honeycombing, wrong rebar spacing)
- Housekeeping issues
- Permit violations

#### Creating NC

**Step 1**: Navigate to **Safety → Non-Conformance → Raise NC**

**Step 2**: Fill NC details:
```
• NC Type: Safety / Quality / Housekeeping
• Priority: Low / Medium / High / Critical
• Location: Block A, Floor 5, Grid E3
• Contractor: ABC Contractors
• Description: "3 workers observed without safety helmets at height work"
• Root Cause: Lack of supervision
```

**Step 3**: Take photo evidence (mandatory):
- Click **"Take Photo"** or upload from gallery
- Capture clear evidence of issue
- Multiple photos allowed (max 5)

**Step 4**: Set deadline:
- Target closure: 15-Nov-2025 (tomorrow)
- If not closed by deadline → Auto-escalation

**Step 5**: Click **"Raise NC"**

**Automatic Actions**:
- ✅ NC number assigned: NC-2025-0045
- ✅ Contractor receives **3 notifications**:
  1. 📱 **WhatsApp**: "NC raised by Safety Officer. Check app."
  2. 📧 **Email**: Full NC details with photo
  3. 🔔 **In-app**: Red badge on NC icon
- ✅ Site Manager notified
- ✅ Timer starts for closure deadline

### For Contractors (Resolving NC)

**Step 1**: Receive notifications (WhatsApp + Email + In-app)

**Step 2**: Navigate to **Safety → Non-Conformance → Assigned to Me**

**Step 3**: Click NC to view:
```
NC-2025-0045
Priority: 🔴 High
Raised by: Ravi Kumar (Safety Officer)
Date: 14-Nov-2025 10:30 AM

Issue: 3 workers without helmets at height work
Location: Block A, Floor 5
Photo: [View evidence]

Deadline: 15-Nov-2025 (23 hours remaining)
```

**Step 4**: Take corrective action:
- Provide helmets to all workers immediately
- Conduct toolbox talk on PPE importance
- Assign supervisor for continuous monitoring

**Step 5**: Reply to NC:
1. Tap **"Add Response"**
2. Type action taken: "All workers provided helmets. Supervisor assigned. TBT conducted."
3. Upload proof (before-after photos)
4. Tap **"Submit Response"**
5. Status: "Response Submitted" (awaits Safety Officer verification)

**Step 6**: Safety Officer verifies:
- Visits site to confirm action
- If satisfied: Closes NC
- If not satisfied: Adds comment → You take further action

### NC Closure

**Safety Officer**:
1. Visit site to verify corrective action
2. Take "after" photo (workers with helmets)
3. Tap **"Close NC"**
4. Add closure comments: "Verified. All workers now wearing helmets. Supervisor monitoring."
5. Status: "Closed"

**Contractor Dashboard**:
- View your NC performance:
  ```
  ABC Contractors - NC Performance
  
  Total NCs: 12
  Closed: 10 (83%)
  Open: 2 (17%)
  
  Average closure time: 1.5 days
  Target: < 2 days ✅
  
  NC by Priority:
  Critical: 1 (closed in 4 hours)
  High: 5 (avg 1 day)
  Medium: 4 (avg 2 days)
  Low: 2 (avg 3 days)
  ```

### NC Escalation (Auto)

**If NC not resolved by deadline**:
- System auto-escalates to Project Manager
- WhatsApp notification to contractor (urgent)
- Penalty may apply (as per contract)

---

## 👁️ Safety Observations

### For Everyone (All Users)

#### Reporting Safety Hazard

**Step 1**: Navigate to **Safety → Observations → New Observation**

**Step 2**: What did you observe?
```
• Observation Type:
  - Unsafe Condition (broken scaffolding, exposed wires)
  - Unsafe Act (worker smoking near fuel)
  - Near Miss (steel bar almost fell on worker)
  - Good Practice (to be appreciated)

• Priority:
  - Low: Minor issue, no immediate danger
  - Medium: Moderate risk, fix soon
  - High: Serious risk, fix today
  - Critical: Imminent danger, STOP WORK!

• Location: Block A, Floor 5, Grid E3

• Description: "Scaffolding plank loose at edge. Worker could fall."

• Suggested Action: "Secure plank with nails. Add toe board."
```

**Step 3**: Take photo (mandatory for Critical/High observations)

**Step 4**: Click **"Submit Observation"**

**Automatic Actions**:
- If Critical: SMS to Safety Officer + Site Manager (immediate)
- If High: WhatsApp + Email within 5 minutes
- Observation assigned to responsible person for action
- You receive updates on corrective action

#### Following Up

**Check your submissions**:
- **Safety → Observations → My Observations**
- View status: Pending / In Progress / Resolved / Closed
- Add comments if action not taken

### For Safety Officers (Acting on Observations)

**Review observations**:
1. **Safety → Observations → Pending Action**
2. Filter by priority (Critical first)
3. Click observation → View details
4. Assign to contractor/engineer
5. Set deadline
6. Monitor progress
7. Verify completion
8. Close observation

---

## 🎓 Quality Training with QR Attendance

### ⚠️ Available Only with BOTH Safety + Concrete Apps

This cross-app feature links:
- **Training sessions** (from Concrete/QMS app)
- **Workers** (from Safety app)

### For Trainers (Quality Engineer)

#### Creating Training Session

**Step 1**: Navigate to **Quality → Training → New Training**

**Step 2**: Training details:
```
• Topic: "Mix Design Procedures"
• Date: 15-Nov-2025
• Duration: 2 hours (9:00 AM - 11:00 AM)
• Location: Site Office Conference Room
• Training Type: Technical / Safety / Quality
```

**Step 3**: Click **"Create Training"**

#### Conducting Training

**During Training**:
1. Explain topic (mix design parameters, slump test, etc.)
2. Demonstrate procedures
3. Q&A session

**After Training - QR Attendance** (same as TBT):
1. Click **"Mark Attendance"**
2. Scan each worker's helmet QR code
3. Attendance marked in 5 seconds per worker

#### Post-Training Assessment

**Step 1**: Click **"Conduct Assessment"**

**Step 2**: For each worker:
```
• Worker: Mohammed Ali (W12345)
• Assessment Score: 85/100
• Passed: Yes (passing score: 60)
• Issue Certificate: Yes
```

**Step 3**: Click **"Submit Assessments"**

**Automatic Actions**:
- ✅ Certificates generated: CERT-{training_id}-{worker_id}-{date}
- ✅ Worker receives certificate via email
- ✅ Certificate stored in worker profile
- ✅ Compliance records updated

### For Workers

**Your Certifications**:
- Navigate to **My Profile → Certifications**
- View all certificates:
  ```
  Mohammed Ali (W12345)
  
  Certifications:
  1. Mix Design Procedures
     Score: 85/100
     Date: 15-Nov-2025
     Certificate: CERT-123-456-20251115
     Download PDF
     
  2. Concrete Testing
     Score: 88/100
     Date: 10-Oct-2025
     
  3. Safety Awareness
     Score: 95/100
     Date: 05-Sep-2025
  ```

---

## 🔧 Troubleshooting

### Common Issues

#### "QR Code Not Scanning"

**Problem**: Conductor's camera not detecting worker QR

**Solutions**:
1. ✅ Clean camera lens (wipe with cloth)
2. ✅ Improve lighting (move to brighter area)
3. ✅ Hold steady (don't shake tablet)
4. ✅ Adjust distance (15-30 cm from QR)
5. ✅ Check QR not damaged (if faded, re-print)
6. ✅ Use manual entry (type worker code instead)

#### "Can't Login"

**Problem**: Email/password not working

**Solutions**:
1. ✅ Check email spelling (case-sensitive)
2. ✅ Check Caps Lock OFF
3. ✅ Click "Forgot Password" → Reset via email
4. ✅ Contact admin if still issues

#### "Don't See Safety Features"

**Problem**: Menu shows only Concrete features

**Solution**:
- Your company subscribed to **Concrete-only** app
- Contact admin to upgrade to **Both Apps** subscription
- Check: Top-right menu → "My Subscription"

#### "Permit Stuck in Pending"

**Problem**: PTW waiting approval for hours

**Solutions**:
1. ✅ Check who needs to approve (signature board)
2. ✅ Contact that person (WhatsApp/call)
3. ✅ Ensure all documents uploaded
4. ✅ Check no rejection comments (fix issues)

#### "NC Notification Not Received"

**Problem**: Contractor didn't get WhatsApp for NC

**Solutions**:
1. ✅ Check WhatsApp number correct in profile
2. ✅ Check in-app notifications (red badge)
3. ✅ Check email (may be in spam folder)
4. ✅ Ask Safety Officer to re-send notification

---

## ❓ FAQs

### General

**Q: Do workers need smartphones for TBT?**  
**A**: NO! Conductor scans worker QR codes. Workers just wear helmet with QR sticker.

**Q: What if worker forgets helmet with QR?**  
**A**: Conductor can mark attendance manually by typing worker code or name.

**Q: Can one worker use another's QR?**  
**A**: No! Conductor verifies face matches name. Proxy attendance is violation (can lead to NC).

**Q: How long is worker QR valid?**  
**A**: Lifetime! QR never expires. Print once, use forever (unless damaged).

### TBT

**Q: Must we conduct TBT daily?**  
**A**: YES! ISO 45001 requires daily safety briefing before work starts.

**Q: Can TBT be conducted in local language?**  
**A**: YES! Conductor explains in language workers understand (Hindi/Tamil/Telugu/etc.). App records in English.

**Q: What if less than 5 workers present?**  
**A**: Still conduct TBT! Even 1 worker needs safety briefing before work.

**Q: How long should TBT last?**  
**A**: Minimum 15 minutes. Typical: 20-30 minutes. Complex work: 45 minutes.

### Permit-to-Work

**Q: Can work start without approved permit?**  
**A**: ABSOLUTELY NOT! Starting high-risk work without permit is serious safety violation.

**Q: What if Safety Officer on leave?**  
**A**: Assign alternate approver in system. Or deputy Safety Officer approves.

**Q: Can permit be approved verbally?**  
**A**: NO! Digital approval in system mandatory for audit trail.

**Q: Permit expired but work not done?**  
**A**: STOP WORK immediately! Request extension or create new permit.

### Non-Conformance

**Q: Will NC affect contractor payment?**  
**A**: Depends on contract. Multiple critical NCs may lead to penalty as per agreement.

**Q: Can contractor close own NC?**  
**A**: NO! Only Safety Officer can close after verification.

**Q: Anonymous NC allowed?**  
**A**: Yes! For safety observations, anonymous reporting encouraged. Go to Safety → Observations → Report Anonymously.

### Technical

**Q: Does app work offline?**  
**A**: Partially. QR scanning requires internet. Future version will support offline mode.

**Q: Can I access from mobile?**  
**A**: YES! Web app is mobile-responsive. Native Android/iOS app coming soon.

**Q: How to export TBT reports?**  
**A**: Safety → TBT → Reports → Select date range → Download PDF/Excel

**Q: Data backup frequency?**  
**A**: Real-time to cloud. Daily backups. 99.9% uptime guaranteed.

---

## 📞 Support

### Need Help?

**Method 1: In-App Chat**
- Click 💬 icon (bottom-right corner)
- Type your question
- Support team responds within 2 hours

**Method 2: Email**
- support@prosite.app
- Include: Your company name, project name, screenshot
- Response: Within 24 hours

**Method 3: WhatsApp**
- +91-XXXXX-XXXXX
- Monday-Saturday, 9 AM - 6 PM

**Method 4: Training Request**
- For new users: Request on-site training
- Email: training@prosite.app
- We visit your site and train your team (free for first 3 months)

### Report Bug

Found an issue?
1. Click **Help → Report Bug**
2. Describe what happened
3. Upload screenshot (if possible)
4. We fix within 48 hours

### Feature Request

Want new feature?
1. Click **Help → Suggest Feature**
2. Describe what you need
3. We review and add to roadmap

---

## 📱 Mobile App (Coming Soon)

**Android + iOS Native App**:
- Download from Google Play / App Store
- Faster QR scanning
- Works offline
- Push notifications
- Available: March 2026

---

## 🎓 Training Videos

**Watch step-by-step tutorials**:

1. **Getting Started** (5 min)
   - First login, dashboard overview
   - Watch: https://prosite.app/help/videos/getting-started

2. **TBT with QR Scanning** (10 min)
   - Creating TBT, scanning worker QRs, completing session
   - Watch: https://prosite.app/help/videos/tbt-qr

3. **Permit-to-Work Complete Flow** (15 min)
   - Contractor submission, approval workflow, signature board
   - Watch: https://prosite.app/help/videos/ptw-flow

4. **NC Management** (8 min)
   - Raising NC, contractor response, closure
   - Watch: https://prosite.app/help/videos/nc-management

5. **Safety Observations** (5 min)
   - Reporting hazards, following up
   - Watch: https://prosite.app/help/videos/observations

---

## 📚 Additional Resources

- **User Manual PDF**: [Download](https://prosite.app/downloads/user-manual.pdf)
- **Admin Guide PDF**: [Download](https://prosite.app/downloads/admin-guide.pdf)
- **API Documentation**: [View](https://prosite.app/docs/api)
- **Release Notes**: [View](https://prosite.app/changelog)

---

**Last Updated**: November 13, 2025  
**Version**: 1.0  
**Help Center**: https://help.prosite.app

---

*ProSite - Making Construction Sites Safer, One QR Code at a Time* 🏗️✅
