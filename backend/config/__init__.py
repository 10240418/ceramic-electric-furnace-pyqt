# ============================================================
# 电炉监控后端 - 配置文件
# ============================================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # ============================================================
    # Mock 模式配置 (核心开关)
    # ============================================================
    # True: 使用 Mock 数据 (开发/测试环境, 无需 PLC 连接)
    # False: 使用真实 PLC 数据 (生产环境)
    mock_mode: bool = False
    
    # ============================================================
    # PLC 配置 (生产环境使用)
    # ============================================================
    plc_ip: str = "192.168.1.10"  # S7-1200 PLC IP
    plc_port: int = 102
    plc_rack: int = 0
    plc_slot: int = 1
    
    # ============================================================
    # InfluxDB 配置
    # ============================================================
    influx_url: str = "http://localhost:8086"
    influx_token: str = "zjIA_7YN4vyApLJhXyzvH7ipuMHLHcwoZMyWhPVJIA1m1kitnEW8eBki0a18MVcLao4IHEYhVUzykmGVw2gsjw=="
    influx_org: str = "furnace"
    influx_bucket: str = "sensor_data"
    
    # ============================================================
    # 轮询配置
    # ============================================================
    polling_interval: int = 2  # 轮询间隔 (秒)
    
    # ============================================================
    # DB 块配置
    # ============================================================
    db32_number: int = 32  # MODBUS_DATA_VALUE (传感器数据)
    db32_size: int = 21    # 读取大小 (实际地址 0~20, 共 21 字节)
    db30_number: int = 30  # MODBUS_DB_Value (通信状态)
    db30_size: int = 40    # 读取大小
    
    # ============================================================
    # Modbus RTU 配置 (料仓重量)
    # ============================================================
    modbus_port: str = "COM1"
    modbus_baudrate: int = 19200
    
    # ============================================================
    # 调试配置
    # ============================================================
    app_debug: bool = False  # 调试模式（打印详细日志）
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"
        env_prefix = "FURNACE_"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def reload_settings():
    """重新加载配置 (清除缓存)
    
    用于在运行时切换 mock_mode 后刷新配置
    """
    get_settings.cache_clear()
    return get_settings()
