# ProSite - Windows Setup Guide

## 🪟 Running ProSite on Windows

This project was originally developed for Linux but has been adapted for Windows. This guide covers Windows-specific setup and differences.

## Prerequisites

1. **Python 3.11+**
   - Download from: https://www.python.org/downloads/
   - ✅ Make sure to check "Add Python to PATH" during installation

2. **Node.js 18+**
   - Download from: https://nodejs.org/
   - LTS version recommended

3. **PowerShell 5.1+** (Included with Windows 10/11)

## Quick Start (Windows)

### Option 1: Automated Setup (Recommended)

```powershell
# Run setup script
.\setup.ps1

# Start the application
.\start.ps1
```

### Option 2: Manual Setup

```powershell
# 1. Create Python virtual environment
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Initialize database
python -c "from server.db import init_db; init_db()"

# 5. Install Next.js dependencies
cd frontend
npm install
cd ..

# 6. Create .env file
Copy-Item .env.example .env  # Or create manually

# 7. Start Backend (in one terminal)
$env:FLASK_APP = "server.app:create_app()"
flask run --host=0.0.0.0 --port=8000

# 8. Start Frontend (in another terminal)
cd frontend
npm run dev
```

## 🐧 Linux vs 🪟 Windows Differences

### Files That DON'T Work on Windows

| Linux File | Windows Alternative | Notes |
|------------|-------------------|-------|
| `run.sh` | `start.ps1` | Bash → PowerShell |
| `setup.sh` | `setup.ps1` | Bash → PowerShell |
| `start.sh` | `start.ps1` | Bash → PowerShell |
| Uses `gunicorn` | Uses Flask dev server | Gunicorn requires POSIX (fcntl module) |
| `#!/bin/bash` shebang | PowerShell scripts | Different scripting language |
| `lsof`, `pkill` commands | PowerShell equivalents | Different system utilities |

### Key Differences

1. **Web Server**
   - **Linux**: Uses Gunicorn (production-grade WSGI server)
   - **Windows**: Uses Flask development server
   - **Why**: Gunicorn requires POSIX-compliant OS (no `fcntl` module on Windows)
   - **Solution for Production**: Use `waitress` or deploy on Linux

2. **Scripts**
   - **Linux**: Bash scripts (`.sh`)
   - **Windows**: PowerShell scripts (`.ps1`)

3. **Path Separators**
   - **Linux**: `/` (forward slash)
   - **Windows**: `\` (backslash) - Python handles this automatically

4. **Virtual Environment Activation**
   - **Linux**: `source .venv/bin/activate`
   - **Windows**: `.\.venv\Scripts\Activate.ps1`

## 🚀 Running the Application

### Using PowerShell Scripts (Easiest)

```powershell
.\start.ps1
```

This will:
- ✅ Start Flask backend on http://localhost:8000
- ✅ Start Next.js frontend on http://localhost:3000
- ✅ Open two PowerShell windows (one for each server)

### Manual Start

**Terminal 1 - Backend:**
```powershell
$env:FLASK_APP = "server.app:create_app()"
.\.venv\Scripts\flask.exe run --host=0.0.0.0 --port=8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 🔧 Troubleshooting

### PowerShell Execution Policy Error

If you get "cannot be loaded because running scripts is disabled":

```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Module 'fcntl' Not Found

This error occurs when trying to use Gunicorn on Windows:
- **Solution**: Use Flask dev server (already configured in `start.ps1`)
- **For Production**: Deploy on Linux or use `waitress` server

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F
```

### Node Modules Installation Failures

```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
Remove-Item -Recurse -Force frontend\node_modules
cd frontend
npm install
```

## 📦 Production Deployment on Windows

### Using Waitress (Python WSGI Server for Windows)

1. Install waitress:
```powershell
pip install waitress
```

2. Create `run_waitress.py`:
```python
from waitress import serve
from server.app import create_app

app = create_app()
serve(app, host='0.0.0.0', port=8000, threads=4)
```

3. Run:
```powershell
python run_waitress.py
```

### Or Deploy on Linux (Recommended)

For production, deploying on Linux with Gunicorn is recommended:
- Use Docker (see `Dockerfile`)
- Deploy to cloud platforms (AWS, Azure, Google Cloud)
- Use WSL2 on Windows for Linux environment

## 🔐 Default Credentials

- **Email**: admin@demo.com
- **Password**: adminpass

**⚠️ Change these immediately in production!**

## 📚 Additional Resources

- [QUICK_START.md](QUICK_START.md) - General quick start guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions (Linux-focused)
- [PROSITE_ARCHITECTURE.md](PROSITE_ARCHITECTURE.md) - System architecture

## ⚡ Performance Tips

1. **Use SSD**: Install project on SSD for faster npm/pip operations
2. **Exclude from Antivirus**: Add project folder to Windows Defender exclusions
3. **WSL2 Alternative**: For better performance, consider using WSL2 with Linux

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Review error messages in PowerShell windows
3. Check `PENDING_TASKS.md` for known issues
4. Contact: support@prosite.com

---

**Note**: This project works fully on Windows, but for production deployment, Linux is recommended for better performance and to use production-grade servers like Gunicorn.
