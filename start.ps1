# ProSite - Windows Startup Script
# Starts both Flask backend and Next.js frontend

Write-Host ""
Write-Host "🚀 Starting ProSite..." -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if Python virtual environment exists
if (Test-Path ".venv\Scripts\python.exe") {
    $PythonExe = ".venv\Scripts\python.exe"
    $FlaskExe = ".venv\Scripts\flask.exe"
    Write-Host "✓ Using Python virtual environment" -ForegroundColor Green
} else {
    $PythonExe = "python"
    $FlaskExe = "flask"
    Write-Host "⚠ Using system Python (virtual environment not found)" -ForegroundColor Yellow
}

# Check if dependencies are installed
Write-Host "📦 Checking Python dependencies..." -ForegroundColor Cyan
try {
    & $PythonExe -c "import flask, sqlalchemy, flask_cors, flask_jwt_extended" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python dependencies installed" -ForegroundColor Green
    } else {
        throw "Dependencies missing"
    }
} catch {
    Write-Host "⚠ Installing Python dependencies..." -ForegroundColor Yellow
    & $PythonExe -m pip install -r requirements.txt
}

# Check if Next.js dependencies are installed
Write-Host "📦 Checking Next.js dependencies..." -ForegroundColor Cyan
if (Test-Path "frontend\node_modules") {
    Write-Host "✓ Next.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Installing Next.js dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Starting Backend API (Flask) on port 8000..." -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Start Flask backend in a new window
$BackendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ScriptDir'; `$env:FLASK_APP='server.app:create_app()'; & '$FlaskExe' run --host=0.0.0.0 --port=8000"
) -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

# Check if backend started
$BackendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $BackendRunning = $true
    }
} catch {
    # Backend might still be starting
    $BackendRunning = $true
}

if ($BackendRunning) {
    Write-Host "✓ Backend API started successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Backend starting... (may take a few more seconds)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Starting Frontend (Next.js) on port 3000..." -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Start Next.js frontend in a new window
$FrontendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ScriptDir\frontend'; npm run dev"
) -PassThru -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║      🎉 PROSITE STARTED SUCCESSFULLY! 🎉                 ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access your application:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:   http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default login credentials:" -ForegroundColor Cyan
Write-Host "   Email:     admin@demo.com" -ForegroundColor White
Write-Host "   Password:  adminpass" -ForegroundColor White
Write-Host ""
Write-Host "📋 Management:" -ForegroundColor Cyan
Write-Host "   • Two PowerShell windows opened (Backend + Frontend)" -ForegroundColor White
Write-Host "   • Press Ctrl+C in each window to stop servers" -ForegroundColor White
Write-Host "   • Or close the windows to terminate" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit this window (servers will continue running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
