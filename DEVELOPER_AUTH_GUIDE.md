# Developer Guide: Using Authentication

This guide shows how to add authentication and authorization to new endpoints and features.

## Quick Reference

```python
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.auth import system_admin_required, company_admin_required, project_access_required
```

## Basic Protected Endpoint

### Simple JWT Protection

```python
@app.get("/api/my-endpoint")
@jwt_required()
def my_endpoint():
    # Get current user info from JWT
    claims = get_jwt_identity()
    user_id = claims.get("user_id")
    email = claims.get("email")
    company_id = claims.get("company_id")
    
    return jsonify({
        "message": f"Hello {email}",
        "user_id": user_id
    })
```

## System Admin Only

```python
@app.post("/api/admin/companies")
@system_admin_required
def create_company():
    # Only system admins can access this
    data = request.get_json()
    
    with session_scope() as s:
        company = Company(name=data["name"])
        s.add(company)
        s.flush()
        return jsonify(company.to_dict()), 201
```

## Company Admin Access

```python
@app.get("/api/company/users")
@company_admin_required
def list_company_users():
    # System admins OR company admins can access
    claims = get_jwt_identity()
    company_id = claims.get("company_id")
    is_system_admin = claims.get("is_system_admin")
    
    with session_scope() as s:
        if is_system_admin:
            # System admin sees all users
            users = s.query(User).all()
        else:
            # Company admin sees only their company
            users = s.query(User).filter(User.company_id == company_id).all()
        
        return jsonify([u.to_dict() for u in users])
```

## Project-Level Access

```python
@app.get("/api/projects/<int:project_id>/mix-designs")
@project_access_required(project_id_param="project_id")
def get_project_mix_designs(project_id, user_role=None):
    # user_role is automatically injected by decorator
    # System/Company admins automatically have access
    
    with session_scope() as s:
        designs = s.query(MixDesign).filter(
            MixDesign.project_id == project_id
        ).all()
        
        return jsonify({
            "project_id": project_id,
            "your_role": user_role,
            "designs": [d.to_dict() for d in designs]
        })
```

## Custom Authorization Logic

### Check Multiple Roles

```python
from functools import wraps
from flask import jsonify

def role_required(allowed_roles):
    """Decorator to check if user has one of the allowed roles."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt_identity()
            user_id = claims.get("user_id")
            project_id = kwargs.get("project_id") or request.view_args.get("project_id")
            
            # Check if system/company admin
            if claims.get("is_system_admin") or claims.get("is_company_admin"):
                kwargs["user_role"] = "admin"
                return fn(*args, **kwargs)
            
            # Check project membership role
            with session_scope() as s:
                membership = s.query(ProjectMembership).filter(
                    ProjectMembership.user_id == user_id,
                    ProjectMembership.project_id == project_id
                ).first()
                
                if not membership or membership.role not in allowed_roles:
                    return jsonify({"error": "Access denied"}), 403
                
                kwargs["user_role"] = membership.role
                return fn(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage:
@app.put("/api/projects/<int:project_id>/approve")
@role_required(["PM", "QualityManager"])
def approve_project(project_id, user_role=None):
    # Only PMs and Quality Managers can approve
    return jsonify({"message": f"Approved by {user_role}"})
```

### Check Resource Ownership

```python
@app.put("/api/mix-designs/<int:item_id>")
@jwt_required()
def update_mix_design_with_ownership(item_id):
    claims = get_jwt_identity()
    user_id = claims.get("user_id")
    
    with session_scope() as s:
        design = s.get(MixDesign, item_id)
        if not design:
            return jsonify({"error": "Not found"}), 404
        
        # Check if user created this design (add created_by_user_id to model)
        if design.created_by_user_id != user_id:
            # Unless they're an admin
            if not (claims.get("is_system_admin") or claims.get("is_company_admin")):
                return jsonify({"error": "Access denied"}), 403
        
        # Update logic...
        return jsonify(design.to_dict())
```

## Frontend Integration

### Making Authenticated Requests

```javascript
// Get token from localStorage
const token = localStorage.getItem('access_token');

// Add to all API calls
fetch('/api/protected-endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/static/login.html';
    return;
  }
  return response.json();
})
.then(data => console.log(data));
```

### Using Auth Utilities

```javascript
// Check auth on page load
if (!Auth.isAuthenticated()) {
  window.location.href = '/static/login.html';
}

// Get user info
const user = Auth.getUser();
console.log(`Logged in as: ${user.fullName}`);
console.log(`Is admin: ${user.isSystemAdmin}`);

// Add token to FormData requests
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${Auth.getToken()}`
  },
  body: formData
});

