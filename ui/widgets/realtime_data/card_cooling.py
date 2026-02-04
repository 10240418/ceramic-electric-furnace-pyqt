"""
冷却水卡片组件 - 左对齐，3行显示（图标+标签、数值、单位）
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager
from ui.widgets.common.label_blinking import LabelBlinkingFade
from ui.utils.alarm_checker import get_alarm_checker
from ui.utils.alarm_sound_manager import get_alarm_sound_manager


class CardCooling(QFrame):
    """冷却水卡片组件（新布局：左对齐，3行显示）"""
    
    # 1. 初始化卡片
    def __init__(self, title: str, items: list = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.title = title
        self.items = items or []
        self.item_widgets = []
        
        # 报警状态
        self.has_alarm = False
        self.blink_visible = True
        
        # 闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        
        # 报警声音播放计数器
        self.alarm_sound_counter = 0
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        title_widget = QWidget()
        title_widget.setObjectName("titleBar")
        title_widget.setFixedHeight(48)  # 增加标题栏高度：40px -> 48px
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(12, 0, 12, 0)
        title_layout.setSpacing(0)
        
        title_label = QLabel(self.title)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_label)
        
        main_layout.addWidget(title_widget)
        
        # 标题栏下方的分割线（带左右间隔）
        title_divider_container = QWidget()
        title_divider_container.setObjectName("titleDividerContainer")
        title_divider_layout = QHBoxLayout(title_divider_container)
        title_divider_layout.setContentsMargins(12, 0, 12, 0)
        title_divider_layout.setSpacing(0)
        
        title_divider = QFrame()
        title_divider.setFrameShape(QFrame.Shape.HLine)
        title_divider.setObjectName("titleDivider")
        title_divider.setFixedHeight(1)
        title_divider_layout.addWidget(title_divider)
        
        main_layout.addWidget(title_divider_container)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentArea")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(12, 2, 12, 2)  # 上下边距：8px -> 2px
        self.content_layout.setSpacing(0)
        
        # 创建数据项
        for i, item in enumerate(self.items):
            item_widget = self.create_data_item(item)
            self.item_widgets.append(item_widget)
            self.content_layout.addWidget(item_widget)
            
            # 每条数据下方都添加分割线（包括最后一项）
            # 使用容器包裹分割线，实现左右间隔
            divider_container = QWidget()
            divider_container_layout = QHBoxLayout(divider_container)
            divider_container_layout.setContentsMargins(0, 0, 0, 0)
            divider_container_layout.setSpacing(0)
            
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setObjectName("dataDivider")
            divider.setFixedHeight(1)
            divider_container_layout.addWidget(divider)
            
            self.content_layout.addWidget(divider_container)
        
        # 在最后添加弹簧，让数据从顶部开始排列（对于只有一条数据的过滤器卡片很重要）
        self.content_layout.addStretch()
        
        main_layout.addWidget(self.content_widget)
    
    # 3. 创建数据项（2行布局：图标+标签、数值+单位）
    def create_data_item(self, item: dict) -> QWidget:
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 4, 0, 4)  # 上下内边距：8px -> 4px
        item_layout.setSpacing(4)  # 标签和数值间距：6px -> 4px
        
        colors = self.theme_manager.get_colors()
        alarm_status = self.get_alarm_status(item)
        is_warning = alarm_status == 'warning'
        is_alarm = alarm_status == 'alarm'
        
        # 第 1 行：图标 + 标签
        label_row = QWidget()
        label_layout = QHBoxLayout(label_row)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(6)
        
        # 图标
        icon_label = QLabel(item['icon'])
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_alarm:
            icon_color = colors.STATUS_ALARM
        elif is_warning:
            icon_color = colors.STATUS_WARNING
        else:
            icon_color = colors.TEXT_SECONDARY
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {icon_color};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
        """)
        label_layout.addWidget(icon_label)
        
        # 标签
        label_widget = QLabel(item['label'])
        label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label_widget.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """)
        label_layout.addWidget(label_widget)
        label_layout.addStretch()
        
        item_layout.addWidget(label_row)
        
        # 第 2 行：数值 + 单位（同一行，左对齐）
        value_row = QWidget()
        value_layout = QHBoxLayout(value_row)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(6)
        
        if is_alarm:
            value_color = colors.STATUS_ALARM
            unit_color = colors.STATUS_ALARM
        elif is_warning:
            value_color = colors.STATUS_WARNING
            unit_color = colors.STATUS_WARNING
        else:
            value_color = colors.GLOW_PRIMARY
            unit_color = colors.TEXT_SECONDARY
        
        # 数值
        value_label = LabelBlinkingFade(item['value'])
        value_label.set_blinking(is_alarm)
        value_label.set_blink_color(colors.STATUS_ALARM)
        value_label.set_normal_color(value_color)
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        font = QFont("Roboto Mono", 26)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {value_color};
                border: none;
                background: transparent;
            }}
        """)
        value_layout.addWidget(value_label)
        
        # 单位
        unit_label = LabelBlinkingFade(item['unit'])
        unit_label.set_blinking(is_alarm)
        unit_label.set_blink_color(colors.STATUS_ALARM)
        unit_label.set_normal_color(colors.TEXT_PRIMARY if not (is_alarm or is_warning) else unit_color)
        unit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        unit_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_PRIMARY if not (is_alarm or is_warning) else unit_color};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
        """)
        value_layout.addWidget(unit_label)
        value_layout.addStretch()
        
        item_layout.addWidget(value_row)
        
        return item_widget
    
    # 4. 获取报警状态
    def get_alarm_status(self, item: dict) -> str:
        """
        获取报警状态
        
        Returns:
            'normal': 正常
            'warning': 警告
            'alarm': 报警
        """
        alarm_param = item.get('alarm_param')
        if alarm_param:
            alarm_checker = get_alarm_checker()
            try:
                num_value = float(item['value'])
                return alarm_checker.check_value(alarm_param, num_value)
            except ValueError:
                return 'normal'
        return 'normal'
    
    # 5. 更新数据项
    def update_items(self, items: list):
        """
        更新数据项
        
        Args:
            items: 数据项列表 [{"icon": "💧", "label": "冷却水流速:", "value": "12.50", "unit": "m³/h", "alarm_param": None}, ...]
        """
        # 检查是否有报警
        old_has_alarm = self.has_alarm
        self.has_alarm = any(self.get_alarm_status(item) == 'alarm' for item in items)
        
        # 只有在"开始记录"时才播放报警声音和闪烁边框
        if not self._is_recording():
            self.has_alarm = False
        
        # 报警声音播放逻辑
        if self.has_alarm:
            if not old_has_alarm:
                self.play_alarm_sound()
                self.alarm_sound_counter = 0
            else:
                self.alarm_sound_counter += 1
                if self.alarm_sound_counter >= 10:
                    self.play_alarm_sound()
                    self.alarm_sound_counter = 0
        else:
            self.alarm_sound_counter = 0
        
        # 启动或停止闪烁
        if self.has_alarm and not self.blink_timer.isActive():
            self.blink_timer.start(500)
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
    
    # 6. 重新创建所有组件
    def _recreate_all_items(self):
        """重新创建所有数据项组件"""
        # 清空旧的组件
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.item_widgets.clear()
        
        # 重新创建
        for i, item in enumerate(self.items):
            item_widget = self.create_data_item(item)
            self.item_widgets.append(item_widget)
            self.content_layout.addWidget(item_widget)
            
            # 每条数据下方都添加分割线（包括最后一项）
            # 使用容器包裹分割线，实现左右间隔
            divider_container = QWidget()
            divider_container_layout = QHBoxLayout(divider_container)
            divider_container_layout.setContentsMargins(0, 0, 0, 0)
            divider_container_layout.setSpacing(0)
            
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setObjectName("dataDivider")
            divider.setFixedHeight(1)
            divider_container_layout.addWidget(divider)
            
            self.content_layout.addWidget(divider_container)
        
        # 在最后添加弹簧，让数据从顶部开始排列
        self.content_layout.addStretch()
        
        self.apply_styles()
    
    # 7. 只更新现有组件的数值和颜色
    def _update_existing_items(self):
        """只更新现有组件的数值和颜色（性能优化）"""
        colors = self.theme_manager.get_colors()
        
        for i, item in enumerate(self.items):
            if i >= len(self.item_widgets):
                break
            
            item_widget = self.item_widgets[i]
            alarm_status = self.get_alarm_status(item)
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
                value_color = colors.GLOW_PRIMARY
                unit_color = colors.TEXT_PRIMARY
            
            # 查找并更新数值和单位标签（数值和单位在同一行）
            blinking_labels = item_widget.findChildren(LabelBlinkingFade)
            if len(blinking_labels) >= 2:
                # 第一个是数值
                value_label = blinking_labels[0]
                value_label.setText(item['value'])
                value_label.set_blinking(is_alarm)
                value_label.set_normal_color(value_color)
                value_label.set_blink_color(colors.STATUS_ALARM)
                
                # 第二个是单位
                unit_label = blinking_labels[1]
                unit_label.setText(item['unit'])
                unit_label.set_blinking(is_alarm)
                unit_label.set_normal_color(unit_color)
                unit_label.set_blink_color(colors.STATUS_ALARM)
    
    # 8. 切换闪烁状态
    def toggle_blink(self):
        """切换边框闪烁状态"""
        self.blink_visible = not self.blink_visible
        self.apply_styles()
    
    # 9. 播放报警声音
    def play_alarm_sound(self):
        """播放报警声音（通过全局管理器）"""
        sound_manager = get_alarm_sound_manager()
        sound_manager.play_alarm()
    
    # 10. 检查是否正在记录
    def _is_recording(self) -> bool:
        """检查是否正在记录（有批次号且正在冶炼）"""
        try:
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            return batch_service.is_smelting
        except Exception as e:
            return False
    
    # 11. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 根据报警状态和闪烁状态设置边框颜色
        if self.has_alarm:
            if self.blink_visible:
                border_color = colors.STATUS_ALARM
            else:
                border_color = colors.BG_LIGHT
        else:
            border_color = colors.BORDER_GLOW
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.BG_LIGHT};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QWidget#titleBar {{
                background: transparent;
                border: none;
                border-radius: 0px;
            }}
            QWidget#titleDividerContainer {{
                background: transparent;
                border: none;
            }}
            QFrame#titleDivider {{
                background: {colors.BORDER_DARK};
                border: none;
                max-height: 1px;
                min-height: 1px;
            }}
            QLabel#titleLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 17px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            QWidget#contentArea {{
                background: transparent;
                border: none;
            }}
            QFrame#dataDivider {{
                background: {colors.BORDER_DARK};
                border: none;
                max-height: 1px;
                min-height: 1px;
            }}
        """)
    
    # 12. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        self.update_items(self.items)

