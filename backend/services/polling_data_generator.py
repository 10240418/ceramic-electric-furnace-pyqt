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


# ============================================================
# 料仓 PLC 模拟器（全局状态，模拟真实的投料过程）
# ============================================================
class HopperPLCSimulator:
    """料仓 PLC 模拟器
    
    模拟料仓的四种状态：
    1. 静止 (idle): 料仓重量稳定，无操作
    2. 上料中 (feeding): Q4.0=True, I4.6=True，重量增加
    3. 排队等待上料 (waiting_feed): Q4.0=True, I4.6=False，等待上料
    4. 排料中 (discharging): Q3.7=True, DB19.2.3=True，重量减少
    """
    
    # 状态常量
    STATE_IDLE = 'idle'              # 静止
    STATE_FEEDING = 'feeding'        # 上料中
    STATE_WAITING_FEED = 'waiting_feed'  # 排队等待上料
    STATE_DISCHARGING = 'discharging'    # 排料中
    
    def __init__(self):
        self.current_weight = 3500.0  # 当前料仓重量 (kg)
        self.discharge_weight = 0.0   # 本次排料重量 (kg)
        self.discharge_weight_ready = False  # 排料重量待读取标志
        
        # 当前状态
        self.state = self.STATE_IDLE
        
        # 信号状态
        self.is_discharging = False  # Q3.7 秤排料
        self.is_requesting = False   # Q4.0 秤要料
        self.is_feeding_back = False # I4.6 供料反馈
        
        # 状态切换时间
        self.state_start_time = time.time()
        self.state_duration = 0
        
        # 上次状态切换时间
        self.last_state_change = time.time()
        self.state_change_interval = random.uniform(15, 30)  # 15-30秒切换一次状态
    
    def update(self):
        """更新料仓状态"""
        current_time = time.time()
        elapsed = current_time - self.state_start_time
        
        # 状态机
        if self.state == self.STATE_IDLE:
            # 静止状态：重量不变
            self.is_discharging = False
            self.is_requesting = False
            self.is_feeding_back = False
            self.discharge_weight_ready = False
            
            # 检查是否需要切换状态
            if current_time - self.last_state_change > self.state_change_interval:
                # 70% 概率排料，30% 概率上料
                if random.random() < 0.7:
                    self._switch_to_discharging()
                else:
                    self._switch_to_waiting_feed()
                self.last_state_change = current_time
                self.state_change_interval = random.uniform(15, 30)
        
        elif self.state == self.STATE_DISCHARGING:
            # 排料中：Q3.7=True，重量逐渐减少
            self.is_discharging = True
            self.is_requesting = False
            self.is_feeding_back = False
            
            # 排料持续 3-5 秒
            if elapsed < self.state_duration:
                # 重量逐渐减少（每次更新减少一点）
                progress = elapsed / self.state_duration
                # 计算当前应该减少的重量
                target_weight = self.discharge_start_weight - self.discharge_weight
                self.current_weight = self.discharge_start_weight - (self.discharge_weight * progress)
                self.current_weight = max(2500, self.current_weight)
            else:
                # 排料结束
                self.is_discharging = False
                self.discharge_weight_ready = True  # 设置待读取标志
                self.current_weight = self.discharge_start_weight - self.discharge_weight
                self.current_weight = max(2500, self.current_weight)
                
                # 如果重量低于 3000kg，进入等待上料状态
                if self.current_weight < 3000:
                    self._switch_to_waiting_feed()
                else:
                    self._switch_to_idle()
        
        elif self.state == self.STATE_WAITING_FEED:
            # 排队等待上料：Q4.0=True, I4.6=False，重量不变
            self.is_discharging = False
            self.is_requesting = True
            self.is_feeding_back = False
            self.discharge_weight_ready = False
            
            # 等待 2-5 秒后开始上料
            if elapsed > self.state_duration:
                self._switch_to_feeding()
        
        elif self.state == self.STATE_FEEDING:
            # 上料中：Q4.0=True, I4.6=True，重量逐渐增加
            self.is_discharging = False
            self.is_requesting = True
            self.is_feeding_back = True
            self.discharge_weight_ready = False
            
            # 上料持续 5-8 秒
            if elapsed < self.state_duration:
                # 重量逐渐增加（每次更新增加一点）
                progress = elapsed / self.state_duration
                # 计算当前应该增加的重量
                target_weight = self.feeding_start_weight + self.feeding_amount
                self.current_weight = self.feeding_start_weight + (self.feeding_amount * progress)
                self.current_weight = min(4900, self.current_weight)
            else:
                # 上料结束
                self.is_requesting = False
                self.is_feeding_back = False
                self.current_weight = self.feeding_start_weight + self.feeding_amount
                self.current_weight = min(4900, self.current_weight)
                self._switch_to_idle()
    
    def _switch_to_idle(self):
        """切换到静止状态"""
        self.state = self.STATE_IDLE
        self.state_start_time = time.time()
        self.state_duration = 0
    
    def _switch_to_discharging(self):
        """切换到排料中状态"""
        self.state = self.STATE_DISCHARGING
        self.state_start_time = time.time()
        self.state_duration = random.uniform(3, 5)  # 3-5秒
        self.discharge_weight = random.uniform(50, 200)  # 50-200kg
        self.discharge_start_weight = self.current_weight  # 记录排料开始时的重量
        self.discharge_weight_ready = False
    
    def _switch_to_waiting_feed(self):
        """切换到排队等待上料状态"""
        self.state = self.STATE_WAITING_FEED
        self.state_start_time = time.time()
        self.state_duration = random.uniform(2, 5)  # 等待 2-5 秒
    
    def _switch_to_feeding(self):
        """切换到上料中状态"""
        self.state = self.STATE_FEEDING
        self.state_start_time = time.time()
        self.state_duration = random.uniform(5, 8)  # 5-8秒
        self.feeding_start_weight = self.current_weight  # 记录上料开始时的重量
        self.feeding_amount = random.uniform(500, 1000)  # 上料量 500-1000kg
    
    def reset_discharge_flag(self):
        """重置排料重量待读取标志（模拟 PLC 外部复位）"""
        self.discharge_weight_ready = False
    
    def get_state(self) -> str:
        """获取当前状态"""
        return self.state


