# 🔴 CRITICAL BUGS & ISSUES REPORT - ProSite Application

**Date:** November 14, 2025  
**Test Suite:** Comprehensive QA Automated Testing  
**Status:** ❌ **9 CRITICAL FAILURES** | ⚠️ 1 WARNING | ✅ 10 PASSED

---

## 📊 TEST RESULTS SUMMARY

| Category | Count |
|----------|-------|
| **Total Tests** | 20 |
| **✅ Passed** | 10 (50%) |
| **✗ Failed** | 9 (45%) |
| **⚠️ Warnings** | 1 (5%) |

**Overall Status:** 🚨 **PRODUCTION DEPLOYMENT BLOCKED** - Critical issues must be fixed

---

## 🔥 CRITICAL ISSUES (Priority 1 - MUST FIX)

### 1. **DATABASE SCHEMA MISMATCH - Company Model**
**Severity:** 🔴 CRITICAL  
**Impact:** Application crashes on Company table access  
**Status:** BLOCKING ALL DATABASE OPERATIONS

**Error:**
```
sqlite3.OperationalError: no such column: companies.subscribed_apps
```

**Root Cause:**
- The `Company` model in `server/models.py` defines a `subscribed_apps` column
- The actual SQLite database does not have this column
- This is a schema migration issue - models updated but database not migrated

**Files Affected:**
- `server/models.py` (lines 32-80)
- `data.sqlite3` (database schema)

**Fix Required:**
```python
# Option 1: Add migration script to add missing column
ALTER TABLE companies ADD COLUMN subscribed_apps TEXT DEFAULT '["safety", "concrete"]';

# Option 2: Remove column from model temporarily
# Comment out or remove 'subscribed_apps' field from Company model
```

**Detailed Steps:**
1. Check actual database schema: `sqlite3 data.sqlite3 ".schema companies"`
2. Compare with `Company` model definition
3. Either:
   - Create migration to add missing column, OR
   - Remove `subscribed_apps` from model definition
4. Test database access after fix

---

### 2. **JWT TOKEN VALIDATION FAILURE**
**Severity:** 🔴 CRITICAL  
**Impact:** Authenticated users cannot access protected routes  
**Status:** BREAKING AUTHENTICATION

**Error:**
```
server.auth - ERROR - Get current user error: 'str' object has no attribute 'get'
Response: {'error': 'Failed to fetch user'}
```

**Root Cause:**
- The `/api/auth/me` endpoint is trying to call `.get()` method on a string object
- Likely issue: `get_jwt_identity()` returns user_id as string, but code expects dict

**Files Affected:**
- `server/auth.py` (JWT me endpoint)

**Fix Required:**
```python
# In server/auth.py - find the /api/auth/me endpoint
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()  # This returns an integer/string
        # DON'T do: current_user_id.get('id')  # WRONG!
        
        # FIX: Query user directly with ID
        with session_scope() as session:
            user = session.query(User).filter_by(id=int(current_user_id)).first()
            if user:
                return jsonify(user.to_dict()), 200
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user'}), 500
```

---

### 3. **MISSING API ENDPOINTS - 404 Errors**
**Severity:** 🔴 HIGH  
**Impact:** Multiple features non-functional  
**Status:** FEATURES BROKEN

**Affected Endpoints:**
1. ❌ `/api/projects` → 404 (Resource not found)
2. ❌ `/api/safety/non-conformances` → 404 (Resource not found)
3. ❌ `/api/safety-inductions/topics` → 404 (Resource not found)

**Root Cause:**
- Blueprints not registered or routes misconfigured
- Possible URL path mismatch (e.g., `/api/nc` vs `/api/safety/non-conformances`)

**Fix Required:**
1. Check blueprint registration in `server/app.py`
2. Verify route definitions match expected paths
3. Check if routes are commented out (we disabled some blueprints)

```python
# In server/app.py - ensure these are registered:
app.register_blueprint(project_bp, url_prefix='/api/projects')  # MISSING?
app.register_blueprint(nc_bp, url_prefix='/api/nc')  # Check URL prefix
app.register_blueprint(safety_induction_bp, url_prefix='/api/safety-inductions')
```

