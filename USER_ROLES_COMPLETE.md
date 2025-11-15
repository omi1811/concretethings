# 🏗️ ProSite - Comprehensive User Roles & Permissions

## Overview
ProSite is a multi-industry site management platform designed for construction, manufacturing, facilities management, and other sectors requiring quality, safety, and project management systems.

---

## 🎭 User Roles Hierarchy

### 1. **System Administrator**
**Industry Scope**: All Industries  
**Access Level**: Full System Access  
**Module Access**: All Modules

#### Responsibilities:
- Complete system configuration and settings management
- User account creation, modification, and deletion
- Role and permission assignment for all users
- Database backup and system maintenance
- Integration setup (SMTP, APIs, third-party services)
- Subscription and billing management
- System monitoring and performance optimization
- Security settings and audit log review
- Multi-project oversight across organization

#### Authorities:
✅ Create/Edit/Delete all users across all projects  
✅ Assign/modify any role  
✅ Access all modules and data  
✅ Configure system-wide settings  
✅ View all audit logs and system reports  
✅ Manage subscriptions and billing  
✅ Database administration  
✅ API key management  

#### Restrictions:
❌ None - Full system access

---

### 2. **Project Manager**
**Industry Scope**: Construction, Infrastructure, Manufacturing  
**Access Level**: Project-Level Full Access  
**Module Access**: All project-specific modules

#### Responsibilities:
- Overall project planning and execution
- Resource allocation and budget management
- Team coordination and task assignment
- Project timeline and milestone tracking
- Client communication and reporting
- Quality and safety oversight
- Material procurement approval
- Contractor management
- Risk management and mitigation
- Project documentation and closeout

#### Authorities:
✅ View/Edit all project data  
✅ Assign tasks to team members  
✅ Approve batches, materials, and tests  
✅ Create and manage NCRs  
✅ Generate project reports  
✅ Access analytics dashboards  
✅ Approve permit-to-work (PTW)  
✅ Manage project team members  
✅ Budget and cost tracking  

#### Restrictions:
❌ Cannot create/delete users  
❌ Cannot access other projects  
❌ Cannot modify system settings  
❌ Cannot manage subscriptions  

---

### 3. **Quality Engineer**
**Industry Scope**: Construction, Manufacturing, Quality Control Labs  
**Access Level**: Quality Module Full Access  
**Module Access**: Batches, Cube Tests, Material Tests, NCR, Labs, Reports

#### Responsibilities:
- Conduct concrete cube testing (7, 14, 28 days)
- Material testing and certification review
- Quality control inspections and audits
- Non-conformance reporting and tracking
- Lab coordination and sample management
- Test result analysis and reporting
- Quality documentation and ISO compliance
- Batch acceptance/rejection decisions
- Supplier quality assessment
- Corrective action verification

#### Authorities:
✅ Create/Edit batch records  
✅ Record cube test results  
✅ Perform material tests  
✅ Issue NCRs (Non-Conformance Reports)  
✅ Reject non-compliant batches  
✅ Access quality analytics  
✅ Generate test certificates  
✅ Manage lab schedules  
✅ Review supplier documents  

#### Restrictions:
❌ Cannot approve budgets  
❌ Cannot manage users  
❌ Limited safety module access (view only)  
❌ Cannot delete test records (audit trail)  

---

### 4. **Safety Engineer / Safety Officer**
**Industry Scope**: All Industries (Construction, Manufacturing, Facilities)  
**Access Level**: Safety Module Full Access  
**Module Access**: Safety NC, PTW, Training, Toolbox Talks, Incidents, Inspections

#### Responsibilities:
- Site safety inspections and audits
- Incident investigation and reporting
- Safety non-conformance (NC) management
- Permit-to-work (PTW) issuance and monitoring
- Safety training coordination
- Toolbox talk delivery and documentation
- PPE compliance monitoring
- Risk assessment and HIRA (Hazard Identification & Risk Assessment)
- Emergency response coordination
- Safety performance tracking (KPIs)

#### Authorities:
✅ Create/Edit safety NCRs  
✅ Issue and approve PTW  
✅ Conduct safety inspections  
✅ Record incidents and near-misses  
✅ Schedule and track training  
✅ Generate safety reports  
✅ Access safety analytics  
✅ Issue safety violations  
✅ Conduct toolbox talks  
✅ Review safety documentation  

#### Restrictions:
❌ Cannot access quality test data  
❌ Cannot approve project budgets  
❌ Cannot manage users  
❌ Cannot access other projects  

---

### 5. **Building Engineer / Site Engineer**
**Industry Scope**: Construction, Infrastructure, Facilities Management  
**Access Level**: Project Execution Access  
**Module Access**: Pour Activities, Batches, Materials, Equipment, Daily Reports

