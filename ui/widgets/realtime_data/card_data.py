"""
数据卡片组件
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager
from ui.widgets.common.label_blinking import LabelBlinkingFade


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
        is_masked: bool = False
    ):
        self.label = label
        self.value = value
        self.unit = unit
        self.icon = icon
        self.threshold = threshold
        self.is_above_threshold = is_above_threshold
        self.is_masked = is_masked
    
    # 2. 检查是否报警
    def is_alarm(self) -> bool:
        if self.threshold is None:
            return False
        try:
            num_value = float(self.value)
            if self.is_above_threshold:
                return num_value > self.threshold
            else:
                return num_value < self.threshold
        except ValueError:
            return False


class CardData(QFrame):
    """数据卡片组件"""
    
    # 1. 初始化卡片
    def __init__(self, items: list = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.items = items or []
        self.item_widgets = []
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
    
    # 3. 创建数据行
    def create_data_row(self, item: DataItem) -> QWidget:
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 3, 0, 3)
        row_layout.setSpacing(8)
        
        colors = self.theme_manager.get_colors()
        is_alarm = item.is_alarm()
        
        # 图标（如果有）
        if item.icon:
            icon_label = QLabel(item.icon)
            icon_label.setFixedSize(26, 26)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_color = colors.GLOW_RED if is_alarm else colors.BORDER_GLOW
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
                color: {colors.TEXT_SECONDARY};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
        """)
        label_layout.addWidget(label)
        
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
                    font-size: 12px;
                    font-weight: bold;
                }}
            """)
            row_layout.addWidget(alarm_label)
        
        # 数值（闪烁）
        value_color = colors.GLOW_RED if is_alarm else colors.BORDER_GLOW
        value_label = LabelBlinkingFade(item.value)
        value_label.set_blinking(is_alarm)
        value_label.set_blink_color(colors.GLOW_RED)
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
        
        # 单位
        unit_label = LabelBlinkingFade(item.unit)
        unit_label.set_blinking(is_alarm)
        unit_label.set_blink_color(colors.GLOW_RED)
        unit_label.set_normal_color(colors.TEXT_SECONDARY if not is_alarm else colors.GLOW_RED)
        unit_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_SECONDARY if not is_alarm else colors.GLOW_RED};
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
    
    # 4. 更新数据项
    def update_items(self, items: list):
        self.items = items
        
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
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
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

