"""
报警阈值配置模块
"""
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


# 项目根目录（backend/ 的上级目录）
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "data"
ALARM_CONFIG_FILE = CONFIG_DIR / "alarm_thresholds.json"


@dataclass
class ThresholdConfig:
    """单个参数的阈值配置"""
    warning_min: Optional[float] = None  # 警告下限
    warning_max: Optional[float] = None  # 警告上限
    alarm_min: Optional[float] = None    # 报警下限
    alarm_max: Optional[float] = None    # 报警上限
    enabled: bool = True                 # 是否启用


@dataclass
class AlarmThresholds:
    """报警阈值配置"""
    
    # 电极深度 (mm)
    electrode_depth_u: ThresholdConfig = None
    electrode_depth_v: ThresholdConfig = None
    electrode_depth_w: ThresholdConfig = None
    
    # 电极弧流 (A)
    arc_current_u: ThresholdConfig = None
    arc_current_v: ThresholdConfig = None
    arc_current_w: ThresholdConfig = None
    
    # 电极弧压 (V)
    arc_voltage_u: ThresholdConfig = None
    arc_voltage_v: ThresholdConfig = None
    arc_voltage_w: ThresholdConfig = None
    
    # 冷却水压力 (kPa)
    cooling_pressure_shell: ThresholdConfig = None  # 炉皮水压
    cooling_pressure_cover: ThresholdConfig = None  # 炉盖水压
    
    # 冷却水流速 (m³/h)
    cooling_flow_shell: ThresholdConfig = None  # 炉皮流速
    cooling_flow_cover: ThresholdConfig = None  # 炉盖流速
    
    # 过滤器压差 (kPa)
    filter_pressure_diff: ThresholdConfig = None
    
    def __post_init__(self):
        """初始化默认值（与 JSON 配置文件保持一致）"""
        # 电极深度默认值：150mm-1960mm
        if self.electrode_depth_u is None:
            self.electrode_depth_u = ThresholdConfig(
                warning_min=145.0, warning_max=1900.0,
                alarm_min=150.0, alarm_max=1960.0
            )
        if self.electrode_depth_v is None:
            self.electrode_depth_v = ThresholdConfig(
                warning_min=145.0, warning_max=1900.0,
                alarm_min=150.0, alarm_max=1960.0
            )
        if self.electrode_depth_w is None:
            self.electrode_depth_w = ThresholdConfig(
                warning_min=145.0, warning_max=1900.0,
                alarm_min=150.0, alarm_max=1960.0
            )
        
        # 电极弧流默认值：0A-7999A
        if self.arc_current_u is None:
            self.arc_current_u = ThresholdConfig(
                warning_min=0.0, warning_max=7999.0,
                alarm_min=0.0, alarm_max=8000.0
            )
        if self.arc_current_v is None:
            self.arc_current_v = ThresholdConfig(
                warning_min=0.0, warning_max=7999.0,
                alarm_min=0.0, alarm_max=8000.0
            )
        if self.arc_current_w is None:
            self.arc_current_w = ThresholdConfig(
                warning_min=0.0, warning_max=7999.0,
                alarm_min=0.0, alarm_max=8000.0
            )
        
        # 电极弧压默认值：50V-100V（默认不启用）
        if self.arc_voltage_u is None:
            self.arc_voltage_u = ThresholdConfig(
                warning_min=60.0, warning_max=70.0,
                alarm_min=50.0, alarm_max=150.0,
                enabled=False
            )
        if self.arc_voltage_v is None:
            self.arc_voltage_v = ThresholdConfig(
                warning_min=60.0, warning_max=70.0,
                alarm_min=50.0, alarm_max=150.0,
                enabled=False
            )
        if self.arc_voltage_w is None:
            self.arc_voltage_w = ThresholdConfig(
                warning_min=60.0, warning_max=70.0,
                alarm_min=50.0, alarm_max=150.0,
                enabled=False
            )
        
        # 冷却水压力默认值：10kPa-10kPa
        if self.cooling_pressure_shell is None:
            self.cooling_pressure_shell = ThresholdConfig(
                warning_min=10.0, warning_max=10.0,
                alarm_min=10.0, alarm_max=10.0
            )
        if self.cooling_pressure_cover is None:
            self.cooling_pressure_cover = ThresholdConfig(
                warning_min=10.0, warning_max=10.0,
                alarm_min=10.0, alarm_max=10.0
            )
        
        # 冷却水流速默认值：禁用
        if self.cooling_flow_shell is None:
            self.cooling_flow_shell = ThresholdConfig(
                warning_min=None, warning_max=None,
                alarm_min=None, alarm_max=None,
                enabled=False
            )
        if self.cooling_flow_cover is None:
            self.cooling_flow_cover = ThresholdConfig(
                warning_min=None, warning_max=None,
                alarm_min=None, alarm_max=None,
                enabled=False
            )
        
        # 过滤器压差默认值：30kPa-50kPa
        if self.filter_pressure_diff is None:
            self.filter_pressure_diff = ThresholdConfig(
                warning_min=None, warning_max=10.0,
                alarm_min=None, alarm_max=10.0
            )


