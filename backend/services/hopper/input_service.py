"""
料仓上限值写入服务
"""
from typing import Dict, Any
from loguru import logger


def set_hopper_upper_limit(upper_limit: float) -> Dict[str, Any]:
    """
    设置料仓上限值（写入 PLC DB18）
    
    Args:
        upper_limit: 料仓上限值 (kg)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. 参数校验
        if upper_limit <= 0:
            return {
                'success': False,
                'message': f'料仓上限值必须大于0，当前值: {upper_limit} kg'
            }
        
        if upper_limit > 10000:
            return {
                'success': False,
                'message': f'料仓上限值不能超过10000kg，当前值: {upper_limit} kg'
            }
        
        # 2. 调用桥接层写入 PLC
        from backend.bridge.plc_writer import write_hopper_upper_limit_to_plc
        
        result = write_hopper_upper_limit_to_plc(upper_limit)
        
        if result['success']:
            logger.info(f"料仓上限值已设置: {upper_limit} kg")
            return {
                'success': True,
                'message': f'料仓上限值已设置为 {int(upper_limit)} kg'
            }
        else:
            logger.error(f"设置料仓上限值失败: {result['message']}")
            return result
        
    except Exception as e:
        logger.error(f"设置料仓上限值异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'设置失败: {str(e)}'
        }

