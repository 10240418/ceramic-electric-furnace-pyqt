"""
泵房/料仓页面 - 包含除尘器、水泵、料仓等设备
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from pathlib import Path
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.realtime_data.card_data import CardData, DataItem
from ui.widgets.realtime_data.hopper import CardHopper, DialogHopperDetail
from backend.bridge.data_cache import get_data_cache
from datetime import datetime, timedelta
import random
from loguru import logger


class PagePumpHopper(QWidget):
    """泵房/料仓页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.data_cache = get_data_cache()
        
        # 模拟投料记录数据
        self.feeding_records = []
        self.generate_mock_feeding_records()
        
        self.init_ui()
        self.apply_styles()
        
        # 定时器：定期更新料仓数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_hopper_data)
        self.timer.start(1000)
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # 顶部：料仓卡片
        self.hopper_card = CardHopper()
        self.hopper_card.detail_clicked.connect(self.show_hopper_detail)
        main_layout.addWidget(self.hopper_card)
        
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
    
    # 6. 生成模拟投料记录
    def generate_mock_feeding_records(self):
        """生成模拟投料记录数据"""
        base_time = datetime.now()
        for i in range(20):
            timestamp = base_time - timedelta(hours=i, minutes=random.randint(0, 59))
            weight = random.uniform(100, 500)
            self.feeding_records.append({
                'timestamp': timestamp,
                'weight': weight
            })
        
        # 按时间排序（最新的在前）
        self.feeding_records.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 7. 更新料仓数据
    def update_hopper_data(self):
        """定期更新料仓数据"""
        # 从缓存读取数据（如果有的话）
        hopper_data = self.data_cache.get("hopper_data")
        
        if hopper_data:
            hopper_weight = hopper_data.get('weight', 0.0)
            feeding_total = hopper_data.get('feeding_total', 0.0)
            upper_limit = hopper_data.get('upper_limit', 5000.0)
            is_feeding = hopper_data.get('is_feeding', False)
        else:
            # 模拟数据
            hopper_weight = random.uniform(3000, 4500)
            feeding_total = random.uniform(10000, 15000)
            upper_limit = 5000.0
            is_feeding = random.choice([True, False])
        
        # 更新料仓卡片
        self.hopper_card.update_data(
            hopper_weight=hopper_weight,
            feeding_total=feeding_total,
            upper_limit=upper_limit,
            is_feeding=is_feeding
        )
    
    # 8. 显示料仓详情弹窗
    def show_hopper_detail(self):
        """显示料仓详情弹窗"""
        dialog = DialogHopperDetail(self)
        
        # 获取当前料仓数据
        hopper_data = self.data_cache.get("hopper_data")
        
        if hopper_data:
            hopper_weight = hopper_data.get('weight', 0.0)
            feeding_total = hopper_data.get('feeding_total', 0.0)
            upper_limit = hopper_data.get('upper_limit', 5000.0)
            is_feeding = hopper_data.get('is_feeding', False)
        else:
            # 模拟数据
            hopper_weight = random.uniform(3000, 4500)
            feeding_total = random.uniform(10000, 15000)
            upper_limit = 5000.0
            is_feeding = random.choice([True, False])
        
        # 更新弹窗数据
        dialog.update_data(
            feeding_total=feeding_total,
            hopper_weight=hopper_weight,
            upper_limit=upper_limit,
            is_feeding=is_feeding
        )
        
        # 设置投料记录
        dialog.set_feeding_records(self.feeding_records)
        
        # 连接信号
        dialog.upper_limit_set.connect(self.on_upper_limit_set)
        
        logger.info("打开料仓详情弹窗")
        dialog.exec()
    
    # 9. 料仓上限设置完成
    def on_upper_limit_set(self, limit: float):
        """料仓上限设置完成"""
        logger.info(f"料仓上限已设置: {limit} kg")
        
        # 更新缓存中的料仓上限
        hopper_data = self.data_cache.get("hopper_data") or {}
        hopper_data['upper_limit'] = limit
        self.data_cache.set("hopper_data", hopper_data)
        
        # 立即更新料仓卡片
        self.update_hopper_data()
    
    # 10. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

