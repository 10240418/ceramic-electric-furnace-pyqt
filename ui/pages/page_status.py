"""
状态监控页面 - DB30/DB41 设备状态监控
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from ui.styles.themes import ThemeManager
from ui.widgets.status.card_status_db30 import CardStatusDb30
from ui.widgets.status.card_status_db41 import CardStatusDb41
from backend.services.polling_data_processor import (
    get_latest_status_data,
    get_latest_db41_data
)


class PageStatus(QWidget):
    """状态监控页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        self.init_ui()
        self.apply_styles()
        
        # 定时器定期刷新数据 (5秒)，页面显示时才启动
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
    
    # 2. 页面显示时启动定时器
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()  # 立即刷新一次
        self.refresh_timer.start(5000)
    
    # 3. 页面隐藏时停止定时器
    def hideEvent(self, event):
        super().hideEvent(event)
        self.refresh_timer.stop()
    
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
    
    # 3. 刷新后端数据
    def refresh_data(self):
        # 获取 DB30 通信状态数据
        db30_result = get_latest_status_data()
        db30_data = db30_result.get('data', {})
        
        if db30_data:
            devices_dict = db30_data.get('devices', {})
            db30_devices = []
            for device_id, device_info in devices_dict.items():
                db30_devices.append({
                    'name': device_info.get('device_name', device_id),
                    'done': device_info.get('done', False),
                    'busy': device_info.get('busy', False),
                    'error': device_info.get('error', False),
                    'status': device_info.get('status', 0)
                })
            
            if db30_devices:
                self.card_db30.update_devices(db30_devices)
        
        # 获取 DB41 数据状态
        db41_result = get_latest_db41_data()
        db41_data = db41_result.get('data', {})
        
        if db41_data:
            devices_dict = db41_data.get('devices', {})
            db41_devices = []
            for device_id, device_info in devices_dict.items():
                db41_devices.append({
                    'name': device_info.get('device_name', device_id),
                    'error': device_info.get('error', False),
                    'status': device_info.get('status', 0)
                })
            
            if db41_devices:
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
                background: {tm.bg_deep()};
            }}
            
            QWidget {{
                background: {tm.bg_deep()};
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

