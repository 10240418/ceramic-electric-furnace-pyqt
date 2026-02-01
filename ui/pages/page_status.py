"""
状态监控页面 - DB30/DB41 设备状态监控
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager
from ui.widgets.status.card_status_db30 import CardStatusDb30
from ui.widgets.status.card_status_db41 import CardStatusDb41


class PageStatus(QWidget):
    """状态监控页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        self.init_ui()
        self.apply_styles()
        self.load_mock_data()
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 内容容器
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # DB30 卡片
        self.card_db30 = CardStatusDb30()
        content_layout.addWidget(self.card_db30)
        
        # DB41 卡片
        self.card_db41 = CardStatusDb41()
        content_layout.addWidget(self.card_db41)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    # 3. 加载模拟数据
    def load_mock_data(self):
        # DB30 模拟数据 (Modbus 通信状态)
        db30_devices = [
            {"name": "1号测距", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "2号测距", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "3号测距", "done": False, "busy": True, "error": False, "status": 0x0000},
            {"name": "1号流量", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "2号流量", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "1号压力", "done": True, "busy": False, "error": True, "status": 0x8001},
            {"name": "2号压力", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "1号电表", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "2号电表", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "3号电表", "done": True, "busy": False, "error": False, "status": 0x0000},
            {"name": "4号电表", "done": False, "busy": False, "error": True, "status": 0x8002},
            {"name": "5号电表", "done": True, "busy": False, "error": False, "status": 0x0000},
        ]
        
        # DB41 模拟数据 (传感器数据状态)
        db41_devices = [
            {"name": "1号测距", "error": False, "status": 0x0000},
            {"name": "2号测距", "error": False, "status": 0x0000},
            {"name": "3号测距", "error": True, "status": 0x8001},
            {"name": "1号流量", "error": False, "status": 0x0000},
            {"name": "2号流量", "error": False, "status": 0x0000},
            {"name": "1号压力", "error": False, "status": 0x0000},
            {"name": "2号压力", "error": True, "status": 0x8003},
        ]
        
        self.card_db30.update_devices(db30_devices)
        self.card_db41.update_devices(db41_devices)
    
    # 4. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        self.setStyleSheet(f"""
            PageStatus {{
                background: {tm.bg_deep()};
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                background: {tm.bg_medium()};
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {tm.border_medium()};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {tm.border_glow()};
            }}
            
            QScrollBar::handle:vertical:pressed {{
                background: {tm.glow_primary()};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
                background: none;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

