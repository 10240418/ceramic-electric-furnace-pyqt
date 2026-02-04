"""
#3电炉 - PyQt6 前端 + 后端集成入口
"""
import sys
import os
from pathlib import Path

# 设置项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 确保当前目录在 sys.path 最前面
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
from loguru import logger

# 导入前端配置
from config import (
    APP_NAME, 
    APP_VERSION, 
    FULLSCREEN, 
    LOG_LEVEL, 
    LOG_FILE,
    LOG_ROTATION,
    LOG_RETENTION,
    LOGS_DIR
)

# 确保日志目录存在
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 配置 loguru 日志
logger.add(
    LOG_FILE,
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    level=LOG_LEVEL,
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


# 1. 创建系统托盘图标（蓝色圆点）
def create_tray_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(0, 123, 255))  # 蓝色
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(8, 8, 48, 48)
    painter.end()
    
    return QIcon(pixmap)


# 2. 应用入口
def main():
    logger.info("=" * 60)
    logger.info(f"🚀 {APP_NAME} v{APP_VERSION} 启动")
    logger.info("=" * 60)
    logger.info(f"📁 项目目录: {BASE_DIR}")
    logger.info(f"📝 日志文件: {LOG_FILE}")
    logger.info("-" * 60)
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Clutch Team")
    
    try:
        # 导入主窗口
        from ui import MainWindow
        
        # 创建主窗口（use_mock=False 使用真实 PLC 数据）
        logger.info("🔨 正在创建主窗口...")
        window = MainWindow(use_mock=False)
        
        # 创建系统托盘
        logger.info("🔨 正在创建系统托盘...")
        tray_icon = QSystemTrayIcon(create_tray_icon(), app)
        tray_icon.setToolTip(f"{APP_NAME} v{APP_VERSION}")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示/隐藏窗口
        show_action = tray_menu.addAction("显示窗口")
        show_action.triggered.connect(lambda: window.show())
        
        hide_action = tray_menu.addAction("隐藏窗口")
        hide_action.triggered.connect(window.hide)
        
        tray_menu.addSeparator()
        
        # 退出应用（触发主窗口的 closeEvent）
        quit_action = tray_menu.addAction("退出程序")
        quit_action.triggered.connect(window.close)
        
        tray_icon.setContextMenu(tray_menu)
        
        # 双击托盘图标显示窗口
        tray_icon.activated.connect(
            lambda reason: window.show() 
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick 
            else None
        )
        
        # 显示托盘图标
        tray_icon.show()
        logger.info("✅ 系统托盘已创建")
        
        # 显示窗口（全屏模式）
        window.showFullScreen()
        logger.info("✅ 主窗口已创建并显示")
        logger.info("📐 窗口功能：")
        logger.info("   • 窗口大小：1260x1004 (固定尺寸)")
        logger.info("   • 启动模式：全屏模式")
        logger.info("   • 最小化：点击工具栏按钮")
        logger.info("   • 切换全屏：F11 或工具栏按钮")
        logger.info("   • 退出程序：Esc 或 Alt+F4")
        logger.info("   • 主题切换：工具栏主题按钮")
        logger.info("   • 系统托盘：右键菜单 / 双击显示窗口")
        logger.info("=" * 60)
        
        # 运行应用
        exit_code = app.exec()
        logger.info(f"👋 应用已退出，退出码: {exit_code}")
        sys.exit(exit_code)
    
    except ImportError as e:
        logger.error(f" 导入错误: {e}")
        logger.error("提示: 请确保已创建 ui/main_window.py 文件")
        sys.exit(1)
    
    except Exception as e:
        import traceback
        logger.error(f" 启动失败: {e}")
        logger.error(f"完整错误堆栈:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