class AlarmThresholdManager:
    """报警阈值管理器 - 单例模式"""
    
    _instance: Optional['AlarmThresholdManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.thresholds: AlarmThresholds = None
        
        # 确保配置目录存在
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.load()
    
    def load(self):
        """从文件加载配置"""
        if ALARM_CONFIG_FILE.exists():
            try:
                with open(ALARM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 转换为 ThresholdConfig 对象
                for key, value in data.items():
                    if isinstance(value, dict):
                        data[key] = ThresholdConfig(**value)
                
                self.thresholds = AlarmThresholds(**data)
                print(f"[OK] 报警阈值配置已加载: {ALARM_CONFIG_FILE}")
            except Exception as e:
                print(f"[WARNING] 加载报警阈值配置失败: {e}，使用默认值")
                self.thresholds = AlarmThresholds()
        else:
            print("[INFO] 使用默认报警阈值配置")
            self.thresholds = AlarmThresholds()
            self.save()  # 保存默认配置
    
    def save(self):
        """保存配置到文件"""
        try:
            # 转换为字典
            data = {}
            for key, value in asdict(self.thresholds).items():
                if isinstance(value, dict):
                    data[key] = value
                else:
                    data[key] = asdict(value) if hasattr(value, '__dict__') else value
            
            with open(ALARM_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] 报警阈值配置已保存: {ALARM_CONFIG_FILE}")
            return True
        except Exception as e:
            print(f"[ERROR] 保存报警阈值配置失败: {e}")
            return False
    
    def get_threshold(self, param_name: str) -> Optional[ThresholdConfig]:
        """获取指定参数的阈值配置"""
        return getattr(self.thresholds, param_name, None)
    
    def set_threshold(self, param_name: str, config: ThresholdConfig):
        """设置指定参数的阈值配置"""
        setattr(self.thresholds, param_name, config)
    
    def check_value(self, param_name: str, value: float) -> str:
        """检查数值是否超限
        
        Returns:
            'normal': 正常
            'warning': 警告
            'alarm': 报警
        """
        config = self.get_threshold(param_name)
        if not config or not config.enabled:
            return 'normal'
        
        # 检查报警上下限
        if config.alarm_min is not None and value < config.alarm_min:
            return 'alarm'
        if config.alarm_max is not None and value > config.alarm_max:
            return 'alarm'
        
        # 检查警告上下限
        if config.warning_min is not None and value < config.warning_min:
            return 'warning'
        if config.warning_max is not None and value > config.warning_max:
            return 'warning'
        
        return 'normal'


# 全局单例
_alarm_threshold_manager: Optional[AlarmThresholdManager] = None


def get_alarm_threshold_manager() -> AlarmThresholdManager:
    """获取报警阈值管理器单例"""
    global _alarm_threshold_manager
    if _alarm_threshold_manager is None:
        _alarm_threshold_manager = AlarmThresholdManager()
    return _alarm_threshold_manager

