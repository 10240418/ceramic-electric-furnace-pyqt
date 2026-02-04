"""
批次对比页面 - 显示多个批次的柱状图对比（6宫格布局）
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from ui.widgets.history_curve import WidgetBatchCompare


class PageBatchCompare(QWidget):
    """批次对比页面 - 使用 WidgetBatchCompare 组件"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 使用批次对比组件
        self.batch_compare_widget = WidgetBatchCompare()
        layout.addWidget(self.batch_compare_widget)
    
    # 3. 更新批次数据（代理方法）
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
        self.batch_compare_widget.update_batch_data(batch_data)

