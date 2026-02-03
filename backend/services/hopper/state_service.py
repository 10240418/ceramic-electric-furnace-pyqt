"""
料仓状态判断服务
"""
from typing import Literal
from loguru import logger

HopperState = Literal['idle', 'feeding', 'waiting_feed', 'discharging']


class HopperStateService:
    """料仓状态判断服务 - 单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    # 1. 初始化
    def __init__(self):
        if self._initialized:
            return
        
        self._current_state: HopperState = 'idle'
        self._initialized = True
        logger.info("料仓状态判断服务已初始化")
    
    # 2. 更新状态
    def update_state(
        self, 
        q3_7_discharge: bool,
        q4_0_request: bool,
        i4_6_feeding_feedback: bool
    ) -> HopperState:
        """
        根据 PLC 信号判断料仓状态
        
        优先级: 排料 > 上料中 > 排队等待 > 静止
        
        Args:
            q3_7_discharge: Q3.7 秤排料 (料仓向炉内排料)
            q4_0_request: Q4.0 秤要料 (料仓请求上料)
            i4_6_feeding_feedback: I4.6 供料反馈 (正在上料)
            
        Returns:
            料仓状态
        """
        
        # 1. 排料中 (最高优先级)
        if q3_7_discharge:
            new_state = 'discharging'
        
        # 2. 上料中 (要料 + 供料反馈)
        elif q4_0_request and i4_6_feeding_feedback:
            new_state = 'feeding'
        
        # 3. 排队等待上料 (要料但未开始供料)
        elif q4_0_request and not i4_6_feeding_feedback:
            new_state = 'waiting_feed'
        
        # 4. 静止
        else:
            new_state = 'idle'
        
        # 状态变化时记录日志
        if new_state != self._current_state:
            logger.info(
                f"料仓状态变化: {self._current_state} -> {new_state} | "
                f"Q3.7(排料)={int(q3_7_discharge)} "
                f"Q4.0(要料)={int(q4_0_request)} "
                f"I4.6(供料反馈)={int(i4_6_feeding_feedback)}"
            )
        
        self._current_state = new_state
        return self._current_state
    
    # 3. 获取当前状态
    def get_current_state(self) -> HopperState:
        """获取当前状态"""
        return self._current_state
    
    # 4. 获取状态描述
    def get_state_description(self, state: HopperState = None) -> str:
        """获取状态描述文字"""
        if state is None:
            state = self._current_state
        
        descriptions = {
            'idle': '静止',
            'feeding': '上料中',
            'waiting_feed': '排队等待上料',
            'discharging': '排料中'
        }
        return descriptions.get(state, '未知')


# 5. 单例获取函数
_hopper_state_service = None

def get_hopper_state_service() -> HopperStateService:
    """获取料仓状态服务单例"""
    global _hopper_state_service
    if _hopper_state_service is None:
        _hopper_state_service = HopperStateService()
    return _hopper_state_service

