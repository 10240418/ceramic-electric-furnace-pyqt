# DB32 MODBUS数据详解

> **文档版本**: v1.0  
> **创建日期**: 2026-01-31  
> **用途**: DB32 数据采集、解析、计算、存储完整流程说明

---

## 目录

1. [DB32 数据概述](#db32-数据概述)
2. [数据结构详解](#数据结构详解)
3. [解析流程](#解析流程)
4. [计算服务](#计算服务)
5. [数据库存储](#数据库存储)
6. [完整数据流](#完整数据流)

---

## DB32 数据概述

### 基本信息
```yaml
DB块号: DB32
名称: MODBUS_DATA_VALUE
总大小: 21 bytes (offset 0-20)
轮询间隔: 5秒 (空闲) / 0.5秒 (冶炼中)
批量写入: 20次轮询后写入 (10秒)
```

### 数据分类

DB32 包含以下几类数据：

| 分类 | Offset 范围 | 说明 | 前端使用 |
|-----|------------|------|---------|
| **红外测距** | 0-11 | 3个电极深度测量 | 主要使用 |
| **压力计** | 12-15 | 2路冷却水压力 | 主要使用 |
| **流量计** | 16-19 | 2路冷却水流量 | 主要使用 |
| **蝶阀状态** | 20 | 4个蝶阀开关状态 | 主要使用 |

---

## 数据结构详解

### 1. 红外测距（电极深度）

**这是电极深度监测的核心数据！**

```python
# Offset 0-11 (12 bytes)
offset 0-3:   LENTH1  (UDInt, mm)  # 1号电极深度
offset 4-7:   LENTH2  (UDInt, mm)  # 2号电极深度
offset 8-11:  LENTH3  (UDInt, mm)  # 3号电极深度
```

**数据类型**: UDInt (无符号32位整数, 4字节)  
**单位**: mm (毫米)  
**转换**: 原始值 × 1.0 → mm

**示例数据**:
```python
{
    'LENTH1': 1250,  # mm (1.25米)
    'LENTH2': 1280,  # mm (1.28米)
    'LENTH3': 1230,  # mm (1.23米)
}
```

**物理意义**:
- 测量电极插入炉料的深度
- 用于判断电极位置是否合理
- 辅助电极升降控制

### 2. 压力计（冷却水压力）

```python
# Offset 12-15 (4 bytes)
offset 12-13: WATER_PRESS_1  (Int, kPa)  # 前置过滤器进口压力
offset 14-15: WATER_PRESS_2  (Int, kPa)  # 前置过滤器出口压力
```

**数据类型**: Int (有符号16位整数, 2字节)  
**单位**: kPa (千帕)  
**转换**: 原始值 × 0.01 → kPa

**示例数据**:
```python
{
    'WATER_PRESS_1': 350,  # kPa (进口压力)
    'WATER_PRESS_2': 320,  # kPa (出口压力)
}
```

**物理意义**:
- 监测冷却水系统压力
- 进出口压差反映过滤器堵塞情况
- 压力过低触发报警

### 3. 流量计（冷却水流量）

```python
# Offset 16-19 (4 bytes)
offset 16-17: WATER_FLOW_1  (Int, m³/h)  # 炉皮冷却水流量
offset 18-19: WATER_FLOW_2  (Int, m³/h)  # 炉盖冷却水流量
```

**数据类型**: Int (有符号16位整数, 2字节)  
**单位**: m³/h (立方米/小时)  
**转换**: 原始值 × 1.0 → m³/h

**示例数据**:
```python
{
    'WATER_FLOW_1': 45,  # m³/h (炉皮侧)
    'WATER_FLOW_2': 38,  # m³/h (炉盖侧)
}
```

**物理意义**:
- 监测冷却水流量
- 流量过低触发报警
- 保护炉体和炉盖

### 4. 蝶阀状态监测

```python
# Offset 20 (1 byte)
offset 20: ValveStatus  (Byte)  # 4个蝶阀状态
```

**数据类型**: Byte (1字节, 8位)  
**编码方式**: 每2个bit对应一个蝶阀的开关状态

**Bit 分配**:
```
Bit 7-6: 蝶阀4 (bit7=开, bit6=关)
Bit 5-4: 蝶阀3 (bit5=开, bit4=关)
Bit 3-2: 蝶阀2 (bit3=开, bit2=关)
Bit 1-0: 蝶阀1 (bit1=开, bit0=关)
```

**状态解析**:
```python
# 示例: 0b01010110 = 0x56 = 86
# Valve 1: bit0=0, bit1=1 → 开启
# Valve 2: bit2=1, bit3=1 → 异常 (同时开关)
# Valve 3: bit4=1, bit5=0 → 关闭
# Valve 4: bit6=1, bit7=0 → 关闭

{
    'valve_1_status': 'open',      # bit1=1
    'valve_2_status': 'error',     # bit2=1 and bit3=1
    'valve_3_status': 'closed',    # bit4=1
    'valve_4_status': 'closed',    # bit6=1
}
```

**状态判断逻辑**:
```python
def parse_valve_status(byte_value: int) -> dict:
    result = {}
    for i in range(4):  # 4个蝶阀
        bit_close = (byte_value >> (i * 2)) & 1      # 关闭位
        bit_open = (byte_value >> (i * 2 + 1)) & 1   # 开启位
        
        if bit_open and not bit_close:
            status = 'open'
        elif bit_close and not bit_open:
            status = 'closed'
        elif bit_open and bit_close:
            status = 'error'  # 异常：同时开关
        else:
            status = 'unknown'  # 未知：都为0
        
        result[f'valve_{i+1}_status'] = status
    
    return result
```

---

## 解析流程

### 1. 原始数据读取

```python
# 文件: backend/services/polling_loops_v2.py

# Mock 模式
if is_mock:
    db32_data = generate_mock_db32_data()  # 生成 21 bytes

# PLC 模式
else:
    plc = get_plc_manager()
    db32_data, err = plc.read_db(32, 0, 21)  # 读取 DB32, 21 bytes
```

### 2. 数据解析

```python
# 文件: backend/plc/parser_config_db32.py

parser = ConfigDrivenDB32Parser()
parsed = parser.parse(db32_data)

# 解析结果
{
    'timestamp': '2026-01-31T10:00:00',
    'db_number': 32,
    'db_name': 'MODBUS_DATA_VALUE',
    
    # 所有字段的原始值
    'all_fields': {
        'LENTH1': {'value': 1250, 'type': 'UDInt', 'offset': 0, 'unit': 'mm'},
        'LENTH2': {'value': 1280, 'type': 'UDInt', 'offset': 4, 'unit': 'mm'},
        'LENTH3': {'value': 1230, 'type': 'UDInt', 'offset': 8, 'unit': 'mm'},
        'WATER_PRESS_1': {'value': 350, 'type': 'Int', 'offset': 12, 'unit': 'kPa'},
        'WATER_PRESS_2': {'value': 320, 'type': 'Int', 'offset': 14, 'unit': 'kPa'},
        'WATER_FLOW_1': {'value': 45, 'type': 'Int', 'offset': 16, 'unit': 'm³/h'},
        'WATER_FLOW_2': {'value': 38, 'type': 'Int', 'offset': 18, 'unit': 'm³/h'},
        'ValveStatus': {'value': 86, 'type': 'Byte', 'offset': 20, 'unit': ''},
    },
    
    # 按分组
    'infrared_distance': {
        'LENTH1': 1250,
        'LENTH2': 1280,
        'LENTH3': 1230,
    },
    'pressure_sensors': {
        'WATER_PRESS_1': 350,
        'WATER_PRESS_2': 320,
    },
    'flow_sensors': {
        'WATER_FLOW_1': 45,
        'WATER_FLOW_2': 38,
    },
    'valve_status': {
        'ValveStatus': 86,
        'valve_1_status': 'open',
        'valve_2_status': 'error',
        'valve_3_status': 'closed',
        'valve_4_status': 'closed',
    },
}
```

### 3. 简化转换

```python
# 文件: backend/tools/converter_db32_simple.py

modbus_data_obj = convert_db32_modbus_data_simple(parsed)

# 转换结果
ModbusDataSimple(
    electrode_depths=[1250, 1280, 1230],  # mm
    water_pressures=[350, 320],           # kPa
    water_flows=[45, 38],                 # m³/h
    valve_statuses=['open', 'error', 'closed', 'closed'],
    timestamp=datetime.now(timezone.utc)
)
```

---

## 计算服务

DB32 的计算服务主要包括：

### 1. 冷却水累计用量计算

```python
# 文件: backend/services/cooling_water_calculator.py

# 使用梯形积分法计算累计用量
water_consumption = CoolingWaterCalculator.calculate_water_consumption()

# 计算结果
{
    'furnace_water_total': 125.5,  # m³ (炉皮侧累计用量)
    'cover_water_total': 98.3,     # m³ (炉盖侧累计用量)
    'calc_duration': 15.0,         # 秒 (计算周期)
    'data_points': 30,             # 使用的数据点数
}

# 梯形积分法
# 炉皮侧: ∫ WATER_FLOW_1 dt
# 炉盖侧: ∫ WATER_FLOW_2 dt
```

### 2. 蝶阀开合度计算

```python
# 文件: backend/services/valve_calculator_service.py

# 根据蝶阀状态和配置计算开合度
valve_opening = ValveCalculatorService.calculate_valve_opening(
    valve_id=1,
    valve_status='open'
)

# 计算结果
{
    'valve_1_opening': 100.0,  # % (完全开启)
    'valve_2_opening': 0.0,    # % (完全关闭)
    'valve_3_opening': 50.0,   # % (半开)
    'valve_4_opening': -1.0,   # 异常状态
}
```

**详细计算逻辑请参考**:
- `backend/services/cooling_water_calculator.py` - 冷却水累计用量计算
- `backend/services/valve_calculator_service.py` - 蝶阀开合度计算
- `backend/services/valve_config_service.py` - 蝶阀配置管理

---

## 数据库存储

### 1. 存储的数据点

#### 1.1 电极深度数据（每次都写）

```python
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: electrode_depth
#   - device_id: electrode
#   - batch_code: 03260131
# Fields:
{
    'electrode_depth_1': 1250,     # mm
    'electrode_depth_2': 1280,     # mm
    'electrode_depth_3': 1230,     # mm
}
```

#### 1.2 冷却水压力数据（每次都写）

```python
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: cooling_pressure
#   - device_id: cooling_system
#   - batch_code: 03260131
# Fields:
{
    'water_pressure_inlet': 350,   # kPa
    'water_pressure_outlet': 320,  # kPa
    'pressure_diff': 30,           # kPa (计算得出)
}
```

#### 1.3 冷却水流量数据（每次都写）

```python
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: cooling_flow
#   - device_id: cooling_system
#   - batch_code: 03260131
# Fields:
{
    'water_flow_furnace': 45,      # m³/h (瞬时流量)
    'water_flow_cover': 38,        # m³/h (瞬时流量)
}
```

#### 1.4 冷却水累计用量（每15秒写一次）

```python
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: water_consumption
#   - device_id: cooling_system
#   - batch_code: 03260131
# Fields:
{
    'furnace_water_total': 125.5,  # m³ (炉皮侧累计)
    'cover_water_total': 98.3,     # m³ (炉盖侧累计)
}
```

#### 1.5 蝶阀开合度数据（每次都写）

```python
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: valve_opening
#   - device_id: valve_system
#   - batch_code: 03260131
# Fields:
{
    'valve_1_opening': 100.0,      # % (开合度)
    'valve_2_opening': 0.0,        # % (开合度)
    'valve_3_opening': 50.0,       # % (开合度)
    'valve_4_opening': 100.0,      # % (开合度)
}
```

### 2. 写入策略

```python
# 批量写入逻辑
_modbus_buffer_count += 1
if _modbus_buffer_count >= _modbus_batch_size:  # 20次
    await flush_modbus_buffer()
    _modbus_buffer_count = 0

# 写入条件
if batch_service.is_smelting and batch_code:
    # 只有冶炼中（running 或 paused）才写数据库
    write_to_influxdb(data)
else:
    # 跳过写入，清空缓存
    skip_write()
```

### 3. 数据库查询示例

```flux
// 查询电极深度数据
from(bucket: "electric_furnace")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "03260131")
    |> filter(fn: (r) => r["module_type"] == "electrode_depth")
    |> filter(fn: (r) => 
        r["_field"] == "electrode_depth_1" or 
        r["_field"] == "electrode_depth_2" or
        r["_field"] == "electrode_depth_3"
    )

// 查询冷却水压力数据
from(bucket: "electric_furnace")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "03260131")
    |> filter(fn: (r) => r["module_type"] == "cooling_pressure")
    |> filter(fn: (r) => 
        r["_field"] == "water_pressure_inlet" or 
        r["_field"] == "water_pressure_outlet" or
        r["_field"] == "pressure_diff"
    )

// 查询冷却水累计用量
from(bucket: "electric_furnace")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "03260131")
    |> filter(fn: (r) => r["module_type"] == "water_consumption")
    |> filter(fn: (r) => 
        r["_field"] == "furnace_water_total" or 
        r["_field"] == "cover_water_total"
    )
    |> last()

// 查询蝶阀开合度
from(bucket: "electric_furnace")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "03260131")
    |> filter(fn: (r) => r["module_type"] == "valve_opening")
```

---

## 完整数据流

### 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    DB32 数据采集流程                          │
└─────────────────────────────────────────────────────────────┘

1. 轮询读取 (0.5s/5s)
   ↓
   PLC DB32 (21 bytes)
   ↓
2. 数据解析
   ↓
   ConfigDrivenDB32Parser.parse()
   ↓
   parsed = {
       'infrared_distance': {...},
       'pressure_sensors': {...},
       'flow_sensors': {...},
       'valve_status': {...}
   }
   ↓
3. 简化转换
   ↓
   convert_db32_modbus_data_simple()
   ↓
   modbus_data_obj = ModbusDataSimple(...)
   ↓
4. 计算服务
   ↓
   ├─ 计算压差
   │  └─ pressure_diff = WATER_PRESS_1 - WATER_PRESS_2
   │
   ├─ CoolingWaterCalculator.calculate_water_consumption()
   │  └─ water_consumption = {
   │      'furnace_water_total': 125.5,  # m³
   │      'cover_water_total': 98.3       # m³
   │  }
   │
   └─ ValveCalculatorService.calculate_valve_opening()
      └─ valve_opening = {
          'valve_1_opening': 100.0,  # %
          'valve_2_opening': 0.0,    # %
          'valve_3_opening': 50.0,   # %
          'valve_4_opening': 100.0   # %
      }
   ↓
5. 缓存更新
   ↓
   _latest_modbus_data = {...}
   data_cache.set_modbus_data(...)
   data_bridge.emit_modbus_data(...)
   ↓
6. 批量写入缓存
   ↓
   _modbus_buffer.append(point_dict)
   ↓
7. 批量写入 InfluxDB (20次/10秒)
   ↓
   flush_modbus_buffer()
   ↓
   InfluxDB
```

### 代码调用链

```python
# 1. 轮询循环
_db32_modbus_polling_loop()
    ↓
# 2. 读取数据
generate_mock_db32_data() / plc.read_db(32, 0, 21)
    ↓
# 3. 处理数据
process_modbus_data(raw_data, batch_code)
    ↓
# 4. 解析
_db32_parser.parse_all(raw_data)
    ↓
# 5. 转换
convert_db32_modbus_data_simple(parsed)
    ↓
# 6. 计算服务
# 计算压差
pressure_diff = WATER_PRESS_1 - WATER_PRESS_2
# 计算冷却水累计用量 (每15秒)
CoolingWaterCalculator.calculate_water_consumption()
# 计算蝶阀开合度
ValveCalculatorService.calculate_valve_opening(...)
    ↓
# 7. 缓存更新
_latest_modbus_data = modbus_cache
data_cache.set_modbus_data(modbus_cache)
data_bridge.emit_modbus_data(modbus_cache)
    ↓
# 8. 添加到批量写入缓存
_modbus_buffer.append(point_dict)
    ↓
# 9. 批量写入 (20次)
flush_modbus_buffer()
```

---

## 涉及的所有数据点总结

### 前端实际使用的数据（来自 offset 0-20）

| 数据点 | Offset | 类型 | 单位 | 说明 | 写入频率 |
|-------|--------|------|------|------|---------|
| **LENTH1** | 0-3 | UDInt | mm | 1号电极深度 | 批量写入（15秒） |
| **LENTH2** | 4-7 | UDInt | mm | 2号电极深度 | 批量写入（15秒） |
| **LENTH3** | 8-11 | UDInt | mm | 3号电极深度 | 批量写入（15秒） |
| **WATER_PRESS_1** | 12-13 | Int | kPa | 进口压力 | 批量写入（15秒） |
| **WATER_PRESS_2** | 14-15 | Int | kPa | 出口压力 | 批量写入（15秒） |
| **WATER_FLOW_1** | 16-17 | Int | m³/h | 炉皮流量 | 批量写入（15秒） |
| **WATER_FLOW_2** | 18-19 | Int | m³/h | 炉盖流量 | 批量写入（15秒） |
| **ValveStatus** | 20 | Byte | - | 蝶阀状态（原始） | ❌ 不写入 |

### 计算生成的数据

| 数据点 | 计算方式 | 单位 | 说明 | 写入频率 |
|-------|---------|------|------|---------|
| **pressure_diff** | P1-P2 | kPa | 压差 | 批量写入（15秒） |
| **furnace_water_total** | 梯形积分 | m³ | 炉皮累计用量 | 批量写入（15秒） |
| **cover_water_total** | 梯形积分 | m³ | 炉盖累计用量 | 批量写入（15秒） |
| **valve_1_opening** | 状态转换 | % | 蝶阀1开合度 | 批量写入（15秒） |
| **valve_2_opening** | 状态转换 | % | 蝶阀2开合度 | 批量写入（15秒） |
| **valve_3_opening** | 状态转换 | % | 蝶阀3开合度 | 批量写入（15秒） |
| **valve_4_opening** | 状态转换 | % | 蝶阀4开合度 | 批量写入（15秒） |

**写入说明**：
- 轮询间隔：0.5秒（每秒2次）
- 批量写入：30次轮询后写入（0.5s × 30 = 15秒）
- 写入条件：冶炼状态（running/paused）且有批次号
- 蝶阀原始状态（00/01/10）不写入数据库，只用于计算开合度

---

## 数据完整性检查

### 必须存在的数据

```python
# 每次轮询必须有的数据
required_fields = [
    'LENTH1',
    'LENTH2',
    'LENTH3',
    'WATER_PRESS_1',
    'WATER_PRESS_2',
    'WATER_FLOW_1',
    'WATER_FLOW_2',
    'ValveStatus',
]
```

### 数据验证

```python
# 电极深度范围: 0-3000 mm
assert 0 <= LENTH1 <= 3000

# 压力范围: 0-1000 kPa
assert 0 <= WATER_PRESS_1 <= 1000

# 流量范围: 0-200 m³/h
assert 0 <= WATER_FLOW_1 <= 200

# 蝶阀状态: 0-255
assert 0 <= ValveStatus <= 255

# 蝶阀开合度: 0-100%
assert 0 <= valve_opening <= 100
```

---

## 报警规则

报警规则由专门的报警服务处理，具体规则请参考：
- `backend/core/alarm_storage.py` - 报警存储服务
- `backend/services/alarm_checker.py` - 报警检查服务（如果存在）

常见报警类型：
- 电极深度异常
- 冷却水压力过低
- 冷却水流量过低
- 蝶阀状态异常

---

**大王，DB32 数据详解文档已完成！这份文档详细说明了 DB32 涉及的所有数据点、解析流程、计算逻辑和存储策略。**

