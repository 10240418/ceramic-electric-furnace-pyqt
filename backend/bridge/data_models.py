"""
前端数据模型定义
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class ElectrodeData:
    phase: str
    arc_current: float = 0.0
    arc_voltage: float = 0.0
    setpoint: float = 0.0
    depth: float = 0.0
    
    current_alarm: bool = False
    depth_alarm: bool = False
    
    def __repr__(self):
        return f"Electrode({self.phase}: {self.arc_current}A, {self.arc_voltage}V, {self.depth}mm)"


@dataclass
class ArcData:
    electrodes: Dict[str, ElectrodeData] = field(default_factory=dict)
    manual_deadzone_percent: float = 0.0
    timestamp: float = 0.0
    
    # 1. 初始化 3 个电极
    def __post_init__(self):
        if not self.electrodes:
            self.electrodes = {
                'U': ElectrodeData(phase='U'),
                'V': ElectrodeData(phase='V'),
                'W': ElectrodeData(phase='W')
            }
    
    # 2. 获取指定相的电极数据
    def get_electrode(self, phase: str) -> ElectrodeData:
        return self.electrodes.get(phase, ElectrodeData(phase=phase))


@dataclass
class CoolingWaterData:
    inlet_temp: float = 0.0
    outlet_temp: float = 0.0
    flow_rate: float = 0.0
    pressure: float = 0.0
    
    temp_alarm: bool = False
    flow_alarm: bool = False
    pressure_alarm: bool = False


@dataclass
class HopperData:
    weight_1: float = 0.0
    weight_2: float = 0.0
    weight_3: float = 0.0
    
    low_level_alarm: bool = False


@dataclass
class ValveStatus:
    valve_id: str
    is_open: bool = False
    is_closed: bool = False
    is_stopped: bool = True
    openness_percent: float = 0.0
    
    # 3. 获取状态文本
    def get_status_text(self) -> str:
        if self.is_open:
            return "开启中"
        elif self.is_closed:
            return "关闭中"
        elif self.is_stopped:
            return "停止"
        return "未知"


@dataclass
class DustCollectorData:
    fan_running: bool = False
    valve_1: ValveStatus = field(default_factory=lambda: ValveStatus(valve_id='1'))
    valve_2: ValveStatus = field(default_factory=lambda: ValveStatus(valve_id='2'))
    valve_3: ValveStatus = field(default_factory=lambda: ValveStatus(valve_id='3'))
    valve_4: ValveStatus = field(default_factory=lambda: ValveStatus(valve_id='4'))


@dataclass
class SensorData:
    cooling_water: CoolingWaterData = field(default_factory=CoolingWaterData)
    hopper: HopperData = field(default_factory=HopperData)
    dust_collector: DustCollectorData = field(default_factory=DustCollectorData)
    timestamp: float = 0.0


@dataclass
class BatchStatus:
    is_smelting: bool = False
    batch_code: str = ""
    start_time: Optional[datetime] = None
    elapsed_seconds: int = 0
    
    # 4. 获取已用时间文本（HH:MM:SS）
    def get_elapsed_time_text(self) -> str:
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass
class AlarmRecord:
    alarm_id: str
    alarm_type: str
    alarm_message: str
    alarm_level: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_acknowledged: bool = False
    
    # 5. 获取报警级别颜色
    def get_level_color(self) -> str:
        colors = {
            'warning': '#FFA500',
            'error': '#FF4444',
            'critical': '#FF0000'
        }
        return colors.get(self.alarm_level, '#FFFFFF')


@dataclass
class HistoryDataPoint:
    timestamp: datetime
    value: float
    label: str = ""
    
    # 6. 获取时间戳（毫秒）
    def get_timestamp_ms(self) -> int:
        return int(self.timestamp.timestamp() * 1000)


# 7. 将字典转换为 ArcData 对象
def dict_to_arc_data(data: Dict) -> ArcData:
    arc_data = ArcData(
        manual_deadzone_percent=data.get('manual_deadzone_percent', 0.0),
        timestamp=data.get('timestamp', 0.0)
    )
    
    # 转换电极数据
    arc_current = data.get('arc_current', {})
    arc_voltage = data.get('arc_voltage', {})
    setpoints = data.get('setpoints', {})
    depths = data.get('electrode_depths', {})
    
    for phase in ['U', 'V', 'W']:
        arc_data.electrodes[phase] = ElectrodeData(
            phase=phase,
            arc_current=arc_current.get(phase, 0.0),
            arc_voltage=arc_voltage.get(phase, 0.0),
            setpoint=setpoints.get(phase, 0.0),
            depth=depths.get(phase, 0.0)
        )
    
    return arc_data


# 8. 将字典转换为 SensorData 对象
def dict_to_sensor_data(data: Dict) -> SensorData:
    sensor_data = SensorData(timestamp=data.get('timestamp', 0.0))
    
    # 冷却水数据
    cooling = data.get('cooling', {})
    sensor_data.cooling_water = CoolingWaterData(
        inlet_temp=cooling.get('inlet_temp', 0.0),
        outlet_temp=cooling.get('outlet_temp', 0.0),
        flow_rate=cooling.get('flow_rate', 0.0),
        pressure=cooling.get('pressure', 0.0)
    )
    
    # 料仓数据
    hopper = data.get('hopper', {})
    sensor_data.hopper = HopperData(
        weight_1=hopper.get('weight_1', 0.0),
        weight_2=hopper.get('weight_2', 0.0),
        weight_3=hopper.get('weight_3', 0.0)
    )
    
    # 除尘器数据
    dust = data.get('dust_collector', {})
    sensor_data.dust_collector = DustCollectorData(
        fan_running=dust.get('fan_running', False)
    )
    
    # 阀门状态
    valve_status = data.get('valve_status', {})
    valve_openness = data.get('valve_openness', {})
    
    for i in range(1, 5):
        valve_id = str(i)
        status = valve_status.get(valve_id, {})
        valve = ValveStatus(
            valve_id=valve_id,
            is_open=status.get('is_open', False),
            is_closed=status.get('is_closed', False),
            is_stopped=status.get('is_stopped', True),
            openness_percent=valve_openness.get(valve_id, 0.0)
        )
        setattr(sensor_data.dust_collector, f'valve_{valve_id}', valve)
    
    return sensor_data


# 9. 将字典转换为 BatchStatus 对象
def dict_to_batch_status(data: Dict) -> BatchStatus:
    start_time = None
    if data.get('start_time'):
        start_time = datetime.fromtimestamp(data['start_time'])
    
    return BatchStatus(
        is_smelting=data.get('is_smelting', False),
        batch_code=data.get('batch_code', ''),
        start_time=start_time,
        elapsed_seconds=data.get('elapsed_seconds', 0)
    )

