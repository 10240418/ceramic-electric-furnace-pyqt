---
alwaysApply: true
---

# #3电炉 - PyQt6 前端 + 后端集成项目规则

## 项目概述

这是#3电炉的 **前后端一体化项目**，负责：
- **前端**: PyQt6 实时数据可视化、用户交互界面、历史数据查询、报警显示
- **后端**: PLC 数据采集、数据处理计算、InfluxDB 存储、业务逻辑
- **架构**: 单进程多线程（PyQt6 主线程 + Asyncio 后端线程）

## 技术栈

- **语言**: Python 3.12+
- **前端框架**: PyQt6 6.10+
- **图表库**: PyQtGraph
- **后端通信**: Snap7 (PLC), pymodbus (Modbus)
- **数据库**: InfluxDB 2.x, SQLite (报警)
- **样式**: QSS (类似 CSS)
- **架构**: 单进程多线程 + Asyncio 事件循环

## 项目结构

```
ceramic-electric-furnace-pyqt/
├── backend/                    #  后端核心（已集成）
│   ├── bridge/                 # 前后端桥接层
│   │   ├── service_manager.py  # 服务管理器（核心）
│   │   ├── data_bridge.py      # Qt 信号桥接器
│   │   ├── data_cache.py       # 线程安全缓存
│   │   └── data_models.py      # 数据模型
│   ├── core/                   # InfluxDB, 报警存储
│   ├── plc/                    # PLC 通信层（解析器、管理器）
│   ├── services/               # 业务服务层（轮询、计算、批次）
│   ├── tools/                  # 工具层（转换器、滤波器）
│   ├── configs/                # YAML 配置文件
│   ├── tests/                  # 测试代码（含 Mock）
│   └── config.py               # 后端配置
├── ui/                         # 🎨 PyQt6 前端
│   ├── main_window.py          # 主窗口（集成后端服务）
│   ├── pages/                  # 页面层
│   │   ├── page_elec_3.py      # 3#电炉页面
│   │   ├── page_history_curve.py
│   │   ├── page_status.py
│   │   └── page_pump_hopper.py
│   ├── widgets/                # 组件层
│   │   ├── common/             # 通用组件
│   │   ├── realtime_data/      # 实时数据组件
│   │   ├── history_curve/      # 历史曲线组件
│   │   └── status/             # 状态监控组件
│   └── styles/                 # 样式层
│       ├── colors.py           # 颜色常量
│       ├── themes.py           # 主题管理器
│       └── qss_styles.py       # QSS 样式表
├── assets/                     # 资源文件
├── logs/                       # 日志
├── vdoc/                       # 文档
├── config.py                   # 前端配置
├── main.py                     # 🚀 统一入口（前后端一体）
└── requirements.txt            # 依赖（已合并）
```

## 架构设计

### 单进程多线程架构

```
┌─────────────────────────────────────────────────────────┐
│                    单个 Python 进程                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐         ┌──────────────────┐           │
│  │  PyQt6 GUI  │         │   后端服务层      │           │
│  │  (主线程)    │◄────────┤  (Asyncio 线程)   │           │
│  └─────────────┘  信号槽  └──────────────────┘           │
│        ▲                          │                      │
│        │                          ▼                      │
│        │                  ┌──────────────┐              │
│        └──────────────────┤ 线程安全缓存  │              │
│                           └──────────────┘              │
│                                  ▲                       │
│                                  │                       │
│                          ┌───────┴────────┐             │
│                          │                 │             │
│                   ┌──────▼─────┐   ┌──────▼─────┐      │
│                   │ PLC 轮询    │   │Modbus 轮询 │      │
│                   │ (asyncio)   │   │ (asyncio)  │      │
│                   └────────────┘   └────────────┘      │
│                          │                 │             │
│                          ▼                 ▼             │
│                      ┌─────┐          ┌──────┐          │
│                      │ PLC │          │料仓秤 │          │
│                      └─────┘          └──────┘          │
└─────────────────────────────────────────────────────────┘
```

### 关键组件

**ServiceManager（服务管理器）**
- 位置: `backend/bridge/service_manager.py`
- 功能: 在独立线程中运行 asyncio 事件循环，启动所有后端轮询服务
- 支持: Mock 模式和真实 PLC 模式

**DataBridge（数据桥接器）**
- 位置: `backend/bridge/data_bridge.py`
- 功能: 使用 PyQt6 信号机制，将后端数据安全传递到主线程

