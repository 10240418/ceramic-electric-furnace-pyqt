# 前端数据流转完整说明

## 📊 点击"开始冶炼"按钮后的完整数据流

### 1. 前端触发（UI 层）

```
用户点击"开始冶炼"按钮
    ↓
BarBatchInfo.start_smelting_clicked 信号发射
    ↓
PageElec3.on_start_smelting() 接收信号
    ↓
弹出 DialogBatchConfig 对话框
    ↓
用户输入批次号（如：26010315）
    ↓
DialogBatchConfig.batch_confirmed 信号发射
    ↓
PageElec3.on_batch_confirmed(batch_code) 接收批次号
```

### 2. 后端服务启动（业务逻辑层）

```python
# PageElec3.on_batch_confirmed()
result = self.batch_service.start(batch_code)

# BatchService.start()
1. 设置状态: IDLE → RUNNING
2. 保存批次号: "26010315"
3. 记录开始时间: datetime.now()
4. 重置累计器:
   - 冷却水累计流量清零
   - 投料累计清零
5. 持久化状态到文件: data/batch_state.json (断电保护)

# 切换 DB1 轮询速度
switch_db1_speed(high_speed=True)
# DB1 轮询间隔: 5s → 0.5s
```

### 3. 三个独立轮询循环（已在程序启动时自动运行）

#### 3.1 DB1 弧流弧压轮询（0.5s 一次）

```
_db1_arc_polling_loop()
    ↓
每 0.5s 读取 PLC DB1 (182字节)
    ↓
解析数据:
    - 弧流 U/V/W (A)
    - 弧压 U/V/W (V)
    - 设定值 U/V/W (A)
    - 手动死区 (%)
    ↓
计算功率:
    - P_U = U_U × I_U × √3 × cos(φ)
    - P_V = U_V × I_V × √3 × cos(φ)
    - P_W = U_W × I_W × √3 × cos(φ)
    - P_total = P_U + P_V + P_W
    ↓
每 15 秒计算能耗:
    - ΔE = P_avg × Δt / 3600
    - E_total += ΔE
    ↓
更新内存缓存:
    - _latest_arc_data
    ↓
写入 DataCache:
    - data_cache.set_arc_data(arc_data)
    ↓
发送信号到前端:
    - data_bridge.emit_arc_data(arc_data)
    ↓
批量写入 InfluxDB:
    - 每 20 次轮询写入一次 (10秒)
    - 只有在冶炼状态 (is_smelting=True) 时才写入
```

#### 3.2 DB32 传感器轮询（0.5s 一次）

```
_db32_sensor_polling_loop()
    ↓
每 0.5s 读取 PLC DB32 (29字节)
    ↓
解析数据:
    - 电极深度 1/2/3 (mm)
    - 冷却水压力 1/2 (kPa)
    - 冷却水流量 1/2 (m³/h)
    - 蝶阀状态字节
    ↓
每 0.5s 读取料仓重量 (Modbus RTU)
    ↓
读取 PLC 投料信号:
    - %Q3.7 秤排料信号 (is_discharging)
    - %Q4.0 秤要料信号 (is_requesting)
    ↓
计算冷却水累计流量 (每 15 秒):
    - V_cover += Q_cover × Δt / 3600
    - V_shell += Q_shell × Δt / 3600
    - 压差 = |P_shell - P_cover|
    ↓
计算投料累计 (每 30 秒):
    - ΔW = W_before - W_after (检测到投料信号时)
    - F_total += ΔW
    ↓
计算蝶阀开度 (滑动窗口 100 次):
    - 开度 = (开状态次数 / 总次数) × 100%
    - 自动校准: 连续 100 次同状态 → 更新基准
    ↓
更新内存缓存:
    - _latest_modbus_data
    - _latest_weight_data
    ↓
写入 DataCache:
    - data_cache.set_sensor_data(sensor_data)
    ↓
发送信号到前端:
    - data_bridge.emit_sensor_data(sensor_data)
    ↓
批量写入 InfluxDB:
    - 每 30 次轮询写入一次 (15秒)
    - 只有在冶炼状态 (is_smelting=True) 时才写入
```

#### 3.3 DB30/DB41 状态轮询（5s 一次）

```
_status_polling_loop()
    ↓
每 5s 读取 PLC DB30 (40字节) + DB41 (28字节)
    ↓
解析数据:
    - DB30: 通信状态
    - DB41: 数据有效性状态
    ↓
更新内存缓存:
    - _latest_status_data
    - _latest_db41_data
    ↓
发送连接状态到前端:
    - data_bridge.emit_connection_status(plc_connected)
    ↓
不写入 InfluxDB (仅内存缓存)
```

### 4. 前端数据刷新（UI 层）

#### 4.1 定时器刷新（每 0.5s）

```python
# PageElec3.__init__()
self.update_timer = QTimer()
self.update_timer.timeout.connect(self.update_realtime_data)
self.update_timer.start(500)  # 500ms = 0.5s

# PageElec3.update_realtime_data()
每 0.5s 从 DataCache 读取数据并更新 UI:

1. 蝶阀开度和状态
   - sensor_data['valve_openness']
   - sensor_data['valve_status']
   → WidgetValveGrid.update_all_valves()

2. 三相电极电流、电压
   - arc_data['arc_current']['U/V/W']
   - arc_data['arc_voltage']['U/V/W']
   → PanelFurnaceBg.update_all_electrodes()

3. 电极深度
   - sensor_data['electrode_depths']['LENTH1/2/3']
   → PanelFurnaceBg.update_all_electrodes()

4. 电极电流图表
   - arc_data['arc_current']['U/V/W']
   - arc_data['setpoints']['U/V/W']
   - arc_data['manual_deadzone_percent']
   → ChartElectrode.update_data()

5. 冷却水数据
   - sensor_data['cooling']['flows']
   - sensor_data['cooling']['pressures']
   - sensor_data['cooling']['pressure_diff']  # 过滤器压差
   - sensor_data['cooling']['cover_total']
   - sensor_data['cooling']['shell_total']
   → CardData.update_items()

6. 料仓数据
   - sensor_data['hopper']['weight']
   - sensor_data['hopper']['feeding_total']
   - sensor_data['hopper']['is_discharging']
   → CardData.update_items()

7. 功率能耗
   - arc_data['power_total']
   - (能耗数据待后端提供接口)
   → PanelFurnaceBg.update_power_energy()

8. 批次运行时长
   - batch_service.get_status()['elapsed_seconds']
   → BarBatchInfo.set_smelting_state()
```

