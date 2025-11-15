# System Admin Workflow - Complete Guide

## 🎯 Scenario: System Admin Managing 3 Projects

**User:** Test System Admin  
**Role:** `system_admin`  
**Projects:** 3 (Commercial Tower, Residential Complex, Infrastructure Project)  
**Tasks:** Create projects, add users, manage teams, oversee operations

---

## 📋 Table of Contents

1. [System Admin Login & Setup](#1-system-admin-login--setup)
2. [Creating 3 Projects](#2-creating-3-projects)
3. [Adding Users to Projects](#3-adding-users-to-projects)
4. [Managing Project Teams](#4-managing-project-teams)
5. [System Admin Daily Tasks](#5-system-admin-daily-tasks)
6. [Monitoring & Reports](#6-monitoring--reports)
7. [Troubleshooting Common Issues](#7-troubleshooting-common-issues)

---

## 1. System Admin Login & Setup

### **Step 1.1: Register as System Admin**

**API Endpoint:** `POST /api/auth/register`

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@prosite.com",
    "password": "Admin@ProSite2024",
    "full_name": "System Administrator",
    "phone": "+91-9876543210",
    "role": "system_admin",
    "company_name": "ProSite Corp",
    "is_system_admin": true
  }'
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "admin@prosite.com",
    "full_name": "System Administrator",
    "role": "system_admin",
    "is_system_admin": true
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Frontend (Next.js):**
```javascript
// app/register/page.js
const handleRegister = async (e) => {
  e.preventDefault();
  
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: formData.email,
      password: formData.password,
      full_name: formData.full_name,
      phone: formData.phone,
      role: 'system_admin',
      is_system_admin: true
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    router.push('/dashboard');
  }
};
```

---

### **Step 1.2: Login to Dashboard**

**API Endpoint:** `POST /api/auth/login`

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@prosite.com",
    "password": "Admin@ProSite2024"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "admin@prosite.com",
    "full_name": "System Administrator",
    "role": "system_admin"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Save token for subsequent requests:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 2. Creating 3 Projects

System Admin can create projects for different clients and purposes.

### **Project 1: Commercial Tower**

**API Endpoint:** `POST /api/projects`

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cyber City Commercial Tower",
    "description": "40-story commercial office complex with retail podium",
    "location": "Gurugram, Haryana",
    "start_date": "2024-01-15T00:00:00Z",
    "expected_end_date": "2026-06-30T00:00:00Z",
    "budget": 500000000.00,
    "client_name": "Cyber Realty Developers Ltd",
    "project_type": "commercial",
    "area_sqft": 1200000
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Project created successfully",
  "project": {
    "id": 1,
    "name": "Cyber City Commercial Tower",
    "location": "Gurugram, Haryana",
    "budget": 500000000.00,
    "status": "active",
    "created_by": 1
  }
}
```

---

### **Project 2: Residential Complex**

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Residential Complex",
    "description": "Luxury 6-tower residential project with 1500+ apartments",
    "location": "Pune, Maharashtra",
    "start_date": "2024-03-01T00:00:00Z",
    "expected_end_date": "2027-12-31T00:00:00Z",
    "budget": 1200000000.00,
    "client_name": "Green Valley Builders Pvt Ltd",
    "project_type": "residential",
    "area_sqft": 3000000
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Project created successfully",
  "project": {
    "id": 2,
    "name": "Green Valley Residential Complex",
    "location": "Pune, Maharashtra",
    "budget": 1200000000.00,
    "status": "active",
    "created_by": 1
  }
}
```

---

### **Project 3: Infrastructure Project**

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eastern Peripheral Expressway Bridge",
    "description": "Cable-stayed bridge construction - 2.5km span",
    "location": "Delhi NCR",
    "start_date": "2024-06-01T00:00:00Z",
    "expected_end_date": "2028-03-31T00:00:00Z",
    "budget": 3500000000.00,
    "client_name": "National Highways Authority of India (NHAI)",
    "project_type": "infrastructure",
    "area_sqft": null
  }'
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Project created successfully",
  "project": {
    "id": 3,
    "name": "Eastern Peripheral Expressway Bridge",
    "location": "Delhi NCR",
    "budget": 3500000000.00,
    "status": "active",
    "created_by": 1
  }
}
```

---

### **Verify Projects Created**

```bash
curl -X GET http://localhost:5000/api/projects \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "projects": [
    {
      "id": 1,
      "name": "Cyber City Commercial Tower",
      "location": "Gurugram, Haryana",
      "status": "active"
    },
    {
      "id": 2,
      "name": "Green Valley Residential Complex",
      "location": "Pune, Maharashtra",
      "status": "active"
    },
    {
      "id": 3,
      "name": "Eastern Peripheral Expressway Bridge",
      "location": "Delhi NCR",
      "status": "active"
    }
  ],
  "total": 3
}
```

---

## 3. Adding Users to Projects

System Admin needs to build teams for each project.

### **Step 3.1: Create User Accounts**

**Create Quality Manager for All Projects:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "qm@prosite.com",
    "password": "QualityManager@2024",
    "full_name": "Rajesh Kumar (Quality Manager)",
    "phone": "+91-9876543211",
    "role": "quality_manager"
  }'
```

**Create Project Manager for Commercial Tower:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "pm.commercial@prosite.com",
    "password": "ProjectManager@2024",
    "full_name": "Amit Sharma (PM - Commercial)",
    "phone": "+91-9876543212",
    "role": "project_manager"
  }'
