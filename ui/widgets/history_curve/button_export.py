"""
导出数据按钮组件
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager


class ButtonExport(QPushButton):
    """导出数据按钮"""
    
    # 导出点击信号
    export_clicked = pyqtSignal()
    
    # 1. 初始化组件
    def __init__(self, accent_color: str = None, parent=None):
        super().__init__("导出数据", parent)
        self.theme_manager = ThemeManager.instance()
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(36)
        
        self.clicked.connect(self.on_clicked)
        
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 点击处理
    def on_clicked(self):
        self.export_clicked.emit()
    
    # 3. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        is_dark = self.theme_manager.is_dark_mode()
        
        # 与下拉框保持一致的样式
        if is_dark:
            bg_normal = f"{colors.BG_LIGHT}4D"
            bg_hover = f"{colors.BG_LIGHT}80"
        else:
            bg_normal = colors.BG_LIGHT  # 白色
            bg_hover = colors.BG_MEDIUM  # 米白色
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg_normal};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {bg_hover};
                border: 1px solid {self.accent_color};
            }}
            QPushButton:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 4. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

