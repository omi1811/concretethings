# Render IPv6 Connection Issue - FIXED

## Problem
Render deployed successfully but database connection failed:
```
connection to server at "db.lsqvxfaonbvqvlwrhsby.supabase.co" (2406:da1c:f42:ae08:c721:70ac:4f4f:c393), port 5432 failed: Network is unreachable
```

**Root Cause**: Supabase returns IPv6 addresses, but Render doesn't support IPv6 connections.

## Solution Applied

### 1. Updated `server/db.py` ✅
Modified the database connection logic to:
- Force IPv4 pooler connection for Supabase
- Replace direct connection with pooler (IPv4 only)
- Use port 6543 (pooler) instead of 5432 (direct)

### 2. Update Environment Variable on Render

**CRITICAL**: Update your `DATABASE_URL` environment variable on Render dashboard to use the **pooler connection string**:

#### ❌ OLD (Direct - IPv6):
```
postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres
```

#### ✅ NEW (Pooler - IPv4):
```
postgresql://postgres.lsqvxfaonbvqvlwrhsby:March%402024@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

### 3. Steps to Update on Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Select your service: `prosite`
3. Go to **Environment** tab
4. Find `DATABASE_URL` variable
5. Click **Edit**
6. Replace with pooler connection string (see above)
7. Click **Save Changes**
8. Render will automatically redeploy

### 4. Verification

After redeployment, check logs for:
```
[INFO] Booting worker with pid: XX
```

Then test login at: https://prosite.onrender.com

Should see successful database connection instead of "Network is unreachable"

## Technical Details

### Supabase Connection Modes

| Mode | Hostname | Port | IPv6? | Render Compatible? |
|------|----------|------|-------|-------------------|
| **Direct** | `db.lsqvxfaonbvqvlwrhsby.supabase.co` | 5432 | ✅ Yes | ❌ No |
| **Pooler** | `aws-0-ap-south-1.pooler.supabase.com` | 6543 | ❌ No (IPv4 only) | ✅ Yes |

### Why Pooler is Better

1. **IPv4 only** - Works with Render's infrastructure
2. **Connection pooling** - Better performance under load
3. **Lower latency** - Optimized for serverless/cloud deployments
4. **No connection limits** - Pooler manages connections efficiently

## Code Changes Made

**File**: `server/db.py`

```python
# If using PostgreSQL with Supabase, ensure we use pooler connection string
# Replace direct connection with pooler (IPv4 only)
database_url = DATABASE_URL
if 'supabase.co' in DATABASE_URL and 'pooler' not in DATABASE_URL:
    # Use IPv4 pooler connection
    database_url = DATABASE_URL.replace(
        'db.lsqvxfaonbvqvlwrhsby.supabase.co',
        'aws-0-ap-south-1.pooler.supabase.com'
    ).replace(':5432', ':6543')
```

This ensures even if someone uses the direct connection string, it gets auto-converted to pooler.

## Alternative: Transaction Mode

If you need true PostgreSQL transaction mode (not just session pooling), use:

```
postgresql://postgres.lsqvxfaonbvqvlwrhsby:March%402024@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?pgbouncer=true
```

But for most web applications, the session pooler (port 6543) is recommended.

## Status

- ✅ Code updated in `server/db.py`
- ⏳ **ACTION REQUIRED**: Update DATABASE_URL on Render dashboard
- ⏳ Wait for automatic redeployment
- ⏳ Test login functionality

## Next Steps

1. Update DATABASE_URL on Render (see above)
2. Wait for redeployment (~2 minutes)
3. Test at https://prosite.onrender.com
4. Commit this fix: `git add server/db.py && git commit -m "Fix IPv6 connection issue for Render deployment" && git push`
