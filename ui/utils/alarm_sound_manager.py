"""
报警声音管理器 - 单例模式，避免多个声音同时播放
"""
from typing import Optional
from pathlib import Path
import threading
import sys


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径（支持打包后的环境）"""
    try:
        # PyInstaller 打包后的临时目录
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # 开发环境
        base_path = Path(__file__).parent.parent.parent
    
    return base_path / relative_path


class AlarmSoundManager:
    """报警声音管理器 - 单例模式"""
    
    _instance: Optional['AlarmSoundManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.play_count = 0
        self.is_playing = False
        self.sound_file = None
        
        self._init_player()
    
    # 1. 初始化播放器
    def _init_player(self):
        """初始化音频播放器"""
        try:
            # 设置音频文件路径（支持打包后的环境）
            self.sound_file = get_resource_path("assets/sounds/aviation-alarm.mp3")
            if self.sound_file.exists():
                print(f"[INFO] 报警音频文件已加载: {self.sound_file}")
            else:
                print(f"[WARNING] 报警音频文件不存在: {self.sound_file}")
        except Exception as e:
            print(f"[ERROR] 初始化报警声音播放器失败: {e}")
    
    # 2. 播放报警声音
    def play_alarm(self):
        """
        播放报警声音（3次）
        如果正在播放，则不重复播放
        """
        if self.is_playing:
            # 正在播放，不重复播放
            return
        
        if not self.sound_file or not self.sound_file.exists():
            print("[ERROR] 音频文件不存在")
            return
        
        # 在后台线程播放，避免阻塞 UI
        self.is_playing = True
        thread = threading.Thread(target=self._play_sound_thread, daemon=True)
        thread.start()
    
    # 3. 播放声音线程
    def _play_sound_thread(self):
        """在后台线程播放声音（播放3次）"""
        try:
            from playsound import playsound
            
            print("[INFO] 开始播放报警声音（3次）")
            for i in range(3):
                print(f"[INFO] 播放第 {i + 1} 次")
                playsound(str(self.sound_file))
            
            print("[INFO] 报警声音全部播放完成（3次）")
        except Exception as e:
            print(f"[ERROR] 播放报警声音失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_playing = False
    
    # 4. 停止播放
    def stop(self):
        """停止播放（playsound 不支持停止，只能等待播放完成）"""
        self.is_playing = False
    
    # 5. 检查是否正在播放
    def is_alarm_playing(self) -> bool:
        """检查是否正在播放报警声音"""
        return self.is_playing
    
    # 6. 设置音量
    def set_volume(self, volume: float):
        """
        设置音量（playsound 使用系统音量，此方法仅用于兼容）
        
        Args:
            volume: 音量大小（0.0-1.0）
        """
        print(f"[INFO] playsound 使用系统音量，无法单独设置")


# 全局单例
_alarm_sound_manager: Optional[AlarmSoundManager] = None


def get_alarm_sound_manager() -> AlarmSoundManager:
    """获取报警声音管理器单例"""
    global _alarm_sound_manager
    if _alarm_sound_manager is None:
        _alarm_sound_manager = AlarmSoundManager()
    return _alarm_sound_manager

