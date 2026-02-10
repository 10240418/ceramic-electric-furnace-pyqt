"""
科技风格按钮组件
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from ui.styles.themes import ThemeManager


class ButtonTech(QPushButton):
    """科技风格按钮"""
    
    # 1. 初始化按钮
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = ThemeManager.instance()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {colors.BUTTON_PRIMARY_BG};
                color: {colors.BUTTON_PRIMARY_TEXT};
                border: 1px solid {colors.BUTTON_PRIMARY_BG};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
                border: 1px solid {colors.BUTTON_PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background: {colors.BUTTON_PRIMARY_BG};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton:disabled {{
                background: {colors.BUTTON_DISABLED_BG};
                color: {colors.BUTTON_DISABLED_TEXT};
                border: 1px solid {colors.BORDER_DARK};
            }}
        """)
    
    # 3. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class ButtonTechSecondary(QPushButton):
    """科技风格次要按钮（透明背景）"""
    
    # 1. 初始化按钮
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = ThemeManager.instance()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {colors.BUTTON_SECONDARY_HOVER};
                border: 1px solid {colors.BORDER_DARK};
                color: {colors.GLOW_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {colors.BUTTON_SECONDARY_BG};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton:disabled {{
                background: transparent;
                color: {colors.BUTTON_DISABLED_TEXT};
                border: 1px solid {colors.BORDER_DARK};
            }}
        """)
    
    # 3. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class ButtonTechDanger(QPushButton):
    """科技风格危险按钮"""
    
    # 1. 初始化按钮
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = ThemeManager.instance()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {colors.BUTTON_DANGER_BG};
                color: {colors.BUTTON_DANGER_TEXT};
                border: 1px solid {colors.BUTTON_DANGER_BG};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {colors.BUTTON_DANGER_HOVER};
                border: 1px solid {colors.BUTTON_DANGER_HOVER};
            }}
            QPushButton:pressed {{
                background: {colors.BUTTON_DANGER_BG};
                border: 1px solid {colors.GLOW_RED};
            }}
            QPushButton:disabled {{
                background: {colors.BUTTON_DISABLED_BG};
                color: {colors.BUTTON_DISABLED_TEXT};
                border: 1px solid {colors.BORDER_DARK};
            }}
        """)
    
    # 3. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class ButtonIcon(QPushButton):
    """图标按钮（无边框）"""
    
    # 1. 初始化按钮
    def __init__(self, icon_path: str = "", size: int = 24, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.icon_path = icon_path
        self.icon_size = size
        
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(size, size))
        
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {colors.OVERLAY_LIGHT};
            }}
            QPushButton:pressed {{
                background: {colors.OVERLAY_MEDIUM};
            }}
            QPushButton:disabled {{
                opacity: 0.5;
            }}
        """)
    
    # 3. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

