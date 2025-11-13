# Render.com Deployment Guide

## Critical: Environment Variables Configuration

The deployment is failing because Render doesn't have the required environment variables configured. You must add these in the Render dashboard before the app can start successfully.

### Step 1: Access Render Dashboard

1. Go to https://dashboard.render.com/
2. Click on your **ProSite** web service
3. Navigate to **Environment** tab in the left sidebar

### Step 2: Add Required Environment Variables

Click **Add Environment Variable** and add the following:

#### Essential Variables (MUST ADD):

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql://postgres:March%402024@db.lsqvxfaonbvqvlwrhsby.supabase.co:5432/postgres` | Your Supabase connection string |
| `FLASK_ENV` | `production` | Important: NOT "development" |
| `SECRET_KEY` | *Generate new* | Run: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `JWT_SECRET_KEY` | *Generate new* | Run: `python3 -c "import secrets; print(secrets.token_hex(32))"` |

#### Optional Variables (Recommended):

| Key | Value | Default |
|-----|-------|---------|
| `DEBUG` | `False` | Already defaults to False |
| `LOG_LEVEL` | `INFO` | For production logging |
| `CORS_ORIGINS` | `*` | Allow all origins (change for security) |

#### Optional - WhatsApp Notifications:

| Key | Value |
|-----|-------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | `whatsapp:+14155238886` |

### Step 3: Generate Secret Keys

Run these commands in your local terminal to generate secure keys:

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (run again for different key)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste into Render environment variables.

### Step 4: Save and Redeploy

1. Click **Save Changes** at the bottom of the Environment tab
2. Render will automatically trigger a new deployment
3. Monitor the deployment logs

### Step 5: Verify Deployment

Once deployed (should take ~2-3 minutes), test the health endpoint:

```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{"status":"healthy","service":"prosite-api"}
```

---

## Why the Current Deployment is Failing

**Error:** `Network is unreachable - connection to server at "db.lsqvxfaonbvqvlwrhsby.supabase.co"`

**Root Cause:** The app is trying to connect to Supabase, but Render doesn't have the `DATABASE_URL` environment variable configured, so it's trying to use SQLite (which doesn't work in production).

**Fix Applied in Code:**
- Changed `init_db()` to only run in development mode
- In production, tables already exist via migration scripts
- This prevents unnecessary table creation attempts on startup

**Required Action:** Add environment variables in Render dashboard (see above).

---

## Production vs Development Behavior

### Development Mode (`FLASK_ENV=development`)
- Calls `init_db()` to auto-create SQLite tables
- Uses local SQLite database at `data.sqlite3`
- Enables debug mode and detailed error messages

### Production Mode (`FLASK_ENV=production`)
- **Does NOT** call `init_db()` (tables created via migration)
- Uses Supabase Postgres database
- Disables debug mode, returns generic error messages
- Requires environment variables to be configured

---

## Troubleshooting

### If deployment still fails after adding environment variables:

1. **Check Render Logs:** Dashboard → Logs tab → Look for specific error messages
2. **Verify DATABASE_URL:** Ensure the connection string is correct (check for typos)
3. **Test Supabase Connection:** Go to Supabase dashboard → ensure database is running
4. **Check Secrets:** Ensure SECRET_KEY and JWT_SECRET_KEY are properly set
5. **Manual Redeploy:** Dashboard → Manual Deploy → Deploy latest commit

### Common Issues:

- **"sqlalchemy.exc.OperationalError"**: Database connection failed - check DATABASE_URL
- **"Network is unreachable"**: Supabase might be down or DATABASE_URL is incorrect
- **"No SECRET_KEY"**: Add SECRET_KEY environment variable
- **Port binding errors**: Render automatically sets $PORT, don't override it

---

## Next Steps After Successful Deployment

1. ✅ Test all API endpoints
2. ✅ Configure custom domain (if using GoDaddy domain)
3. ✅ Set up monitoring/alerts in Render
4. ✅ Enable automatic deployments from GitHub (already enabled)
5. ✅ Configure Supabase Row Level Security (RLS) policies
6. ✅ Migrate file uploads to Supabase Storage (currently using local `/uploads`)
7. ✅ Set up background job scheduler for reminders/notifications
