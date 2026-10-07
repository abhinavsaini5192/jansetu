# JanSetu Platform PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "JanSetu Platform Launcher"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "             JanSetu Platform Launcher             " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = $PSScriptRoot
$backendDir = Join-Path $rootDir "jansetu-backend"

$pyCmd = "python"
if (Test-Path "$backendDir\.venv\Scripts\python.exe") {
    $pyCmd = "$backendDir\.venv\Scripts\python.exe"
    Write-Host "[*] Found virtualenv at: jansetu-backend\.venv" -ForegroundColor Green
} elseif (Test-Path "$backendDir\venv\Scripts\python.exe") {
    $pyCmd = "$backendDir\venv\Scripts\python.exe"
    Write-Host "[*] Found virtualenv at: jansetu-backend\venv" -ForegroundColor Green
} else {
    Write-Host "[*] Using system Python" -ForegroundColor Yellow
}

Write-Host "`n[1/2] Launching Backend (FastAPI on http://localhost:8000)..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k", "cd /d `"$backendDir`" && `"$pyCmd`" run.py"

Write-Host "[2/2] Launching Frontend (Vite on http://localhost:3000)..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k", "cd /d `"$rootDir`" && npm run dev"

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "  JanSetu is running!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  - Frontend Portal  : http://localhost:3000" -ForegroundColor White
Write-Host "  - Backend API      : http://localhost:8000" -ForegroundColor White
Write-Host "  - API Swagger Docs : http://localhost:8000/docs" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Leave the opened terminal windows running while using the app." -ForegroundColor Gray
