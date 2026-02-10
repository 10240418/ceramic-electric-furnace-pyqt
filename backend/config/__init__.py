# ============================================================
# 电炉监控后端 - 配置文件
# ============================================================

import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


def _get_env_file_path() -> str:
    """获取 .env 文件路径 (兼容开发模式和打包模式)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后: .env 在 exe 同级目录
        app_dir = Path(sys.executable).parent
    else:
        # 开发模式: .env 在项目根目录
        app_dir = Path(__file__).resolve().parent.parent.parent
    return str(app_dir / ".env")


class Settings(BaseSettings):
    """应用配置 (.env 文件可配置, 打包后修改 .env 重启生效)"""
    
    # ============================================================
    # Mock 模式配置 (核心开关)
    # ============================================================
    mock_mode: bool = False
    
    # ============================================================
    # PLC 配置 (生产环境使用)
    # ============================================================
    plc_ip: str = "192.168.1.10"
    plc_port: int = 102
    plc_rack: int = 0
    plc_slot: int = 1
    
    # ============================================================
    # InfluxDB 配置
    # ============================================================
    influx_url: str = "http://localhost:8086"
    influx_token: str = "Y8Cxnn1ysEmgcPKexvLDBG8I03b00zJbLNk1QPDQGwlkXisGBKXE6Zyg7kXfBR1QR46Q9pyFnWPpmqtXcD7Nsw=="
    influx_org: str = "furnace"
    influx_bucket: str = "sensor_data"
    
    # ============================================================
    # 轮询间隔配置 (秒)
    # ============================================================
    db1_polling_interval: float = 0.5       # DB1 弧流弧压轮询 (高速)
    db32_polling_interval: float = 0.5      # DB32 传感器轮询
    status_polling_interval: float = 5.0    # DB30/DB41 状态轮询 (低速)
    db1_idle_polling_interval: float = 5.0  # DB1 空闲时轮询间隔
    
    # ============================================================
    # 炉号配置
    # ============================================================
    number: int = 3  # 电炉编号 (用于生成批次编号)
    
    # ============================================================
    # 调试配置
    # ============================================================
    app_debug: bool = False
    
    class Config:
        env_file = _get_env_file_path()
        extra = "ignore"
        env_file_encoding = "utf-8"
        env_prefix = "FURNACE_"


# 全局单例缓存
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """获取配置单例 (启动时从 .env 加载一次)"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def reload_settings() -> Settings:
    """重新加载配置 (清除缓存)"""
    global _settings_instance
    _settings_instance = None
    return get_settings()
