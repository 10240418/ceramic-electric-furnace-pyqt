# ========================================
# 3号电炉 - 任务计划程序自动配置脚本
# ========================================
# 以管理员身份运行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "3号电炉 - 任务计划程序配置" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[错误] 必须以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[信息] 以管理员身份运行" -ForegroundColor Green
Write-Host ""

# ========================================
# 步骤 1: 复制脚本到目标目录
# ========================================
Write-Host "[1/4] 复制脚本文件..." -ForegroundColor Yellow

$sourceDir = "D:\download"
$targetDir = "D:\dist\3号电炉"

# 复制启动脚本
Copy-Item "$sourceDir\start_furnace.ps1" "$targetDir\start_furnace.ps1" -Force
Write-Host "  [OK] start_furnace.ps1 已复制" -ForegroundColor Green

# 复制监控脚本
Copy-Item "$sourceDir\monitor_furnace.ps1" "$targetDir\monitor_furnace.ps1" -Force
Write-Host "  [OK] monitor_furnace.ps1 已复制" -ForegroundColor Green

# ========================================
# 步骤 2: 删除旧的任务计划（如果存在）
# ========================================
Write-Host "[2/4] 清理旧的任务计划..." -ForegroundColor Yellow

$taskNames = @("3号电炉-启动", "3号电炉-监控")
foreach ($taskName in $taskNames) {
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "  删除旧任务: $taskName" -ForegroundColor Gray
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
}

Write-Host "  [OK] 旧任务已清理" -ForegroundColor Green

# ========================================
# 步骤 3: 创建启动任务
# ========================================
Write-Host "[3/4] 创建启动任务..." -ForegroundColor Yellow

# 任务动作：执行启动脚本
$action1 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$targetDir\start_furnace.ps1`""

# 触发器：开机启动，延迟 30 秒
$trigger1 = New-ScheduledTaskTrigger -AtStartup
$trigger1.Delay = "PT30S"  # 延迟 30 秒

# 设置：以最高权限运行
$settings1 = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

# 主体：以 SYSTEM 账户运行（可以显示窗口）
$principal1 = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# 注册任务
Register-ScheduledTask `
    -TaskName "3号电炉-启动" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Settings $settings1 `
    -Principal $principal1 `
    -Description "开机自动启动 3号电炉（延迟 30 秒，等待 InfluxDB）" `
    -Force | Out-Null

Write-Host "  [OK] 启动任务已创建" -ForegroundColor Green

# ========================================
# 步骤 4: 创建监控任务
# ========================================
Write-Host "[4/4] 创建监控任务..." -ForegroundColor Yellow

# 任务动作：执行监控脚本
$action2 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$targetDir\monitor_furnace.ps1`""

# 触发器：开机启动，延迟 60 秒（等待 3号电炉先启动）
$trigger2 = New-ScheduledTaskTrigger -AtStartup
$trigger2.Delay = "PT60S"  # 延迟 60 秒

# 设置：以最高权限运行
$settings2 = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)  # 允许长时间运行

# 主体：以 SYSTEM 账户运行
$principal2 = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# 注册任务
Register-ScheduledTask `
    -TaskName "3号电炉-监控" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Settings $settings2 `
    -Principal $principal2 `
    -Description "监控 3号电炉进程，崩溃自动重启（每 30 秒检查）" `
    -Force | Out-Null

Write-Host "  [OK] 监控任务已创建" -ForegroundColor Green

# ========================================
# 配置完成
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "已创建的任务计划：" -ForegroundColor Yellow
Get-ScheduledTask -TaskName "3号电炉-*" | Format-Table -Property TaskName, State, @{Label="下次运行时间";Expression={$_.Triggers[0].StartBoundary}}

Write-Host ""
Write-Host "任务说明：" -ForegroundColor Yellow
Write-Host "  1. 3号电炉-启动" -ForegroundColor White
Write-Host "     - 开机自动启动（延迟 30 秒，等待 InfluxDB）" -ForegroundColor Gray
Write-Host "     - 启动前自动杀死旧进程（单实例保护）" -ForegroundColor Gray
Write-Host "     - 显示 GUI 窗口" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 3号电炉-监控" -ForegroundColor White
Write-Host "     - 开机自动启动（延迟 60 秒）" -ForegroundColor Gray
Write-Host "     - 每 30 秒检查一次进程" -ForegroundColor Gray
Write-Host "     - 崩溃自动重启" -ForegroundColor Gray
Write-Host "     - 日志文件: D:\dist\3号电炉\logs\monitor.log" -ForegroundColor Gray
Write-Host ""

Write-Host "立即测试：" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '3号电炉-启动'" -ForegroundColor White
Write-Host ""

Write-Host "管理命令：" -ForegroundColor Yellow
Write-Host "  查看任务:  Get-ScheduledTask -TaskName '3号电炉-*'" -ForegroundColor White
Write-Host "  启动任务:  Start-ScheduledTask -TaskName '3号电炉-启动'" -ForegroundColor White
Write-Host "  停止任务:  Stop-ScheduledTask -TaskName '3号电炉-监控'" -ForegroundColor White
Write-Host "  禁用任务:  Disable-ScheduledTask -TaskName '3号电炉-启动'" -ForegroundColor White
Write-Host "  启用任务:  Enable-ScheduledTask -TaskName '3号电炉-启动'" -ForegroundColor White
Write-Host "  删除任务:  Unregister-ScheduledTask -TaskName '3号电炉-启动' -Confirm:`$false" -ForegroundColor White
Write-Host ""

Write-Host "查看监控日志：" -ForegroundColor Yellow
Write-Host "  Get-Content D:\dist\3号电炉\logs\monitor.log -Tail 50" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置成功！重启电脑后自动生效" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan






