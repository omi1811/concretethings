# Login Credentials & Troubleshooting

## Current Login Credentials

After database migration and password reset, use these credentials:

```
Email: test@example.com
Password: Test@123
```

## Login Issues Fixed

### Issue 1: JWT Secret Key Configuration
**Problem:** The application was using `SECRET_KEY` for JWT instead of a separate `JWT_SECRET_KEY`.

**Fix Applied:**
- Updated `server/config.py` to include `JWT_SECRET_KEY` configuration
- Modified `server/app.py` to use `config_obj.JWT_SECRET_KEY`
- `JWT_SECRET_KEY` now falls back to `SECRET_KEY` if not set separately

### Issue 2: Password Hash Compatibility
**Problem:** The password hash migrated from SQLite used `scrypt` method, which may have compatibility issues.

**Fix Applied:**
- Reset the test user's password hash to use `pbkdf2:sha256` (more compatible)
- New password: `Test@123`
- Password meets all requirements (8+ chars, uppercase, lowercase, digit, special char)

## How to Login

### Using API (curl):

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123"
  }'
```

### Using Frontend:

1. Navigate to the login page
2. Enter email: `test@example.com`
3. Enter password: `Test@123`
4. Click "Login"

### Expected Response:

```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User",
    "phone": "+919876543210",
    "company_id": 1,
    "role": "SuperAdmin",
    "is_active": true,
    "is_company_admin": false,
    "is_support_admin": false,
    "is_system_admin": false
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 7200
}
```

## Password Reset Utility

If you need to reset a user's password in the future, run this:

```python
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspaces/concretethings')
from server.db import session_scope
from server.models import User
from werkzeug.security import generate_password_hash

# Change these values
user_email = 'test@example.com'
new_password = 'NewPassword@123'

with session_scope() as session:
    user = session.query(User).filter(User.email == user_email).first()
    if user:
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.failed_login_attempts = 0
        session.flush()
        print(f"✅ Password reset for {user.email}")
        print(f"   New password: {new_password}")
    else:
        print(f"❌ User {user_email} not found")
PYEOF
```

## Account Lockout

The system has account lockout protection:

- **Maximum Failed Attempts:** 5
- **Lockout Duration:** 30 minutes
- **Current Status:** Test account has 0 failed attempts (unlocked)

If locked, you'll see: `"Account locked due to too many failed attempts. Try again in 30 minutes."`

## JWT Token Details

### Access Token:
- **Expires In:** 2 hours (7200 seconds)
- **Claim:** `sub` (subject) contains user ID as string
- **Usage:** Include in Authorization header: `Bearer <access_token>`

### Refresh Token:
- **Expires In:** 30 days
- **Usage:** Use `/api/auth/refresh` endpoint to get new access token

### Token Usage Example:

```bash
# Store the access token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Use it for authenticated requests
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### "Invalid credentials" error:
- ✅ Check email is correct: `test@example.com`
- ✅ Check password is correct: `Test@123`
- ✅ Ensure password has uppercase T
- ✅ Run password reset utility if needed

### "Account is inactive" error:
- User's `is_active` flag is set to false
- Contact admin or use SQL to activate: `UPDATE users SET is_active = true WHERE email = 'test@example.com'`

### "Account locked" error:
- Wait 30 minutes OR
- Run password reset utility (also resets failed attempts)

### "Email/phone and password are required" error:
- Ensure you're sending proper JSON
- Check Content-Type header is `application/json`

### Network/Connection errors:
- ✅ Ensure server is running: `python3 -m server.app` or `./run.sh`
- ✅ Check port 8000 is accessible
- ✅ Verify DATABASE_URL is set correctly

## Environment Variables for Production

When deploying to Render.com, ensure these are set:

```
FLASK_ENV=production
SECRET_KEY=<your-generated-secret>
JWT_SECRET_KEY=<your-generated-jwt-secret>
DATABASE_URL=postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres
```

Generate secrets with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Next Steps

1. ✅ Login with credentials: `test@example.com` / `Test@123`
2. ✅ Test all API endpoints with the access token
3. ✅ Create additional users via `/api/auth/register` (requires system admin token)
4. ✅ Configure environment variables in Render.com dashboard
5. ✅ Deploy to production
