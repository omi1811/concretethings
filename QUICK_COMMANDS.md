# Quick Command Reference

## Development Server

### Start Server
```bash
# With gunicorn (recommended)
cd /workspaces/concretethings
gunicorn -w 4 -b 0.0.0.0:8001 --timeout 30 'server.app:create_app()'

# With Flask (development only)
python -m server.app
```

### Run Tests
```bash
# Full test suite
python test_material_vehicle.py

# API health check
curl http://localhost:8001/health
```

## Database Management

### Reset Database
```bash
# Clean all data
python -c "from server.db import SessionLocal; from server.models import *; session = SessionLocal(); session.query(MaterialVehicleRegister).delete(); session.query(BatchRegister).delete(); session.commit(); session.close()"

# Full recreate
rm data.sqlite3
python -c "from server.db import Base, engine; import server.models; Base.metadata.create_all(engine); print('✓ Database recreated')"
```

### Run Migrations
```bash
# Material Vehicle Register + Project Settings
python migrate_material_vehicle.py

# Other migrations
python migrate_users.py
python migrate_pour_activities.py
```

## Background Jobs

### Manual Triggers
```bash
# Check vehicle time limits (RMC only)
curl -X POST http://localhost:8001/api/background-jobs/run-vehicle-check \
  -H "Authorization: Bearer YOUR_TOKEN"

# Send test reminders
curl -X POST http://localhost:8001/api/background-jobs/run-test-reminder \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check missed tests
curl -X POST http://localhost:8001/api/background-jobs/run-missed-test-check \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Testing

### Login
```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### Create Vehicle
```bash
curl -X POST http://localhost:8001/api/material-vehicles/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "vehicleNumber": "MH-01-1234",
    "materialType": "Concrete",
    "supplierName": "ABC Concrete",
    "driverName": "John Doe",
    "driverPhone": "+919876543210"
  }'
```

### List Vehicles
```bash
curl -X GET "http://localhost:8001/api/material-vehicles/list?projectId=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Available Vehicles for Bulk Entry
```bash
curl -X GET "http://localhost:8001/api/bulk-entry/available-vehicles?projectId=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Batches (Bulk Entry)
```bash
curl -X POST http://localhost:8001/api/bulk-entry/create-batches \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": 1,
    "vehicleIds": [1, 2, 3],
    "concreteDetails": {
      "vendorName": "ABC Concrete",
      "grade": "M45FF",
      "totalQuantity": 3.0,
      "location": "Building A / 5th Floor Slab",
      "slump": 100,
      "temperature": 32
    }
  }'
```

### Check Time Limits
```bash
curl -X POST http://localhost:8001/api/material-vehicles/check-time-limits \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"projectId": 1}'
```

## Production Deployment

### Install Dependencies
```bash
pip install -r requirements.txt
pip install apscheduler  # For background jobs
```

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///data.sqlite3
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
MAX_UPLOAD_SIZE=10485760
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
WHATSAPP_API_KEY=your-whatsapp-api-key
EOF
```

### Start with Gunicorn
```bash
# Production
gunicorn -c gunicorn.conf.py 'server.app:create_app()'

