"""
批次对比页面组件 - 显示多个批次的柱状图对比
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.history_curve.chart_bar import ChartBar


class PageBatchCompare(QWidget):
    """批次对比页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 批次数据
        self.batch_data = {}
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        colors = self.theme_manager.get_colors()
        
        # 上半部分容器（70%）
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        
        # 投料重量对比（上半部分的上部，50%）
        self.feed_weight_panel = PanelTech("投料重量对比")
        self.feed_weight_chart = ChartBar(y_label="kg", accent_color=colors.GLOW_ORANGE)
        feed_layout = QVBoxLayout()
        feed_layout.setContentsMargins(0, 0, 0, 0)
        feed_layout.addWidget(self.feed_weight_chart)
        self.feed_weight_panel.set_content_layout(feed_layout)
        top_layout.addWidget(self.feed_weight_panel, 1)
        
        # 炉皮冷却水用量对比（上半部分的下部，50%）
        self.shell_water_panel = PanelTech("炉皮冷却水用量对比")
        self.shell_water_chart = ChartBar(y_label="m³", accent_color=colors.GLOW_BLUE)
        shell_water_layout = QVBoxLayout()
        shell_water_layout.setContentsMargins(0, 0, 0, 0)
        shell_water_layout.addWidget(self.shell_water_chart)
        self.shell_water_panel.set_content_layout(shell_water_layout)
        top_layout.addWidget(self.shell_water_panel, 1)
        
        # 炉盖冷却水用量对比（下半部分，30%）
        self.cover_water_panel = PanelTech("炉盖冷却水用量对比")
        self.cover_water_chart = ChartBar(y_label="m³", accent_color=colors.GLOW_CYAN)
        cover_water_layout = QVBoxLayout()
        cover_water_layout.setContentsMargins(0, 0, 0, 0)
        cover_water_layout.addWidget(self.cover_water_chart)
        self.cover_water_panel.set_content_layout(cover_water_layout)
        
        # 添加到主布局（70% + 30%）
        main_layout.addWidget(top_container, 7)
        main_layout.addWidget(self.cover_water_panel, 3)
    
    # 3. 更新批次数据
    def update_batch_data(self, batch_data: dict):
        """
        更新批次数据
        batch_data 格式:
        {
            'batches': ['20260128001', '20260128002', ...],
            'feed_weight': {'20260128001': 3580, ...},
            'shell_water': {'20260128001': 125.5, ...},
            'cover_water': {'20260128001': 98.3, ...}
        }
        """
        self.batch_data = batch_data
        self.update_charts()
    
    # 4. 更新图表
    def update_charts(self):
        if not self.batch_data:
            return
        
        batches = self.batch_data.get('batches', [])
        
        # 投料重量对比
        feed_values = [self.batch_data.get('feed_weight', {}).get(b, 0) for b in batches]
        self.feed_weight_chart.update_data(batches, feed_values)
        
        # 炉皮冷却水用量对比
        shell_values = [self.batch_data.get('shell_water', {}).get(b, 0) for b in batches]
        self.shell_water_chart.update_data(batches, shell_values)
        
        # 炉盖冷却水用量对比
        cover_values = [self.batch_data.get('cover_water', {}).get(b, 0) for b in batches]
        self.cover_water_chart.update_data(batches, cover_values)
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            PageBatchCompare {{
                background: {colors.BG_DEEP};
            }}
        """)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