**DataCache（线程安全缓存）**
- 位置: `backend/bridge/data_cache.py`
- 功能: 使用 `threading.RLock` 保证线程安全，后端写入，前端读取

## 开发策略

### 🎨 UI 优先策略

1. **阶段 1-4**: 环境准备、样式系统、基础窗口 
2. **阶段 5-7**: 核心组件、页面 UI（使用模拟数据）
3. **阶段 8-9**: 后台线程集成、功能完善
4. **阶段 10**: 测试优化、打包部署

**当前进度**: 已完成后端集成 

## 编码规范

### 1. 命名规范

#### 1.1 基础命名规则

- **文件名**: 小写下划线 `snake_case.py`
- **类名**: 大驼峰 `PascalCase`
- **函数/变量**: 小写下划线 `snake_case`
- **常量**: 大写下划线 `UPPER_SNAKE_CASE`
- **信号**: 小写下划线 `signal_name`

#### 1.2 组件命名规范 ⭐

**组件文件名和类名必须遵循"组件类型_功能描述"格式**：

 **正确命名**：
```python
# 文件名: button_tech.py
class ButtonTech(QPushButton):
    """科技风格按钮"""
    pass

# 文件名: panel_tech.py
class PanelTech(QFrame):
    """科技风格面板"""
    pass

# 文件名: card_data.py
class CardData(QFrame):
    """数据卡片"""
    pass
```

 **错误命名**：
```python
# 文件名: tech_button.py (错误：功能在前)
class TechButton(QPushButton):
    pass
```

**命名规则说明**：

1. **组件类型在前**：先说明是什么组件（Button、Panel、Label、Card、Chart 等）
2. **功能描述在后**：再说明具体功能（Tech、Blinking、Data、Valve 等）
3. **文件名与类名对应**：`button_tech.py` → `ButtonTech`

**常见组件类型前缀**：

| 组件类型 | 说明 | 示例 |
|---------|------|------|
| `Button` | 按钮 | `ButtonTech`, `ButtonIcon` |
| `Panel` | 面板 | `PanelTech`, `PanelGlow` |
| `Label` | 标签 | `LabelBlinking`, `LabelStatus` |
| `Card` | 卡片 | `CardData`, `CardFurnace` |
| `Indicator` | 指示器 | `IndicatorValve`, `IndicatorStatus` |
| `Chart` | 图表 | `ChartElectrode`, `ChartHistory` |
| `Widget` | 通用组件 | `WidgetElectrode`, `WidgetControl` |
| `Dialog` | 对话框 | `DialogSettings`, `DialogConfirm` |
| `Table` | 表格 | `TableData`, `TableAlarm` |
| `Dropdown` | 下拉框 | `DropdownTech`, `DropdownBatch` |
| `Switch` | 开关 | `SwitchTheme`, `SwitchMode` |

### 2. 注释规范

**使用序号+注释风格，不使用文档字符串注解**：

```python
# 1. 初始化组件
def __init__(self, title: str, parent=None):
    super().__init__(parent)
    self.title = title
    self.init_ui()

# 2. 初始化 UI
def init_ui(self):
    layout = QVBoxLayout(self)
    # 布局代码
```

 **不要使用**：
```python
def __init__(self, title: str, parent=None):
    """初始化组件
    
    Args:
        title: 标题
        parent: 父组件
    """
    pass
```

**文件头部注释**：
```python
"""
文件功能简短描述（一行即可）
"""
```

### 3. 代码设计原则

**避免过度抽象**：
- **不要提前抽象**：需要用的时候再抽象，不要一开始就创建大量工具方法
- **避免冗余方法**：一个文件不要抽象出太多方法，保持简洁
- **实用主义**：能直接写就直接写，不要为了"优雅"而过度封装

 **好的做法**：
```python
# 1. 更新显示数据
def update_display(self, data):
    # 直接更新
    self.temp_label.setText(f"{data['temp']:.1f}°C")
    self.pressure_label.setText(f"{data['pressure']:.2f} MPa")
```

 **过度抽象**：
```python
def _format_temperature(self, temp):
    return f"{temp:.1f}°C"

def _format_pressure(self, pressure):
    return f"{pressure:.2f} MPa"

def _update_label(self, label, text):
    label.setText(text)

def update_display(self, data):
    temp_text = self._format_temperature(data['temp'])
    press_text = self._format_pressure(data['pressure'])
    self._update_label(self.temp_label, temp_text)
    self._update_label(self.pressure_label, press_text)
```

