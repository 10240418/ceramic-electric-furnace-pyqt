"""
数据卡片组件
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager
from ui.widgets.common.label_blinking import LabelBlinkingFade
from ui.utils.alarm_checker import get_alarm_checker
from ui.utils.alarm_sound_manager import get_alarm_sound_manager


class DataItem:
    """数据项模型"""
    
    # 1. 初始化数据项
    def __init__(
        self,
        label: str,
        value: str,
        unit: str,
        icon: str = "",
        threshold: float = None,
        is_above_threshold: bool = False,
        is_masked: bool = False,
        alarm_param: str = None  # 报警参数名称（用于阈值检查）
    ):
        self.label = label
        self.value = value
        self.unit = unit
        self.icon = icon
        self.threshold = threshold
        self.is_above_threshold = is_above_threshold
        self.is_masked = is_masked
        self.alarm_param = alarm_param  # 如 'cooling_pressure_shell', 'filter_pressure_diff'
    
    # 2. 检查报警状态
    def get_alarm_status(self) -> str:
        """
        获取报警状态
        
        Returns:
            'normal': 正常
            'warning': 警告
            'alarm': 报警
        """
        if self.alarm_param:
            # 使用报警检查器
            alarm_checker = get_alarm_checker()
            try:
                num_value = float(self.value)
                return alarm_checker.check_value(self.alarm_param, num_value)
            except ValueError:
                return 'normal'
        
        # 兼容旧的阈值检查方式
        if self.threshold is None:
            return 'normal'
        try:
            num_value = float(self.value)
            if self.is_above_threshold:
                return 'alarm' if num_value > self.threshold else 'normal'
            else:
                return 'alarm' if num_value < self.threshold else 'normal'
        except ValueError:
            return 'normal'
    
    # 3. 检查是否报警（兼容旧代码）
    def is_alarm(self) -> bool:
        return self.get_alarm_status() == 'alarm'


class CardData(QFrame):
    """数据卡片组件"""
    
    # 1. 初始化卡片
    def __init__(self, items: list = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.items = items or []
        self.item_widgets = []
        
        # 报警状态
        self.has_alarm = False
        self.blink_visible = True
        
        # 闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        
        # 报警声音播放计数器（每 10 次更新播放一次，避免频繁播放）
        self.alarm_sound_counter = 0
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)  # 统一左右上下 16px
        main_layout.setSpacing(8)
        
        # 创建数据行
        for i, item in enumerate(self.items):
            row_widget = self.create_data_row(item)
            self.item_widgets.append(row_widget)
            main_layout.addWidget(row_widget)
            
            # 添加分割线（最后一行不添加）
            if i < len(self.items) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setObjectName("dataDivider")
                main_layout.addWidget(divider)
    
    # 3. 创建数据行（不显示报警标签，只改变颜色）
    def create_data_row(self, item: DataItem) -> QWidget:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 3, 0, 3)
        row_layout.setSpacing(8)
        
        colors = self.theme_manager.get_colors()
        alarm_status = item.get_alarm_status()
        is_warning = alarm_status == 'warning'
        is_alarm = alarm_status == 'alarm'
        
        # 图标（如果有）
        if item.icon:
            icon_label = QLabel(item.icon)
            icon_label.setFixedSize(26, 26)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_alarm:
                icon_color = colors.STATUS_ALARM
            elif is_warning:
                icon_color = colors.STATUS_WARNING
            else:
                icon_color = colors.BORDER_GLOW
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {icon_color};
                    font-size: 20px;
                    border: none;
                    background: transparent;
                }}
            """)
            row_layout.addWidget(icon_label)
        
        # 标签
        label_widget = QWidget()
        label_layout = QVBoxLayout(label_widget)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(2)
        
        label = QLabel(item.label)
        label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
        """)
        label_layout.addWidget(label)
        
        row_layout.addWidget(label_widget)
        row_layout.addStretch()
        
        # 不显示报警/警告标签
        
        # 数值（报警时闪烁）
        if is_alarm:
            value_color = colors.STATUS_ALARM
        elif is_warning:
            value_color = colors.STATUS_WARNING
        else:
            value_color = colors.BORDER_GLOW
        
        value_label = LabelBlinkingFade(item.value)
        value_label.set_blinking(is_alarm)  # 只有报警时闪烁
        value_label.set_blink_color(colors.STATUS_ALARM)
        value_label.set_normal_color(value_color)
        
        font = QFont("Roboto Mono", 20)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {value_color};
                border: none;
                background: transparent;
            }}
        """)
        row_layout.addWidget(value_label)
        
        # 单位（如果有）
        if item.unit:
            unit_label = LabelBlinkingFade(item.unit)
            unit_label.set_blinking(is_alarm)  # 只有报警时闪烁
            unit_label.set_blink_color(colors.STATUS_ALARM)
            if is_alarm:
                unit_color = colors.STATUS_ALARM
            elif is_warning:
                unit_color = colors.STATUS_WARNING
            else:
                unit_color = colors.TEXT_SECONDARY
            unit_label.set_normal_color(unit_color)
            unit_label.setStyleSheet(f"""
                QLabel {{
                    color: {unit_color};
                    font-size: 18px;
                    border: none;
                    background: transparent;
                }}
            """)
            row_layout.addWidget(unit_label)
        
        # 遮罩层
        if item.is_masked:
            mask = QFrame(row_widget)
            mask.setGeometry(row_widget.rect())
            mask.setStyleSheet(f"""
                QFrame {{
                    background: rgba(0, 0, 0, 0.6);
                    border-radius: 4px;
                }}
            """)
            mask.raise_()
        
        return row_widget
    
    # 3.5 切换闪烁状态
    def toggle_blink(self):
        """切换边框闪烁状态"""
        self.blink_visible = not self.blink_visible
        self.apply_styles()
    
    # 3.6 播放报警声音（使用全局管理器）
    def play_alarm_sound(self):
        """播放报警声音（通过全局管理器，避免多个声音同时播放）"""
        sound_manager = get_alarm_sound_manager()
        sound_manager.play_alarm()
    
    # 3.7 声音播放完成回调（已移除，由全局管理器处理）
    
    # 4. 更新数据项（优化：只更新数值，不重新创建组件）
    def update_items(self, items: list):
        """
        更新数据项
        
        优化：只更新数值和颜色，不重新创建所有组件
        """
        # 检查是否有报警
        old_has_alarm = self.has_alarm
        self.has_alarm = any(item.get_alarm_status() == 'alarm' for item in items)
        
        # 只有在"开始记录"时才播放报警声音和闪烁边框
        if not self._is_recording():
            self.has_alarm = False
        
        # 报警声音播放逻辑：
        # 1. 如果从无报警变为有报警，立即播放声音
        # 2. 如果一直处于报警状态，每 10 次更新播放一次（避免频繁播放）
        if self.has_alarm:
            if not old_has_alarm:
                # 从无报警变为有报警，立即播放
                self.play_alarm_sound()
                self.alarm_sound_counter = 0
            else:
                # 一直处于报警状态，每 10 次更新播放一次
                self.alarm_sound_counter += 1
                if self.alarm_sound_counter >= 10:
                    self.play_alarm_sound()
                    self.alarm_sound_counter = 0
        else:
            # 无报警时重置计数器
            self.alarm_sound_counter = 0
        
        # 启动或停止闪烁
        if self.has_alarm and not self.blink_timer.isActive():
            self.blink_timer.start(500)  # 500ms 闪烁一次
        elif not self.has_alarm and self.blink_timer.isActive():
            self.blink_timer.stop()
            self.blink_visible = True
        
        # 如果数据项数量变化，需要重新创建
        if len(items) != len(self.items):
            self.items = items
            self._recreate_all_items()
            return
        
        # 否则只更新现有组件的数值和颜色
        self.items = items
        self._update_existing_items()
        
        # 更新边框样式
        self.apply_styles()
    
    # 4.05 检查是否正在记录
    def _is_recording(self) -> bool:
        """检查是否正在记录（有批次号且正在冶炼）"""
        try:
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            return batch_service.is_smelting
        except Exception as e:
            return False
    

    
    # 4.1 重新创建所有组件
    def _recreate_all_items(self):
        """重新创建所有数据行组件"""
        # 清空旧的组件
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.item_widgets.clear()
        
        # 重新创建
        for i, item in enumerate(self.items):
            row_widget = self.create_data_row(item)
            self.item_widgets.append(row_widget)
            layout.addWidget(row_widget)
            
            if i < len(self.items) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setObjectName("dataDivider")
                layout.addWidget(divider)
        
        self.apply_styles()
    
    # 4.2 只更新现有组件的数值和颜色
    def _update_existing_items(self):
        """只更新现有组件的数值和颜色（性能优化）"""
        colors = self.theme_manager.get_colors()
        
        for i, item in enumerate(self.items):
            if i >= len(self.item_widgets):
                break
            
            row_widget = self.item_widgets[i]
            alarm_status = item.get_alarm_status()
            is_warning = alarm_status == 'warning'
            is_alarm = alarm_status == 'alarm'
            
            # 更新数值颜色
            if is_alarm:
                value_color = colors.STATUS_ALARM
                unit_color = colors.STATUS_ALARM
            elif is_warning:
                value_color = colors.STATUS_WARNING
                unit_color = colors.STATUS_WARNING
            else:
                value_color = colors.BORDER_GLOW
                unit_color = colors.TEXT_SECONDARY
            
            # 查找并更新数值和单位标签
            blinking_labels = row_widget.findChildren(LabelBlinkingFade)
            if len(blinking_labels) >= 1:
                # 第一个是数值
                value_label = blinking_labels[0]
                
                # 更新数值（不设置 setStyleSheet，让 LabelBlinkingFade 自己处理颜色）
                value_label.setText(item.value)
                value_label.set_blinking(is_alarm)
                value_label.set_normal_color(value_color)
                value_label.set_blink_color(colors.STATUS_ALARM)
                
                # 如果有单位标签，更新单位
                if len(blinking_labels) >= 2 and item.unit:
                    unit_label = blinking_labels[1]
                    unit_label.setText(item.unit)
                    unit_label.set_blinking(is_alarm)
                    unit_label.set_normal_color(unit_color)
                    unit_label.set_blink_color(colors.STATUS_ALARM)
    
    # 5. 应用样式（支持边框闪烁）
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 根据报警状态和闪烁状态设置边框颜色
        if self.has_alarm:
            if self.blink_visible:
                border_color = colors.STATUS_ALARM
            else:
                border_color = colors.BG_LIGHT  # 闪烁时隐藏边框
        else:
            border_color = colors.BORDER_GLOW
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.BG_LIGHT};
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
            QFrame#dataDivider {{
                background: {colors.BORDER_DARK};
                border: none;
                max-height: 1px;
            }}
        """)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        # 重新创建所有数据行以更新颜色
        self.update_items(self.items)


class CardDataFurnace(CardData):
    """电炉专用数据卡片（显示阈值信息）"""
    
    # 1. 创建数据行（带阈值显示）
    def create_data_row(self, item: DataItem) -> QWidget:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(8)
        
        colors = self.theme_manager.get_colors()
        is_alarm = item.is_alarm()
        
        # 图标
        if item.icon:
            icon_label = QLabel(item.icon)
            icon_label.setFixedSize(18, 18)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_color = colors.GLOW_RED if is_alarm else colors.BORDER_GLOW
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {icon_color};
                    font-size: 16px;
                    border: none;
                    background: transparent;
                }}
            """)
            row_layout.addWidget(icon_label)
        
        # 标签和阈值
        label_widget = QWidget()
        label_layout = QVBoxLayout(label_widget)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(2)
        
        label = QLabel(item.label)
        label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """)
        label_layout.addWidget(label)
        
        # 阈值信息
        if item.threshold is not None:
            threshold_text = f"阈值: {item.threshold}{item.unit}"
            threshold_label = QLabel(threshold_text)
            threshold_color = colors.GLOW_RED if is_alarm else colors.TEXT_MUTED
            threshold_label.setStyleSheet(f"""
                QLabel {{
                    color: {threshold_color};
                    font-size: 12px;
                    border: none;
                    background: transparent;
                }}
            """)
            label_layout.addWidget(threshold_label)
        
        row_layout.addWidget(label_widget)
        row_layout.addStretch()
        
        # 报警标签
        if is_alarm:
            alarm_label = QLabel("报警")
            alarm_label.setStyleSheet(f"""
                QLabel {{
                    background: {colors.GLOW_RED}33;
                    color: {colors.GLOW_RED};
                    border: 1px solid {colors.GLOW_RED};
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
            row_layout.addWidget(alarm_label)
        
        # 数值
        value_color = colors.GLOW_RED if is_alarm else colors.BORDER_GLOW
        value_label = QLabel(item.value)
        font = QFont("Roboto Mono", 16)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {value_color};
                border: none;
                background: transparent;
            }}
        """)
        row_layout.addWidget(value_label)
        
        # 单位
        unit_label = QLabel(item.unit)
        unit_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_SECONDARY if not is_alarm else colors.GLOW_RED};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """)
        row_layout.addWidget(unit_label)
        
        return row_widget