#### Responsibilities:
- Supervise concrete pouring activities
- Coordinate with suppliers for material delivery
- Monitor construction progress
- Equipment management and maintenance
- Daily site reporting
- Coordinate with subcontractors
- Ensure work quality and specifications
- Material receipt and inspection
- RFI (Request for Information) management
- As-built documentation

#### Authorities:
✅ Create pour activity records  
✅ Log batch deliveries  
✅ Record material usage  
✅ Equipment check-in/check-out  
✅ Submit daily progress reports  
✅ View project drawings and specs  
✅ Request materials  
✅ Coordinate with Quality Engineer  

#### Restrictions:
❌ Cannot approve/reject batches (QE only)  
❌ Cannot issue NCRs  
❌ Cannot manage safety records  
❌ Cannot access financial data  
❌ Cannot modify project settings  

---

### 6. **Contractor Supervisor**
**Industry Scope**: Construction, Subcontractor Management  
**Access Level**: Extended Project Access (Quality NC Response, Safety NCs, PTW, TBT)  
**Module Access**: Assigned Tasks, Timesheets, Daily Reports, Materials (View), Quality NCR (View/Respond), Safety NC, PTW, Training

#### Responsibilities:
- Supervise subcontractor workforce
- Task execution as per project plan
- Timesheet submission for workers
- Daily progress reporting
- Material usage tracking
- **Respond to Quality Non-Conformances (NCRs)** with corrective action plans
- **Close safety non-conformances (NCs)** after corrective actions
- **Fill and submit Safety Work Permits (PTW)** for crew activities
- **Conduct Toolbox Talks (TBT)** for crew safety training
- Quality compliance at crew level
- Safety compliance for crew
- Coordinate with Building Engineer
- Equipment and tool management
- Rework coordination

#### Authorities:
✅ View assigned tasks  
✅ Submit timesheets  
✅ Record daily progress  
✅ View material allocations  
✅ **View Quality NCs assigned to crew**  
✅ **Respond to Quality NCRs** with corrective action plans (root cause, solution, timeline)  
✅ **Create and close safety NCs** (for crew-related issues)  
✅ **Fill Safety Work Permits (PTW)** (submit for approval)  
✅ **Conduct Toolbox Talks (TBT)** and mark crew attendance  
✅ Upload photos/documentation  
✅ View safety requirements  
✅ Communicate with project team  

#### Restrictions:
❌ Cannot create Quality NCRs (Quality Engineer only)  
❌ Cannot approve Quality NCRs (Quality Manager only)  
❌ Cannot create batches or tests  
❌ Cannot approve PTW (Safety Engineer/Manager only)  
❌ Cannot access other contractor data  
❌ Cannot view project financials  
❌ Cannot modify project schedule  

---

### 7. **Watchman / Security Guard**
**Industry Scope**: All Industries (Site Security)  
**Access Level**: Gate/Security Module Access + Worker Attendance  
**Module Access**: Gate Register, Vehicle Log, RMC Register, Worker Attendance, Visitor Management, Incident Reporting

#### Responsibilities:
- Site gate management
- Vehicle entry/exit logging
- **RMC delivery register entry** (basic details, slump/temperature optional)
- **Worker attendance tracking** (QR code scanning for entry/exit)
- Material delivery verification
- Visitor registration and escort
- Security incident reporting
- Patrol and surveillance
- Access control enforcement
- Emergency contact coordination
- Lost and found management
- After-hours monitoring

#### Authorities:
✅ Register vehicles (in/out)  
✅ **Fill RMC register** (without mandatory slump/temperature)  
✅ **Scan QR codes for worker attendance** (entry/exit tracking)  
✅ Log material deliveries  
✅ Register visitors  
✅ Report security incidents  
✅ View gate logs  
✅ Check vehicle documents  
✅ Issue temporary passes  

#### Restrictions:
❌ Cannot approve batches (Quality Engineer only)  
❌ Cannot fill quality parameters (slump/temperature - QE only)  
❌ Cannot view project data beyond gate operations  
❌ Cannot access financial information  
❌ Cannot generate reports  
❌ Read-only access to delivery notes  

---

### 8. **Client / Client Representative**
**Industry Scope**: All Industries  
**Access Level**: Read-Only Project Access  
**Module Access**: Reports, Analytics, Progress Photos, Documents (View Only)

#### Responsibilities:
- Monitor project progress
- Review quality and safety reports
- Access project documentation
- Attend project meetings
- Provide feedback and approvals
- Review test results and certificates
- Monitor budget and timeline
- Request information and clarifications

#### Authorities:
✅ View project dashboard  
✅ Access reports and analytics  
✅ View test results  
✅ Download certificates  
✅ View progress photos  
✅ Access project documents  
✅ Submit feedback/comments  
✅ View project timeline  

#### Restrictions:
❌ Cannot create/edit any records  
❌ Cannot access internal communications  
❌ Cannot view cost breakdowns (unless approved)  
❌ Cannot access system settings  
❌ Cannot download raw data  
❌ Cannot access other projects  

---

### 9. **Auditor / Inspector**
**Industry Scope**: Quality Assurance, Compliance, Third-Party Inspection  
**Access Level**: Read-Only Full Project Access  
**Module Access**: All modules (Read-Only)

#### Responsibilities:
- Conduct compliance audits (ISO 9001, ISO 45001)
- Review quality and safety documentation
- Verify test results and certifications
- Inspect NCR closure effectiveness
- Assess system conformance
- Generate audit reports
- Recommend improvements
- Verify corrective actions
- Check regulatory compliance

#### Authorities:
✅ View all project data  
✅ Access all test records  
✅ Review all NCRs  
✅ View safety records  
✅ Access audit trails  
✅ Generate audit reports  
✅ Download documentation  
✅ Submit audit findings  

#### Restrictions:
❌ Cannot create/edit/delete any records  
❌ Cannot approve/reject items  
❌ Cannot access user management  
❌ Cannot modify system settings  
❌ Cannot access financial data (unless specified)  

---

### 10. **Supplier / Material Vendor**
**Industry Scope**: Manufacturing, Construction Supply Chain  
**Access Level**: Limited Portal Access  
**Module Access**: Orders, Deliveries, Certificates, Invoices

#### Responsibilities:
- Submit material delivery schedules
- Upload material certificates (MTCs, COAs)
- Track purchase orders
- Submit invoices
- Respond to quality queries
- Update delivery status
- Provide technical data sheets
- Handle returns and replacements

#### Authorities:
✅ View assigned purchase orders  
✅ Upload delivery documents  
✅ Submit material certificates  
✅ Update delivery status  
✅ Upload invoices  
✅ View rejection notices  
✅ Communicate with Quality Engineer  

#### Restrictions:
❌ Cannot access project data  
❌ Cannot view other supplier information  
❌ Cannot access test results  
❌ Cannot modify approved documents  
❌ Cannot view project timeline  
❌ Cannot access financial data  

---

### 11. **Quality Manager**
**Industry Scope**: Construction, Manufacturing, Quality Assurance  
**Access Level**: Quality Module Full Access + Approvals  
**Module Access**: All Quality Modules + Reports + Analytics

#### Responsibilities:
- Quality system oversight
- Approve quality procedures
- Review and approve NCRs
- Manage quality team
- ISO compliance management
- Quality audit coordination
- Approve corrective actions
- Quality KPI monitoring
- Supplier quality management
- Management review preparation

#### Authorities:
✅ All Quality Engineer authorities  
✅ Approve/reject NCRs  
✅ Approve corrective actions  
✅ Manage quality team  
✅ Generate management reports  
✅ Access all quality analytics  
✅ Approve quality procedures  
✅ Supplier assessment approval  

#### Restrictions:
❌ Cannot manage users outside quality team  
❌ Cannot access safety module (full)  
❌ Cannot modify system settings  

---

### 12. **Safety Manager**
**Industry Scope**: All Industries  
**Access Level**: Safety Module Full Access + Approvals  
**Module Access**: All Safety Modules + Reports + Analytics

#### Responsibilities:
- Safety system oversight
- Approve safety procedures
- Review and approve safety NCRs
- Manage safety team
- ISO 45001 compliance
- Safety audit coordination
- Approve PTW for high-risk work
- Safety KPI monitoring
- Emergency response planning
- Management review (safety)

#### Authorities:
✅ All Safety Engineer authorities  
✅ Approve high-risk PTW  
✅ Close safety NCRs  
✅ Manage safety team  
✅ Generate safety reports  
✅ Access all safety analytics  
✅ Approve safety procedures  
✅ Issue stop-work orders  

#### Restrictions:
❌ Cannot manage users outside safety team  
❌ Cannot access quality module (full)  
❌ Cannot modify system settings  

---

## 📊 Permission Matrix