// Logout
Auth.logout(); // Clears tokens and redirects
```

### Conditional UI Based on Role

```javascript
const user = Auth.getUser();

// Show admin panel only to admins
if (user.isSystemAdmin || user.isCompanyAdmin) {
  document.getElementById('admin-panel').style.display = 'block';
}

// Show different buttons based on role
if (user.isSystemAdmin) {
  showButton('delete-company-btn');
  showButton('create-user-btn');
}
```

## Testing Protected Endpoints

### Using cURL

```bash
# 1. Login first
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","password":"adminpass"}' \
  | jq -r '.access_token')

# 2. Use token in requests
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer $TOKEN"

# 3. Create user (admin only)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "newuser@company.com",
    "phone": "+15559999999",
    "full_name": "New User",
    "password": "SecurePass123!",
    "company_id": 1
  }'
```

### Using Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "admin@demo.com", "password": "adminpass"}
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}

# Get protected resource
response = requests.get(
    "http://localhost:8000/api/protected",
    headers=headers
)
print(response.json())

# Create resource
response = requests.post(
    "http://localhost:8000/api/resource",
    headers=headers,
    json={"name": "My Resource"}
)
```

## Common Patterns

### Get Current User in Endpoint

```python
@app.get("/api/profile")
@jwt_required()
def get_profile():
    claims = get_jwt_identity()
    user_id = claims.get("user_id")
    
    with session_scope() as s:
        user = s.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(user.to_dict())
```

### Audit Trail with User Info

```python
@app.post("/api/critical-action")
@jwt_required()
def critical_action():
    claims = get_jwt_identity()
    user_id = claims.get("user_id")
    
    # Log action with user info
    logger.info(f"Critical action performed by user {user_id}")
    
    # Store in audit log
    with session_scope() as s:
        audit = AuditLog(
            user_id=user_id,
            action="critical_action",
            timestamp=datetime.utcnow()
        )
        s.add(audit)
        s.flush()
    
    return jsonify({"message": "Action completed"})
```

### Filter Data by Company

```python
@app.get("/api/company-data")
@jwt_required()
def get_company_data():
    claims = get_jwt_identity()
    company_id = claims.get("company_id")
    is_system_admin = claims.get("is_system_admin")
    
    with session_scope() as s:
        if is_system_admin:
            # System admin sees all
            data = s.query(Data).all()
        else:
            # Regular users see only their company
            data = s.query(Data).filter(Data.company_id == company_id).all()
        
        return jsonify([d.to_dict() for d in data])
```

## Error Handling

### Handle 401 Globally

```python
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Authentication required",
        "message": "Please login to access this resource"
    }), 401
```

### Handle 403 (Forbidden)

```python
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Access denied",
        "message": "You don't have permission to access this resource"
    }), 403
```

## Best Practices

### ✅ DO

- Always use `@jwt_required()` on protected endpoints
- Use specific decorators (`@system_admin_required`, etc.) when appropriate
- Log security events (login, failed attempts, admin actions)
- Validate all user input, even in protected endpoints
- Use company_id from JWT claims to filter data
- Include user_id in audit logs
- Test both authenticated and unauthenticated access
- Handle 401 responses gracefully in frontend

### ❌ DON'T

- Trust client-sent user_id or company_id (use JWT claims)
- Store sensitive data in JWT (use only IDs and roles)
- Forget to check authorization (authentication ≠ authorization)
- Expose system admin endpoints to company admins
- Return different errors for invalid user vs invalid password (timing attacks)
- Log passwords or tokens
- Assume @jwt_required() checks authorization (it only checks authentication)

## Security Checklist

When adding new endpoints:

- [ ] Added `@jwt_required()` decorator
- [ ] Checked user authorization (role/membership)
- [ ] Validated all input
- [ ] Filtered data by company_id (if applicable)
- [ ] Logged the action (if sensitive)
- [ ] Added tests for both success and failure cases
- [ ] Tested with different user roles
- [ ] Updated API documentation
- [ ] Checked for SQL injection vulnerabilities
- [ ] Handled 401/403 errors properly

## Next Steps

See these files for more examples:
- `server/auth.py` - Core authentication logic
- `server/app.py` - Protected endpoint examples
- `static/app.js` - Frontend auth integration
- `AUTHENTICATION.md` - Full documentation
- `test_auth.py` - Testing examples

---

**Questions?** Check the full documentation in [AUTHENTICATION.md](AUTHENTICATION.md)
