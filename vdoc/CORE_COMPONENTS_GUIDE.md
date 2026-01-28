# 核心 UI 组件使用指南

## 概述

本文档介绍#3电炉 PyQt6 前端的核心 UI 组件，所有组件都支持主题切换（深色/浅色）。

## 组件列表

### 1. 通用组件 (`ui/widgets/common/`)

#### 1.1 TechButton - 科技风格按钮

**功能**: 提供主要、次要、危险三种风格的按钮。

**使用示例**:

```python
from ui.widgets.common import TechButton, TechButtonSecondary, TechButtonDanger

# 主要按钮
btn_primary = TechButton("确认")
btn_primary.clicked.connect(self.on_confirm)

# 次要按钮（透明背景）
btn_secondary = TechButtonSecondary("取消")
btn_secondary.clicked.connect(self.on_cancel)

# 危险按钮
btn_danger = TechButtonDanger("删除")
btn_danger.clicked.connect(self.on_delete)
```

**特性**:
- ✅ 自动适应主题切换
- ✅ 悬停/按下状态动画
- ✅ 禁用状态样式
- ✅ 发光边框效果

#### 1.2 TechIconButton - 图标按钮

**功能**: 无边框的图标按钮，适用于工具栏。

**使用示例**:

```python
from ui.widgets.common import TechIconButton

icon_btn = TechIconButton("ui/icons/settings.svg", size=24)
icon_btn.clicked.connect(self.open_settings)
```

#### 1.3 TechPanel - 科技风格面板

**功能**: 带标题的卡片面板容器。

**使用示例**:

```python
from ui.widgets.common import TechPanel

panel = TechPanel("实时数据")

# 方式1: 设置布局
layout = QVBoxLayout()
layout.addWidget(widget1)
layout.addWidget(widget2)
panel.set_content_layout(layout)

# 方式2: 添加组件
panel.add_content_widget(widget1)
panel.add_content_widget(widget2)
```

**特性**:
- ✅ 自动适应主题
- ✅ 圆角边框
- ✅ 标题高亮显示

#### 1.4 TechPanelWithGlow - 发光面板

**功能**: 带发光效果的面板，用于强调重要内容。

**使用示例**:

```python
from ui.widgets.common import TechPanelWithGlow

glow_panel = TechPanelWithGlow("报警信息")
glow_panel.set_content_layout(layout)
```

**特性**:
- ✅ 边框发光效果
- ✅ 主题色自适应

#### 1.5 BlinkingLabel - 闪烁文本（开关式）

**功能**: 文本闪烁显示，适用于报警提示。

**使用示例**:

```python
from ui.widgets.common import BlinkingLabel

label = BlinkingLabel("报警！温度过高")
label.set_blinking(True)  # 开启闪烁
label.set_blink_color("#ff3b30")  # 设置闪烁颜色
label.set_normal_color("#e6edf3")  # 设置正常颜色
```

**特性**:
- ✅ 500ms 闪烁间隔
- ✅ 可自定义颜色
- ✅ 可动态开关

#### 1.6 BlinkingTextWidget - 闪烁文本（渐变式）

**功能**: 文本透明度渐变闪烁，更柔和的效果。

**使用示例**:

```python
from ui.widgets.common import BlinkingTextWidget

label = BlinkingTextWidget("警告信息")
label.set_blinking(True)
label.set_blink_color("#ff9500")
```

**特性**:
- ✅ 透明度渐变（0.3 - 1.0）
- ✅ 50ms 更新间隔
- ✅ 更平滑的视觉效果

### 2. 实时数据组件 (`ui/widgets/realtime_data/`)

#### 2.1 DataCard - 数据卡片

**功能**: 展示多行数据，支持报警、阈值、遮罩。

**使用示例**:

```python
from ui.widgets.realtime_data import DataCard, DataItem

# 创建数据项
items = [
    DataItem("温度", "1250.5", "°C", "🌡️"),
    DataItem("压力", "0.85", "MPa", "📊"),
    DataItem("电流", "450.2", "A", "⚡", threshold=500, is_above_threshold=True),
]

# 创建卡片
card = DataCard(items)

# 更新数据
new_items = [
    DataItem("温度", "1580.0", "°C", "🌡️", threshold=1500, is_above_threshold=True),
]
card.update_items(new_items)
```

**DataItem 参数**:
- `label`: 标签文字
- `value`: 数值（字符串）
- `unit`: 单位
- `icon`: 图标（可选，支持 emoji 或字符）
- `threshold`: 阈值（可选）
- `is_above_threshold`: 是否超过阈值报警（默认 False）
- `is_masked`: 是否添加遮罩层（默认 False）

**特性**:
- ✅ 自动报警检测
- ✅ 报警时闪烁显示
- ✅ 报警标签显示
- ✅ 遮罩层支持
- ✅ 主题自适应

#### 2.2 FurnaceDataCard - 电炉数据卡片