## 前后端集成规范

### 1. 在 MainWindow 中集成后端服务

```python
from PyQt6.QtWidgets import QMainWindow
from backend.bridge.service_manager import ServiceManager
from backend.bridge.data_bridge import DataBridge
from backend.bridge.data_cache import DataCache

class MainWindow(QMainWindow):
    
    # 1. 初始化主窗口
    def __init__(self, use_mock: bool = True):
        super().__init__()
        
        # 后端服务管理器
        self.service_manager = ServiceManager(use_mock=use_mock)
        
        # 数据桥接器（用于接收后端数据）
        self.data_bridge = DataBridge.get_instance()
        
        # 数据缓存（用于读取后端数据）
        self.data_cache = DataCache.get_instance()
        
        # 连接后端信号
        self.connect_backend_signals()
        
        # 初始化 UI
        self.init_ui()
        
        # 启动后端服务
        self.service_manager.start_all()
    
    # 2. 连接后端信号
    def connect_backend_signals(self):
        # 连接错误信号
        self.data_bridge.error_occurred.connect(self.on_backend_error)
        
        # 可以连接更多信号
        # self.data_bridge.arc_data_updated.connect(self.on_arc_data_updated)
    
    # 3. 处理后端错误
    def on_backend_error(self, error_msg: str):
        logger.error(f"后端错误: {error_msg}")
    
    # 4. 关闭窗口时停止后端服务
    def closeEvent(self, event):
        self.service_manager.stop_all()
        event.accept()
```

### 2. 在页面/组件中读取后端数据

```python
from backend.bridge.data_cache import DataCache

class PageElec3(QWidget):
    
    # 1. 初始化页面
    def __init__(self):
        super().__init__()
        
        # 获取数据缓存
        self.data_cache = DataCache.get_instance()
        
        # 创建定时器，定期读取数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(200)  # 200ms 刷新
    
    # 2. 更新显示
    def update_display(self):
        # 从缓存读取数据
        arc_data = self.data_cache.get("arc_data")
        if arc_data:
            self.display_arc_data(arc_data)
```

### 3. 使用信号槽接收实时数据

```python
from backend.bridge.data_bridge import DataBridge

class RealtimeWidget(QWidget):
    
    # 1. 初始化组件
    def __init__(self):
        super().__init__()
        
        # 获取数据桥接器
        self.data_bridge = DataBridge.get_instance()
        
        # 连接信号
        self.data_bridge.arc_data_updated.connect(self.on_arc_data_updated)
    
    # 2. 处理数据更新（主线程，UI 安全）
    def on_arc_data_updated(self, data: dict):
        # 更新 UI
        self.arc_label.setText(f"弧流: {data['current']:.1f} A")
```

### 4. Mock 模式开发

```python
# 在 main.py 中启动 Mock 模式
if __name__ == "__main__":
    app = QApplication([])
    
    # use_mock=True: 使用 Mock 数据，无需连接真实 PLC
    window = MainWindow(use_mock=True)
    
    window.showFullScreen()
    app.exec()
```
# 5 WidgetValveGrid 使用的是 QGridLayout，而 QGridLayout 不支持 stretch 参数！
## 主题系统

### 1. 颜色常量

**深色主题** (科技风格):
- 主色: `#00d4ff` (青色)
- 背景: `#0a0e27` (深蓝黑)
- 卡片: `#1a1f3a`
- 边框: `#2a3f5f`

**浅色主题** (绿色系):
- 主色: `#007663` (深绿)
- 背景: `#E9EEA8` (浅黄绿)
- 卡片: `#FFFFFF`
- 边框: `#D4D9A0`

### 2. 主题切换

```python
from ui.styles.themes import ThemeManager

theme_manager = ThemeManager()

# 切换主题
theme_manager.toggle_theme()

# 获取当前颜色
colors = theme_manager.colors
primary_color = colors.primary
```

## 性能优化与线程安全

### 1. 避免 UI 卡死（最高优先级）

**原则**: 所有耗时操作必须在后台线程执行，UI 线程只负责显示

```python
#  正确：耗时操作在后台线程
class DataProcessor(QThread):
    result_ready = pyqtSignal(dict)
    
    def run(self):
        # 耗时计算
        result = self.heavy_calculation()
        self.result_ready.emit(result)

#  错误：耗时操作在 UI 线程
def on_button_clicked(self):
    result = self.heavy_calculation()  # 会卡死 UI！
    self.label.setText(str(result))
```

