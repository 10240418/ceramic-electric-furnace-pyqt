"""
轮询速度配置管理器
"""
import threading
from typing import Literal

PollingSpeed = Literal["0.2s", "0.5s"]


class PollingConfig:
    """轮询速度配置管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config_lock = threading.Lock()
        
        # 1. 默认轮询速度: 0.2s
        self._polling_speed: PollingSpeed = "0.2s"
        
        # 2. 回调函数列表 (当配置变化时通知)
        self._callbacks = []
        
        print(" 轮询配置管理器已初始化 (默认: 0.2s)")
    
    # 1. 获取当前轮询速度
    def get_polling_speed(self) -> PollingSpeed:
        """获取当前轮询速度
        
        Returns:
            "0.2s" 或 "0.5s"
        """
        with self._config_lock:
            return self._polling_speed
    
    # 2. 获取轮询间隔（秒）
    def get_polling_interval(self) -> float:
        """获取轮询间隔（秒）
        
        Returns:
            0.2 或 0.5
        """
        with self._config_lock:
            if self._polling_speed == "0.2s":
                return 0.2
            else:
                return 0.5
    
    # 3. 设置轮询速度
    def set_polling_speed(self, speed: PollingSpeed):
        """设置轮询速度
        
        Args:
            speed: "0.2s" 或 "0.5s"
        """
        if speed not in ["0.2s", "0.5s"]:
            raise ValueError(f"无效的轮询速度: {speed}，只能是 '0.2s' 或 '0.5s'")
        
        with self._config_lock:
            old_speed = self._polling_speed
            self._polling_speed = speed
            
            print(f" 轮询速度已修改: {old_speed} -> {speed}")
            
            # 异步通知所有回调函数（避免阻塞 UI 线程）
            for callback in self._callbacks:
                try:
                    # 使用 lambda 捕获当前的 callback 和 speed
                    self._async_call_callback(callback, speed)
                except Exception as e:
                    print(f" 回调函数调度失败: {e}")
    
    # 3.1. 异步调用回调函数
    def _async_call_callback(self, callback, speed):
        """异步调用回调函数（在下一个事件循环中执行）"""
        try:
            # 尝试使用 QTimer.singleShot 异步调用
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._safe_call_callback(callback, speed))
        except:
            # 如果 PyQt6 不可用，直接同步调用
            self._safe_call_callback(callback, speed)
    
    # 3.2. 安全调用回调函数
    def _safe_call_callback(self, callback, speed):
        """安全调用回调函数（捕获异常）"""
        try:
            callback(speed)
        except Exception as e:
            print(f" 回调函数执行失败: {e}")
    
    # 4. 注册回调函数
    def register_callback(self, callback):
        """注册回调函数（当配置变化时调用）
        
        Args:
            callback: 回调函数，签名为 callback(speed: PollingSpeed)
        """
        with self._config_lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)
    
    # 5. 取消注册回调函数
    def unregister_callback(self, callback):
        """取消注册回调函数
        
        Args:
            callback: 回调函数
        """
        with self._config_lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)


# 全局单例获取函数
_polling_config = None

def get_polling_config() -> PollingConfig:
    """获取轮询配置管理器单例"""
    global _polling_config
    if _polling_config is None:
        _polling_config = PollingConfig()
    return _polling_config

