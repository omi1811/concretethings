# Quick Reference - New Features ⚡

## 🔑 Admin Login
```bash
Email: shrotrio@gmail.com
Password: Admin@123
⚠️ CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN
```

---

## 🔐 Password Reset API

### Request Reset
```bash
POST /api/auth/forgot-password
{
  "email": "user@example.com"
}
```

### Reset Password
```bash
POST /api/auth/reset-password
{
  "token": "abc123...",
  "new_password": "NewPassword123!"
}
```

### Verify Token
```bash
POST /api/auth/verify-reset-token
{
  "token": "abc123..."
}
```

---

## 📦 Module System

### Check Module Access
```python
# In your code
from server.module_access import require_module

@app.route("/feature")
@jwt_required()
@require_module('concrete_nc')  # Requires Concrete NC module
def feature():
    pass
```

### Available Modules
- `safety` - Safety management
- `concrete` - Concrete testing
- `concrete_nc` - Concrete NC (separate billing)
- `safety_nc` - Safety NC scoring

### Company Modules (Database)
```sql
-- View subscribed modules
SELECT name, subscribed_modules FROM companies WHERE id = 1;

-- Add module
UPDATE companies 
SET subscribed_modules = '["safety", "concrete", "concrete_nc"]'
WHERE id = 1;
```

---

## 📊 Safety NC Scoring

### Dashboard
```bash
GET /api/safety/nc/dashboard?project_id=1&contractor=ABC
```

**Response:**
```json
{
  "total": 21,
  "open": 11,
  "closed": 10,
  "overdue": 3,
  "total_score": 8.5,
  "performance_grade": "D",
  "severity_counts": {"critical": 2, "major": 8, "minor": 11}
}
```

### Generate Report
```bash
GET /api/safety/nc/reports/monthly?project_id=1&contractor=ABC&period=2025-01
```

**Response:**
```json
{
  "report": {
    "critical_count": 2,
    "major_count": 5,
    "minor_count": 8,
    "total_score": 6.5,
    "closure_rate": 66.7,
    "performance_grade": "C"
  }
}
```

---

## 🎯 Severity Scores

### Concrete NC
- HIGH: 1.0 points
- MODERATE: 0.5 points
- LOW: 0.25 points

### Safety NC
- Critical: 1.5 points
- Major: 1.0 points
- Minor: 0.5 points

---

## 📈 Performance Grades

| Grade | Score Range | Status |
|-------|-------------|--------|
| A | 0 | Perfect |
| B | ≤ 2.0 | Good |
| C | ≤ 5.0 | Acceptable |
| D | ≤ 10.0 | Poor |
| F | > 10.0 | Failing |

---

## 🧪 Testing

### Run Safety NC Tests
```bash
python3 test_safety_nc_scoring.py
```

### Check App Status
```bash
python3 -c "from server.app import app; print(f'{len(app.url_map._rules)} routes')"
# Should output: 212 routes
```

---

## 🗄️ Database Migrations

### Run Migrations
```bash
# Auth and modules
python3 migrate_auth_modules.py

# Safety NC scoring
python3 migrate_safety_nc_scoring.py
```

### Verify Tables
```sql
-- Check password reset tokens table
SELECT * FROM password_reset_tokens;

-- Check Safety NC scoring columns
PRAGMA table_info(safety_non_conformances);

-- Check score reports
SELECT * FROM safety_nc_score_reports;
```

---

## 📱 Frontend Integration

### Check Module Access
```javascript
const hasConcreteNC = user.company.subscribedModules.includes('concrete_nc');

{hasConcreteNC ? (
  <Link to="/concrete/nc">Concrete NC</Link>
) : (
  <span>Upgrade Required</span>
)}
```

### Password Reset Flow
```javascript
// Login page
<Link to="/forgot-password">Forgot Password?</Link>

// Forgot password page
<form onSubmit={() => 
  fetch('/api/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email })
  })
}>

// Reset password page
<form onSubmit={() =>
  fetch('/api/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password })
  })
}>
```

---

## 🚨 Common Issues

### Module Access Denied
```
Error: "Access denied: concrete_nc module not subscribed"
Fix: Add 'concrete_nc' to company's subscribed_modules
```

### Password Reset Token Expired
```
Error: "Invalid or expired reset token"
Fix: Request new reset link (tokens expire after 1 hour)
```

### Admin Can't Login
```
Email: shrotrio@gmail.com
Password: Admin@123
Check: failed_login_attempts should be 0
```

---

## 📄 Documentation Files

1. **SESSION_SUMMARY.md** - This implementation overview
2. **SAFETY_NC_SCORING_COMPLETE.md** - Safety NC scoring system
3. **MODULE_SYSTEM_AND_AUTH_COMPLETE.md** - Module & password reset
4. **NC_IMPLEMENTATION_COMPLETE.md** - Concrete NC system
5. **QUICK_REFERENCE_NEW_FEATURES.md** - This file

---

## 🎉 Quick Stats

- **Total Routes**: 212 (+5 from 207)
- **New Endpoints**: 5 (3 password reset + 2 Safety NC)
- **Protected Endpoints**: 15 Concrete NC endpoints
- **Database Tables Added**: 2
- **Database Columns Added**: 6
- **Indexes Created**: 11
- **Lines of Code**: ~2,865

---

## ⚡ Fast Commands

```bash
# Login as admin
curl -X POST localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"shrotrio@gmail.com","password":"Admin@123"}'

# Request password reset
curl -X POST localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"shrotrio@gmail.com"}'

# Get Safety NC dashboard
curl localhost:5000/api/safety/nc/dashboard \
  -H "Authorization: Bearer TOKEN"

# Test Concrete NC access (should work with token)
curl localhost:5000/api/concrete/nc/batches \
  -H "Authorization: Bearer TOKEN"

# Run migrations
python3 migrate_auth_modules.py && python3 migrate_safety_nc_scoring.py

# Test app
python3 test_safety_nc_scoring.py
```

---

**All Features Ready! 🚀**
