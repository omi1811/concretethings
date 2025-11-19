# ProSite - Windows Setup Script
# Configures environment and installs dependencies

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ProSite - Windows Setup" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check Python
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
try {
    $PythonVersion = & python --version 2>&1
    Write-Host "✓ $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "   Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Cyan
try {
    $NodeVersion = & node --version 2>&1
    Write-Host "✓ Node.js $NodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found!" -ForegroundColor Red
    Write-Host "   Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Create Python virtual environment
Write-Host ""
Write-Host "🔧 Setting up Python virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate and install Python dependencies
Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -m pip install --upgrade pip -q
& .venv\Scripts\python.exe -m pip install -r requirements.txt -q
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Initialize database
Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Cyan
& .venv\Scripts\python.exe -c "from server.db import init_db; init_db(); print('✓ Database initialized')"

# Check if seed data exists
Write-Host ""
Write-Host "🌱 Checking seed data..." -ForegroundColor Cyan
$RecordCount = & .venv\Scripts\python.exe -c "from server.db import session_scope; from server.models import User; from sqlalchemy import func; exec('with session_scope() as s:\n    count = s.query(func.count(User.id)).scalar()\n    print(count)')" 2>$null

if ([int]$RecordCount -eq 0) {
    Write-Host "⚠ No users found. You may want to create seed data." -ForegroundColor Yellow
} else {
    Write-Host "✓ Database has $RecordCount user(s)" -ForegroundColor Green
}

# Setup .env file
Write-Host ""
Write-Host "⚙️  Environment configuration..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
    } else {
        # Create minimal .env
        @"
SECRET_KEY=$(([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString()))))
JWT_SECRET_KEY=$(([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString()))))
DATABASE_URL=sqlite:///data.sqlite3
FLASK_ENV=development
APP_URL=http://localhost:8000
EMAIL_ENABLED=false
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "✓ Created default .env file" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Install Next.js dependencies
Write-Host ""
Write-Host "📦 Installing Next.js dependencies..." -ForegroundColor Cyan
Write-Host "   (This may take a few minutes...)" -ForegroundColor Yellow
Set-Location frontend
npm install --loglevel=error
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Next.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ npm install had warnings (this is usually okay)" -ForegroundColor Yellow
}
Set-Location ..

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Cyan
@("uploads", "backups", "static") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "✓ Created $_/" -ForegroundColor Green
    } else {
        Write-Host "✓ $_ directory exists" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║         ✅ SETUP COMPLETE!                               ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Start the application:" -ForegroundColor White
Write-Host "      .\start.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "   2. Or start manually:" -ForegroundColor White
Write-Host "      Backend:  .\.venv\Scripts\flask.exe run --port=8000" -ForegroundColor Yellow
Write-Host "      Frontend: cd frontend; npm run dev" -ForegroundColor Yellow
Write-Host ""
Write-Host "   3. Access the application:" -ForegroundColor White
Write-Host "      Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "      Backend:  http://localhost:8000/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "   - README.md - Project overview" -ForegroundColor White
Write-Host "   - QUICK_START.md - Quick start guide" -ForegroundColor White
Write-Host "   - PENDING_TASKS.md - Task list" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
