"""
科技风格下拉选择器组件
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from ui.styles.themes import ThemeManager


class DropdownTech(QWidget):
    """科技风格下拉选择器"""
    
    # 选择变化信号
    selection_changed = pyqtSignal(str)
    
    # 1. 初始化组件
    def __init__(self, options: list[str], default_value: str = None, accent_color: str = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.options = options
        self.current_value = default_value or (options[0] if options else "")
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        
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
        self.button = QPushButton(self.current_value)
        self.button.setFixedHeight(28)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self.show_menu)
        
        layout.addWidget(self.button)
    
    # 3. 显示下拉菜单
    def show_menu(self):
        menu = QMenu(self)
        colors = self.theme_manager.get_colors()
        
        # 设置菜单样式
        menu.setStyleSheet(f"""
            QMenu {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                padding: 6px 16px;
                border-radius: 2px;
            }}
            QMenu::item:selected {{
                background: {self.accent_color}33;
                color: {self.accent_color};
            }}
            QMenu::item:disabled {{
                color: {colors.TEXT_DISABLED};
            }}
        """)
        
        # 添加选项
        for option in self.options:
            action = menu.addAction(option)
            if option == self.current_value:
                action.setEnabled(False)
            action.triggered.connect(lambda checked, opt=option: self.on_option_selected(opt))
        
        # 显示菜单
        menu.exec(self.button.mapToGlobal(self.button.rect().bottomLeft()))
    
    # 4. 选项被选中
    def on_option_selected(self, option: str):
        if option != self.current_value:
            self.current_value = option
            self.button.setText(option)
            self.selection_changed.emit(option)
    
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
        is_dark = self.theme_manager.is_dark_mode()
        
        # 浅色主题：未选中用白色背景，深色主题：用半透明背景
        if is_dark:
            bg_normal = f"{colors.BG_LIGHT}4D"
            bg_hover = f"{colors.BG_LIGHT}80"
        else:
            bg_normal = colors.BG_LIGHT  # 白色
            bg_hover = colors.BG_MEDIUM  # 米白色
        
        self.button.setStyleSheet(f"""
            QPushButton {{
                background: {bg_normal};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 4px 12px;
                text-align: left;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {bg_hover};
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
        self.button.clicked.connect(self.show_menu)
        
        layout.addWidget(self.button)
    
    # 3. 显示下拉菜单
    def show_menu(self):
        menu = QMenu(self)
        colors = self.theme_manager.get_colors()
        
        # 设置菜单样式
        menu.setStyleSheet(f"""
            QMenu {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                padding: 6px 16px;
                border-radius: 2px;
            }}
            QMenu::item:selected {{
                background: {self.accent_color}33;
                color: {self.accent_color};
            }}
            QMenu::indicator {{
                width: 16px;
                height: 16px;
            }}
            QMenu::indicator:checked {{
                image: none;
                background: {self.accent_color};
                border: 1px solid {self.accent_color};
                border-radius: 2px;
            }}
            QMenu::indicator:unchecked {{
                background: transparent;
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 2px;
            }}
        """)
        
        # 添加选项（可勾选）
        for option in self.options:
            action = menu.addAction(option)
            action.setCheckable(True)
            action.setChecked(option in self.selected_values)
            action.triggered.connect(lambda checked, opt=option: self.on_option_toggled(opt, checked))
        
        # 显示菜单
        menu.exec(self.button.mapToGlobal(self.button.rect().bottomLeft()))
    
    # 4. 选项被切换
    def on_option_toggled(self, option: str, checked: bool):
        if checked:
            if option not in self.selected_values:
                self.selected_values.append(option)
        else:
            if option in self.selected_values and len(self.selected_values) > 1:
                self.selected_values.remove(option)
        
        self.button.setText(f"已选 {len(self.selected_values)} 项")
        self.selection_changed.emit(self.selected_values)
    
    # 5. 获取选中值列表
    def get_values(self) -> list[str]:
        return self.selected_values.copy()
    
    # 6. 设置选中值列表
    def set_values(self, values: list[str]):
        self.selected_values = [v for v in values if v in self.options]
        self.button.setText(f"已选 {len(self.selected_values)} 项")
    
    # 7. 设置选项列表
    def set_options(self, options: list[str]):
        self.options = options
        # 过滤掉不存在的选中值
        self.selected_values = [v for v in self.selected_values if v in options]
        if not self.selected_values and options:
            self.selected_values = [options[0]]
        self.button.setText(f"已选 {len(self.selected_values)} 项")
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        is_dark = self.theme_manager.is_dark_mode()
        
        # 浅色主题：未选中用白色背景，深色主题：用半透明背景
        if is_dark:
            bg_normal = f"{colors.BG_LIGHT}4D"
            bg_hover = f"{colors.BG_LIGHT}80"
        else:
            bg_normal = colors.BG_LIGHT  # 白色
            bg_hover = colors.BG_MEDIUM  # 米白色
        
        self.button.setStyleSheet(f"""
            QPushButton {{
                background: {bg_normal};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 4px 12px;
                text-align: left;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {bg_hover};
                border: 1px solid {self.accent_color};
            }}
            QPushButton:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
