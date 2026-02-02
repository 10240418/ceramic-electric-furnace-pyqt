# ========================================
# Deploy on Industrial PC (D Drive)
# ========================================
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "3# Electric Furnace - Industrial PC Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Running as Administrator" -ForegroundColor Green
Write-Host ""

# ========================================
# Step 1: Create Directory Structure
# ========================================
Write-Host "[1/6] Creating directory structure..." -ForegroundColor Yellow

# Create InfluxDB data and logs directories
New-Item -ItemType Directory -Force -Path "D:\influxdb\data" | Out-Null
New-Item -ItemType Directory -Force -Path "D:\influxdb\logs" | Out-Null

# Create FurnaceMonitor logs directory
New-Item -ItemType Directory -Force -Path "D:\dist\3号电炉\logs" | Out-Null

Write-Host "  [OK] Directories created" -ForegroundColor Green

# ========================================
# Step 2: Check Required Files
# ========================================
Write-Host "[2/6] Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "D:\influxdb\influxd.exe",
    "D:\influxdb\WinSW.exe",
    "D:\influxdb\InfluxDB-service.xml",
    "D:\dist\3号电炉\3号电炉.exe",
    "D:\dist\3号电炉\WinSW.exe",
    "D:\dist\3号电炉\FurnaceMonitor-service.xml"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "[ERROR] Some required files are missing!" -ForegroundColor Red
    Write-Host "Please make sure all files are copied to D:\" -ForegroundColor Yellow
    exit 1
}

Write-Host "  [OK] All required files found" -ForegroundColor Green

# ========================================
# Step 3: Stop and Uninstall Existing Services
# ========================================
Write-Host "[3/6] Stopping and uninstalling existing services..." -ForegroundColor Yellow

# Stop FurnaceMonitor service
$furnaceService = Get-Service -Name "FurnaceMonitor" -ErrorAction SilentlyContinue
if ($furnaceService) {
    Write-Host "  Stopping FurnaceMonitor service..." -ForegroundColor Gray
    Stop-Service -Name "FurnaceMonitor" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Uninstall FurnaceMonitor service
if (Test-Path "D:\dist\3号电炉\WinSW.exe") {
    Write-Host "  Uninstalling FurnaceMonitor service..." -ForegroundColor Gray
    & "D:\dist\3号电炉\WinSW.exe" uninstall 2>$null
    Start-Sleep -Seconds 1
}

# Stop InfluxDB service
$influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
if ($influxService) {
    Write-Host "  Stopping InfluxDB service..." -ForegroundColor Gray
    Stop-Service -Name "InfluxDB" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Uninstall InfluxDB service
if (Test-Path "D:\influxdb\WinSW.exe") {
    Write-Host "  Uninstalling InfluxDB service..." -ForegroundColor Gray
    & "D:\influxdb\WinSW.exe" uninstall 2>$null
    Start-Sleep -Seconds 1
}

# Kill any remaining influxd.exe processes
$influxProcesses = Get-Process -Name "influxd" -ErrorAction SilentlyContinue
if ($influxProcesses) {
    Write-Host "  Killing remaining influxd.exe processes..." -ForegroundColor Gray
    $influxProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Kill any remaining 3号电炉.exe processes
$furnaceProcesses = Get-Process -Name "3号电炉" -ErrorAction SilentlyContinue
if ($furnaceProcesses) {
    Write-Host "  Killing remaining 3号电炉.exe processes..." -ForegroundColor Gray
    $furnaceProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

Write-Host "  [OK] Existing services stopped and uninstalled" -ForegroundColor Green

# ========================================
# Step 4: Install InfluxDB Service
# ========================================
Write-Host "[4/6] Installing InfluxDB service..." -ForegroundColor Yellow

cd "D:\influxdb"
& ".\WinSW.exe" install

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] InfluxDB service installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] InfluxDB service installation failed (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

# ========================================
# Step 5: Install FurnaceMonitor Service
# ========================================
Write-Host "[5/6] Installing FurnaceMonitor service..." -ForegroundColor Yellow

cd "D:\dist\3号电炉"
& ".\WinSW.exe" install

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] FurnaceMonitor service installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] FurnaceMonitor service installation failed (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

# ========================================
# Step 6: Start Services
# ========================================
Write-Host "[6/6] Starting services..." -ForegroundColor Yellow

# Start InfluxDB first
Write-Host "  Starting InfluxDB service..." -ForegroundColor Gray
Start-Service InfluxDB
Start-Sleep -Seconds 5

$influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
if ($influxService -and $influxService.Status -eq "Running") {
    Write-Host "  [OK] InfluxDB service started" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] InfluxDB service may not be running" -ForegroundColor Yellow
    Write-Host "  Check logs: D:\influxdb\logs\" -ForegroundColor Gray
}

# Wait for InfluxDB to be fully ready
Write-Host "  Waiting for InfluxDB to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Start FurnaceMonitor
Write-Host "  Starting FurnaceMonitor service..." -ForegroundColor Gray
Start-Service FurnaceMonitor
Start-Sleep -Seconds 3

$furnaceService = Get-Service -Name "FurnaceMonitor" -ErrorAction SilentlyContinue
if ($furnaceService -and $furnaceService.Status -eq "Running") {
    Write-Host "  [OK] FurnaceMonitor service started" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] FurnaceMonitor service may not be running" -ForegroundColor Yellow
    Write-Host "  Check logs: D:\dist\3号电炉\logs\" -ForegroundColor Gray
}

