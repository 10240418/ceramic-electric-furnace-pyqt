# ========================================
# 3号电炉启动脚本（单实例保护）
# ========================================

# 1. 设置工作目录
$workDir = "D:\dist\3号电炉"
$exePath = "$workDir\3号电炉.exe"
$processName = "3号电炉"

# 2. 检查 InfluxDB 是否运行
Write-Host "检查 InfluxDB 服务状态..." -ForegroundColor Yellow
$influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
if (-not $influxService -or $influxService.Status -ne "Running") {
    Write-Host "InfluxDB 服务未运行，等待 30 秒..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# 3. 再次检查 InfluxDB
$influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
if (-not $influxService -or $influxService.Status -ne "Running") {
    Write-Host "警告: InfluxDB 服务仍未运行，但继续启动 3号电炉..." -ForegroundColor Red
}

# 4. 杀死所有旧进程（单实例保护）
Write-Host "检查并清理旧进程..." -ForegroundColor Yellow
$oldProcesses = Get-Process -Name $processName -ErrorAction SilentlyContinue
if ($oldProcesses) {
    Write-Host "发现 $($oldProcesses.Count) 个旧进程，正在清理..." -ForegroundColor Yellow
    $oldProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# 5. 启动 3号电炉
Write-Host "启动 3号电炉..." -ForegroundColor Green
Set-Location $workDir
Start-Process -FilePath $exePath -WorkingDirectory $workDir

Write-Host "3号电炉已启动！" -ForegroundColor Green





