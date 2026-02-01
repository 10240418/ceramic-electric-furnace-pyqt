# ============================================================
# 文件说明: polling_data_generator.py - Mock数据生成器
# ============================================================
# 功能:
#   为开发和测试提供 Mock 数据生成
#   包含: DB1/DB30/DB32/DB41 等所有数据块的 Mock 生成
# ============================================================

import random
import struct
import time
from typing import Dict, Any


# ============================================================
# 蝶阀状态模拟器（全局状态，模拟真实的开关过程）
# ============================================================
class ValveSimulator:
    """蝶阀状态模拟器
    
    模拟4个蝶阀的真实开关过程：
    - 关闭状态 "10" (bit_close=1, bit_open=0)
    - 打开状态 "01" (bit_close=0, bit_open=1)
    - 开关过程中会经历中间状态
    """
    
    def __init__(self):
        # 每个蝶阀的当前状态: "10"=关闭, "01"=打开
        self.valve_states = {
            1: "10",  # 蝶阀1初始关闭
            2: "01",  # 蝶阀2初始打开
            3: "10",  # 蝶阀3初始关闭
            4: "01",  # 蝶阀4初始打开
        }
        
        # 每个蝶阀的目标状态（用于模拟开关过程）
        self.target_states = {
            1: "10",
            2: "01",
            3: "10",
            4: "01",
        }
        
        # 上次状态变化时间
        self.last_change_time = time.time()
        
        # 状态变化间隔（秒）
        self.change_interval = random.uniform(10, 30)  # 10-30秒随机变化一次
    
    def update(self):
        """更新蝶阀状态（模拟随机开关）"""
        current_time = time.time()
        
        # 每隔一段时间随机改变一个蝶阀的目标状态
        if current_time - self.last_change_time > self.change_interval:
            # 随机选择一个蝶阀改变状态
            valve_id = random.randint(1, 4)
            current = self.valve_states[valve_id]
            
            # 切换目标状态
            if current == "10":  # 当前关闭，目标打开
                self.target_states[valve_id] = "01"
            else:  # 当前打开，目标关闭
                self.target_states[valve_id] = "10"
            
            self.last_change_time = current_time
            self.change_interval = random.uniform(10, 30)
        
        # 逐步向目标状态靠近（模拟开关过程）
        for valve_id in range(1, 5):
            if self.valve_states[valve_id] != self.target_states[valve_id]:
                # 模拟开关过程：80%概率到达目标，20%概率保持中间状态
                if random.random() < 0.8:
                    self.valve_states[valve_id] = self.target_states[valve_id]
    
    def get_status_byte(self) -> int:
        """获取蝶阀状态字节
        
        Returns:
            int: 8位状态字节
                bit0-1: 蝶阀1 (bit0=close, bit1=open)
                bit2-3: 蝶阀2
                bit4-5: 蝶阀3
                bit6-7: 蝶阀4
        """
        status_byte = 0
        
        for valve_id in range(1, 5):
            state = self.valve_states[valve_id]
            bit_offset = (valve_id - 1) * 2
            
            # 解析状态字符串 "10" -> bit_close=1, bit_open=0
            bit_close = int(state[0])
            bit_open = int(state[1])
            
            # 设置对应的bit
            status_byte |= (bit_close << bit_offset)
            status_byte |= (bit_open << (bit_offset + 1))
        
        return status_byte


# 全局蝶阀模拟器实例
_valve_simulator = ValveSimulator()


def generate_mock_db32_data() -> bytes:
    """生成 Mock DB32 数据 (21字节)
    
    数据结构 (根据 config_L3_P2_F2_C4_db32.yaml):
    - LENTH1-3: 红外测距 UDInt (3 x 4 bytes = 12 bytes) offset 0-11
    - WATER_PRESS_1-2: 压力 Int (2 x 2 bytes = 4 bytes) offset 12-15
    - WATER_FLOW_1-2: 流量 Int (2 x 2 bytes = 4 bytes) offset 16-19
    - ValveStatus: 蝶阀状态监测 Byte (1 byte) offset 20
    """
    data = bytearray(21)
    
    # LENTH1-3: 红外测距 UDInt (模拟电极深度 100-500mm，缓慢变化)
    for i in range(3):
        offset = i * 4
        # 电极深度在 100-500mm 之间缓慢变化
        distance = random.randint(100, 500)
        # UDInt: 无符号32位整数，大端序
        struct.pack_into('>I', data, offset, distance)
    
    # WATER_PRESS_1-2: 压力 Int (模拟 150-200 kPa，原始值 150-200)
    # 炉皮水压（过滤器进口）
    struct.pack_into('>h', data, 12, random.randint(150, 200))
    # 炉盖水压（过滤器出口）
    struct.pack_into('>h', data, 14, random.randint(140, 190))
    
    # WATER_FLOW_1-2: 流量 Int (模拟 2-4 m³/h，原始值 200-400)
    # 炉皮流量
    struct.pack_into('>h', data, 16, random.randint(200, 400))
    # 炉盖流量
    struct.pack_into('>h', data, 18, random.randint(200, 400))
    
    # ValveStatus: 蝶阀状态监测 Byte (使用模拟器生成真实的开关过程)
    global _valve_simulator
    _valve_simulator.update()  # 更新状态
    valve_status = _valve_simulator.get_status_byte()
    data[20] = valve_status
    
    return bytes(data)


