# ========================================
# 完整清理 + 增强版看门狗部署
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始清理旧配置..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[错误] 必须以管理员身份运行！" -ForegroundColor Red
    exit 1
}

# ========================================
# 清理阶段
# ========================================

Write-Host "[清理 1/5] 停止所有相关任务..." -ForegroundColor Yellow
Get-ScheduledTask | Where-Object { 
    $_.TaskName -like "*3号电炉*" -or 
    $_.TaskName -like "*watch*" -or 
    $_.TaskName -like "*Furnace*" -or 
    $_.TaskName -like "*电炉*" 
} | ForEach-Object {
    Write-Host "  停止任务: $($_.TaskName)" -ForegroundColor Gray
    Stop-ScheduledTask -TaskName $_.TaskName -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2
Write-Host "  [OK] 任务已停止" -ForegroundColor Green

Write-Host "[清理 2/5] 删除所有相关任务计划..." -ForegroundColor Yellow
Get-ScheduledTask | Where-Object { 
    $_.TaskName -like "*3号电炉*" -or 
    $_.TaskName -like "*watch*" -or 
    $_.TaskName -like "*Furnace*" -or 
    $_.TaskName -like "*电炉*" 
} | ForEach-Object {
    Write-Host "  删除任务: $($_.TaskName)" -ForegroundColor Gray
    Unregister-ScheduledTask -TaskName $_.TaskName -Confirm:$false -ErrorAction SilentlyContinue
}
Write-Host "  [OK] 任务计划已清理" -ForegroundColor Green

Write-Host "[清理 3/5] 停止所有 3号电炉进程..." -ForegroundColor Yellow
Get-Process -Name "3号电炉" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  停止进程: PID $($_.Id)" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force
}
Start-Sleep -Seconds 2
Write-Host "  [OK] 进程已清理" -ForegroundColor Green