| Module | System Admin | Project Manager | Quality Engineer | Safety Engineer | Building Engineer | Contractor Supervisor | Watchman | Client | Auditor | Supplier | Quality Manager | Safety Manager |
|--------|--------------|-----------------|------------------|-----------------|-------------------|----------------------|----------|--------|---------|----------|-----------------|----------------|
| **Dashboard** | Full | Full | Full | Full | Full | Limited | Limited | View | View | Limited | Full | Full |
| **Projects** | Full | Full | View | View | View | View | None | View | View | None | View | View |
| **Batches** | Full | Full | Full | View | Full | View | Create* | View | View | Upload | Full | View |
| **Cube Tests** | Full | Full | Full | View | View | View | None | View | View | None | Full | View |
| **Material Tests** | Full | Full | Full | View | View | View | None | View | View | Upload | Full | View |
| **NCR (Quality)** | Full | Full | Full | View | View | View+Respond** | None | View | View | None | Full | View |
| **Safety NC** | Full | Full | View | Full | View | Create+Close | View | View | View | None | View | Full |
| **PTW** | Full | Full | View | Full | View | Create | View | View | View | None | View | Full |
| **Training** | Full | Full | View | Full | View | Create | View | View | View | None | View | Full |
| **Worker Attendance** | Full | Full | View | View | View | Mark | Mark | None | View | None | View | View |
| **Pour Activities** | Full | Full | View | View | Full | View | None | View | View | None | View | View |
| **Labs** | Full | Full | Full | View | View | None | None | View | View | None | Full | View |
| **Handovers** | Full | Full | View | View | Full | None | None | View | View | None | View | View |
| **Gate Register** | Full | View | View | View | View | View | Full | None | View | None | View | View |
| **Reports** | Full | Full | Full | Full | View | View | View | View | Full | View | Full | Full |
| **Analytics** | Full | Full | Full | Full | View | None | None | View | Full | None | Full | Full |
| **User Management** | Full | Limited | None | None | None | None | None | None | None | None | None | None |
| **Settings** | Full | Limited | None | None | None | None | None | None | None | None | None | None |

**Legend:**
- `*` Batches: Watchman can create basic entries (slump/temp optional)
- `**` NCR (Quality): Contractor Supervisor can View and Respond with corrective action plans

---

## 🔐 Access Control Implementation

### Role Hierarchy:
```
System Administrator (Level 1)
    ├── Project Manager (Level 2)
    │   ├── Quality Manager (Level 3)
    │   │   └── Quality Engineer (Level 4)
    │   ├── Safety Manager (Level 3)
    │   │   └── Safety Engineer (Level 4)
    │   └── Building Engineer (Level 4)
    │       └── Contractor Supervisor (Level 5)
    ├── Watchman (Level 5)
    ├── Client (External - View Only)
    ├── Auditor (External - View Only)
    └── Supplier (External - Limited)
```

### Permission Levels:
- **Full**: Create, Read, Update, Delete
- **Limited**: Create, Read, Update (specific records only)
- **View**: Read-only access
- **Report**: Can report incidents only
- **Upload**: Can upload documents only
- **None**: No access

---

## 🏭 Industry-Specific Role Mapping

### Construction Industry:
- System Administrator → IT Manager
- Project Manager → Site Manager
- Quality Engineer → QC Engineer
- Safety Engineer → HSE Officer
- Building Engineer → Site Engineer
- Contractor Supervisor → Foreman
- Watchman → Security Guard
- Client → Owner Representative

### Manufacturing Industry:
- System Administrator → IT Admin
- Project Manager → Production Manager
- Quality Engineer → QA Inspector
- Safety Engineer → Safety Officer
- Building Engineer → Production Supervisor
- Contractor Supervisor → Shift Lead
- Watchman → Security
- Supplier → Raw Material Vendor

### Facilities Management:
- System Administrator → Facilities IT
- Project Manager → Facilities Manager
- Quality Engineer → Maintenance QC
- Safety Engineer → HSE Coordinator
- Building Engineer → Maintenance Engineer
- Contractor Supervisor → Service Vendor
- Watchman → Security Guard
- Client → Tenant/Occupant

---

## 🎯 Implementation Notes

### Backend Implementation:
1. Role-based authentication middleware
2. Permission decorators on API routes
3. Database role assignment per user
4. Module-level access control
5. Data isolation per project
6. Audit logging for all actions

### Frontend Implementation:
1. Role-based navigation menu
2. Conditional component rendering
3. Permission-based button visibility
4. Route guards and access control
5. Module-specific dashboards
6. Role-appropriate UI/UX

---

## ✅ Commercial Readiness

This comprehensive role system ensures:
- ✅ Multi-industry applicability
- ✅ Scalable from 5 to 500+ users
- ✅ Clear separation of duties
- ✅ Audit trail compliance
- ✅ ISO 9001 & ISO 45001 alignment
- ✅ Data security and privacy
- ✅ Enterprise-grade access control

**Status**: Ready for commercial deployment and on-site testing.