def generate_mock_db1_data() -> bytes:
    """生成 Mock DB1 弧流弧压数据 (182字节)
    
    数据结构（根据实际PLC配置）:
    - offset 0-7: 电机输出 (4 x Int)
    - offset 8-9: U相弧流中间值 (不存储)
    - offset 10-11: U相弧流 (INT, A)
    - offset 12-13: U相弧压 (INT, V)
    - offset 14-15: V相弧流中间值 (不存储)
    - offset 16-17: V相弧流 (INT, A)
    - offset 18-19: V相弧压 (INT, V)
    - offset 20-21: W相弧流中间值 (不存储)
    - offset 22-23: W相弧流 (INT, A)
    - offset 24-25: W相弧压 (INT, V)
    - offset 26-27: 弧流给定中间值 (不存储)
    - offset 28-29: 弧流设定值 (INT, A)
    - offset 30-63: Vw变量
    - offset 64-67: 死区上下限
      - 64-65: 死区下限 (INT, A)
      - 66-67: 死区上限 (INT, A)
    - offset 68-181: 其他变量
    """
    data = bytearray(182)
    
    # ========================================
    # 电机输出 (offset 0-7, 4 x Int)
    # ========================================
    for i in range(4):
        motor_value = random.randint(0, 100)  # 0-100%
        struct.pack_into('>h', data, i * 2, motor_value)
    
    # ========================================
    # 动态设定值和死区（模拟真实PLC变化）
    # ========================================
    # 设定值在 5978-6100 A 之间动态变化
    ARC_CURRENT_TARGET = random.randint(5978, 6100)
    
    # 死区在 10%-15% 之间动态变化
    manual_deadzone_percent = random.choice([10, 11, 12, 13, 14, 15])
    
    # 目标弧压 80 V
    ARC_VOLTAGE_TARGET = 80
    
    # U相弧流中间值 (offset 8-9, 不使用)
    struct.pack_into('>h', data, 8, random.randint(5000, 6000))
    
    # U相弧流 (offset 10-11)
    arc_current_U = int(ARC_CURRENT_TARGET + random.uniform(-598, 598))
    struct.pack_into('>h', data, 10, arc_current_U)
    
    # U相弧压 (offset 12-13)
    arc_voltage_U = int(ARC_VOLTAGE_TARGET + random.uniform(-10, 10))
    struct.pack_into('>h', data, 12, arc_voltage_U)
    
    # V相弧流中间值 (offset 14-15, 不使用)
    struct.pack_into('>h', data, 14, random.randint(5000, 6000))
    
    # V相弧流 (offset 16-17)
    arc_current_V = int(ARC_CURRENT_TARGET + random.uniform(-598, 598))
    struct.pack_into('>h', data, 16, arc_current_V)
    
    # V相弧压 (offset 18-19)
    arc_voltage_V = int(ARC_VOLTAGE_TARGET + random.uniform(-10, 10))
    struct.pack_into('>h', data, 18, arc_voltage_V)
    
    # W相弧流中间值 (offset 20-21, 不使用)
    struct.pack_into('>h', data, 20, random.randint(5000, 6000))
    
    # W相弧流 (offset 22-23)
    arc_current_W = int(ARC_CURRENT_TARGET + random.uniform(-598, 598))
    struct.pack_into('>h', data, 22, arc_current_W)
    
    # W相弧压 (offset 24-25)
    arc_voltage_W = int(ARC_VOLTAGE_TARGET + random.uniform(-10, 10))
    struct.pack_into('>h', data, 24, arc_voltage_W)
    
    # 弧流给定中间值 (offset 26-27, 不使用)
    struct.pack_into('>h', data, 26, random.randint(5000, 6000))
    
    # 弧流设定值 (offset 28-29, 旧版本，已废弃)
    arc_setpoint = ARC_CURRENT_TARGET
    struct.pack_into('>h', data, 28, arc_setpoint)
    
    # ========================================
    # Vw变量 (offset 30-31, 填充随机值)
    # ========================================
    struct.pack_into('>h', data, 30, random.randint(0, 1000))
    
    # ========================================
    # UVW 三相弧流设定值 (offset 32-43)
    # ========================================
    # U相弧流设定值 (offset 32-33)
    struct.pack_into('>h', data, 32, ARC_CURRENT_TARGET)
    # U相弧流自动灵敏度值 (offset 34-35)
    struct.pack_into('>h', data, 34, 100)
    
    # V相弧流设定值 (offset 36-37)
    struct.pack_into('>h', data, 36, ARC_CURRENT_TARGET)
    # V相弧流自动灵敏度值 (offset 38-39)
    struct.pack_into('>h', data, 38, 100)
    
    # W相弧流设定值 (offset 40-41)
    struct.pack_into('>h', data, 40, ARC_CURRENT_TARGET)
    # W相弧流自动灵敏度值 (offset 42-43)
    struct.pack_into('>h', data, 42, 100)
    
    # ========================================
    # Vw变量 (offset 44-47, 填充随机值)
    # ========================================
    for i in range(44, 48, 2):
        struct.pack_into('>h', data, i, random.randint(0, 1000))
    
    # ========================================
    # 手动死区百分比 (offset 48-49)
    # ========================================
    # 死区百分比已在上面动态生成（10-15%）
    struct.pack_into('>h', data, 48, manual_deadzone_percent)
    
    # ========================================
    # Vw变量 (offset 50-63, 填充随机值)
    # ========================================
    for i in range(50, 64, 2):
        struct.pack_into('>h', data, i, random.randint(0, 1000))
    
    # ========================================
    # 死区上下限 (offset 64-67)
    # ========================================
    # 根据动态死区百分比计算上下限
    deadzone_percent_decimal = manual_deadzone_percent / 100.0
    deadzone_lower = int(ARC_CURRENT_TARGET * (1 - deadzone_percent_decimal))  # 下限
    deadzone_upper = int(ARC_CURRENT_TARGET * (1 + deadzone_percent_decimal))  # 上限
    
    struct.pack_into('>h', data, 64, deadzone_lower)  # offset 64: 下限
    struct.pack_into('>h', data, 66, deadzone_upper)  # offset 66: 上限
    
    # ========================================
    # 其他变量 (offset 68-181, 填充随机值)
    # ========================================
    for i in range(68, 182, 2):
        struct.pack_into('>h', data, i, random.randint(0, 100))
    
    return bytes(data)


