# ============================================================
# 文件说明: feeding_accumulator.py - 投料重量累计计算服务
# ============================================================
# 功能:
#   1. 维护60个数据点的队列（30秒历史，每0.5秒一个点）
#   2. 每30秒计算一次投料量
#   3. 根据 %Q3.7 (秤排料) 信号检测投料事件
#   4. 使用前3个点和后3个点的平均值计算投料量，防抖动
#   5. 从数据库查询累计值并更新
# ============================================================
# 【数据库写入说明 - 料仓重量数据】
# ============================================================
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: hopper_weight
#   - device_id: hopper_1
#   - batch_code: 批次号 (动态)
# Fields (共3个数据点):
# ============================================================
#   - net_weight: 料仓净重 (kg)
#   - feeding_total: 累计投料量 (kg) - 每30秒计算一次增量
#   - is_discharging: 投料状态 (0=未投料, 1=正在投料) - %Q3.7秤排料信号
# ============================================================
# 写入逻辑:
#   - 轮询间隔: 0.5秒 (与DB32同步)
#   - 批量写入: 30次轮询后写入 (15秒)
#   - 投料检测: 根据 %Q3.7 信号检测连续投料段，计算投料量
#   - 投料量计算: 开始3点平均重量 - 结束3点平均重量
#   - 最小投料阈值: 1.0kg (防止误检测)
#   - 批次重置: 新批次开始时从数据库恢复累计值或从0开始
# ============================================================

import threading
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from collections import deque
from dataclasses import dataclass


@dataclass
class FeedingDataPoint:
    """单个数据点"""
    weight: float           # 料仓重量 (kg)
    is_discharging: bool    # %Q3.7 秤排料 (True=正在投料)
    is_requesting: bool     # %Q4.0 秤要料
    timestamp: datetime


