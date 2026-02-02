# ============================================================
# 文件说明: batch_service.py - 批次状态管理服务（单例模式）
# ============================================================
# 功能:
#   1. 维护全局冶炼状态 (is_smelting)
#   2. 维护当前批次编号 (batch_code)
#   3. 支持暂停/恢复冶炼（保留批次号）
#   4. 断电恢复保护（状态持久化到文件）
# ============================================================

import json
import os
from datetime import datetime
from typing import Optional
from enum import Enum
import threading


# 计算项目根目录的绝对路径 (避免工作目录变化导致路径问题)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")


class SmeltingState(str, Enum):
    """冶炼状态枚举"""
    IDLE = "idle"           # 空闲（未开始冶炼）
    RUNNING = "running"     # 运行中（正在冶炼）
    PAUSED = "paused"       # 暂停（保留批次号）
    STOPPED = "stopped"     # 停止（批次结束）


class BatchService:
    """批次状态管理服务 - 单例模式"""
    
    _instance: Optional['BatchService'] = None
    _lock = threading.Lock()
    
    # 状态持久化文件路径 (使用绝对路径)
    STATE_FILE = os.path.join(_DATA_DIR, "batch_state.json")
    
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
        self._state = SmeltingState.IDLE
        self._batch_code: Optional[str] = None
        self._last_batch_code: Optional[str] = None  # 上次停止的批次号（用于续炼判断）
        self._start_time: Optional[datetime] = None
        self._pause_time: Optional[datetime] = None
        self._total_pause_duration: float = 0.0  # 累计暂停时长（秒）
        
        # 确保 data 目录存在
        os.makedirs(_DATA_DIR, exist_ok=True)
        
        # 尝试从文件恢复状态（断电保护）
        self._load_state_from_file()
    
    # ============================================================
    # 属性访问器
    # ============================================================
    
    @property
    def state(self) -> SmeltingState:
        """获取当前冶炼状态"""
        return self._state
    
    @property
    def is_smelting(self) -> bool:
        """是否正在冶炼（运行中或暂停中都算）"""
        return self._state in (SmeltingState.RUNNING, SmeltingState.PAUSED)
    
    @property
    def is_running(self) -> bool:
        """是否正在运行（只有运行中才写数据库）"""
        return self._state == SmeltingState.RUNNING
    
    @property
    def batch_code(self) -> Optional[str]:
        """获取当前批次编号"""
        return self._batch_code
    
    @property
    def start_time(self) -> Optional[datetime]:
        """获取冶炼开始时间"""
        return self._start_time
    
    @property
    def elapsed_seconds(self) -> float:
        """获取有效冶炼时长（排除暂停时间）"""
        if not self._start_time:
            return 0.0
        
        total = (datetime.now() - self._start_time).total_seconds()
        
        # 如果当前是暂停状态，减去当前暂停时长
        if self._state == SmeltingState.PAUSED and self._pause_time:
            current_pause = (datetime.now() - self._pause_time).total_seconds()
            total -= current_pause
        
        return total - self._total_pause_duration
    
    # ============================================================
    # 状态控制方法
    # ============================================================
    
    def start(self, batch_code: str) -> dict:
        """
        开始冶炼
        
        Args:
            batch_code: 批次编号 (格式: YYMMFFDD 如 26010315)
            
        Returns:
            {"success": bool, "message": str, "batch_code": str}
        """
        if self._state == SmeltingState.RUNNING:
            return {
                "success": False,
                "message": f"冶炼已在进行中，批次号: {self._batch_code}",
                "batch_code": self._batch_code
            }
        
        if self._state == SmeltingState.PAUSED:
            return {
                "success": False,
                "message": f"存在暂停中的批次: {self._batch_code}，请先停止或恢复",
                "batch_code": self._batch_code
            }
        
        # 设置新批次
        self._batch_code = batch_code
        self._state = SmeltingState.RUNNING
        self._start_time = datetime.now()
        self._pause_time = None
        self._total_pause_duration = 0.0
        
        # 统一处理：无论是续炼还是新批次，每次计算时都从数据库查询最新值
        # 只需要重置累计器（清空队列、设置批次号）
        print(f"[BatchService] 开始冶炼：批次号 {batch_code}")
        self._reset_accumulators(batch_code)
        
        # 持久化状态
        self._save_state_to_file()
        
        return {
            "success": True,
            "message": f"冶炼开始，批次号: {batch_code}",
            "batch_code": batch_code,
            "start_time": self._start_time.isoformat()
        }
    
    def _reset_accumulators(self, batch_code: str):
        """重置累计器（新批次时调用）"""
        # 重置冷却水累计流量
        try:
            from backend.services.db32.cooling_water_calculator import get_cooling_water_calculator
            cooling_calc = get_cooling_water_calculator()
            cooling_calc.reset_for_new_batch(batch_code)
        except Exception as e:
            print(f"[BatchService] 重置冷却水累计流量失败: {e}")
        
        # 重置投料累计器
        try:
            from backend.services.hopper.accumulator import get_feeding_plc_accumulator
            feeding_acc = get_feeding_plc_accumulator()
            feeding_acc.reset_for_new_batch(batch_code)
        except Exception as e:
            print(f"[BatchService] 重置投料累计器失败: {e}")
        
        # 重置能耗计算器
        try:
            from backend.services.db1.power_energy_calculator import get_power_energy_calculator
            power_calc = get_power_energy_calculator()
            power_calc.reset_for_new_batch(batch_code)
        except Exception as e:
            print(f"[BatchService] 重置能耗计算器失败: {e}")
    
    def pause(self) -> dict:
        """
        暂停冶炼（保留批次号，不写数据库）
        
        Returns:
            {"success": bool, "message": str}
        """
        if self._state != SmeltingState.RUNNING:
            return {
                "success": False,
                "message": f"当前状态不支持暂停: {self._state.value}"
            }
        
        self._state = SmeltingState.PAUSED
        self._pause_time = datetime.now()
        
        # 持久化状态
        self._save_state_to_file()
        
        return {
            "success": True,
            "message": f"冶炼已暂停，批次号: {self._batch_code}",
            "batch_code": self._batch_code,
            "pause_time": self._pause_time.isoformat()
        }
    
    def resume(self) -> dict:
        """
        恢复冶炼（从暂停状态恢复）
        
        Returns:
            {"success": bool, "message": str}
        """
        if self._state != SmeltingState.PAUSED:
            return {
                "success": False,
                "message": f"当前状态不支持恢复: {self._state.value}"
            }
        
        # 累加暂停时长
        if self._pause_time:
            pause_duration = (datetime.now() - self._pause_time).total_seconds()
            self._total_pause_duration += pause_duration
        
        self._state = SmeltingState.RUNNING
        self._pause_time = None
        
        # 持久化状态
        self._save_state_to_file()
        
        return {
            "success": True,
            "message": f"冶炼已恢复，批次号: {self._batch_code}",
            "batch_code": self._batch_code,
            "total_pause_duration": self._total_pause_duration
        }
    
    def terminate(self) -> dict:
        """
        终止冶炼（暂停写入数据库，但保留批次号和状态）
        
        与 pause() 的区别：
        - pause(): 临时暂停，可以恢复
        - terminate(): 终止冶炼，不再写入数据库，但保留批次信息
        
        Returns:
            {"success": bool, "message": str}
        """
        if self._state == SmeltingState.IDLE:
            return {
                "success": False,
                "message": "当前没有进行中的冶炼"
            }
        
        if self._state == SmeltingState.PAUSED:
            return {
                "success": False,
                "message": f"冶炼已终止，批次号: {self._batch_code}"
            }
        
        # 切换到暂停状态（不写数据库）
        self._state = SmeltingState.PAUSED
        self._pause_time = datetime.now()
        
        # 持久化状态
        self._save_state_to_file()
        
        return {
            "success": True,
            "message": f"冶炼已终止，批次号: {self._batch_code}",
            "batch_code": self._batch_code,
            "terminate_time": self._pause_time.isoformat()
        }
    
    async def force_flush_all_caches(self) -> dict:
        """
        强制刷新所有缓存，立即写入数据库
        
        用于终止记录时，确保所有缓存数据都写入数据库
        
        Returns:
            {"success": bool, "message": str, "flushed": list}
        """
        flushed_services = []
        errors = []
        
        try:
            # 1. 刷新投料累计器缓存
            try:
                from backend.services.hopper.accumulator import get_feeding_plc_accumulator
                feeding_acc = get_feeding_plc_accumulator()
                await feeding_acc.force_flush()
                flushed_services.append("投料累计器")
                print(f"[OK] 投料累计器缓存已刷新")
            except Exception as e:
                errors.append(f"投料累计器: {e}")
                print(f"[ERROR] 投料累计器刷新失败: {e}")
            
            # 2. 冷却水计算器（无缓存，跳过）
            # 冷却水数据是实时计算并批量写入的，无需单独刷新
            
            # 3. 能耗计算器（无缓存，跳过）
            # 能耗数据是实时计算并批量写入的，无需单独刷新
            
            if errors:
                return {
                    "success": False,
                    "message": f"部分缓存刷新失败: {', '.join(errors)}",
                    "flushed": flushed_services
                }
            else:
                return {
                    "success": True,
                    "message": f"所有缓存已刷新: {', '.join(flushed_services)}",
                    "flushed": flushed_services
                }
        
        except Exception as e:
            print(f"[ERROR] 强制刷新缓存异常: {e}")
            return {
                "success": False,
                "message": f"刷新缓存异常: {e}",
                "flushed": flushed_services
            }
    
    def stop(self) -> dict:
        """
        停止冶炼（结束批次）
        
        Returns:
            {"success": bool, "message": str, "summary": dict}
        """
        if self._state == SmeltingState.IDLE:
            return {
                "success": False,
                "message": "当前没有进行中的冶炼"
            }
        
        # 记录结束信息
        summary = {
            "batch_code": self._batch_code,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": datetime.now().isoformat(),
            "elapsed_seconds": self.elapsed_seconds,
            "total_pause_duration": self._total_pause_duration
        }
        
        # 保存上次批次号（用于续炼判断）
        old_batch = self._batch_code
        self._last_batch_code = old_batch
        
        # 重置状态
        self._state = SmeltingState.IDLE
        self._batch_code = None
        self._start_time = None
        self._pause_time = None
        self._total_pause_duration = 0.0
        
        # 持久化状态（清除）
        self._save_state_to_file()
        
        return {
            "success": True,
            "message": f"冶炼已停止，批次号: {old_batch}",
            "summary": summary
        }
    
    def get_status(self) -> dict:
        """
        获取当前状态（用于前端轮询和断电恢复）
        
        Returns:
            完整的状态信息
        """
        return {
            "state": self._state.value,
            "is_smelting": self.is_smelting,
            "is_running": self.is_running,
            "batch_code": self._batch_code,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "pause_time": self._pause_time.isoformat() if self._pause_time else None,
            "elapsed_seconds": self.elapsed_seconds,
            "total_pause_duration": self._total_pause_duration
        }
    
    # ============================================================
    # 状态持久化（断电保护）
    # ============================================================
    
    def _save_state_to_file(self):
        """保存状态到文件（断电保护）"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
            
            state_data = {
                "state": self._state.value,
                "batch_code": self._batch_code,
                "last_batch_code": self._last_batch_code,  # 保存上次批次号
                "start_time": self._start_time.isoformat() if self._start_time else None,
                "pause_time": self._pause_time.isoformat() if self._pause_time else None,
                "total_pause_duration": self._total_pause_duration,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            print(f"[BatchService] 状态已保存: {self._state.value}, batch={self._batch_code}")
            
        except Exception as e:
            print(f"[BatchService] 保存状态失败: {e}")
    
    def _load_state_from_file(self):
        """从文件恢复状态（断电恢复）"""
        try:
            if not os.path.exists(self.STATE_FILE):
                print("[BatchService] 无历史状态文件，使用默认状态")
                return
            
            with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 恢复状态
            saved_state = state_data.get("state", "idle")
            
            # 如果之前是运行中或暂停中，恢复为运行状态（断电保护）
            if saved_state in ("running", "paused"):
                self._state = SmeltingState.RUNNING  # 恢复后自动运行，继续写入数据
                self._batch_code = state_data.get("batch_code")
                self._last_batch_code = state_data.get("last_batch_code")  # 恢复上次批次号
                
                if state_data.get("start_time"):
                    self._start_time = datetime.fromisoformat(state_data["start_time"])
                
                self._total_pause_duration = state_data.get("total_pause_duration", 0.0)
                self._pause_time = None  # 断电恢复后不计算暂停时长
                
                print(f"[BatchService] 断电恢复: 批次={self._batch_code}, 状态=running")
                print(f"[BatchService]    原状态={saved_state}, 已运行={self.elapsed_seconds:.0f}秒")
                print(f"[BatchService]    自动恢复为运行状态，继续写入数据")
                
                # 断电恢复时也需要重置累计器，设置批次号
                if self._batch_code:
                    self._reset_accumulators(self._batch_code)
            else:
                # 空闲状态也恢复 last_batch_code（用于续炼判断）
                self._last_batch_code = state_data.get("last_batch_code")
                if self._last_batch_code:
                    print(f"[BatchService] 历史状态为空闲，上次批次号: {self._last_batch_code}")
                else:
                    print("[BatchService] 历史状态为空闲，无需恢复")
                
        except Exception as e:
            print(f"[BatchService] 恢复状态失败: {e}")


# ============================================================
# 全局单例获取函数
# ============================================================

_batch_service: Optional[BatchService] = None

def get_batch_service() -> BatchService:
    """获取批次服务单例"""
    global _batch_service
    if _batch_service is None:
        _batch_service = BatchService()
    return _batch_service
