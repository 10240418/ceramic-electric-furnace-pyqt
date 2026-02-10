"""
报警声音管理器 - 单例模式，引用计数，报警期间持续循环播放
"""
from typing import Optional, Set
from pathlib import Path
import threading
import time
import shutil
import tempfile
import sys


def get_resource_path(relative_path: str) -> Path:
    # 获取资源文件路径（支持打包后的环境）
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).parent.parent.parent
    return base_path / relative_path


def get_safe_sound_path(original_path: Path) -> Path:
    try:
        str(original_path).encode('ascii')
        return original_path
    except UnicodeEncodeError:
        pass
    
    safe_dir = Path(tempfile.gettempdir()) / "furnace_alarm"
    safe_dir.mkdir(exist_ok=True)
    safe_file = safe_dir / original_path.name
    if not safe_file.exists():
        shutil.copy2(original_path, safe_file)
        print(f"[INFO] 音频复制到安全路径: {safe_file}")
    return safe_file


class AlarmSoundManager:
    """报警声音管理器 - 单例模式，引用计数"""
    
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
        self.is_playing = False
        self._active_sources: Set[str] = set()  # 当前活跃的报警源
        self._lock = threading.Lock()
        self.sound_file = None
        
        self._init_player()
    
    # 1. 初始化播放器
    def _init_player(self):
        try:
            raw_path = get_resource_path("assets/sounds/aviation-alarm.mp3")
            if raw_path.exists():
                self.sound_file = get_safe_sound_path(raw_path)
                print(f"[INFO] 报警音频文件已加载: {self.sound_file}")
            else:
                print(f"[WARNING] 报警音频文件不存在: {raw_path}")
        except Exception as e:
            print(f"[ERROR] 初始化报警声音播放器失败: {e}")
    
    # 2. 注册报警源并开始播放
    def play_alarm(self, source: str = "default"):
        if not self._is_recording():
            return
        
        with self._lock:
            self._active_sources.add(source)
            if self.is_playing:
                return
            self.is_playing = True
        
        if not self.sound_file or not self.sound_file.exists():
            with self._lock:
                self.is_playing = False
            return
        
        thread = threading.Thread(target=self._play_sound_thread, daemon=True)
        thread.start()
    
    # 2.1 注销报警源（全部解除才停止播放）
    def stop_alarm(self, source: str = "default"):
        with self._lock:
            self._active_sources.discard(source)
    
    # 2.2 检查是否正在记录
    def _is_recording(self) -> bool:
        try:
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            return batch_service.is_smelting
        except Exception as e:
            return False
    
    # 2.3 检查是否还有活跃报警源
    def _has_active_sources(self) -> bool:
        with self._lock:
            return len(self._active_sources) > 0
    
    # 3. 播放声音线程（持续循环直到所有报警源解除）
    def _play_sound_thread(self):
        try:
            from playsound import playsound
            
            while self._has_active_sources() and self._is_recording():
                playsound(str(self.sound_file))
                time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] 播放报警声音失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_playing = False
    
    # 4. 强制停止所有报警声音
    def stop(self):
        with self._lock:
            self._active_sources.clear()
    
    # 5. 检查是否正在播放
    def is_alarm_playing(self) -> bool:
        return self.is_playing


# 全局单例
_alarm_sound_manager: Optional[AlarmSoundManager] = None


def get_alarm_sound_manager() -> AlarmSoundManager:
    global _alarm_sound_manager
    if _alarm_sound_manager is None:
        _alarm_sound_manager = AlarmSoundManager()
    return _alarm_sound_manager

