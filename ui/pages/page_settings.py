"""
系统配置页面 - 系统设置和配置管理
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager, Theme
from loguru import logger


class PageSettings(QWidget):
    """系统配置页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        self.init_ui()
        self.apply_styles()
    
    # 2. 初始化 UI
    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 页面标题
        title = QLabel("系统配置")
        title.setObjectName("page_title")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # 滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 主题设置区域
        theme_section = self.create_theme_section()
        scroll_layout.addWidget(theme_section)
        
        # 占位符（未来可以添加更多配置项）
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    # 3. 创建主题设置区域
    def create_theme_section(self):
        section = QFrame()
        section.setObjectName("settings_section")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 区域标题
        section_title = QLabel("外观设置")
        section_title.setObjectName("section_title")
        section_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(section_title)
        
        # 主题切换行
        theme_row = QHBoxLayout()
        theme_row.setSpacing(15)
        
        # 主题标签
        theme_label = QLabel("主题模式:")
        theme_label.setObjectName("setting_label")
        theme_label.setFont(QFont("Microsoft YaHei", 13))
        theme_row.addWidget(theme_label)
        
        # 浅色主题按钮
        self.btn_light_theme = QPushButton("浅色主题")
        self.btn_light_theme.setObjectName("btn_light_theme")
        self.btn_light_theme.setFixedSize(120, 40)
        self.btn_light_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_light_theme.clicked.connect(self.on_light_theme_clicked)
        theme_row.addWidget(self.btn_light_theme)
        
        # 深色主题按钮
        self.btn_dark_theme = QPushButton("深色主题")
        self.btn_dark_theme.setObjectName("btn_dark_theme")
        self.btn_dark_theme.setFixedSize(120, 40)
        self.btn_dark_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dark_theme.clicked.connect(self.on_dark_theme_clicked)
        theme_row.addWidget(self.btn_dark_theme)
        
        theme_row.addStretch()
        
        layout.addLayout(theme_row)
        
        # 主题说明
        theme_desc = QLabel("选择您喜欢的主题模式，更改将立即生效")
        theme_desc.setObjectName("setting_desc")
        theme_desc.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(theme_desc)
        
        return section
    
    # 4. 浅色主题按钮点击
    def on_light_theme_clicked(self):
        self.theme_manager.set_theme(Theme.LIGHT)
        logger.info("切换到浅色主题")
    
    # 5. 深色主题按钮点击
    def on_dark_theme_clicked(self):
        self.theme_manager.set_theme(Theme.DARK)
        logger.info("切换到深色主题")
    
    # 6. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        current_theme = tm.get_current_theme()
        
        # 页面背景
        self.setStyleSheet(f"""
            QWidget {{
                background: {tm.bg_deep()};
            }}
            
            /* 页面标题 */
            QLabel#page_title {{
                color: {tm.text_primary()};
            }}
            
            /* 设置区域 */
            QFrame#settings_section {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            /* 区域标题 */
            QLabel#section_title {{
                color: {tm.border_glow()};
            }}
            
            /* 设置标签 */
            QLabel#setting_label {{
                color: {tm.text_primary()};
            }}
            
            /* 设置说明 */
            QLabel#setting_desc {{
                color: {tm.text_secondary()};
            }}
            
            /* 滚动区域 */
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            
            /* 滚动条 */
            QScrollBar:vertical {{
                background: {tm.bg_medium()};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {tm.border_medium()};
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {tm.border_glow()};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # 更新主题按钮样式
        if current_theme == Theme.LIGHT:
            # 浅色主题激活
            self.btn_light_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.border_glow()};
                    color: {tm.white()};
                    border: 2px solid {tm.border_glow()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                
                QPushButton:hover {{
                    background: {tm.glow_primary()};
                    border: 2px solid {tm.glow_primary()};
                }}
            """)
            
            self.btn_dark_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.bg_medium()};
                    color: {tm.text_primary()};
                    border: 1px solid {tm.border_medium()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: normal;
                }}
                
                QPushButton:hover {{
                    background: {tm.bg_light()};
                    border: 1px solid {tm.border_glow()};
                }}
            """)
        else:
            # 深色主题激活
            self.btn_dark_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.border_glow()};
                    color: {tm.white()};
                    border: 2px solid {tm.border_glow()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                
                QPushButton:hover {{
                    background: {tm.glow_primary()};
                    border: 2px solid {tm.glow_primary()};
                }}
            """)
            
            self.btn_light_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.bg_medium()};
                    color: {tm.text_primary()};
                    border: 1px solid {tm.border_medium()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: normal;
                }}
                
                QPushButton:hover {{
                    background: {tm.bg_light()};
                    border: 1px solid {tm.border_glow()};
                }}
            """)

