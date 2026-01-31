# 组件命名重构完成报告

## 📋 重构概述

按照新的命名规范"组件类型_功能描述"，对所有 PyQt6 组件进行了重命名。

**重构时间**: 2026-01-28  
**重构范围**: 所有 UI 组件

##  重构内容

### 1. 通用组件 (ui/widgets/common/)

| 旧文件名 | 新文件名 | 旧类名 | 新类名 |
|---------|---------|--------|--------|
| `tech_panel.py` | `panel_tech.py` | `TechPanel` | `PanelTech` |
| `tech_panel.py` | `panel_tech.py` | `TechPanelWithGlow` | `PanelTechGlow` |
| `tech_button.py` | `button_tech.py` | `TechButton` | `ButtonTech` |
| `tech_button.py` | `button_tech.py` | `TechButtonSecondary` | `ButtonTechSecondary` |
| `tech_button.py` | `button_tech.py` | `TechButtonDanger` | `ButtonTechDanger` |
| `tech_button.py` | `button_tech.py` | `TechIconButton` | `ButtonIcon` |
| `blinking_label.py` | `label_blinking.py` | `BlinkingLabel` | `LabelBlinking` |
| `blinking_label.py` | `label_blinking.py` | `BlinkingTextWidget` | `LabelBlinkingFade` |
| `theme_switch.py` | `switch_theme.py` | `ThemeSwitch` | `SwitchTheme` |

### 2. 实时数据组件 (ui/widgets/realtime_data/)

| 旧文件名 | 新文件名 | 旧类名 | 新类名 |
|---------|---------|--------|--------|
| `data_card.py` | `card_data.py` | `DataCard` | `CardData` |
| `data_card.py` | `card_data.py` | `FurnaceDataCard` | `CardDataFurnace` |
| `valve_indicator.py` | `indicator_valve.py` | `ValveIndicator` | `IndicatorValve` |
| `valve_indicator.py` | `indicator_valve.py` | `ValveControlWidget` | `WidgetValveControl` |

### 3. 数据模型

| 类名 | 说明 | 变化 |
|------|------|------|
| `DataItem` | 数据项模型 | 无变化 |

## 📝 命名规范

### 新规范：组件类型_功能描述

 **正确示例**：
```python
# 文件名: button_tech.py
class ButtonTech(QPushButton):
    """科技风格按钮"""
    pass

# 文件名: panel_tech.py
class PanelTech(QFrame):
    """科技风格面板"""
    pass

# 文件名: label_blinking.py
class LabelBlinking(QLabel):
    """闪烁文本标签"""
    pass
```

 **旧规范（已废弃）**：
```python
# 文件名: tech_button.py (错误：功能在前)
class TechButton(QPushButton):
    pass
```

### 命名规则说明

1. **组件类型在前**：先说明是什么组件（Button、Panel、Label、Card 等）
2. **功能描述在后**：再说明具体功能（Tech、Blinking、Data、Valve 等）
3. **文件名与类名对应**：`button_tech.py` → `ButtonTech`

## 🔄 更新的文件

### 组件文件

-  `ui/widgets/common/panel_tech.py` - 新建
-  `ui/widgets/common/button_tech.py` - 新建
-  `ui/widgets/common/label_blinking.py` - 新建
-  `ui/widgets/common/switch_theme.py` - 新建
-  `ui/widgets/realtime_data/card_data.py` - 新建
-  `ui/widgets/realtime_data/indicator_valve.py` - 新建

### 配置文件

-  `ui/widgets/common/__init__.py` - 更新导出
-  `ui/widgets/realtime_data/__init__.py` - 更新导出

### 引用文件

-  `test_components.py` - 更新所有导入和使用
-  `ui/bar/top_nav_bar.py` - 更新主题切换导入

### 规则文档

-  `.cursor/rules/pyqt-frontend.mdc` - 添加命名规范
-  `.cursor/rules/backend.mdc` - 添加命名规范引用

### 删除的旧文件

-  `ui/widgets/common/tech_panel.py` - 已删除
-  `ui/widgets/common/tech_button.py` - 已删除
-  `ui/widgets/common/blinking_label.py` - 已删除
-  `ui/widgets/common/theme_switch.py` - 已删除
-  `ui/widgets/realtime_data/data_card.py` - 已删除
-  `ui/widgets/realtime_data/valve_indicator.py` - 已删除

