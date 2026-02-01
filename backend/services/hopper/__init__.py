"""
料仓模块 (Hopper Module)

包含料仓相关的所有服务：
- accumulator.py: 投料累计器（基于 PLC DB18/DB19）
- input_service.py: 料仓上限值写入服务
"""

from backend.services.hopper.accumulator import (
    FeedingPLCAccumulator,
    get_feeding_plc_accumulator,
    FeedingRecord
)

from backend.services.hopper.input_service import (
    set_hopper_upper_limit
)

__all__ = [
    'FeedingPLCAccumulator',
    'get_feeding_plc_accumulator',
    'FeedingRecord',
    'set_hopper_upper_limit',
]