class FeedingAccumulator:
    """投料重量累计计算器 - 单例模式
    
    投料检测逻辑:
    1. 每0.5秒读取一次料仓重量和投料信号
    2. 缓存60个数据点（30秒）
    3. 每30秒分析一次：找出所有 is_discharging=True 的连续段
    4. 每个连续段视为一次投料事件
    5. 投料量 = 开始3点平均重量 - 结束3点平均重量
    
    状态判断逻辑 (基于 PLC Q 区信号):
    - Q3.7=1, Q4.0=0 -> 排料中
    - Q3.7=0, Q4.0=1 -> 上料中
    - Q3.7=1, Q4.0=1 -> 异常
    - Q3.7=0, Q4.0=0 -> 静止
    """
    
    _instance: Optional['FeedingAccumulator'] = None
    _lock = threading.Lock()
    
    # 队列大小: 60个点 (0.5s × 60 = 30秒)
    QUEUE_SIZE = 60
    # 计算间隔: 60次轮询 = 30秒
    CALC_INTERVAL = 60
    # 平均点数: 用于计算开始/结束重量
    AVG_POINTS = 3
    # 最小投料量阈值 (kg): 防止误检测
    MIN_FEEDING_KG = 1.0
    
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
        self._data_lock = threading.Lock()
        
        # ============================================================
        # 数据队列
        # ============================================================
        self._data_queue: deque = deque(maxlen=self.QUEUE_SIZE)
        
        # ============================================================
        # 累计状态
        # ============================================================
        # 【修复】恢复内存缓存，用于实时显示
        self._feeding_total: float = 0.0       # 累计投料量 (kg)
        self._feeding_count: int = 0           # 投料次数
        self._current_batch_code: Optional[str] = None
        
        # ============================================================
        # 计数器
        # ============================================================
        self._poll_count: int = 0
        
        # ============================================================
        # 最近一次计算结果
        # ============================================================
        self._last_calc_result: Dict[str, Any] = {}
        
        print(" 投料累计器已初始化 (30秒窗口, 信号检测模式)")
    
    # ============================================================
    # 1: 批次管理模块
    # ============================================================
    def reset_for_new_batch(self, batch_code: str):
        """重置累计量 (新批次开始时调用)
        
        【修复】从数据库恢复累计值到内存
        """
        with self._data_lock:
            # 清空队列和计数器
            self._data_queue.clear()
            self._poll_count = 0
            self._last_calc_result = {}
            self._current_batch_code = batch_code
            self._feeding_count = 0
            
            # 从数据库恢复累计值到内存
            latest_total = self._get_latest_from_database(batch_code)
            self._feeding_total = latest_total
            
            print(f"[NEW] 投料累计器已重置 (批次: {batch_code}, 恢复: {latest_total:.1f}kg)")
    
    def _get_latest_from_database(self, batch_code: str) -> float:
        """从 InfluxDB 查询该批次的最新投料累计值
        
        【修改】使用 max() 而不是 last()，因为累计值是递增的
        
        Returns:
            feeding_total (kg)
        """
        try:
            from backend.core.influxdb import get_influxdb_client
            from backend.config import get_settings
            
            settings = get_settings()
            influx = get_influxdb_client()
            
            # 【修改】使用 max() 获取最大累计值（最新值）
            query = f'''
                from(bucket: "{settings.influx_bucket}")
                    |> range(start: -7d)
                    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                    |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
                    |> filter(fn: (r) => r["module_type"] == "hopper_weight")
                    |> filter(fn: (r) => r["_field"] == "feeding_total")
                    |> max()
            '''
            
            print(f"[DEBUG] 查询投料累计 - 批次: {batch_code}")
            print(f"[DEBUG] 查询语句: {query}")
            
            result = influx.query_api().query(query)
            
            feeding_total = 0.0
            record_count = 0
            
            for table in result:
                for record in table.records:
                    record_count += 1
                    value = record.get_value()
                    feeding_total = float(value) if value else 0.0
                    print(f"[DEBUG] 查询到投料累计: {feeding_total}kg (记录时间: {record.get_time()})")
                    break
            
            if record_count == 0:
                print(f"[DEBUG] 未查询到投料累计数据，返回 0.0kg")
            
            return feeding_total
            
        except Exception as e:
            print(f" 从数据库恢复投料累计失败: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    # ============================================================
    # 2: 数据添加模块
    # ============================================================
    def add_measurement(
        self,
        weight_kg: float,
        is_discharging: bool,
        is_requesting: bool = False
    ) -> Dict[str, Any]:
        """添加一次测量数据
        
        Args:
            weight_kg: 料仓当前重量 (kg)
            is_discharging: %Q3.7 秤排料信号 (True=正在投料)
            is_requesting: %Q4.0 秤要料信号
            
        Returns:
            {
                'should_calc': bool,          # 是否需要计算投料
                'queue_size': int,            # 当前队列大小
                'feeding_total': float,       # 当前累计投料量
            }
        """
        with self._data_lock:
            # 1. 添加到队列
            point = FeedingDataPoint(
                weight=weight_kg,
                is_discharging=is_discharging,
                is_requesting=is_requesting,
                timestamp=datetime.now(timezone.utc)
            )
            self._data_queue.append(point)
            
            # 2. 计数器递增
            self._poll_count += 1
            
            # 3. 检查是否需要计算 (每60次 = 30秒)
            should_calc = self._poll_count >= self.CALC_INTERVAL
            
            return {
                'should_calc': should_calc,
                'queue_size': len(self._data_queue),
                'feeding_total': self._feeding_total,
                'is_discharging': is_discharging,
            }
    
    # ============================================================
    # 3: 投料计算模块
    # ============================================================
    def calculate_feeding(self) -> Dict[str, Any]:
        """分析队列数据，计算投料量
        
        逻辑:
        1. 找出所有 is_discharging=True 的连续段
        2. 每个连续段视为一次投料事件
        3. 投料量 = 开始3点平均 - 结束3点平均
        4. 累加到 feeding_total
        
        Returns:
            {
                'feeding_events': List[Dict],  # 检测到的投料事件列表
                'total_added': float,          # 本次新增投料量
                'feeding_total': float,        # 累计投料量
                'feeding_count': int,          # 累计投料次数
            }
        """
        with self._data_lock:
            # 重置计数器
            self._poll_count = 0
            
            if len(self._data_queue) < 10:
                return {
                    'feeding_events': [],
                    'total_added': 0.0,
                    'feeding_total': self._feeding_total,
                    'feeding_count': self._feeding_count,
                    'message': '队列数据不足'
                }
            
            # 转换为列表便于索引
            data_list = list(self._data_queue)
            feeding_events = []
            
            # 查找连续的 is_discharging=True 段
            i = 0
            while i < len(data_list):
                if data_list[i].is_discharging:
                    # 找到投料开始
                    start_idx = i
                    
                    # 找到投料结束
                    while i < len(data_list) and data_list[i].is_discharging:
                        i += 1
                    end_idx = i - 1
                    
                    # 需要至少2个连续点才算有效投料
                    if end_idx - start_idx >= 1:
                        # 计算开始重量 (前3个点平均)
                        start_points = min(self.AVG_POINTS, end_idx - start_idx + 1)
                        start_weights = [data_list[j].weight for j in range(start_idx, start_idx + start_points)]
                        start_avg = sum(start_weights) / len(start_weights)
                        
                        # 计算结束重量 (后3个点平均)
                        end_points = min(self.AVG_POINTS, end_idx - start_idx + 1)
                        end_weights = [data_list[j].weight for j in range(end_idx - end_points + 1, end_idx + 1)]
                        end_avg = sum(end_weights) / len(end_weights)
                        
                        # 投料量
                        feeding_amount = start_avg - end_avg
                        
                        # 只记录有效投料 (重量减少且超过阈值)
                        if feeding_amount >= self.MIN_FEEDING_KG:
                            event = {
                                'start_idx': start_idx,
                                'end_idx': end_idx,
                                'duration_points': end_idx - start_idx + 1,
                                'start_weight': start_avg,
                                'end_weight': end_avg,
                                'amount': feeding_amount,
                                'start_time': data_list[start_idx].timestamp.isoformat(),
                                'end_time': data_list[end_idx].timestamp.isoformat(),
                            }
                            feeding_events.append(event)
                else:
                    i += 1
            
            # 累加投料量
            total_added = sum(e['amount'] for e in feeding_events)
            self._feeding_count += len(feeding_events)
            
            # 【修复】使用内存累计值
            self._feeding_total += total_added
            
            result = {
                'feeding_events': feeding_events,
                'total_added': total_added,
                'feeding_total': self._feeding_total,
                'feeding_count': self._feeding_count,
                'queue_analyzed': len(data_list),
            }
            
            self._last_calc_result = result
            
            # 打印日志
            if feeding_events:
                print(f"[FEEDING] 检测到 {len(feeding_events)} 次投料:")
                for idx, e in enumerate(feeding_events):
                    print(f"   第{idx+1}次: {e['start_weight']:.1f}kg -> {e['end_weight']:.1f}kg = {e['amount']:.1f}kg")
                print(f"   本次新增: {total_added:.1f}kg, 新累计: {self._feeding_total:.1f}kg")
            
            return result
    
    # ============================================================
    # 3.1: 重量变化率计算模块
    # ============================================================
    def calculate_weight_change_rate(self) -> Dict[str, Any]:
        """计算重量变化率（kg/s）
        
        用途:
        1. 验证 PLC 信号的准确性
        2. 检测无信号的异常投料/上料
        3. 区分上料和排料
        
        Returns:
            {
                'state': '排料中' | '上料中' | '静止' | '未知',
                'rate': float,        # kg/s
                'confidence': float   # 0-1
            }
        """
        with self._data_lock:
            if len(self._data_queue) < 10:
                return {
                    'state': '未知',
                    'rate': 0.0,
                    'confidence': 0.0
                }
            
            # 取最近10个点 (5秒)
            recent_points = list(self._data_queue)[-10:]
            
            # 计算线性回归斜率
            weights = [p.weight for p in recent_points]
            times = [(p.timestamp - recent_points[0].timestamp).total_seconds() 
                     for p in recent_points]
            
            # 简单线性回归
            n = len(weights)
            sum_x = sum(times)
            sum_y = sum(weights)
            sum_xy = sum(t * w for t, w in zip(times, weights))
            sum_x2 = sum(t * t for t in times)
            
            if n * sum_x2 - sum_x * sum_x == 0:
                return {'state': '静止', 'rate': 0.0, 'confidence': 0.0}
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # 判断状态
            if slope < -5:
                state = '排料中'  # 排料
                confidence = min(abs(slope) / 10.0, 1.0)
            elif slope > 5:
                state = '上料中'  # 上料
                confidence = min(abs(slope) / 10.0, 1.0)
            else:
                state = '静止'  # 稳定
                confidence = 1.0 - min(abs(slope) / 5.0, 1.0)
            
            return {
                'state': state,
                'rate': round(slope, 2),  # kg/s
                'confidence': round(confidence, 2)
            }
    
    # ============================================================
    # 3.2: 综合状态判断模块
    # ============================================================
    def get_hopper_state_comprehensive(self) -> Dict[str, Any]:
        """综合判断料仓状态（PLC Q区信号 + 重量变化率）
        
        状态优先级:
        1. 异常检测 (Q3.7=1 且 Q4.0=1)
        2. 排料中 (Q3.7=1, Q4.0=0)
        3. 上料中 (Q3.7=0, Q4.0=1)
        4. 静止 (Q3.7=0, Q4.0=0)
        
        Returns:
            {
                'state': '排料中' | '上料中' | '静止' | '异常' | '未知',
                'confidence': 'high' | 'medium' | 'low',
                'is_discharging': bool,      # PLC Q3.7
                'is_requesting': bool,       # PLC Q4.0
                'weight_rate': float,        # kg/s
                'current_weight': float,     # kg
                'source': str,               # 判断依据
                'warnings': List[str]        # 异常警告
            }
        """
        with self._data_lock:
            if not self._data_queue:
                return {
                    'state': '未知',
                    'confidence': 'low',
                    'is_discharging': False,
                    'is_requesting': False,
                    'weight_rate': 0.0,
                    'current_weight': 0.0,
                    'source': 'no_data',
                    'warnings': ['数据队列为空']
                }
            
            # 获取最新数据点
            latest = self._data_queue[-1]
            is_discharging = latest.is_discharging  # %Q3.7
            is_requesting = latest.is_requesting    # %Q4.0
            current_weight = latest.weight
            
            # 计算重量变化率
            rate_result = self.calculate_weight_change_rate()
            weight_rate = rate_result['rate']
            rate_state = rate_result['state']
            
            warnings = []
            
            # ========================================
            # 1. 异常检测（最高优先级）
            # ========================================
            if is_discharging and is_requesting:
                warnings.append('同时检测到投料和上料信号，PLC逻辑异常')
                return {
                    'state': '异常',
                    'confidence': 'high',
                    'is_discharging': True,
                    'is_requesting': True,
                    'weight_rate': weight_rate,
                    'current_weight': current_weight,
                    'source': 'plc_signal_conflict',
                    'warnings': warnings
                }
            
            # ========================================
            # 2. 排料中 Q3.7=1, Q4.0=0
            # ========================================
            if is_discharging and not is_requesting:
                # 验证：重量应该在下降
                if weight_rate < -1:
                    return {
                        'state': '排料中',
                        'confidence': 'high',
                        'is_discharging': True,
                        'is_requesting': False,
                        'weight_rate': weight_rate,
                        'current_weight': current_weight,
                        'source': 'plc_signal + weight_rate',
                        'warnings': []
                    }
                else:
                    warnings.append('PLC显示投料但重量未下降，可能阀门故障或传感器异常')
                    return {
                        'state': '排料中',
                        'confidence': 'low',
                        'is_discharging': True,
                        'is_requesting': False,
                        'weight_rate': weight_rate,
                        'current_weight': current_weight,
                        'source': 'plc_signal_only',
                        'warnings': warnings
                    }
            
            # ========================================
            # 3. 上料中 Q3.7=0, Q4.0=1
            # ========================================
            if not is_discharging and is_requesting:
                # 验证：重量应该在上升或较低
                if weight_rate > 1:
                    return {
                        'state': '上料中',
                        'confidence': 'high',
                        'is_discharging': False,
                        'is_requesting': True,
                        'weight_rate': weight_rate,
                        'current_weight': current_weight,
                        'source': 'plc_signal + weight_rate',
                        'warnings': []
                    }
                elif current_weight < 200:
                    return {
                        'state': '上料中',
                        'confidence': 'high',
                        'is_discharging': False,
                        'is_requesting': True,
                        'weight_rate': weight_rate,
                        'current_weight': current_weight,
                        'source': 'plc_signal + weight_threshold',
                        'warnings': []
                    }
                else:
                    warnings.append('上料信号激活但重量未上升且不低')
                    return {
                        'state': '上料中',
                        'confidence': 'medium',
                        'is_discharging': False,
                        'is_requesting': True,
                        'weight_rate': weight_rate,
                        'current_weight': current_weight,
                        'source': 'plc_signal_only',
                        'warnings': warnings
                    }
            
            # ========================================
            # 4. 静止状态 Q3.7=0, Q4.0=0
            # ========================================
            # 无信号时，使用重量变化率辅助判断
            if abs(weight_rate) > 5:
                if weight_rate > 0:
                    warnings.append('检测到重量上升但无PLC上料信号')
                    state = '上料中'
                else:
                    warnings.append('检测到重量下降但无PLC投料信号')
                    state = '排料中'
                
                return {
                    'state': state,
                    'confidence': 'low',
                    'is_discharging': False,
                    'is_requesting': False,
                    'weight_rate': weight_rate,
                    'current_weight': current_weight,
                    'source': 'weight_rate_only',
                    'warnings': warnings
                }
            else:
                return {
                    'state': '静止',
                    'confidence': 'high',
                    'is_discharging': False,
                    'is_requesting': False,
                    'weight_rate': weight_rate,
                    'current_weight': current_weight,
                    'source': 'plc_signal + weight_rate',
                    'warnings': []
                }
    
    # ============================================================
    # 4: 数据获取模块
    # ============================================================
    def get_feeding_total(self) -> float:
        """获取累计投料量 (kg)
        
        【修复】直接返回内存中的累计值
        """
        with self._data_lock:
            return self._feeding_total
    
    def get_realtime_data(self) -> Dict[str, Any]:
        """获取实时数据 (供API调用)
        
        Returns:
            {
                'feeding_total': float,           # 累计投料量
                'feeding_count': int,             # 投料次数
                'current_weight': float,          # 当前重量
                'is_discharging': bool,           # Q3.7 投料信号
                'is_requesting': bool,            # Q4.0 上料信号
                'batch_code': str,                # 当前批次号
                'queue_size': int,                # 队列大小
                'last_calc_result': dict,         # 最近一次计算结果
                'hopper_state': dict,             # 综合状态判断
                'weight_change_rate': dict        # 重量变化率
            }
        """
        with self._data_lock:
            current_weight = self._data_queue[-1].weight if self._data_queue else 0.0
            is_discharging = self._data_queue[-1].is_discharging if self._data_queue else False
            is_requesting = self._data_queue[-1].is_requesting if self._data_queue else False
            
            # 获取综合状态判断
            hopper_state = self.get_hopper_state_comprehensive()
            
            # 获取重量变化率
            weight_change_rate = self.calculate_weight_change_rate()
            
            return {
                'feeding_total': self._feeding_total,
                'feeding_count': self._feeding_count,
                'current_weight': current_weight,
                'is_discharging': is_discharging,
                'is_requesting': is_requesting,
                'batch_code': self._current_batch_code,
                'queue_size': len(self._data_queue),
                'last_calc_result': self._last_calc_result,
                'hopper_state': hopper_state,
                'weight_change_rate': weight_change_rate,
            }


# ============================================================
# 全局单例获取函数
# ============================================================

_feeding_accumulator: Optional[FeedingAccumulator] = None

def get_feeding_accumulator() -> FeedingAccumulator:
    """获取投料累计器单例"""
    global _feeding_accumulator
    if _feeding_accumulator is None:
        _feeding_accumulator = FeedingAccumulator()
    return _feeding_accumulator