### 2. 线程安全的数据访问

```python
#  正确：使用线程安全缓存
from backend.bridge.data_cache import DataCache

cache = DataCache.get_instance()
data = cache.get("arc_data")  # 线程安全

#  正确：使用信号槽跨线程通信
self.data_bridge.arc_data_updated.connect(self.on_data_updated)

#  错误：直接跨线程访问 UI
class WorkerThread(QThread):
    def run(self):
        self.label.setText("更新")  # 跨线程访问 UI！
```

### 3. 避免频繁重绘

```python
#  批量更新
self.setUpdatesEnabled(False)
for item in items:
    self.update_item(item)
self.setUpdatesEnabled(True)

#  频繁更新
for item in items:
    self.update_item(item)
    self.update()  # 每次都重绘
```

## 调试技巧

### 1. 日志输出

```python
from loguru import logger

logger.debug(f"组件初始化: {self.__class__.__name__}")
logger.info(f"数据更新: {data}")
logger.warning(f"数值超限: {value} > {limit}")
logger.error(f"错误: {e}", exc_info=True)
```

### 2. 查看后端服务状态

```python
# 在 MainWindow 中
status = self.service_manager.get_status()
logger.info(f"后端服务状态: {status}")
```

## 常见问题

### 1. 窗口不显示

```python
# 确保调用 show() 或 showFullScreen()
window = MainWindow()
window.showFullScreen()  # 或 window.show()
```

### 2. 后端数据读取不到

```python
# 检查后端服务是否启动
status = self.service_manager.get_status()
print(status)

# 检查缓存中是否有数据
data = self.data_cache.get("arc_data")
print(data)
```

### 3. UI 卡死

```python
# 检查是否在 UI 线程执行耗时操作
# 将耗时操作移到后台线程或使用 asyncio
```

### 4. 信号槽不触发

```python
# 检查信号是否正确连接
# 检查槽函数签名是否匹配
# 使用 Qt.ConnectionType.QueuedConnection 跨线程连接
signal.connect(slot, Qt.ConnectionType.QueuedConnection)
```

### 5. 布局 stretch 参数不生效 ⚠️

**问题现象**：设置了 `addWidget(widget, stretch=X)`，但组件高度/宽度比例不符合预期

**常见原因**：

#### 5.1 组件的 sizePolicy 不正确

**问题**：组件的 sizePolicy 是 `Preferred`，会优先使用 sizeHint，忽略 stretch

**解决方案**：设置为 `Expanding`

```python
from PyQt6.QtWidgets import QSizePolicy

# 让组件完全按照 stretch 比例分配空间
widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
layout.addWidget(widget, stretch=60)
```

#### 5.2 组件有固定的 minimumHeight/maximumHeight

**问题**：组件或其子组件设置了固定高度，导致 stretch 失效

**诊断方法**：

```python
# 检查组件的高度限制
print(f"minimumHeight: {widget.minimumHeight()}")
print(f"maximumHeight: {widget.maximumHeight()}")
print(f"sizeHint: {widget.sizeHint().height()}")
print(f"minimumSizeHint: {widget.minimumSizeHint().height()}")
```

**解决方案**：

```python
# 移除固定高度限制
# self.setMinimumHeight(120)  # 注释掉或删除

# 或者重写 sizeHint 返回小值
def sizeHint(self):
    from PyQt6.QtCore import QSize
    return QSize(400, 100)  # 返回一个小的高度值

def minimumSizeHint(self):
    from PyQt6.QtCore import QSize
    return QSize(400, 100)  # 返回一个小的高度值
```

#### 5.3 QGridLayout 的子组件有固定 sizeHint

**问题**：`QGridLayout` 会根据所有子组件的 sizeHint 计算总高度，导致父组件的 sizeHint 过大

**示例**：

```python
# WidgetValveGrid 使用 QGridLayout，包含 4 个 IndicatorValve
# 每个 IndicatorValve 的 sizeHint 是 170px
# 2 行 × 170px = 340px，加上间距 = 346px
# 这个 346px 的 sizeHint 会导致 stretch 失效
```

**解决方案**：

