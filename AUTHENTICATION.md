# Authentication System Documentation

## Overview

The ConcretThings application now features a **robust, production-ready authentication system** with JWT tokens, multi-tenant support, and role-based access control (RBAC).

## Key Features

### Security Features
- ✅ **JWT Token Authentication** - Industry-standard JSON Web Tokens
- ✅ **Strong Password Requirements** - Min 8 chars, uppercase, lowercase, digit, special char
- ✅ **Account Lockout Protection** - 5 failed attempts = 30-minute lockout
- ✅ **Password Hashing** - pbkdf2:sha256 secure hashing
- ✅ **Token Refresh** - Long-lived refresh tokens (30 days)
- ✅ **Rate Limiting** - Failed login attempt tracking
- ✅ **Email & Phone Validation** - Comprehensive input validation
- ✅ **HTTPS-Ready** - Secure headers and CORS configuration

### Multi-Tenant Support
- **Companies** - Organization-level separation
- **Users** - Belong to companies with roles
- **Projects** - Company-specific projects
- **Project Memberships** - Granular project access control

### Role-Based Access Control (RBAC)

#### User Roles
1. **System Admin** - Full system access
   - Can create companies
   - Can create users across all companies
   - Access to all projects
   - Manage system-wide settings

2. **Company Admin** - Company-level management
   - Manage users within their company
   - Access to all company projects
   - Create and manage projects

3. **Project Roles** (via ProjectMembership)
   - **PM** (Project Manager) - Project oversight
   - **QualityManager** - Quality control
   - **Quality** - Quality team member
   - **Entry** - Data entry personnel
   - **RMC** - Ready-Mix Concrete users

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/login
Login with email/phone and password.

**Request:**
```json
{
  "email": "admin@demo.com",  // or "phone": "+15551234567"
  "password": "adminpass"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "admin@demo.com",
    "phone": "+15551234567",
    "fullName": "System Admin",
    "companyId": 1,
    "isCompanyAdmin": true,
    "isSystemAdmin": true,
    "isActive": true,
    "lastLogin": "2025-11-10T09:00:00Z",
    "createdAt": "2025-11-01T00:00:00Z"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 7200
}
```

**Error Responses:**
- `401` - Invalid credentials (shows remaining attempts)
- `403` - Account locked or inactive

#### POST /api/auth/register
Create a new user (System Admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "email": "user@company.com",
  "phone": "+15559876543",
  "full_name": "John Doe",
  "password": "SecurePass123!",
  "company_id": 1,
  "is_company_admin": false,
  "is_system_admin": false
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "email": "user@company.com",
    "phone": "+15559876543",
    "fullName": "John Doe",
    "companyId": 1,
    "isCompanyAdmin": false,
    "isSystemAdmin": false,
    "isActive": true
  }
}
```

**Error Responses:**
- `400` - Validation error (weak password, invalid email/phone)
- `403` - Not authorized (not a system admin)
- `409` - User already exists

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 7200
}
```

