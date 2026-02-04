"""
科技风格下拉选择器组件
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout, QScrollArea, QFrame, QScroller
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QIcon
from ui.styles.themes import ThemeManager
from loguru import logger


class DropdownTech(QWidget):
    """科技风格下拉选择器（单选，支持拖动滚动）"""
    
    # 选择变化信号
    selection_changed = pyqtSignal(str)
    
    # 1. 初始化组件
    def __init__(self, options: list[str], default_value: str = None, accent_color: str = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.options = options
        self.current_value = default_value or (options[0] if options else "")
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        
        # 弹出窗口
        self.popup = None
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 显示当前值的按钮
        self.button = QPushButton(self.current_value if self.current_value else "请选择")
        self.button.setFixedHeight(36)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self.show_popup)
        
        layout.addWidget(self.button)
    
    # 3. 显示弹出窗口
    def show_popup(self):
        """显示单选弹出窗口"""
        try:
            logger.info(f"创建单选弹出窗口，选项数量: {len(self.options)}, 当前选中: {self.current_value}")
            
            # 如果已有弹出窗口，先关闭
            if self.popup:
                self.popup.close()
                self.popup = None
            
            # 创建弹出窗口
            self.popup = SingleSelectPopup(
                self.options,
                self.current_value,
                self.accent_color,
                self
            )
            
            # 连接选择变化信号
            self.popup.selection_changed.connect(self.on_popup_selection_changed)
            
            # 计算弹出窗口位置（在按钮下方）
            button_global_pos = self.button.mapToGlobal(QPoint(0, 0))
            popup_x = button_global_pos.x()
            popup_y = button_global_pos.y() + self.button.height() + 2
            
            self.popup.move(popup_x, popup_y)
            self.popup.show()
            
            logger.info("单选弹出窗口已显示")
            
        except Exception as e:
            logger.error(f"显示单选弹出窗口失败: {e}", exc_info=True)
    
    # 4. 弹出窗口选择变化
    def on_popup_selection_changed(self, value: str):
        """弹出窗口选择变化"""
        if value != self.current_value:
            self.current_value = value
            self.button.setText(value)
            self.selection_changed.emit(value)
            logger.info(f"单选值变化: {value}")
        
        # 关闭弹出窗口
        if self.popup:
            self.popup.close()
            self.popup = None
    
    # 5. 获取当前值
    def get_value(self) -> str:
        return self.current_value
    
    # 6. 设置当前值
    def set_value(self, value: str):
        if value in self.options and value != self.current_value:
            self.current_value = value
            self.button.setText(value)
    
    # 7. 设置选项列表
    def set_options(self, options: list[str]):
        self.options = options
        if self.current_value not in options and options:
            self.current_value = options[0]
            self.button.setText(self.current_value)
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.button.setStyleSheet(f"""
            QPushButton {{
                background: {colors.BTN_BG_NORMAL};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 6px 16px;
                text-align: left;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {colors.BTN_BG_HOVER};
                border: 1px solid {self.accent_color};
            }}
            QPushButton:pressed {{
                background: {colors.BG_MEDIUM};
            }}
            QPushButton::menu-indicator {{
                image: none;
                width: 0px;
            }}
        """)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class SingleSelectPopup(QWidget):
    """单选弹出窗口（支持拖动滚动）"""
    
    # 选择变化信号
    selection_changed = pyqtSignal(str)
    
    # 1. 初始化弹出窗口
    def __init__(self, options: list[str], current_value: str, accent_color: str, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.options = options
        self.current_value = current_value
        self.accent_color = accent_color
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        self.radio_buttons = []
        
        self.init_ui()
        self.apply_styles()
    
    # 2. 初始化 UI
    def init_ui(self):
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(4, 4, 4, 4)
            main_layout.setSpacing(0)
            
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            # 创建容器
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(2)
            
            # 添加单选按钮选项
            for option in self.options:
                radio = QRadioButton(option)
                radio.setChecked(option == self.current_value)
                radio.toggled.connect(lambda checked, opt=option: self.on_radio_toggled(opt, checked))
                container_layout.addWidget(radio)
                self.radio_buttons.append(radio)
            
            scroll_area.setWidget(container)
            
            # 启用拖动滚动功能（关键代码）
            QScroller.grabGesture(scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
            
            # 设置最大高度（最多显示10个选项，超过则滚动）
            max_visible_items = 10
            item_height = 36
            max_height = max_visible_items * item_height
            
            if len(self.options) > max_visible_items:
                scroll_area.setFixedHeight(max_height)
            else:
                scroll_area.setFixedHeight(len(self.options) * item_height)
            
            scroll_area.setFixedWidth(250)
            
            main_layout.addWidget(scroll_area)
            
            # 设置窗口大小
            self.setFixedWidth(258)
            if len(self.options) > max_visible_items:
                self.setFixedHeight(max_height + 8)
            else:
                self.setFixedHeight(len(self.options) * item_height + 8)
            
            logger.info(f"SingleSelectPopup UI 初始化完成，选项数: {len(self.options)}")
            
        except Exception as e:
            logger.error(f"SingleSelectPopup UI 初始化失败: {e}", exc_info=True)
    
    # 3. 单选按钮切换
    def on_radio_toggled(self, option: str, checked: bool):
        if checked:
            logger.info(f"单选按钮选中: {option}")
            self.selection_changed.emit(option)
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            SingleSelectPopup {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
            }}
            
            QRadioButton {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                padding: 8px 12px;
                border-radius: 2px;
                font-size: 15px;
                spacing: 8px;
            }}
            QRadioButton:hover {{
                background: {self.accent_color}1A;
                color: {colors.TEXT_PRIMARY};
            }}
            QRadioButton:checked {{
                color: {self.accent_color};
                font-weight: bold;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {colors.BORDER_MEDIUM};
                background: transparent;
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {self.accent_color};
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {self.accent_color};
                background: {self.accent_color};
            }}
            
            QScrollBar:vertical {{
                background: {colors.BG_MEDIUM};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.BORDER_MEDIUM};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.accent_color};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)


class DropdownMultiSelect(QWidget):
    """科技风格多选下拉选择器"""
    
    # 选择变化信号（返回选中的列表）
    selection_changed = pyqtSignal(list)
    
    # 1. 初始化组件
    def __init__(self, options: list[str], default_values: list[str] = None, accent_color: str = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.options = options
        self.selected_values = default_values or []
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        
        # 弹出窗口
        self.popup = None
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 显示选中数量的按钮
        self.button = QPushButton(f"已选 {len(self.selected_values)} 项")
        self.button.setFixedHeight(28)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self.toggle_popup)
        
        layout.addWidget(self.button)
    
    # 3. 切换弹出窗口
    def toggle_popup(self):
        if self.popup and self.popup.isVisible():
            self.popup.hide()
        else:
            self.show_popup()
    
    # 4. 显示弹出窗口
    def show_popup(self):
        from PyQt6.QtWidgets import QCheckBox, QVBoxLayout, QScrollArea, QFrame
        from PyQt6.QtCore import QEvent
        from loguru import logger
        
        try:
            # 如果已有弹出窗口，先关闭
            if self.popup:
                self.popup.close()
            
            logger.info(f"创建多选弹出窗口，选项数量: {len(self.options)}, 已选: {len(self.selected_values)}")
            
            # 创建弹出窗口
            self.popup = MultiSelectPopup(
                self.options,
                self.selected_values,
                self.accent_color,
                self.theme_manager,
                self
            )
            
            # 连接信号
            self.popup.selection_changed.connect(self.on_popup_selection_changed)
            
            # 计算弹出窗口位置
            button_pos = self.button.mapToGlobal(self.button.rect().bottomLeft())
            self.popup.move(button_pos)
            
            # 显示弹出窗口
            self.popup.show()
            logger.info("多选弹出窗口已显示")
            
        except Exception as e:
            logger.error(f"显示多选弹出窗口失败: {e}", exc_info=True)
    
    # 5. 弹出窗口选择变化
    def on_popup_selection_changed(self, selected_values: list):
        self.selected_values = selected_values
        self.button.setText(f"已选 {len(self.selected_values)} 项")
        self.selection_changed.emit(self.selected_values)
    
    # 6. 获取选中值列表
    def get_values(self) -> list[str]:
        return self.selected_values.copy()
    
    # 7. 设置选中值列表
    def set_values(self, values: list[str]):
        self.selected_values = [v for v in values if v in self.options]
        self.button.setText(f"已选 {len(self.selected_values)} 项")
    
    # 8. 设置选项列表
    def set_options(self, options: list[str]):
        self.options = options
        # 过滤掉不存在的选中值
        self.selected_values = [v for v in self.selected_values if v in options]
        if not self.selected_values and options:
            self.selected_values = [options[0]]
        self.button.setText(f"已选 {len(self.selected_values)} 项")
    
    # 9. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.button.setStyleSheet(f"""
            QPushButton {{
                background: {colors.BTN_BG_NORMAL};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 4px 12px;
                text-align: left;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {colors.BTN_BG_HOVER};
                border: 1px solid {self.accent_color};
            }}
            QPushButton:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 10. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class MultiSelectPopup(QWidget):
    """多选弹出窗口（支持拖动滚动，点击外部关闭）"""
    
    # 选择变化信号
    selection_changed = pyqtSignal(list)
    
    # 1. 初始化弹出窗口
    def __init__(self, options: list[str], selected_values: list[str], accent_color: str, theme_manager, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.options = options
        self.selected_values = selected_values.copy()
        self.accent_color = accent_color
        self.theme_manager = theme_manager
        
        self.init_ui()
        self.apply_styles()
    
    # 2. 初始化 UI
    def init_ui(self):
        from PyQt6.QtWidgets import QCheckBox, QVBoxLayout, QScrollArea, QFrame, QScroller
        from functools import partial
        from loguru import logger
        
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(4, 4, 4, 4)
            main_layout.setSpacing(0)
            
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            # 创建容器
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(2)
            
            # 添加复选框选项（使用 partial 避免闭包问题）
            self.checkboxes = []
            for option in self.options:
                checkbox = QCheckBox(option)
                checkbox.setChecked(option in self.selected_values)
                # 使用 partial 绑定参数，避免 lambda 闭包问题
                checkbox.stateChanged.connect(partial(self.on_checkbox_changed, option))
                container_layout.addWidget(checkbox)
                self.checkboxes.append(checkbox)
            
            scroll_area.setWidget(container)
            
            # 启用拖动滚动功能（关键代码）
            QScroller.grabGesture(scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
            
            # 设置最大高度（最多显示10个选项，超过则滚动）
            max_visible_items = 10
            item_height = 36
            max_height = max_visible_items * item_height
            
            if len(self.options) > max_visible_items:
                scroll_area.setFixedHeight(max_height)
            else:
                scroll_area.setFixedHeight(len(self.options) * item_height)
            
            scroll_area.setFixedWidth(250)
            
            main_layout.addWidget(scroll_area)
            
            # 设置窗口大小
            self.setFixedWidth(258)
            if len(self.options) > max_visible_items:
                self.setFixedHeight(max_height + 8)
            else:
                self.setFixedHeight(len(self.options) * item_height + 8)
            
            logger.info(f"MultiSelectPopup UI 初始化完成，选项数: {len(self.options)}")
            
        except Exception as e:
            logger.error(f"MultiSelectPopup UI 初始化失败: {e}", exc_info=True)
    
    # 3. 复选框状态变化（使用 partial 绑定）
    def on_checkbox_changed(self, option: str, state: int):
        from loguru import logger
        try:
            checked = (state == 2)  # Qt.CheckState.Checked = 2
            logger.info(f"复选框变化: {option}, checked={checked}")
            
            if checked:
                if option not in self.selected_values:
                    self.selected_values.append(option)
            else:
                if option in self.selected_values and len(self.selected_values) > 1:
                    self.selected_values.remove(option)
            
            # 发送选择变化信号
            self.selection_changed.emit(self.selected_values)
            logger.info(f"当前已选: {self.selected_values}")
            
        except Exception as e:
            logger.error(f"复选框变化处理失败: {e}", exc_info=True)
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            MultiSelectPopup {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
            }}
            QCheckBox {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                padding: 6px 16px;
                border-radius: 2px;
                font-size: 14px;
            }}
            QCheckBox:hover {{
                background: {self.accent_color}33;
                color: {self.accent_color};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:checked {{
                image: none;
                background: {self.accent_color};
                border: 1px solid {self.accent_color};
                border-radius: 2px;
            }}
            QCheckBox::indicator:unchecked {{
                background: transparent;
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 2px;
            }}
            QScrollArea {{
                background: {colors.BG_MEDIUM};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {colors.BG_MEDIUM};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.BORDER_MEDIUM};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.accent_color};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