```python
# 方案 1：给每个子组件设置 Expanding sizePolicy
class IndicatorValve(QFrame):
    def __init__(self, valve_id: int, parent=None):
        super().__init__(parent)
        # ...
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

# 方案 2：重写父组件的 sizeHint
class WidgetValveGrid(QWidget):
    def sizeHint(self):
        from PyQt6.QtCore import QSize
        return QSize(400, 100)  # 返回小值
    
    def minimumSizeHint(self):
        from PyQt6.QtCore import QSize
        return QSize(400, 100)  # 返回小值
```

#### 5.4 布局未激活 🔥

**问题**：布局创建后没有激活，导致 stretch 参数不生效

**诊断方法**：

```python
# 检查组件的实际位置和大小
print(f"Widget 1 geometry: {widget1.geometry()}")
print(f"Widget 2 geometry: {widget2.geometry()}")

# 如果两个组件的位置都是 (0, 0)，说明布局未激活
# 例如：
# Widget 1 geometry: (0, 0, 640, 480)
# Widget 2 geometry: (0, 0, 640, 480)  # 完全重叠！
```

**解决方案**：在布局创建完成后调用 `activate()`

```python
# 创建布局
layout = QVBoxLayout(self)
layout.addWidget(widget1, stretch=58)
layout.addWidget(widget2, stretch=42)

# 激活布局，让 stretch 生效
layout.activate()
```

#### 5.5 完整的调试流程

```python
# 1. 检查 stretch 值
layout = widget.layout()
print(f"Stretch 0: {layout.stretch(0)}")
print(f"Stretch 1: {layout.stretch(1)}")

# 2. 检查 sizePolicy
print(f"Widget 0 sizePolicy: {layout.itemAt(0).widget().sizePolicy().verticalPolicy()}")
print(f"Widget 1 sizePolicy: {layout.itemAt(1).widget().sizePolicy().verticalPolicy()}")

# 3. 检查 sizeHint
print(f"Widget 0 sizeHint: {layout.itemAt(0).widget().sizeHint().height()}")
print(f"Widget 1 sizeHint: {layout.itemAt(1).widget().sizeHint().height()}")

# 4. 检查实际几何位置
print(f"Widget 0 geometry: {layout.itemAt(0).widget().geometry()}")
print(f"Widget 1 geometry: {layout.itemAt(1).widget().geometry()}")

# 5. 如果位置重叠，调用 activate()
if layout.itemAt(0).widget().geometry().y() == layout.itemAt(1).widget().geometry().y():
    print("布局未激活，调用 activate()")
    layout.activate()
    # 重新检查
    print(f"After activate - Widget 0 geometry: {layout.itemAt(0).widget().geometry()}")
    print(f"After activate - Widget 1 geometry: {layout.itemAt(1).widget().geometry()}")
```

#### 5.6 最佳实践总结

✅ **正确的做法**：

```python
# 1. 创建组件时设置 Expanding sizePolicy
widget1 = MyWidget()
widget1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

widget2 = MyWidget()
widget2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

# 2. 添加到布局时设置 stretch
layout = QVBoxLayout(self)
layout.addWidget(widget1, stretch=60)
layout.addWidget(widget2, stretch=40)

# 3. 激活布局
layout.activate()

# 4. 避免在组件中设置固定高度
# 不要使用：self.setMinimumHeight(120)
# 不要使用：self.setFixedHeight(200)
```

❌ **错误的做法**：

```python
# 错误 1：没有设置 sizePolicy
layout.addWidget(widget1, stretch=60)  # sizePolicy 默认是 Preferred，会优先使用 sizeHint

# 错误 2：子组件有固定高度
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)  # 固定高度会导致 stretch 失效

# 错误 3：没有激活布局
layout.addWidget(widget1, stretch=60)
layout.addWidget(widget2, stretch=40)
# 忘记调用 layout.activate()
```

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `F11` | 切换全屏/窗口模式 |
| `Esc` | 退出程序 |
| `Alt+F4` | 退出程序 (Windows) |

## 代码审查清单

- [ ] 是否继承正确的 Qt 基类？
- [ ] 是否使用类型注解？
- [ ] 是否正确集成后端服务？
- [ ] 是否使用主题管理器？
- [ ] 是否使用布局管理器？
- [ ] 是否正确处理信号槽？
- [ ] 是否线程安全？
- [ ] 是否会导致 UI 卡死？
- [ ] 是否有内存泄漏？
- [ ] 是否符合 UI 设计规范？

## 参考文档