---

### 4. **MISSING QUERY PARAMETERS - Bad Request Handling**
**Severity:** 🟡 MEDIUM  
**Impact:** APIs require parameters but don't provide defaults  
**Status:** UX ISSUE

**Errors:**
```
/api/batches → {'error': 'project_id is required'}
/api/vendors → {'error': 'project_id is required'}
```

**Root Cause:**
- APIs are hardcoded to require `project_id` parameter
- No default behavior or "all projects" option
- Poor API design for listing endpoints

**Fix Required:**
```python
# In batch/vendor list endpoints:
@batches_bp.route('', methods=['GET'])
@jwt_required()
def get_batches():
    project_id = request.args.get('project_id', type=int)
    
    with session_scope() as session:
        query = session.query(BatchRegister)
        
        # FIX: Make project_id optional
        if project_id:
            query = query.filter_by(project_id=project_id)
        # else: return all batches user has access to
        
        batches = query.all()
        return jsonify([b.to_dict() for b in batches]), 200
```

---

### 5. **ERROR HANDLING - Invalid JSON Returns 500 Instead of 400**
**Severity:** 🟡 MEDIUM  
**Impact:** Poor error messages confuse developers/users  
**Status:** PRODUCTION READINESS ISSUE

**Error:**
```
POST /api/auth/login with invalid JSON → 500 Internal Server Error
Expected: 400 Bad Request
```

**Root Cause:**
- Missing try-catch for JSON parsing errors
- Flask's error handling not configured properly

**Fix Required:**
```python
# In server/app.py - add error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# In auth endpoints - add JSON validation
try:
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400
except Exception as e:
    return jsonify({'error': 'Malformed JSON'}), 400
```

---

## ✅ WORKING FEATURES (Good News!)

1. ✅ **Authentication Login** - Credentials work, tokens generated
2. ✅ **Unauthorized Access Prevention** - 401 errors correctly returned
3. ✅ **Safety Workers API** - Returns worker list successfully
4. ✅ **Safety Inductions List** - 3 inductions found and retrieved
5. ✅ **File Upload Permissions** - Upload directory writable
6. ✅ **Static Files Serving** - Static routes configured
7. ✅ **Email Uniqueness Constraint** - Database prevents duplicates
8. ✅ **404 Handling** - Invalid endpoints return 404
9. ✅ **Missing Fields Validation** - Required fields checked
10. ✅ **CORS Configuration** - Headers present for frontend

---

## 🔧 RECOMMENDED FIXES (In Priority Order)

### Priority 1 - CRITICAL (Fix Today)
1. **Fix Company model schema mismatch** → Remove `subscribed_apps` column or migrate database
2. **Fix JWT /api/auth/me endpoint** → Correct user retrieval logic
3. **Register missing blueprints** → Enable projects, NC, induction topics endpoints

### Priority 2 - HIGH (Fix This Week)
4. **Make project_id optional in list APIs** → Better API design
5. **Fix error handling for invalid JSON** → Return 400 instead of 500
6. **Enable disabled blueprints** → Refactor incident_investigation, safety_audits, ppe_tracking, geofence_api to use session_scope()

### Priority 3 - MEDIUM (Fix Before Production)
7. **Add comprehensive input validation** → Prevent injection attacks
8. **Add API rate limiting** → Prevent abuse
9. **Add database connection pooling** → Better performance
10. **Add logging for all errors** → Better debugging

---

## 📝 DETAILED FIX INSTRUCTIONS

### Fix #1: Company Schema Mismatch

**Option A: Quick Fix (Remove Column from Model)**
```python
# File: server/models.py
# COMMENT OUT this line:
# subscribed_apps: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default='["safety", "concrete"]')

# Also remove from to_dict():
def to_dict(self) -> dict:
    return {
        "id": self.id,
        "name": self.name,
        # "subscribedApps": json_module.loads(self.subscribed_apps) if self.subscribed_apps else ["safety", "concrete"],  # REMOVE
        "subscriptionPlan": self.subscription_plan,
        # ... rest of fields
    }
```

