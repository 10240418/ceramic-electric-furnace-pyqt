"""
#3电炉 - 前端配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 后端目录（用于导入后端模块）
BACKEND_DIR = BASE_DIR.parent / "ceramic-electric-furnace-backend"

# 资源目录
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"

# 日志目录
LOGS_DIR = Path("D:/data/logs")

# 应用配置
APP_NAME = "#3电炉"
APP_VERSION = "1.0.0"

# 窗口配置
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FULLSCREEN = True

# 刷新频率（毫秒）
ARC_REFRESH_INTERVAL = 200      # 弧流数据刷新间隔（0.2s）
SENSOR_REFRESH_INTERVAL = 2000  # 传感器数据刷新间隔（2s）

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "app_{time:YYYY-MM-DD}.log"  # 按天分割日志文件
LOG_ROTATION = "00:00"  # 每天凌晨0点切换新文件
LOG_RETENTION = "30 days"  # 保留30天的日志

# 后端 API 配置（可选，用于远程访问）
BACKEND_API_URL = "http://localhost:8082"