# 全局料仓模拟器实例
_hopper_plc_simulator = HopperPLCSimulator()


def generate_mock_db18_data() -> bytes:
    """生成 Mock DB18 数据 (48字节)
    
    数据结构:
    - offset 0-3: 当前料仓重量 (DInt, kg)
    - offset 16-19: 本次排料重量 (DInt, kg)
    - offset 20-23: 排料结束重量 (DInt, kg)
    - offset 24-27: 排料起始重量 (DInt, kg)
    - offset 40-43: 上料上限值 (DInt, kg)
    """
    global _hopper_plc_simulator
    _hopper_plc_simulator.update()
    
    data = bytearray(48)
    
    # 当前料仓重量 (offset 0-3)
    struct.pack_into('>i', data, 0, int(_hopper_plc_simulator.current_weight))
    
    # 本次排料重量 (offset 16-19)
    struct.pack_into('>i', data, 16, int(_hopper_plc_simulator.discharge_weight))
    
    # 排料结束重量 (offset 20-23)
    end_weight = int(_hopper_plc_simulator.current_weight - _hopper_plc_simulator.discharge_weight)
    struct.pack_into('>i', data, 20, end_weight)
    
    # 排料起始重量 (offset 24-27)
    start_weight = int(_hopper_plc_simulator.current_weight)
    struct.pack_into('>i', data, 24, start_weight)
    
    # 上料上限值 (offset 40-43)
    struct.pack_into('>i', data, 40, 4900)
    
    return bytes(data)


def generate_mock_db19_data() -> bytes:
    """生成 Mock DB19 数据 (4字节)
    
    数据结构:
    - offset 2.3: 本次排料重量待读取标志 (Bool)
    """
    global _hopper_plc_simulator
    
    data = bytearray(4)
    
    # offset 2.3: 本次排料重量待读取标志
    if _hopper_plc_simulator.discharge_weight_ready:
        data[2] |= (1 << 3)  # 设置 bit 3
        # 模拟读取后自动复位
        _hopper_plc_simulator.reset_discharge_flag()
    
    return bytes(data)


def generate_mock_q_data() -> bytes:
    """生成 Mock Q区数据 (2字节: Q3, Q4)
    
    数据结构:
    - Q3.7: 秤排料信号
    - Q4.0: 秤要料信号
    """
    global _hopper_plc_simulator
    
    data = bytearray(2)
    
    # Q3.7: 秤排料
    if _hopper_plc_simulator.is_discharging:
        data[0] |= (1 << 7)
    
    # Q4.0: 秤要料
    if _hopper_plc_simulator.is_requesting:
        data[1] |= (1 << 0)
    
    return bytes(data)


def generate_mock_i_data() -> bytes:
    """生成 Mock I区数据 (1字节: I4)
    
    数据结构:
    - I4.6: 供料反馈信号
    """
    global _hopper_plc_simulator
    
    data = bytearray(1)
    
    # I4.6: 供料反馈
    if _hopper_plc_simulator.is_feeding_back:
        data[0] |= (1 << 6)
    
    return bytes(data)


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
    """生成 Mock DB1 弧流弧压数据 (185字节)
    
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
    - offset 182-184: 紧急停电弧流设置
      - 182-183: 弧流上限 (INT, A)
      - 184: 紧急停电标志和启用位 (BYTE)
    """
    data = bytearray(185)
    
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
    
    # ========================================
    # 高压紧急停电弧流设置 (offset 182-186)
    # ========================================
    # emergency_stop_arc_limit (offset 182-183, INT, A)
    # 模拟弧流上限值 6000-7000 A
    emergency_arc_limit = random.randint(6000, 7000)
    struct.pack_into('>h', data, 182, emergency_arc_limit)
    
    # emergency_stop_flag (offset 184, bit 0, BOOL)
    # emergency_stop_enabled (offset 184, bit 1, BOOL)
    # 模拟: 80% 概率启用, 20% 概率触发紧急停电
    emergency_byte = 0x00
    if random.random() < 0.8:
        emergency_byte |= 0x02  # bit 1 = 1 (启用)
    if random.random() < 0.2:
        emergency_byte |= 0x01  # bit 0 = 1 (触发紧急停电)
    data[184] = emergency_byte
    
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