Write-Host "[清理 4/5] 删除旧的脚本文件..." -ForegroundColor Yellow
$oldScripts = @(
    "D:\dist\3号电炉\start_furnace.ps1",
    "D:\dist\3号电炉\monitor_furnace.ps1",
    "D:\dist\3号电炉\watchdog.ps1",
    "D:\dist\3号电炉\watch.ps1"
)
foreach ($script in $oldScripts) {
    if (Test-Path $script) {
        Write-Host "  删除: $script" -ForegroundColor Gray
        Remove-Item $script -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "  [OK] 旧脚本已清理" -ForegroundColor Green

Write-Host "[清理 5/5] 清理旧日志..." -ForegroundColor Yellow
if (Test-Path "D:\dist\3号电炉\logs") {
    Get-ChildItem "D:\dist\3号电炉\logs" -Filter "*.log" | ForEach-Object {
        Write-Host "  清理日志: $($_.Name)" -ForegroundColor Gray
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "  [OK] 日志已清理" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清理完成！开始部署新配置..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# 部署阶段
# ========================================

Write-Host "[1/6] 创建启动脚本..." -ForegroundColor Yellow

$startScript = @'
$workDir = "D:\dist\3号电炉"
$exePath = "$workDir\3号电炉.exe"
$processName = "3号电炉"

Write-Host "检查 InfluxDB 服务..." -ForegroundColor Yellow
$influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
if (-not $influxService -or $influxService.Status -ne "Running") {
    Write-Host "等待 InfluxDB 启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

Write-Host "清理旧进程..." -ForegroundColor Yellow
Get-Process -Name $processName -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "启动 3号电炉..." -ForegroundColor Green
Set-Location $workDir
Start-Process -FilePath $exePath -WorkingDirectory $workDir
Write-Host "3号电炉已启动！" -ForegroundColor Green
'@

New-Item -ItemType Directory -Force -Path "D:\dist\3号电炉\logs" | Out-Null
Set-Content -Path "D:\dist\3号电炉\start_furnace.ps1" -Value $startScript -Encoding UTF8
Write-Host "  [OK] 启动脚本已创建" -ForegroundColor Green

Write-Host "[2/6] 创建增强版看门狗脚本（监控 InfluxDB + 3号电炉，10秒检测）..." -ForegroundColor Yellow

$watchdogScript = @'
$workDir = "D:\dist\3号电炉"
$exePath = "$workDir\3号电炉.exe"
$processName = "3号电炉"
$checkInterval = 10
$logFile = "$workDir\logs\watchdog.log"

if (-not (Test-Path "$workDir\logs")) {
    New-Item -ItemType Directory -Force -Path "$workDir\logs" | Out-Null
}

function Write-Log {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $logMessage -ErrorAction SilentlyContinue
    Write-Host $logMessage
}

Write-Log "=========================================="
Write-Log "看门狗启动 - 监控 InfluxDB + 3号电炉"
Write-Log "检查间隔: $checkInterval 秒"
Write-Log "=========================================="

while ($true) {
    try {
        # 检查 InfluxDB 服务
        $influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
        
        if (-not $influxService) {
            Write-Log "[错误] InfluxDB 服务不存在！"
        } elseif ($influxService.Status -ne "Running") {
            Write-Log "[警告] InfluxDB 服务已停止，正在重启..."
            try {
                Start-Service -Name "InfluxDB" -ErrorAction Stop
                Start-Sleep -Seconds 5
                
                $influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
                if ($influxService.Status -eq "Running") {
                    Write-Log "[成功] InfluxDB 服务已重启"
                } else {
                    Write-Log "[失败] InfluxDB 服务重启失败"
                }
            } catch {
                Write-Log "[错误] InfluxDB 服务重启异常: $_"
            }
        }
        
        # 检查 3号电炉进程
        $furnaceProcess = Get-Process -Name $processName -ErrorAction SilentlyContinue
        
        if (-not $furnaceProcess) {
            Write-Log "[警告] 3号电炉进程不存在，正在重启..."
            
            # 确保 InfluxDB 运行
            $influxCheck = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
            if (-not $influxCheck -or $influxCheck.Status -ne "Running") {
                Write-Log "[警告] InfluxDB 未运行，等待 10 秒..."
                Start-Sleep -Seconds 10
            }
            
            # 清理可能的残留进程
            Get-Process -Name $processName -ErrorAction SilentlyContinue | Stop-Process -Force
            Start-Sleep -Seconds 2
            
            # 启动 3号电炉
            try {
                Set-Location $workDir
                Start-Process -FilePath $exePath -WorkingDirectory $workDir -ErrorAction Stop
                Start-Sleep -Seconds 3
                
                $furnaceProcess = Get-Process -Name $processName -ErrorAction SilentlyContinue
                if ($furnaceProcess) {
                    Write-Log "[成功] 3号电炉已重启 (PID: $($furnaceProcess.Id))"
                } else {
                    Write-Log "[失败] 3号电炉重启失败"
                }
            } catch {
                Write-Log "[错误] 3号电炉重启异常: $_"
            }
        }
        
    } catch {
        Write-Log "[错误] 看门狗异常: $_"
    }
    
    Start-Sleep -Seconds $checkInterval
}
'@

Set-Content -Path "D:\dist\3号电炉\watchdog.ps1" -Value $watchdogScript -Encoding UTF8
Write-Host "  [OK] 看门狗脚本已创建（10秒检测间隔）" -ForegroundColor Green

Write-Host "[3/6] 创建启动任务..." -ForegroundColor Yellow

$action1 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"D:\dist\3号电炉\start_furnace.ps1`""

$trigger1 = New-ScheduledTaskTrigger -AtStartup
$trigger1.Delay = "PT30S"

$settings1 = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

$principal1 = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName "3号电炉-启动" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Settings $settings1 `
    -Principal $principal1 `
    -Description "开机自动启动 3号电炉（延迟 30 秒）" `
    -Force | Out-Null

Write-Host "  [OK] 启动任务已创建" -ForegroundColor Green

Write-Host "[4/6] 创建看门狗任务（监控 InfluxDB + 3号电炉）..." -ForegroundColor Yellow

$action2 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"D:\dist\3号电炉\watchdog.ps1`""

$trigger2 = New-ScheduledTaskTrigger -AtStartup
$trigger2.Delay = "PT45S"

$settings2 = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)

$principal2 = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName "3号电炉-看门狗" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Settings $settings2 `
    -Principal $principal2 `
    -Description "监控 InfluxDB 服务和 3号电炉进程，崩溃自动重启（10秒检测）" `
    -Force | Out-Null

Write-Host "  [OK] 看门狗任务已创建" -ForegroundColor Green

Write-Host "[5/6] 启动测试..." -ForegroundColor Yellow

Start-ScheduledTask -TaskName "3号电炉-启动"
Start-Sleep -Seconds 8

$furnaceProcess = Get-Process -Name "3号电炉" -ErrorAction SilentlyContinue
if ($furnaceProcess) {
    Write-Host "  [OK] 3号电炉进程已启动 (PID: $($furnaceProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "  [警告] 未检测到进程" -ForegroundColor Yellow
}

Write-Host "[6/6] 启动看门狗..." -ForegroundColor Yellow

Start-ScheduledTask -TaskName "3号电炉-看门狗"
Write-Host "  [OK] 看门狗已启动" -ForegroundColor Green

# ========================================
# 部署完成
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "任务状态：" -ForegroundColor Yellow
Get-ScheduledTask -TaskName "3号电炉-*" | Format-Table -Property TaskName, State -AutoSize
Write-Host ""

Write-Host "服务状态：" -ForegroundColor Yellow
Get-Service -Name "InfluxDB" | Format-Table -Property Status, Name, DisplayName -AutoSize
Write-Host ""

Write-Host "进程状态：" -ForegroundColor Yellow
Get-Process -Name "3号电炉","influxd" -ErrorAction SilentlyContinue | Format-Table -Property Id, ProcessName, StartTime -AutoSize
Write-Host ""

Write-Host "看门狗功能：" -ForegroundColor Yellow
Write-Host "  监控 InfluxDB 服务（10秒检测一次）" -ForegroundColor White
Write-Host "  监控 3号电炉进程（10秒检测一次）" -ForegroundColor White
Write-Host "  InfluxDB 停止时自动重启服务" -ForegroundColor White
Write-Host "  3号电炉崩溃时自动重启进程" -ForegroundColor White
Write-Host "  开机自动启动（延迟 45 秒）" -ForegroundColor White
Write-Host "  记录详细日志" -ForegroundColor White
Write-Host ""

Write-Host "管理命令：" -ForegroundColor Yellow
Write-Host "  查看任务:  Get-ScheduledTask -TaskName '3号电炉-*'" -ForegroundColor White
Write-Host "  查看日志:  Get-Content D:\dist\3号电炉\logs\watchdog.log -Tail 50" -ForegroundColor White
Write-Host "  实时监控:  Get-Content D:\dist\3号电炉\logs\watchdog.log -Wait" -ForegroundColor White
Write-Host "  手动启动:  Start-ScheduledTask -TaskName '3号电炉-启动'" -ForegroundColor White
Write-Host "  停止看门狗:  Stop-ScheduledTask -TaskName '3号电炉-看门狗'" -ForegroundColor White
Write-Host "  禁用开机启动:  Disable-ScheduledTask -TaskName '3号电炉-看门狗'" -ForegroundColor White
Write-Host ""

Write-Host "测试崩溃恢复：" -ForegroundColor Yellow
Write-Host "  1. 停止 InfluxDB:  Stop-Service InfluxDB" -ForegroundColor White
Write-Host "  2. 等待 10 秒，看门狗会自动重启" -ForegroundColor White
Write-Host "  3. 查看日志:  Get-Content D:\dist\3号电炉\logs\watchdog.log -Tail 20" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "部署成功！重启电脑后自动生效" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan





