"""
科技风格折线图组件（基于 PyQtGraph）
"""
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager


class ChartLine(QWidget):
    """科技风格折线图"""
    
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
        
        # 数据缓存
        self.data_series = []  # [(label, x_data, y_data, color), ...]
        
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
        
        # 添加图例
        self.plot_widget.addLegend(offset=(10, 10))
        
        layout.addWidget(self.plot_widget)
    
    # 3. 更新单条曲线数据
    def update_data(self, x_data: list, y_data: list, label: str = "数据"):
        """更新单条曲线"""
        self.plot_widget.clear()
        
        if not x_data or not y_data:
            return
        
        # 绘制曲线
        pen = pg.mkPen(color=self.accent_color, width=2)
        self.plot_widget.plot(x_data, y_data, pen=pen, name=label)
    
    # 4. 更新多条曲线数据
    def update_multi_data(self, data_list: list):
        """
        更新多条曲线
        data_list: [(label, x_data, y_data, color), ...]
        """
        self.plot_widget.clear()
        
        if not data_list:
            return
        
        colors = self.theme_manager.get_colors()
        default_colors = [
            colors.CHART_LINE_1,
            colors.CHART_LINE_2,
            colors.CHART_LINE_3,
            colors.CHART_LINE_4,
            colors.CHART_LINE_5,
            colors.CHART_LINE_6,
        ]
        
        for i, data in enumerate(data_list):
            if len(data) == 3:
                label, x_data, y_data = data
                color = default_colors[i % len(default_colors)]
            else:
                label, x_data, y_data, color = data
            
            if not x_data or not y_data:
                continue
            
            # 绘制曲线
            pen = pg.mkPen(color=color, width=2)
            self.plot_widget.plot(x_data, y_data, pen=pen, name=label)
    
    # 5. 清空图表
    def clear(self):
        self.plot_widget.clear()
    
    # 6. 设置Y轴范围
    def set_y_range(self, min_y: float, max_y: float):
        self.plot_widget.setYRange(min_y, max_y)
    
    # 7. 设置X轴范围
    def set_x_range(self, min_x: float, max_x: float):
        self.plot_widget.setXRange(min_x, max_x)
    
    # 8. 应用样式
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
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        # 重新绘制数据
        if self.data_series:
            self.update_multi_data(self.data_series)

