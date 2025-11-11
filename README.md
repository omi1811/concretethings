# ConcreteThings – Concrete Quality Management System

A **production-ready** full-stack application for managing concrete quality with **JWT authentication**, image storage, WhatsApp notifications, multi-tenant support, and a commercial-grade Python Flask backend.

## ✨ Features

### Core Quality Management Features
- ✅ **RMC Vendor Management** - Vendor registration, contact info, quality approval
- ✅ **Batch Register** - Mandatory batch sheet photo, detailed location tracking
- ✅ **Cube Test Register** - IS 516-1959 compliant, auto pass/fail calculation
- ✅ **WhatsApp Notifications** - Real-time alerts on test failures and batch rejections
- ✅ **Mix Design Management** - Vendor-linked designs with approval workflow
- ✅ **NCR Generation** - Automatic Non-Conformance Reports on failures
- ✅ **Location Tracking** - Building, floor, zone, grid, element identification

### Technical Features
- ✅ **Full CRUD REST API** with Flask + SQLAlchemy
- ✅ **JWT Authentication** - Secure token-based auth with role-based access control
- ✅ **Multi-Tenant Support** - Companies, users, projects, and memberships
- ✅ **Image Upload & Storage** - Store mix design photos and batch sheets in database
- ✅ **Document Management** - Upload PDF/Word files
- ✅ **Responsive Web UI** - Works on desktop, tablet, and mobile
- ✅ **Search & Filter** - Quickly find designs by project or ID

### Security Features
- ✅ **Robust Authentication** - Email/phone login, strong password requirements
- ✅ **Account Protection** - Failed login lockout (5 attempts = 30 min)
- ✅ **Password Hashing** - pbkdf2:sha256 secure hashing
- ✅ **Token Refresh** - Long-lived refresh tokens
- ✅ **Role-Based Access** - System Admin, Company Admin, Project roles
- ✅ **Email & Phone Validation** - Mandatory contact information

### Production Features
- ✅ **Production-Ready** - CORS, security headers, logging, error handling
- ✅ **Database Flexible** - Works with SQLite, PostgreSQL, or MySQL
- ✅ **Docker Support** - Easy deployment with Docker Compose
- ✅ **Pure JavaScript** - No TypeScript compilation needed
- ✅ **Data Protection** - Soft delete (no permanent deletion)
- ✅ **Audit Trail** - Track who created, modified, deleted records

## 🔔 WhatsApp Notifications

Real-time alerts for critical quality events:
- 🚨 **Test Failures** - Notify QM, PM, and RMC vendor when concrete strength tests fail
- ❌ **Batch Rejections** - Alert vendor and PM when batches are rejected
- 📋 **NCR Generation** - Notify stakeholders of Non-Conformance Reports

**Quick Setup:**
1. Sign up for Twilio: https://www.twilio.com/try-twilio
2. Copy `.env.example` to `.env` and add credentials
3. Set `WHATSAPP_ENABLED=true`
4. Test: `python test_notifications.py`

📖 **See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) for complete guide**

## 🔐 Authentication

The app now requires authentication. See [AUTHENTICATION.md](AUTHENTICATION.md) for complete documentation.

**Quick Start:**
1. Navigate to: `http://localhost:8000/static/login.html`
2. Use demo credentials: `admin@demo.com` / `adminpass`
3. All API endpoints require JWT token in Authorization header

## 🎯 Commercial Use Ready

This application is built for **commercial deployment** with:
- Production-grade security (CORS, headers, validation)
- Environment-based configuration
- Gunicorn WSGI server
- Docker containerization
- PostgreSQL support for scalability
- Comprehensive deployment guide

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup and database recommendations**

## 📁 Project Structure

```
/workspaces/concretethings/
├── server/               # Backend (Flask + SQLAlchemy)
│   ├── __init__.py
│   ├── app.py           # Flask app with REST API endpoints
│   ├── db.py            # Database configuration
│   └── models.py        # MixDesign SQLAlchemy model
├── static/              # Frontend
│   ├── index.html       # Main UI
│   ├── app.js           # JavaScript for API calls
│   └── styles.css       # Styling
├── uploads/             # Uploaded documents
├── archive/             # Old React/TypeScript files (not used)
├── data.sqlite3         # SQLite database
├── requirements.txt     # Python dependencies
├── seed.py              # Database seeding script
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed Sample Data (Optional)

```bash
python seed.py
```

This creates 3 sample mix designs to get started.

### 3. Start the Server

```bash
python -m server.app
```

The server runs on **http://localhost:8000**

### 4. Open the Application

Visit http://localhost:8000 in your browser to use the web interface.

## 🔧 API Reference

Base URL: `http://localhost:8000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/mix-designs` | List all mix designs |
| `POST` | `/api/mix-designs` | Create a new mix design |
| `PUT` | `/api/mix-designs/{id}` | Update a mix design |
| `DELETE` | `/api/mix-designs/{id}` | Delete a mix design |
| `GET` | `/uploads/{filename}` | Download uploaded document |

### Request Body (POST/PUT)

```json
{
  "projectName": "Downtown Plaza",
  "mixDesignId": "MD-3000-A",
  "specifiedStrengthPsi": 3000,
  "slumpInches": 4.0,
  "airContentPercent": 6.0,
  "batchVolume": 1.0,
  "volumeUnit": "cubic_yards",
  "materials": "Portland Cement: 517 lbs\nAggregate: 1840 lbs",
  "notes": "Standard foundation mix"
}
```

**Note:** Use `multipart/form-data` when uploading files with the `document` field.

## 🧪 Testing

### Test Database
```bash
python test_db.py
```

### Test API (requires server running)
```bash
python test_api.py
```

## 📝 Database Schema

**MixDesign Model:**
- `id` - Primary key
- `project_name` - Project identifier
- `mix_design_id` - Mix design reference number
- `specified_strength_psi` - Concrete strength in PSI
- `slump_inches` - Slump measurement
- `air_content_percent` - Air content percentage
- `batch_volume` - Volume of batch
- `volume_unit` - "cubic_yards" or "cubic_meters"
- `materials` - Material specifications (text)
- `notes` - Additional notes
- `document_name` - Uploaded file name
- `ocr_text` - OCR extracted text
- `created_at` - Timestamp
- `updated_at` - Timestamp

## 🛠️ Development

### File Organization

- **Working files**: All files in `server/`, `static/`, and root-level scripts
- **Archived files**: Old React/TypeScript components in `archive/` (not used by the application)

### Adding Features

To extend the application:
1. Add new models in `server/models.py`
2. Add endpoints in `server/app.py`
3. Update frontend in `static/app.js` and `static/index.html`

## 📦 Dependencies

- Flask 3.0.3
- SQLAlchemy 2.0.35
- Werkzeug 3.0.4
- itsdangerous 2.2.0
- click 8.1.7

## 🎯 Features

- **Create**: Add new mix designs with all specifications
- **Read**: View all mix designs in a sortable table
- **Update**: Edit existing mix designs inline
- **Delete**: Remove mix designs with confirmation
- **Search**: Filter by project name or mix design ID
- **Upload**: Attach documents to mix designs
- **Responsive**: Works on desktop and mobile devices

## 📄 License

This project is for educational/internal use.