# ========================================
# Deployment Complete
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installation Directories:" -ForegroundColor Yellow
Write-Host "  InfluxDB:        D:\influxdb\" -ForegroundColor White
Write-Host "  FurnaceMonitor:  D:\dist\3号电炉\" -ForegroundColor White
Write-Host ""

Write-Host "Data Directories:" -ForegroundColor Yellow
Write-Host "  InfluxDB Data:   D:\influxdb\data\" -ForegroundColor White
Write-Host "  InfluxDB Logs:   D:\influxdb\logs\" -ForegroundColor White
Write-Host "  App Logs:        D:\dist\3号电炉\logs\" -ForegroundColor White
Write-Host ""

Write-Host "Service Status:" -ForegroundColor Yellow
Get-Service InfluxDB,FurnaceMonitor | Format-Table -AutoSize
Write-Host ""

Write-Host "Service Features:" -ForegroundColor Yellow
Write-Host "  - Auto-start on system boot" -ForegroundColor White
Write-Host "  - InfluxDB starts first, then FurnaceMonitor" -ForegroundColor White
Write-Host "  - FurnaceMonitor depends on InfluxDB" -ForegroundColor White
Write-Host "  - Auto-restart on crash (3 attempts)" -ForegroundColor White
Write-Host "  - Single instance guaranteed by Windows Service" -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open browser: http://localhost:8086" -ForegroundColor White
Write-Host "  2. Initialize InfluxDB (first time only):" -ForegroundColor White
Write-Host "     - Username: admin" -ForegroundColor Gray
Write-Host "     - Password: admin_password" -ForegroundColor Gray
Write-Host "     - Organization: furnace" -ForegroundColor Gray
Write-Host "     - Bucket: sensor_data" -ForegroundColor Gray
Write-Host "  3. Copy the generated Token" -ForegroundColor White
Write-Host "  4. Update Token in config:" -ForegroundColor White
Write-Host "     D:\dist\3号电炉\backend\config.py" -ForegroundColor Gray
Write-Host "  5. Restart FurnaceMonitor:" -ForegroundColor White
Write-Host "     Restart-Service FurnaceMonitor" -ForegroundColor Gray
Write-Host ""

Write-Host "Management Commands:" -ForegroundColor Yellow
Write-Host "  Check status:  Get-Service InfluxDB,FurnaceMonitor" -ForegroundColor White
Write-Host "  Start:         Start-Service InfluxDB" -ForegroundColor White
Write-Host "                 Start-Service FurnaceMonitor" -ForegroundColor White
Write-Host "  Stop:          Stop-Service FurnaceMonitor" -ForegroundColor White
Write-Host "                 Stop-Service InfluxDB" -ForegroundColor White
Write-Host "  Restart:       Restart-Service FurnaceMonitor" -ForegroundColor White
Write-Host "  View logs:     Get-Content D:\influxdb\logs\*.log -Tail 50" -ForegroundColor White
Write-Host "                 Get-Content D:\dist\3号电炉\logs\*.log -Tail 50" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Successful!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

