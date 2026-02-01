"""
泵房/料仓页面 - 包含除尘器、水泵等设备（料仓功能已迁移到 page_elec_3.py）
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from loguru import logger


class PagePumpHopper(QWidget):
    """泵房/料仓页面（暂时只显示除尘器和水泵）"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # 水平布局
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)
        
        # 左侧：除尘器
        self.create_dust_collector_panel()
        h_layout.addWidget(self.dust_panel, stretch=1)
        
        # 右侧：水泵图片
        self.create_waterpump_panel()
        h_layout.addWidget(self.waterpump_panel, stretch=1)
        
        main_layout.addLayout(h_layout)
    
    # 3. 创建除尘器面板
    def create_dust_collector_panel(self):
        self.dust_panel = PanelTech("除尘器")
        
        # 加载除尘器图片
        dust_path = Path(__file__).parent.parent.parent / "assets" / "images" / "dust_collector.png"
        dust_label = QLabel()
        
        if dust_path.exists():
            pixmap = QPixmap(str(dust_path))
            scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            dust_label.setPixmap(scaled_pixmap)
            dust_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            dust_label.setText("除尘器图片\n(dust_collector.png)")
            dust_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            colors = self.theme_manager.get_colors()
            dust_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_SECONDARY};
                    font-size: 14px;
                    background: {colors.BG_MEDIUM};
                    border: 2px dashed {colors.BORDER_DARK};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """)
        
        layout = QVBoxLayout()
        layout.addWidget(dust_label)
        self.dust_panel.set_content_layout(layout)
    
    # 4. 创建水泵面板
    def create_waterpump_panel(self):
        self.waterpump_panel = PanelTech("水泵")
        
        # 加载水泵图片
        pump_path = Path(__file__).parent.parent.parent / "assets" / "images" / "waterpump.png"
        pump_label = QLabel()
        
        if pump_path.exists():
            pixmap = QPixmap(str(pump_path))
            scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            pump_label.setPixmap(scaled_pixmap)
            pump_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            pump_label.setText("水泵图片\n(waterpump.png)")
            pump_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            colors = self.theme_manager.get_colors()
            pump_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_SECONDARY};
                    font-size: 14px;
                    background: {colors.BG_MEDIUM};
                    border: 2px dashed {colors.BORDER_DARK};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """)
        
        layout = QVBoxLayout()
        layout.addWidget(pump_label)
        self.waterpump_panel.set_content_layout(layout)
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            PagePumpHopper {{
                background: {colors.BG_DEEP};
            }}
        """)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


