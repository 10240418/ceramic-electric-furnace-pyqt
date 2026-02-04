# ========================================
# 3号电炉监控脚本（崩溃自动重启）
# ========================================

# 1. 配置参数
$workDir = "D:\dist\3号电炉"
$exePath = "$workDir\3号电炉.exe"
$processName = "3号电炉"
$checkInterval = 30  # 检查间隔（秒）
$logFile = "$workDir\logs\monitor.log"

# 2. 创建日志目录
if (-not (Test-Path "$workDir\logs")) {
    New-Item -ItemType Directory -Force -Path "$workDir\logs" | Out-Null
}

# 3. 写日志函数
function Write-Log {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $logMessage
    Write-Host $logMessage
}

Write-Log "监控脚本启动"

# 4. 无限循环监控
while ($true) {
    # 检查进程是否存在
    $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
    
    if (-not $process) {
        Write-Log "检测到 3号电炉 进程不存在，准备重启..."
        
        # 检查 InfluxDB 是否运行
        $influxService = Get-Service -Name "InfluxDB" -ErrorAction SilentlyContinue
        if (-not $influxService -or $influxService.Status -ne "Running") {
            Write-Log "警告: InfluxDB 服务未运行"
        }
        
        # 清理可能的残留进程
        Get-Process -Name $processName -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep -Seconds 2
        
        # 启动 3号电炉
        try {
            Set-Location $workDir
            Start-Process -FilePath $exePath -WorkingDirectory $workDir
            Write-Log "3号电炉 已重启"
        } catch {
            Write-Log "错误: 启动失败 - $_"
        }
    }
    
    # 等待下次检查
    Start-Sleep -Seconds $checkInterval
}