def generate_mock_db30_data() -> bytes:
    """生成 Mock DB30 状态数据 (40字节)
    
    10个状态模块，每个4字节:
    - Byte 0: Done/Error/Running 位状态
    - Byte 1-3: Reserved / Status
    """
    data = bytearray(40)
    
    # 10个状态模块，每个4字节
    for i in range(10):
        offset = i * 4
        # 90% 概率正常 (Done=true, Error=false, Status=0)
        if random.random() < 0.9:
            data[offset] = 0x01  # Done=true
            data[offset + 1] = 0x00
            data[offset + 2] = 0x00
            data[offset + 3] = 0x00
        else:
            # 10% 概率异常
            data[offset] = 0x04  # Error=true
            data[offset + 1] = 0x00
            data[offset + 2] = 0x80
            data[offset + 3] = 0x01  # Status=0x8001
    
    return bytes(data)


def generate_mock_db41_data() -> bytes:
    """生成 Mock DB41 数据状态 (28字节)
    
    7个设备的数据状态 (每设备 4 字节):
    - LENTH1-3: 测距传感器 @ 0, 4, 8
    - WATER_1-2: 流量计 @ 12, 16
    - PRESS_1-2: 压力计 @ 20, 24
    
    每个模块结构 (4字节对齐):
    - Error: Bool @ offset+0
    - (保留) @ offset+1
    - Status: Word @ offset+2
    """
    data = bytearray(28)  # 7 设备 × 4 字节 = 28 字节
    
    # LENTH1-3 @ 0, 4, 8
    for offset in [0, 4, 8]:
        if random.random() < 0.92:
            data[offset] = 0x00  # Error = false
            struct.pack_into('>H', data, offset + 2, 0x0000)  # Status = 0 (正常)
        else:
            data[offset] = 0x01  # Error = true
            struct.pack_into('>H', data, offset + 2, 0x8001)  # Status 错误码
    
    # WATER_1-2 @ 12, 16
    for offset in [12, 16]:
        if random.random() < 0.92:
            data[offset] = 0x00
            struct.pack_into('>H', data, offset + 2, 0x0000)
        else:
            data[offset] = 0x01
            struct.pack_into('>H', data, offset + 2, 0x8002)
    
    # PRESS_1-2 @ 20, 24 (修正偏移量)
    for offset in [20, 24]:
        if random.random() < 0.92:
            data[offset] = 0x00
            struct.pack_into('>H', data, offset + 2, 0x0000)
        else:
            data[offset] = 0x01
            struct.pack_into('>H', data, offset + 2, 0x8003)
    
    return bytes(data)


# ============================================================
# 料仓重量模拟器（全局状态，模拟真实的上料和下料过程）
# ============================================================
class HopperWeightSimulator:
    """料仓重量模拟器
    
    模拟真实的上料和下料过程：
    - 上料阶段：重量从 200kg 缓慢增加到 4800kg（约 2-3 分钟）
    - 稳定阶段：重量保持在 4500-4900kg（约 30-60 秒）
    - 下料阶段：重量从 4800kg 缓慢减少到 200kg（约 2-3 分钟）
    - 空仓阶段：重量保持在 200-500kg（约 30-60 秒）
    """
    
    def __init__(self):
        self.current_weight = 300.0  # 当前重量 (kg)
        self.target_weight = 4800.0  # 目标重量 (kg)
        self.phase = "loading"  # 当前阶段: loading, stable_full, unloading, stable_empty
        self.phase_start_time = time.time()
        self.phase_duration = random.uniform(120, 180)  # 阶段持续时间（秒）
        
        # 上料/下料速度 (kg/s)
        self.loading_speed = 30.0  # 30 kg/s (约 2.5 分钟从 200kg 到 4800kg)
        self.unloading_speed = 25.0  # 25 kg/s (约 3 分钟从 4800kg 到 200kg)
    
    def update(self) -> float:
        """更新料仓重量并返回当前值"""
        current_time = time.time()
        elapsed = current_time - self.phase_start_time
        
        if self.phase == "loading":
            # 上料阶段：重量缓慢增加
            self.current_weight += self.loading_speed * 0.5  # 每 0.5s 增加
            
            # 到达目标重量，切换到稳定阶段
            if self.current_weight >= self.target_weight:
                self.current_weight = self.target_weight
                self.phase = "stable_full"
                self.phase_start_time = current_time
                self.phase_duration = random.uniform(30, 60)  # 稳定 30-60 秒
        
        elif self.phase == "stable_full":
            # 稳定阶段（满仓）：重量在 4500-4900kg 之间小幅波动
            self.current_weight = random.uniform(4500, 4900)
            
            # 稳定一段时间后，开始下料
            if elapsed > self.phase_duration:
                self.phase = "unloading"
                self.phase_start_time = current_time
                self.phase_duration = random.uniform(120, 180)
        
        elif self.phase == "unloading":
            # 下料阶段：重量缓慢减少
            self.current_weight -= self.unloading_speed * 0.5  # 每 0.5s 减少
            
            # 到达最低重量，切换到空仓阶段
            if self.current_weight <= 200:
                self.current_weight = 200
                self.phase = "stable_empty"
                self.phase_start_time = current_time
                self.phase_duration = random.uniform(30, 60)  # 稳定 30-60 秒
        
        elif self.phase == "stable_empty":
            # 稳定阶段（空仓）：重量在 200-500kg 之间小幅波动
            self.current_weight = random.uniform(200, 500)
            
            # 稳定一段时间后，开始上料
            if elapsed > self.phase_duration:
                self.phase = "loading"
                self.phase_start_time = current_time
                self.phase_duration = random.uniform(120, 180)
        
        return self.current_weight
    
    def is_discharging(self) -> bool:
        """判断是否正在下料"""
        return self.phase == "unloading"


# 全局料仓重量模拟器实例
_hopper_simulator = HopperWeightSimulator()


def generate_mock_weight_data() -> Dict[str, Any]:
    """生成 Mock 料仓重量数据（模拟真实的上料和下料过程）
    
    Returns:
        与 read_hopper_weight() 相同格式的结果
    """
    from backend.tools.operation_modbus_weight_reader import mock_read_weight
    
    # 使用模拟器生成缓慢变化的重量
    global _hopper_simulator
    weight = _hopper_simulator.update()
    
    # 转换为整数（mock_read_weight 需要 int）
    return mock_read_weight(weight=int(weight))
