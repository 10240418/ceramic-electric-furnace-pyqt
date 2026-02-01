"""
批次对比页面组件 - 显示多个批次的柱状图对比（6宫格布局）
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.history_curve.chart_bar import ChartBar


class PageBatchCompare(QWidget):
    """批次对比页面 - 6宫格布局（3行2列）"""
    
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
    
    # 2. 初始化 UI（6宫格布局）
    def init_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        colors = self.theme_manager.get_colors()
        
        # 第1行第1列：累计能耗对比
        self.energy_panel = PanelTech("累计能耗对比 (kWh)")
        self.energy_chart = ChartBar(y_label="", accent_color=colors.GLOW_YELLOW)
        energy_layout = QVBoxLayout()
        energy_layout.setContentsMargins(0, 0, 0, 0)
        energy_layout.addWidget(self.energy_chart)
        self.energy_panel.set_content_layout(energy_layout)
        main_layout.addWidget(self.energy_panel, 0, 0)
        
        # 第1行第2列：累计投料对比
        self.feeding_panel = PanelTech("累计投料对比 (kg)")
        self.feeding_chart = ChartBar(y_label="", accent_color=colors.GLOW_ORANGE)
        feeding_layout = QVBoxLayout()
        feeding_layout.setContentsMargins(0, 0, 0, 0)
        feeding_layout.addWidget(self.feeding_chart)
        self.feeding_panel.set_content_layout(feeding_layout)
        main_layout.addWidget(self.feeding_panel, 0, 1)
        
        # 第2行第1列：炉皮累计水流量对比
        self.shell_water_panel = PanelTech("炉皮累计水流量对比 (m³)")
        self.shell_water_chart = ChartBar(y_label="", accent_color=colors.GLOW_BLUE)
        shell_water_layout = QVBoxLayout()
        shell_water_layout.setContentsMargins(0, 0, 0, 0)
        shell_water_layout.addWidget(self.shell_water_chart)
        self.shell_water_panel.set_content_layout(shell_water_layout)
        main_layout.addWidget(self.shell_water_panel, 1, 0)
        
        # 第2行第2列：炉盖累计水流量对比
        self.cover_water_panel = PanelTech("炉盖累计水流量对比 (m³)")
        self.cover_water_chart = ChartBar(y_label="", accent_color=colors.GLOW_CYAN)
        cover_water_layout = QVBoxLayout()
        cover_water_layout.setContentsMargins(0, 0, 0, 0)
        cover_water_layout.addWidget(self.cover_water_chart)
        self.cover_water_panel.set_content_layout(cover_water_layout)
        main_layout.addWidget(self.cover_water_panel, 1, 1)
        
        # 第3行第1列：开炉时长对比
        self.duration_panel = PanelTech("开炉时长对比 (小时)")
        self.duration_chart = ChartBar(y_label="", accent_color=colors.GLOW_GREEN)
        duration_layout = QVBoxLayout()
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.addWidget(self.duration_chart)
        self.duration_panel.set_content_layout(duration_layout)
        main_layout.addWidget(self.duration_panel, 2, 0)
        
        # 第3行第2列：预留（可以添加其他对比指标）
        self.reserved_panel = PanelTech("预留对比项")
        reserved_label = QWidget()
        reserved_layout = QVBoxLayout()
        reserved_layout.setContentsMargins(0, 0, 0, 0)
        reserved_layout.addWidget(reserved_label)
        self.reserved_panel.set_content_layout(reserved_layout)
        main_layout.addWidget(self.reserved_panel, 2, 1)
        
        # 设置行列拉伸比例（均匀分布）
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
    
    # 3. 更新批次数据
    def update_batch_data(self, batch_data: dict):
        """
        更新批次数据
        batch_data 格式:
        {
            'batches': ['20260128001', '20260128002', ...],
            'energy_total': {'20260128001': 1500.5, ...},
            'feeding_total': {'20260128001': 3580, ...},
            'shell_water_total': {'20260128001': 125.5, ...},
            'cover_water_total': {'20260128001': 98.3, ...},
            'duration_hours': {'20260128001': 8.5, ...}
        }
        """
        self.batch_data = batch_data
        self.update_charts()
    
    # 4. 更新图表
    def update_charts(self):
        if not self.batch_data:
            return
        
        batches = self.batch_data.get('batches', [])
        
        # 累计能耗对比
        energy_values = [self.batch_data.get('energy_total', {}).get(b, 0) for b in batches]
        self.energy_chart.update_data(batches, energy_values)
        
        # 累计投料对比
        feeding_values = [self.batch_data.get('feeding_total', {}).get(b, 0) for b in batches]
        self.feeding_chart.update_data(batches, feeding_values)
        
        # 炉皮累计水流量对比
        shell_values = [self.batch_data.get('shell_water_total', {}).get(b, 0) for b in batches]
        self.shell_water_chart.update_data(batches, shell_values)
        
        # 炉盖累计水流量对比
        cover_values = [self.batch_data.get('cover_water_total', {}).get(b, 0) for b in batches]
        self.cover_water_chart.update_data(batches, cover_values)
        
        # 开炉时长对比
        duration_values = [self.batch_data.get('duration_hours', {}).get(b, 0) for b in batches]
        self.duration_chart.update_data(batches, duration_values)
    
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