```

**Create Quality Engineer for Commercial Tower:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "qe.commercial@prosite.com",
    "password": "QualityEng@2024",
    "full_name": "Priya Singh (QE - Commercial)",
    "phone": "+91-9876543213",
    "role": "quality_engineer"
  }'
```

**Create Contractor Supervisor:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "supervisor.commercial@prosite.com",
    "password": "Supervisor@2024",
    "full_name": "Suresh Patil (Contractor Supervisor)",
    "phone": "+91-9876543214",
    "role": "contractor_supervisor"
  }'
```

**Create Watchman:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "watchman.commercial@prosite.com",
    "password": "Watchman@2024",
    "full_name": "Raju Yadav (Gate Security)",
    "phone": "+91-9876543215",
    "role": "watchman"
  }'
```

**Repeat for Residential & Infrastructure Projects...**

---

### **Step 3.2: Add Users to Project 1 (Commercial Tower)**

**API Endpoint:** `POST /api/projects/{project_id}/members`

**Add Project Manager:**
```bash
curl -X POST http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "role": "project_manager"
  }'
```

**Add Quality Engineer:**
```bash
curl -X POST http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "role": "quality_engineer"
  }'
```

**Add Contractor Supervisor:**
```bash
curl -X POST http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 4,
    "role": "contractor_supervisor"
  }'
```

**Add Watchman:**
```bash
curl -X POST http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 5,
    "role": "watchman"
  }'
```

---

### **Step 3.3: Verify Project Team**

```bash
curl -X GET http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "project": {
    "id": 1,
    "name": "Cyber City Commercial Tower"
  },
  "members": [
    {
      "user_id": 2,
      "full_name": "Amit Sharma (PM - Commercial)",
      "role": "project_manager",
      "email": "pm.commercial@prosite.com"
    },
    {
      "user_id": 3,
      "full_name": "Priya Singh (QE - Commercial)",
      "role": "quality_engineer",
      "email": "qe.commercial@prosite.com"
    },
    {
      "user_id": 4,
      "full_name": "Suresh Patil (Contractor Supervisor)",
      "role": "contractor_supervisor",
      "email": "supervisor.commercial@prosite.com"
    },
    {
      "user_id": 5,
      "full_name": "Raju Yadav (Gate Security)",
      "role": "watchman",
      "email": "watchman.commercial@prosite.com"
    }
  ],
  "total_members": 4
}
```

---

## 4. Managing Project Teams

### **Step 4.1: Update User Role in Project**

```bash
curl -X PUT http://localhost:5000/api/projects/1/members/3 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "quality_manager"
  }'
```

---

### **Step 4.2: Remove User from Project**

```bash
curl -X DELETE http://localhost:5000/api/projects/1/members/5 \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User removed from project successfully"
}
```

---

### **Step 4.3: List All Users (System-Wide)**

```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "email": "admin@prosite.com",
      "full_name": "System Administrator",
      "role": "system_admin",
      "is_active": true
    },
    {
      "id": 2,
      "email": "pm.commercial@prosite.com",
      "full_name": "Amit Sharma (PM - Commercial)",
      "role": "project_manager",
      "is_active": true
    },
    // ... more users
  ],
  "total": 15
}
```

---

## 5. System Admin Daily Tasks

### **Task 1: Monitor All Projects**

**Dashboard API:**
```bash
curl -X GET http://localhost:5000/api/dashboard/admin \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes:**
- Total projects (3)
- Total users (15)
- Active batches across all projects
- Pending verifications
- Critical safety NCs
- System health metrics

---

### **Task 2: Review User Activity**

```bash
curl -X GET http://localhost:5000/api/admin/activity-logs \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "user_id": null
  }'
```

---

### **Task 3: Manage User Permissions**

**Deactivate User:**
```bash
curl -X PUT http://localhost:5000/api/users/5/deactivate \
  -H "Authorization: Bearer $TOKEN"