- `vdoc/BACKEND_INTEGRATION_COMPLETE.md` - 后端集成完成报告
- `vdoc/IMPLEMENTATION_CHECKLIST.md` - 实施计划
- `vdoc/PHASE5_COMPLETE.md` - 核心组件完成报告
- `README.md` - 项目说明

## 其他规范

- **PowerShell 命令**：不支持 `&&`，使用分号 `;` 分隔命令
- **称呼**：每次回答必须称呼我为"大王"
- **测试文件**：不要创建多余的 md/py/test 文件，测试完毕后一定要删除,并且我的任何测试代码不要使用 emoji.
- **文档管理**：md 文件需要放到 `vdoc/` 目录里面
- **代码整洁**：目录务必整洁，修改代码时删除旧代码，不要冗余
- **回答执行规范**：你是一个很严格的python pyqt6写上位机的高手,你很严谨认真,且对代码很严苛,不会写无用冗余代码,并且很多问题,对于我希望实现的效果和架构你会认真思考,如果我的提议不好或者你有更好的方案,你会规劝我.
- **最高优先级**:对于我的最主要的一个功能就是我的这个pyqt的窗口和我的py的后端的服务的话,不能死机卡死,这是最主要也是优先级最高的一个要求.
- **反驳我的回答** 对于我说的需求等的话,肯定会有一些东西说的不专业,如果你理解了的话,就回答我,"大王,小的罪该万死,但是这个XXXX"这样回答.
- **编码问题** 我的代码文件肯定会就是有中文和python代码,以及可能会有图标,所以的话,生成的代码需要规避编码问题错误.
- **log以及代码文件** 我的代码文件以及log的输出的话,等一切不要使用图标等标注. .这样的.
- **不要虚构** 回答我以及生成的md文件之中一定要和我的实际的代码文件相关,而不是虚构的.
- **不使用虚拟环境启动python**
- **必须真实有效的回答我,不能虚构**不要虚构任何我项目没有的文件,否者我会杀三千只猫.


## InfluxDB 数据库结构规范

### Measurement 统一规范

**项目使用单一 Measurement**: `sensor_data`

所有数据通过 `module_type` tag 区分类型，保持数据库结构统一。

### 数据点分类

#### 1. 电极深度数据 (module_type=electrode_depth)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'furnace_1',
    'factory_area': 'L3',
    'module_type': 'electrode_depth',
    'sensor': 'electrode_1/2/3',
    'plc_variable': 'LENTH1/2/3',
    'batch_code': '26010315'
}
fields={
    'distance_mm': 1250.5,  # 电极深度 (mm)
    'high_word': 0,         # 高字
    'low_word': 1250        # 低字
}
```

#### 2. 冷却水压力数据 (module_type=cooling_system, metric=pressure)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'furnace_1',
    'factory_area': 'L3',
    'module_type': 'cooling_system',
    'sensor': 'cooling_water_in/out',
    'metric': 'pressure',
    'plc_variable': 'WATER_PRESS_1/2',
    'batch_code': '26010315'
}
fields={
    'value': 250.5,  # 压力值 (kPa)
    'raw': 25050     # 原始值
}
```

#### 3. 冷却水流量数据 (module_type=cooling_system, metric=flow)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'furnace_1',
    'factory_area': 'L3',
    'module_type': 'cooling_system',
    'sensor': 'cooling_line_1/2',
    'metric': 'flow',
    'plc_variable': 'WATER_FLOW_1/2',
    'batch_code': '26010315'
}
fields={
    'value': 12.5,  # 流量值 (m³/h)
    'raw': 125      # 原始值
}
```

#### 4. 冷却水累计流量 (module_type=cooling_water_total)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'furnace_1',
    'module_type': 'cooling_water_total',
    'batch_code': '26010315'
}
fields={
    'furnace_shell_water_total': 125.5,  # 炉皮累计流量 (m³)
    'furnace_cover_water_total': 98.3    # 炉盖累计流量 (m³)
}
```