## 📊 统计数据

- **重构文件数**: 6 个组件文件
- **重构类数**: 13 个类
- **更新引用**: 3 个文件
- **更新文档**: 2 个规则文档
- **删除旧文件**: 6 个

##  测试结果

### 功能测试

-  所有组件正常显示
-  主题切换正常工作
-  闪烁效果正常
-  报警检测正常
-  点击事件正常
-  状态切换正常

### 导入测试

```python
# 新的导入方式
from ui.widgets.common import (
    PanelTech, PanelTechGlow, 
    ButtonTech, ButtonTechSecondary, ButtonTechDanger, ButtonIcon,
    LabelBlinking, LabelBlinkingFade,
    SwitchTheme
)

from ui.widgets.realtime_data import (
    CardData, CardDataFurnace, DataItem,
    IndicatorValve, WidgetValveControl
)
```

## 📖 使用示例

### 按钮组件

```python
# 主要按钮
btn = ButtonTech("确认")
btn.clicked.connect(self.on_confirm)

# 次要按钮
btn = ButtonTechSecondary("取消")

# 危险按钮
btn = ButtonTechDanger("删除")

# 图标按钮
btn = ButtonIcon("ui/icons/settings.svg", size=24)
```

### 面板组件

```python
# 标准面板
panel = PanelTech("标题")
panel.set_content_layout(layout)

# 发光面板
panel = PanelTechGlow("重要信息")
```

### 数据卡片

```python
# 数据卡片
items = [
    DataItem("温度", "1250.5", "°C", "🌡️"),
    DataItem("压力", "0.85", "MPa", "📊"),
]
card = CardData(items)

# 电炉数据卡片（带阈值）
card = CardDataFurnace(items)
```

### 阀门指示器

```python
# 单个阀门
valve = IndicatorValve("进气阀")
valve.set_open(True)
valve.clicked.connect(self.on_valve_clicked)

# 多阀门控制
control = WidgetValveControl(["阀门A", "阀门B", "阀门C"])
control.set_valve_state(0, True)
```

### 闪烁标签

```python
# 开关式闪烁
label = LabelBlinking("报警信息")
label.set_blinking(True)
label.set_blink_color("#ff3b30")

# 渐变式闪烁
label = LabelBlinkingFade("警告信息")
label.set_blinking(True)
```

## 🎯 命名规范优势

### 1. 更清晰的组件识别

```python
# 新规范：一眼就知道是按钮
ButtonTech()
ButtonTechSecondary()
ButtonIcon()

# 旧规范：需要看后缀才知道
TechButton()
TechButtonSecondary()
TechIconButton()
```

### 2. 更好的代码组织

```python
# 按组件类型分组
Button*     # 所有按钮
Panel*      # 所有面板
Label*      # 所有标签
Card*       # 所有卡片
Indicator*  # 所有指示器
```

### 3. 更符合直觉

```python
# 问：这是什么？
ButtonTech  # 答：按钮（科技风格）
PanelTech   # 答：面板（科技风格）
CardData    # 答：卡片（数据展示）

# 而不是
TechButton  # 答：科技...按钮？
TechPanel   # 答：科技...面板？
DataCard    # 答：数据...卡片？
```

## 📚 相关文档

- `.cursor/rules/pyqt-frontend.mdc` - PyQt6 前端开发规范（已更新）
- `.cursor/rules/backend.mdc` - 后端开发规范（已更新）
- `vdoc/CORE_COMPONENTS_GUIDE.md` - 核心组件使用指南（需更新）
- `vdoc/PHASE5_COMPLETE.md` - 阶段5完成报告（需更新）

## 🎉 总结

本次重构成功将所有组件命名统一为"组件类型_功能描述"格式，使代码更加清晰、易读、易维护。所有组件功能正常，测试通过！

**重构原则**：
1.  组件类型在前，功能描述在后
2.  文件名与类名对应
3.  保持功能不变，只改名称
4.  更新所有引用
5.  删除旧文件
6.  更新文档

**下一步**：
- 继续使用新命名规范开发新组件
- 更新相关文档中的示例代码
- 在新功能开发中严格遵循命名规范