**功能**: 带阈值显示的数据卡片，适用于电炉监控。

**使用示例**:

```python
from ui.widgets.realtime_data import FurnaceDataCard, DataItem

items = [
    DataItem("炉温", "1450.5", "°C", "🌡️", threshold=1500, is_above_threshold=True),
    DataItem("炉压", "0.95", "MPa", "📊", threshold=1.0, is_above_threshold=True),
]

card = FurnaceDataCard(items)
```

**特性**:
- ✅ 显示阈值信息
- ✅ 紧凑型布局
- ✅ 报警颜色高亮

#### 2.3 ValveIndicator - 阀门指示器

**功能**: 单个阀门状态指示器，带圆形指示灯。

**使用示例**:

```python
from ui.widgets.realtime_data import ValveIndicator

valve = ValveIndicator("进气阀")
valve.set_open(True)  # 设置为打开状态
valve.set_blinking(True)  # 开启闪烁（报警）
valve.clicked.connect(self.on_valve_clicked)  # 点击事件
```

**特性**:
- ✅ 圆形指示灯
- ✅ 打开/关闭状态
- ✅ 闪烁报警
- ✅ 可点击交互

#### 2.4 ValveControlWidget - 阀门控制组件

**功能**: 多个阀门的控制面板。

**使用示例**:

```python
from ui.widgets.realtime_data import ValveControlWidget

valve_control = ValveControlWidget(["阀门A", "阀门B", "阀门C"])
valve_control.set_valve_state(0, True)  # 设置阀门0为打开
valve_control.set_valve_blinking(2, True)  # 阀门2闪烁
valve_control.valve_clicked.connect(self.on_valve_clicked)  # 点击事件
```

**特性**:
- ✅ 多阀门管理
- ✅ 统一样式
- ✅ 点击事件带索引

### 3. 主题切换组件

#### 3.1 ThemeSwitch - 主题切换开关

**功能**: 深色/浅色主题切换按钮。

**使用示例**:

```python
from ui.widgets.common import ThemeSwitch

theme_switch = ThemeSwitch()
# 自动切换主题，无需额外代码
```

**特性**:
- ✅ 自动切换主题
- ✅ 图标动态变化
- ✅ 全局生效

## 主题系统

### 获取主题管理器

```python
from ui.styles.themes import ThemeManager

theme_manager = ThemeManager.instance()
```

### 监听主题变化

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def on_theme_changed(self):
        self.apply_styles()
```

### 获取颜色

```python
colors = theme_manager.get_colors()

# 使用颜色
bg_color = colors.BG_DEEP
primary_color = colors.GLOW_PRIMARY
text_color = colors.TEXT_PRIMARY
```

### 便捷方法

```python
# 直接获取颜色
bg_deep = theme_manager.bg_deep()
glow_primary = theme_manager.glow_primary()
text_primary = theme_manager.text_primary()
```

## 样式规范

### 边框设计

所有组件统一使用细亮边框：

```python
border: 1px solid {colors.BORDER_DARK};  # 默认
border: 1px solid {colors.GLOW_PRIMARY}; # 激活
border: 1px solid {colors.BORDER_MEDIUM}; # 悬停
```

### 图标设计

图标无边框，只有图标本身：

```python
QLabel {{
    border: none;
    background: transparent;
}}
```

### 状态样式

```python
# 默认
border: 1px solid {colors.BORDER_DARK};
background: {colors.CARD_BG};

# 悬停
border: 1px solid {colors.BORDER_GLOW};
background: {colors.CARD_HOVER_BG};

# 激活
border: 1px solid {colors.GLOW_PRIMARY};
background: {colors.GLOW_PRIMARY}33;  # 20% 透明度
```

## 测试

运行测试文件查看所有组件效果：

```bash
python test_components.py
```

测试窗口包含：
- ✅ 所有按钮样式
- ✅ 数据卡片（正常/报警/遮罩）
- ✅ 阀门指示器
- ✅ 发光面板
- ✅ 闪烁文本
- ✅ 主题切换

## 注意事项

1. **主题切换**: 所有组件都会自动响应主题变化，无需手动刷新
2. **资源清理**: 闪烁组件会自动清理定时器资源
3. **性能**: 闪烁效果使用 QTimer，不会阻塞主线程
4. **颜色**: 使用主题管理器获取颜色，不要硬编码颜色值
5. **布局**: 使用 Qt 布局管理器，不要使用固定位置

## 下一步

- [ ] 创建电极组件 (`ElectrodeWidget`)
- [ ] 创建电极电流图表 (`ElectrodeChart`)
- [ ] 创建历史曲线组件
- [ ] 创建报警记录组件
- [ ] 创建设置页面组件

## 参考

- Flutter 项目: `ceramic-electric-furnace-flutter/lib/widgets/`
- 主题系统: `ui/styles/themes.py`
- 颜色常量: `ui/styles/colors.py`