#### GET /api/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "admin@demo.com",
  "phone": "+15551234567",
  "fullName": "System Admin",
  "companyId": 1,
  "isCompanyAdmin": true,
  "isSystemAdmin": true,
  "isActive": true,
  "lastLogin": "2025-11-10T09:00:00Z",
  "createdAt": "2025-11-01T00:00:00Z"
}
```

#### POST /api/auth/change-password
Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "current_password": "oldpass",
  "new_password": "NewSecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

## Protected Endpoints

All `/api/mix-designs/*` endpoints now require authentication:

```
GET    /api/mix-designs          - List all mix designs
POST   /api/mix-designs          - Create mix design
PUT    /api/mix-designs/:id      - Update mix design
DELETE /api/mix-designs/:id      - Delete mix design
GET    /api/mix-designs/:id/image - Get mix design image
```

### Using Protected Endpoints

Include the JWT token in the Authorization header:

```bash
curl -X GET http://localhost:8000/api/mix-designs \
  -H "Authorization: Bearer <access_token>"
```

## Frontend Integration

### Login Page
Access at `/static/login.html`

Features:
- Email or phone login
- Client-side validation
- Password strength hints
- Error messages with remaining attempts
- Auto-redirect on success
- Remember me via localStorage

### Main App (index.html)
Features:
- Auto-redirect to login if not authenticated
- User info display (name, email, role badges)
- Logout button
- JWT token in all API calls
- Auto-logout on 401 (token expired)

### JavaScript Auth Utilities

```javascript
// Check if authenticated
if (!Auth.isAuthenticated()) {
  window.location.href = '/static/login.html';
}

// Get current user
const user = Auth.getUser();
console.log(user.fullName, user.isSystemAdmin);

// Make authenticated API call
fetch('/api/mix-designs', {
  headers: {
    'Authorization': `Bearer ${Auth.getToken()}`
  }
});

// Logout
Auth.logout();
```

## Password Requirements

Passwords must meet ALL of the following criteria:
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)
- ✅ At least one special character (!@#$%^&*(),.?":{}|<>)
- ✅ Maximum 128 characters

**Examples:**
- ✅ `SecurePass123!`
- ✅ `MyP@ssw0rd`
- ✅ `Admin#2024`
- ❌ `password` (no uppercase, digit, or special char)
- ❌ `Password` (no digit or special char)
- ❌ `Pass1!` (too short)

## Email & Phone Validation

### Email Requirements
- Valid RFC 5322 format
- Maximum 255 characters
- Must be unique in system

**Examples:**
- ✅ `user@example.com`
- ✅ `john.doe+test@company.co.uk`
- ❌ `invalid@` (incomplete domain)
- ❌ `@example.com` (missing local part)

### Phone Requirements
- 10-15 digits only
- International format preferred: `+15551234567`
- Allowed separators (removed automatically): `- ( ) +` and spaces
- Must be unique in system

**Examples:**
- ✅ `+15551234567`
- ✅ `+447911123456`
- ✅ `(555) 123-4567` (cleaned to `5551234567`)
- ❌ `123` (too short)
- ❌ `abc1234567` (contains letters)

## Account Security

### Failed Login Protection
- Maximum **5 failed login attempts**
- Account locked for **30 minutes** after 5 failures
- Counter resets on successful login
- Lockout timer displayed to user

### Token Expiration
- **Access Token**: 2 hours
- **Refresh Token**: 30 days
- Use refresh endpoint to get new access token
- Frontend auto-redirects to login on 401

## Authorization Decorators

Use these decorators to protect endpoints:

### @jwt_required()
Requires valid JWT token.

```python
@app.get("/api/protected")
@jwt_required()
def protected():
    claims = get_jwt_identity()
    user_id = claims.get("user_id")
    return jsonify({"message": f"Hello user {user_id}"})
```

### @system_admin_required
Requires System Admin role.

```python
from server.auth import system_admin_required

@app.post("/api/admin/users")
@system_admin_required
def create_user():
    # Only system admins can access this
    pass
```

### @company_admin_required
Requires Company Admin or System Admin role.

```python
from server.auth import company_admin_required

@app.get("/api/company/projects")
@company_admin_required
def list_company_projects():
    # Company admins and system admins can access
    pass
```

### @project_access_required
Requires project membership.

```python
from server.auth import project_access_required

@app.get("/api/projects/<int:project_id>/data")
@project_access_required(project_id_param="project_id")
def get_project_data(project_id, user_role=None):
    # user_role is automatically injected
    # System/Company admins have auto-access
    return jsonify({"role": user_role})
```

## Database Schema

### User Model
```python
class User:
    id: int (PK)
    email: str (unique, indexed)
    phone: str (indexed, required)
    full_name: str (required)
    password_hash: str (required)
    company_id: int (FK to Company)
    is_company_admin: bool
    is_system_admin: bool
    is_active: bool
    failed_login_attempts: int
    last_login: datetime
    created_at: datetime
    updated_at: datetime
```

## Demo Credentials

**System Admin:**
- Email: `admin@demo.com`
- Phone: `+15551234567`
- Password: `adminpass`
- Company: Demo Concrete Co
- Roles: System Admin, Company Admin

## Testing

### Test Script
Run the automated test suite:

```bash
python test_auth.py
```

Tests include:
- ✅ Successful login
- ✅ Invalid credentials
- ✅ Account lockout
- ✅ Token refresh
- ✅ Protected endpoint access
- ✅ Missing token rejection
- ✅ User info retrieval

### Manual Testing with cURL

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","password":"adminpass"}'
```

**Get User Info:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token>"
```

**Access Protected Endpoint:**
```bash
curl -X GET http://localhost:8000/api/mix-designs \
  -H "Authorization: Bearer <your_token>"
```

## Migration

To update existing databases:

```bash
python migrate_users.py
```

This adds:
- `phone` column (string, indexed)
- `is_system_admin` column (boolean)
- `failed_login_attempts` column (integer)
- `last_login` column (datetime)
- `updated_at` column (datetime)
- `created_at` column (datetime)

## Production Considerations

### Environment Variables
Set in `.env` file:

```bash
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
```

### HTTPS Required
**CRITICAL:** Always use HTTPS in production to protect tokens in transit.

### Token Storage
- **Frontend:** localStorage (current implementation)
- **Production Alternative:** HttpOnly cookies for XSS protection

### Rate Limiting
Consider adding:
- Global rate limiting (e.g., 100 requests/minute)
- Login endpoint throttling (e.g., 5 attempts/minute per IP)
- Use Flask-Limiter or similar

### Monitoring
Log these events:
- ✅ Successful logins (already logged)
- ✅ Failed login attempts (already logged)
- ✅ Account lockouts (already logged)
- ✅ Password changes (already logged)
- Consider: Token refreshes, user creation, role changes

## Future Enhancements

Recommended additions:
- [ ] Email verification on registration
- [ ] Password reset via email
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2/OIDC integration (Google, Microsoft)
- [ ] API key authentication for service accounts
- [ ] Session management (list active sessions, revoke)
- [ ] Audit trail for sensitive operations
- [ ] IP whitelisting for admin accounts
- [ ] CAPTCHA on login after 3 failed attempts
- [ ] Password expiry policy (e.g., 90 days)

## Security Best Practices

✅ **Implemented:**
- Passwords hashed with pbkdf2:sha256
- JWT tokens with expiration
- Account lockout protection
- Input validation and sanitization
- CORS configuration
- Security headers (X-Frame-Options, X-XSS-Protection)
- HTTPS-ready

⚠️ **Recommendations:**
- Use environment variables for secrets (already supported)
- Rotate JWT secret keys periodically
- Implement HTTPS in production (mandatory)
- Enable rate limiting on production
- Regular security audits
- Keep dependencies updated
- Monitor for suspicious activity

## Support

For issues or questions:
1. Check this documentation
2. Review `server/auth.py` for implementation details
3. Run `test_auth.py` for troubleshooting
4. Check application logs

---

**Last Updated:** November 10, 2025
**Version:** 1.0.0