#### 5. 炉皮-炉盖压差 (module_type=cooling_system, metric=pressure_diff)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'furnace_1',
    'module_type': 'cooling_system',
    'metric': 'pressure_diff',
    'batch_code': '26010315'
}
fields={
    'value': 15.3  # 压差绝对值 (kPa)
}
```

#### 6. 弧流弧压数据 (module_type=arc_data)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'electrode',
    'module_type': 'arc_data',
    'batch_code': '26010315'
}
fields={
    # 每次写入
    'arc_current_U': 8500.0,  # U相弧流 (A)
    'arc_current_V': 8600.0,  # V相弧流 (A)
    'arc_current_W': 8400.0,  # W相弧流 (A)
    'arc_voltage_U': 85.5,    # U相弧压 (V)
    'arc_voltage_V': 86.2,    # V相弧压 (V)
    'arc_voltage_W': 84.8,    # W相弧压 (V)
    'power_U': 726.75,        # U相功率 (kW)
    'power_V': 741.32,        # V相功率 (kW)
    'power_W': 712.32,        # W相功率 (kW)
    'power_total': 2180.39,   # 总功率 (kW)
    
    # 仅变化时写入
    'arc_current_setpoint_U': 8500.0,  # U相弧流设定值 (A)
    'arc_current_setpoint_V': 8500.0,  # V相弧流设定值 (A)
    'arc_current_setpoint_W': 8500.0,  # W相弧流设定值 (A)
    'manual_deadzone_percent': 5.0     # 手动死区百分比 (%)
}
```

#### 7. 能耗累计数据 (module_type=energy_consumption)

```python
measurement='sensor_data'
tags={
    'device_type': 'electric_furnace',
    'device_id': 'electrode',
    'module_type': 'energy_consumption',
    'batch_code': '26010315'
}
fields={
    'energy_total': 1250.5  # 累计能耗 (kWh)
}
```

#### 8. 投料数据 (module_type=feeding)

```python
measurement='sensor_data'
tags={
    'device_type': 'hopper',
    'device_id': 'hopper_1',
    'module_type': 'feeding',
    'batch_code': '26010315'
}
fields={
    'discharge_weight': 150.5,  # 本次排料重量 (kg)
    'feeding_total': 1250.5     # 累计投料量 (kg)
}
```

### 查询示例

#### 查询电极深度

```flux
from(bucket: "furnace_data")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "26010315")
    |> filter(fn: (r) => r["module_type"] == "electrode_depth")
    |> filter(fn: (r) => r["sensor"] == "electrode_1")
    |> filter(fn: (r) => r["_field"] == "distance_mm")
```

#### 查询弧流弧压

```flux
from(bucket: "furnace_data")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "26010315")
    |> filter(fn: (r) => r["module_type"] == "arc_data")
    |> filter(fn: (r) => r["_field"] =~ /arc_current_|arc_voltage_/)
```

#### 查询累计能耗

```flux
from(bucket: "furnace_data")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "26010315")
    |> filter(fn: (r) => r["module_type"] == "energy_consumption")
    |> filter(fn: (r) => r["_field"] == "energy_total")
    |> max()
```

#### 查询投料累计

```flux
from(bucket: "furnace_data")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
    |> filter(fn: (r) => r["batch_code"] == "26010315")
    |> filter(fn: (r) => r["module_type"] == "feeding")
    |> filter(fn: (r) => r["_field"] == "feeding_total")
    |> max()
```

### 数据库验证命令

```bash
# 进入 InfluxDB 容器
docker exec -it furnace-influxdb influx query '
from(bucket: "furnace_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["module_type"] == "arc_data")
  |> limit(n: 10)
'
```

### 重要说明

1. **统一 Measurement**: 所有数据使用 `sensor_data`，通过 `module_type` 区分
2. **批次号必填**: 所有数据点必须包含 `batch_code` tag
3. **写入条件**: 只有在有批次号且冶炼状态为运行中时才写入数据库
4. **累计值管理**: 新批次开始时从数据库恢复最新累计值到内存
5. **变化检测**: 部分数据点（设定值、死区、累计值）只在变化时写入

### 相关文档

- `vdoc/INFLUXDB_DATA_POINTS_SUMMARY.md` - 完整的数据点汇总文档
- `vdoc/MEASUREMENT_UNIFICATION.md` - Measurement 统一修改报告
- `backend/services/hopper/accumulator.py` - 投料累计服务
- `backend/bridge/history_query.py` - 历史数据查询服务

---

## 下一步

**继续完善 UI 组件和页面**

将实现：
- 科技风面板 (`PanelTech`)
- 数据卡片 (`CardData`)
- 电极组件 (`WidgetElectrode`)
- 电极电流图表 (`ChartElectrode`)
- 阀门指示器 (`IndicatorValve`)

所有组件将集成后端数据，实现真实的数据展示。