#### 4.2 信号槽刷新（实时）

```python
# 可选：使用信号槽接收实时数据
data_bridge.arc_data_updated.connect(self.on_arc_data_updated)
data_bridge.sensor_data_updated.connect(self.on_sensor_data_updated)

# 优点：数据更新立即触发 UI 刷新
# 缺点：频繁触发可能影响性能
# 当前方案：使用定时器统一刷新（更稳定）
```

### 5. 数据存储（InfluxDB）

#### 5.1 批量写入策略

```
DB1 弧流弧压:
    - 轮询间隔: 0.5s
    - 批量大小: 20 次
    - 写入间隔: 10 秒
    - 数据点: 弧流(3) + 弧压(3) + 功率(4) + 设定值(3,变化时) + 死区(1,变化时)

DB32 传感器:
    - 轮询间隔: 0.5s
    - 批量大小: 30 次
    - 写入间隔: 15 秒
    - 数据点: 电极深度(3) + 冷却水压力(2) + 冷却水流量(2) + 冷却水累计(2) + 压差(1)

料仓重量:
    - 轮询间隔: 0.5s
    - 批量大小: 30 次
    - 写入间隔: 15 秒
    - 数据点: 净重(1) + 投料累计(1)

能耗数据:
    - 计算间隔: 15 秒
    - 写入方式: 计算完成后立即写入
    - 数据点: 累计能耗(1)
```

#### 5.2 写入条件

```python
# 只有在冶炼状态时才写入数据库
if batch_service.is_smelting and batch_code:
    write_to_influxdb(data)
else:
    skip_write()  # 清空缓存但不写入
```

### 6. 断电恢复机制

```
程序启动时:
    ↓
BatchService.__init__()
    ↓
读取 data/batch_state.json
    ↓
如果之前是 running 或 paused:
    ↓
自动恢复为 running 状态
    ↓
继续写入数据到 InfluxDB
    ↓
前端显示批次信息和运行时长
```

## 📝 关键数据结构

### DataCache 缓存结构

```python
{
    'arc_data': {
        'arc_current': {'U': 3000.0, 'V': 3050.0, 'W': 2950.0},
        'arc_voltage': {'U': 145.0, 'V': 148.0, 'W': 142.0},
        'power_total': 1850.5,
        'setpoints': {'U': 2800.0, 'V': 2850.0, 'W': 2750.0},
        'manual_deadzone_percent': 15.0,
        'timestamp': 1706789123.456
    },
    'sensor_data': {
        'electrode_depths': {
            'LENTH1': {'distance_mm': -150.0},
            'LENTH2': {'distance_mm': -150.0},
            'LENTH3': {'distance_mm': -150.0}
        },
        'cooling': {
            'flows': {
                'WATER_FLOW_1': {'flow': 3.5},
                'WATER_FLOW_2': {'flow': 2.8}
            },
            'pressures': {
                'WATER_PRESS_1': {'pressure': 180.0},
                'WATER_PRESS_2': {'pressure': 165.0}
            },
            'pressure_diff': {'value': 15.0},  # 过滤器压差
            'cover_total': 98.3,
            'shell_total': 125.5
        },
        'hopper': {
            'weight': 1250.0,
            'feeding_total': 3580.0,
            'is_discharging': False,
            'is_requesting': False
        },
        'valve_status': {'raw_byte': 0b01100110},
        'valve_openness': {1: 75.0, 2: 50.0, 3: 25.0, 4: 90.0},
        'timestamp': 1706789123.456
    },
    'batch_status': {
        'is_smelting': True,
        'batch_code': '26010315',
        'start_time': '2026-01-03 15:30:00',
        'elapsed_time': 3600.0
    }
}
```

## 🎯 总结

### 料仓重量轮询

✅ **已存在**！在 `_db32_sensor_polling_loop` 中每 0.5s 读取一次：
- 读取 Modbus RTU 料仓重量
- 读取 PLC 投料信号 (%Q3.7, %Q4.0)
- 每 30 秒计算投料累计
- 写入 DataCache 和 InfluxDB

### DB1 轮询速度

✅ **已修改**！开始冶炼后：
- 5s → 0.5s（而不是 0.2s）
- 每 20 次轮询写入一次（10 秒）

### 前端刷新策略

✅ **已实现**！每 0.5s 刷新：
1. 蝶阀开度和状态
2. 三相电极电流、电压
3. 电极深度
4. 冷却水流量、水压、累计流量
5. **过滤器压差**（新增）
6. 料仓重量、投料累计
7. 功率、能耗
8. 批次运行时长

### 过滤器压差

✅ **已添加**！在炉盖冷却水面板：
- 位置：第一行（在冷却水流速上方）
- 数据来源：`sensor_data['cooling']['pressure_diff']`
- 计算方式：`|炉皮压力 - 炉盖压力|`
- 单位：kPa

