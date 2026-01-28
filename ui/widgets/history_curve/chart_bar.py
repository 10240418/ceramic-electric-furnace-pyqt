"""
科技风格柱状图组件（基于 PyQtGraph）
"""
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager


class ChartBar(QWidget):
    """科技风格柱状图"""
    
    # 1. 初始化组件
    def __init__(self, 
                 y_label: str = "", 
                 accent_color: str = None,
                 show_grid: bool = True,
                 parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.y_label = y_label
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        self.show_grid = show_grid
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建 PyQtGraph 图表
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)
        self.plot_widget.showGrid(x=False, y=self.show_grid, alpha=0.3)
        
        # 设置坐标轴标签
        if self.y_label:
            self.plot_widget.setLabel('left', self.y_label)
        
        layout.addWidget(self.plot_widget)
    
    # 3. 更新柱状图数据
    def update_data(self, labels: list[str], values: list[float]):
        """
        更新柱状图数据
        labels: X轴标签列表
        values: Y轴数值列表
        """
        self.plot_widget.clear()
        
        if not labels or not values:
            return
        
        # 创建柱状图
        x = list(range(len(labels)))
        width = 0.6
        
        # 创建 BarGraphItem
        bar_item = pg.BarGraphItem(
            x=x, 
            height=values, 
            width=width, 
            brush=self.accent_color,
            pen=pg.mkPen(color=self.accent_color, width=1)
        )
        self.plot_widget.addItem(bar_item)
        
        # 设置X轴刻度标签
        x_dict = {i: label for i, label in enumerate(labels)}
        x_axis = self.plot_widget.getAxis('bottom')
        x_axis.setTicks([list(x_dict.items())])
        
        # 自动调整Y轴范围
        if values:
            max_val = max(values)
            self.plot_widget.setYRange(0, max_val * 1.1)
    
    # 4. 更新分组柱状图数据
    def update_grouped_data(self, labels: list[str], data_dict: dict[str, list[float]], colors: list[str] = None):
        """
        更新分组柱状图数据
        labels: X轴标签列表
        data_dict: {系列名: [值列表], ...}
        colors: 颜色列表（可选）
        """
        self.plot_widget.clear()
        
        if not labels or not data_dict:
            return
        
        # 默认颜色
        if not colors:
            theme_colors = self.theme_manager.get_colors()
            colors = [
                theme_colors.CHART_LINE_1,
                theme_colors.CHART_LINE_2,
                theme_colors.CHART_LINE_3,
                theme_colors.CHART_LINE_4,
                theme_colors.CHART_LINE_5,
                theme_colors.CHART_LINE_6,
            ]
        
        # 计算柱子宽度和位置
        num_groups = len(labels)
        num_series = len(data_dict)
        total_width = 0.8
        bar_width = total_width / num_series
        
        # 添加图例
        legend = self.plot_widget.addLegend(offset=(10, 10))
        
        # 绘制每个系列
        for i, (series_name, values) in enumerate(data_dict.items()):
            # 计算每个柱子的X位置
            x_positions = [j + (i - num_series / 2 + 0.5) * bar_width for j in range(num_groups)]
            
            # 创建柱状图
            color = colors[i % len(colors)]
            bar_item = pg.BarGraphItem(
                x=x_positions,
                height=values,
                width=bar_width,
                brush=color,
                pen=pg.mkPen(color=color, width=1),
                name=series_name
            )
            self.plot_widget.addItem(bar_item)
        
        # 设置X轴刻度标签
        x_dict = {i: label for i, label in enumerate(labels)}
        x_axis = self.plot_widget.getAxis('bottom')
        x_axis.setTicks([list(x_dict.items())])
        
        # 自动调整Y轴范围
        all_values = [v for values in data_dict.values() for v in values]
        if all_values:
            max_val = max(all_values)
            self.plot_widget.setYRange(0, max_val * 1.1)
    
    # 5. 清空图表
    def clear(self):
        self.plot_widget.clear()
    
    # 6. 设置Y轴范围
    def set_y_range(self, min_y: float, max_y: float):
        self.plot_widget.setYRange(min_y, max_y)
    
    # 7. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 设置背景色
        self.plot_widget.setBackground(colors.BG_DARK)
        
        # 设置坐标轴样式
        axis_pen = pg.mkPen(color=colors.BORDER_MEDIUM, width=1)
        self.plot_widget.getAxis('left').setPen(axis_pen)
        self.plot_widget.getAxis('bottom').setPen(axis_pen)
        
        # 设置文字颜色
        text_color = colors.TEXT_SECONDARY
        font = QFont("Microsoft YaHei", 10)
        
        for axis in ['left', 'bottom']:
            ax = self.plot_widget.getAxis(axis)
            ax.setTextPen(text_color)
            ax.setTickFont(font)
        
        # 设置网格线颜色
        if self.show_grid:
            self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
    
    # 8. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

