@echo off
chcp 65001 >nul
echo ========================================
echo #3电炉 - PyQt6 打包脚本
echo ========================================
echo.

REM 1. 检查是否安装 PyInstaller
echo [1/4] 检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller 未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo 安装 PyInstaller 失败！
        pause
        exit /b 1
    )
) else (
    echo PyInstaller 已安装
)
echo.

REM 2. 清理旧的打包文件
echo [2/4] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo 清理完成
echo.

REM 3. 开始打包
echo [3/4] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.
pyinstaller build_exe.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo 打包失败！请检查错误信息。
    pause
    exit /b 1
)
echo.

REM 4. 打包完成
echo [4/4] 打包完成！
echo.
echo ========================================
echo 打包结果：
echo   可执行文件位置: dist\3号电炉\3号电炉.exe
echo   文件夹大小: 
dir dist\3号电炉 | find "个文件"
echo ========================================
echo.
echo 提示：
echo   1. 首次运行前，请确保 D:\data\logs 目录存在
echo   2. 如需连接真实 PLC，请修改 backend\config.py
echo   3. 如需修改窗口大小，请修改 config.py
echo.
pause