```

**Reactivate User:**
```bash
curl -X PUT http://localhost:5000/api/users/5/activate \
  -H "Authorization: Bearer $TOKEN"
```

---

### **Task 4: System Configuration**

**Update System Settings:**
```bash
curl -X PUT http://localhost:5000/api/admin/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_notifications": true,
    "whatsapp_notifications": true,
    "auto_backup_enabled": true,
    "max_file_upload_size_mb": 10
  }'
```

---

## 6. Monitoring & Reports

### **Report 1: Project-wise Summary**

```bash
curl -X GET "http://localhost:5000/api/reports/project-summary?project_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes:**
- Total batches delivered
- Batches approved/rejected
- Cube tests conducted
- NCs raised and closed
- Budget utilization

---

### **Report 2: Quality Metrics (All Projects)**

```bash
curl -X GET http://localhost:5000/api/reports/quality-metrics \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes:**
- Overall pass/fail rate
- Project-wise comparison
- Vendor performance
- Test compliance

---

### **Report 3: User Performance**

```bash
curl -X GET "http://localhost:5000/api/reports/user-performance?user_id=3" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 7. Troubleshooting Common Issues

### **Issue 1: User Cannot Access Project**

**Check project membership:**
```bash
curl -X GET http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN"
```

**Solution:** Add user to project:
```bash
curl -X POST http://localhost:5000/api/projects/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_id": 10, "role": "quality_engineer"}'
```

---

### **Issue 2: Permission Denied Errors**

**Check user role:**
```bash
curl -X GET http://localhost:5000/api/users/10 \
  -H "Authorization: Bearer $TOKEN"
```

**Solution:** Update role if needed:
```bash
curl -X PUT http://localhost:5000/api/users/10 \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"role": "quality_manager"}'
```

---

### **Issue 3: Project Not Visible**

**Verify project status:**
```bash
curl -X GET http://localhost:5000/api/projects/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Solution:** Reactivate if archived:
```bash
curl -X PUT http://localhost:5000/api/projects/1/reactivate \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 System Admin Dashboard View

### **Frontend Implementation:**

```javascript
// app/admin/dashboard/page.js
'use client';

import { useEffect, useState } from 'react';
import { apiOptimized } from '@/lib/api-optimized';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      // Load all projects
      const projectsRes = await apiOptimized.get('/projects');
      setProjects(projectsRes.projects);

      // Load all users
      const usersRes = await apiOptimized.get('/users');
      setUsers(usersRes.users);

      // Load system stats
      const statsRes = await apiOptimized.get('/dashboard/admin');
      setStats(statsRes);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    }
  };

  return (
    <div className="admin-dashboard">
      <h1>System Admin Dashboard</h1>
      
      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Projects</h3>
          <p className="stat-value">{projects.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Users</h3>
          <p className="stat-value">{users.length}</p>
        </div>
        <div className="stat-card">
          <h3>Active Sessions</h3>
          <p className="stat-value">{stats?.active_sessions || 0}</p>
        </div>
      </div>

      {/* Projects List */}
      <div className="projects-section">
        <h2>Managed Projects</h2>
        <table>
          <thead>
            <tr>
              <th>Project Name</th>
              <th>Location</th>
              <th>Budget</th>
              <th>Status</th>
              <th>Team Size</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {projects.map(project => (
              <tr key={project.id}>
                <td>{project.name}</td>
                <td>{project.location}</td>
                <td>₹{(project.budget / 10000000).toFixed(1)}Cr</td>
                <td>{project.status}</td>
                <td>{project.team_count || 0}</td>
                <td>
                  <button onClick={() => viewProject(project.id)}>
                    View
                  </button>
                  <button onClick={() => manageTeam(project.id)}>
                    Manage Team
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Users Management */}
      <div className="users-section">
        <h2>User Management</h2>
        <button onClick={() => setShowAddUser(true)}>
          Add New User
        </button>
        
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Projects</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.is_active ? 'Active' : 'Inactive'}</td>
                <td>{user.project_count || 0}</td>
                <td>
                  <button onClick={() => editUser(user.id)}>Edit</button>
                  <button onClick={() => toggleUserStatus(user.id)}>
                    {user.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## ✅ Summary

**System Admin with 3 Projects can:**

✅ Create and manage multiple projects simultaneously  
✅ Add/remove users across all projects  
✅ Assign roles and permissions  
✅ Monitor system-wide activity  
✅ Generate cross-project reports  
✅ Configure system settings  
✅ Handle user issues and troubleshooting  
✅ Access all modules across all projects  
✅ Perform database migrations  
✅ Manage email and notification settings  

**Next:** Proceed to Supabase migration guide...