**Option B: Proper Fix (Migrate Database)**
```bash
# Create migration script
cd /workspaces/concretethings
sqlite3 data.sqlite3 "ALTER TABLE companies ADD COLUMN subscribed_apps TEXT DEFAULT '[\"safety\", \"concrete\"]';"
```

### Fix #2: JWT Me Endpoint

**File:** `server/auth.py`

Find this code pattern:
```python
current_user = get_jwt_identity()
user_id = current_user.get('id')  # ❌ WRONG - current_user is already the ID!
```

Replace with:
```python
user_id = get_jwt_identity()  # ✅ CORRECT - this IS the user ID
```

### Fix #3: Register Missing Blueprints

**File:** `server/app.py`

Check if these exist and are not commented out:
```python
# Around line 35-45:
from .projects import projects_bp  # If this doesn't exist, create it
from .safety_nc import nc_bp
from .safety_inductions import safety_induction_bp

# Around line 100-150:
app.register_blueprint(projects_bp, url_prefix='/api/projects')  # ADD THIS
app.register_blueprint(nc_bp, url_prefix='/api/nc')  # VERIFY URL PREFIX
app.register_blueprint(safety_induction_bp, url_prefix='/api/safety-inductions')  # VERIFY
```

---

## 🧪 HOW TO TEST FIXES

After applying fixes, run:

```bash
# 1. Test database access
python3 -c "from server.models import Company; from server.db import SessionLocal; s = SessionLocal(); print(s.query(Company).first())"

# 2. Run QA test suite
python3 qa_test_suite.py

# 3. Manual API testing
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123"}'

# Expected: {"access_token": "..."}

# 4. Test JWT validation
TOKEN="<paste_token_here>"
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: {"id":1,"email":"test@example.com",...}
```

---

## 📈 SUCCESS CRITERIA

✅ All 20 tests passing  
✅ No 500 errors in logs  
✅ All core APIs returning 200  
✅ Database queries work without errors  
✅ JWT authentication fully functional  

---

## 🚀 DEPLOYMENT READINESS CHECKLIST

Before deploying to production:

- [ ] Fix Company model schema mismatch
- [ ] Fix JWT /api/auth/me endpoint
- [ ] Register all missing blueprints
- [ ] Make project_id optional in list endpoints
- [ ] Fix invalid JSON error handling (500 → 400)
- [ ] Enable disabled blueprints (after refactoring)
- [ ] Run full QA test suite (20/20 passing)
- [ ] Load test with 100+ concurrent users
- [ ] Security audit (SQL injection, XSS, CSRF)
- [ ] Add environment-specific configs
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure database backups
- [ ] Add health check endpoint
- [ ] Test on Render staging environment

---

## 📞 NEXT STEPS

1. **Immediate Action:** Fix Priority 1 issues (schema mismatch, JWT, missing endpoints)
2. **Testing:** Re-run QA suite after each fix
3. **Code Review:** Review all new safety modules for similar issues
4. **Documentation:** Update API documentation with correct endpoints
5. **Monitoring:** Set up error tracking before production deployment

---

**Generated by:** ProSite QA Automation Suite  
**Test Execution Time:** 2025-11-14 05:33:53  
**Test Coverage:** Authentication, Database, Core APIs, Safety Modules, File Handling, Validation, Error Handling, CORS, Performance

---

## 💡 DEVELOPER TIPS

- Always run QA suite before committing
- Test database migrations on copy before production
- Use `session_scope()` pattern, not `db.session`
- Add `@jwt_required()` with parentheses, not `@jwt_required`
- Validate all user inputs
- Return proper HTTP status codes (400 for client errors, 500 for server errors)
- Log all errors for debugging
- Keep models in sync with database schema

---

**Status Update:** 🔴 Application is NOT production-ready. Address critical issues before deployment.
