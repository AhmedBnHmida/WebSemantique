# Quick Start Script for Web Sémantique Platform
# Run this script to start all services

Write-Host "🚀 Starting Web Sémantique Platform..." -ForegroundColor Green
Write-Host ""

# Check if Java is installed
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1
    Write-Host "✓ Java found" -ForegroundColor Green
} catch {
    Write-Host "✗ Java not found. Please install Java JDK 8 or higher." -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16 or higher." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Starting Services..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start Fuseki
Write-Host "1️⃣ Starting Fuseki Server (Terminal 1)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd fuseki/apache-jena-fuseki-5.6.0; Write-Host '🔵 Fuseki Server' -ForegroundColor Blue; Write-Host 'Starting on http://localhost:3030' -ForegroundColor Cyan; java -jar fuseki-server.jar"

Write-Host "   Waiting 5 seconds for Fuseki to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Step 2: Load Data (optional - only if not already loaded)
Write-Host ""
Write-Host "2️⃣ Loading Data (Terminal 2)..." -ForegroundColor Yellow
$loadData = Read-Host "   Load data into Fuseki? (y/n)"
if ($loadData -eq "y" -or $loadData -eq "Y") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd scripts; Write-Host '📊 Data Loader' -ForegroundColor Blue; python load_data.py; Write-Host ''; Write-Host 'Press any key to close...' -ForegroundColor Gray; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')"
    Write-Host "   Waiting 10 seconds for data to load..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
}

# Step 3: Start Backend
Write-Host ""
Write-Host "3️⃣ Starting Backend Server (Terminal 3)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; Write-Host '🔴 Backend Server' -ForegroundColor Red; Write-Host 'Starting on http://localhost:5000' -ForegroundColor Cyan; python app.py"

Write-Host "   Waiting 3 seconds for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Step 4: Start Frontend
Write-Host ""
Write-Host "4️⃣ Starting Frontend Server (Terminal 4)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; Write-Host '🟢 Frontend Server' -ForegroundColor Green; Write-Host 'Starting on http://localhost:3000' -ForegroundColor Cyan; npm start"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application:" -ForegroundColor Cyan
Write-Host "  • Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  • Backend:   http://localhost:5000" -ForegroundColor White
Write-Host "  • Fuseki:    http://localhost:3030" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Keep all terminal windows open!" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C in each terminal to stop services" -ForegroundColor Gray
Write-Host ""