# With background jobs
nohup python -c "from scheduler import start_scheduler; start_scheduler()" &
gunicorn -c gunicorn.conf.py 'server.app:create_app()'
```

### Nginx Configuration
```bash
# /etc/nginx/sites-available/concretethings
server {
    listen 80;
    server_name yourdomain.com;

    # API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/concretethings /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Monitoring

### Check Logs
```bash
# Gunicorn logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log

# Application logs
tail -f logs/app.log
```

### Check Process Status
```bash
# Gunicorn
ps aux | grep gunicorn

# Background scheduler
ps aux | grep scheduler

# Database size
ls -lh data.sqlite3
```

### Database Backup
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
cp data.sqlite3 backups/data_$DATE.sqlite3
# Keep only last 30 days
find backups/ -name "data_*.sqlite3" -mtime +30 -delete
```

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:8001 | xargs kill -9
```

### Clear Sessions
```bash
python -c "from server.db import SessionLocal; SessionLocal.remove()"
```

### Reload Gunicorn
```bash
# Graceful reload
pkill -HUP gunicorn

# Force restart
pkill -9 gunicorn
gunicorn -c gunicorn.conf.py 'server.app:create_app()'
```

### Check Database Integrity
```bash
sqlite3 data.sqlite3 "PRAGMA integrity_check;"
```

## Migration to Supabase

### Export Data
```bash
# Export to SQL
sqlite3 data.sqlite3 .dump > backup.sql

# Export to JSON
python -c "
from server.db import SessionLocal
from server.models import *
import json

session = SessionLocal()

# Export vehicles
vehicles = session.query(MaterialVehicleRegister).all()
with open('vehicles.json', 'w') as f:
    json.dump([v.to_dict() for v in vehicles], f, indent=2, default=str)

# Export batches
batches = session.query(BatchRegister).all()
with open('batches.json', 'w') as f:
    json.dump([b.to_dict() for b in batches], f, indent=2, default=str)

session.close()
print('✓ Exported to vehicles.json and batches.json')
"
```

### Update Connection String
```bash
# In .env
DATABASE_URL=postgresql://user:password@db.your-project.supabase.co:5432/postgres

# Test connection
python -c "from server.db import engine; engine.connect(); print('✓ Connected to Supabase')"
```

### Run Migrations on Supabase
```bash
# Supabase uses standard PostgreSQL
python migrate_material_vehicle.py
python migrate_users.py
# ... other migrations
```

## Performance Optimization

### Database Indexes
```bash
# Check index usage
sqlite3 data.sqlite3 "SELECT * FROM sqlite_master WHERE type='index';"

# Analyze query performance
sqlite3 data.sqlite3 "EXPLAIN QUERY PLAN SELECT * FROM material_vehicle_register WHERE project_id = 1;"
```

### Cache Configuration
```bash
# Install Redis
pip install redis

# Update config
REDIS_URL=redis://localhost:6379/0
```

## Quick Development Workflow

### 1. Start Development
```bash
# Terminal 1: Start backend
gunicorn -w 1 -b 0.0.0.0:8001 --reload 'server.app:create_app()'

# Terminal 2: Start frontend
cd frontend && npm run dev

# Terminal 3: Watch logs
tail -f /tmp/gunicorn.log
```

### 2. Make Changes
```bash
# Backend auto-reloads with --reload flag
# Frontend auto-reloads with npm run dev
```

### 3. Test Changes
```bash
# Run API tests
python test_material_vehicle.py

# Manual test
curl http://localhost:8001/health
```

---

## Useful Queries

### Count Records
```bash
python -c "
from server.db import SessionLocal
from server.models import *

session = SessionLocal()
print(f'Vehicles: {session.query(MaterialVehicleRegister).count()}')
print(f'Batches: {session.query(BatchRegister).count()}')
print(f'Users: {session.query(User).count()}')
print(f'Projects: {session.query(Project).count()}')
session.close()
"
```

### View Recent Vehicles
```bash
python -c "
from server.db import SessionLocal
from server.models import MaterialVehicleRegister

session = SessionLocal()
vehicles = session.query(MaterialVehicleRegister).order_by(MaterialVehicleRegister.created_at.desc()).limit(5).all()
for v in vehicles:
    print(f'{v.vehicle_number}: {v.material_type} - {v.status}')
session.close()
"
```

### Check Time Violations
```bash
python -c "
from server.db import SessionLocal
from server.models import MaterialVehicleRegister
from datetime import datetime, timedelta

session = SessionLocal()
cutoff = datetime.utcnow() - timedelta(hours=3)
exceeded = session.query(MaterialVehicleRegister).filter(
    MaterialVehicleRegister.material_type.in_(['Concrete', 'RMC', 'Ready Mix Concrete']),
    MaterialVehicleRegister.status == 'on_site',
    MaterialVehicleRegister.entry_time <= cutoff
).all()

print(f'Vehicles exceeding time limit: {len(exceeded)}')
for v in exceeded:
    duration = (datetime.utcnow() - v.entry_time).total_seconds() / 3600
    print(f'  {v.vehicle_number}: {duration:.1f} hours')
session.close()
"
```

---

**For more details, see BACKEND_COMPLETE_SUMMARY.md**
