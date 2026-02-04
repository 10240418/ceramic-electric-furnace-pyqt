"""
科技风格柱状图组件（基于 PyQtGraph）
"""
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from ui.styles.themes import ThemeManager


class ChartBar(QWidget):
    """科技风格柱状图"""
    
    # 1. 初始化组件
    def __init__(self, 
                 y_label: str = "", 
                 accent_color: str = None,
                 show_grid: bool = True,
                 enable_mouse: bool = True,
                 parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.y_label = y_label
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        self.show_grid = show_grid
        self.enable_mouse = enable_mouse
        
        # 保存初始视图范围
        self.initial_x_range = None
        self.initial_y_range = None
        
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
        
        # 设置鼠标交互
        if not self.enable_mouse:
            # 禁用所有鼠标交互
            self.plot_widget.setMouseEnabled(x=False, y=False)
            self.plot_widget.setMenuEnabled(False)
        else:
            # 启用鼠标交互，并添加自定义右键菜单
            self.plot_widget.setMouseEnabled(x=True, y=True)
            self.setup_context_menu()
        
        # 设置坐标轴标签
        if self.y_label:
            self.plot_widget.setLabel('left', self.y_label)
        
        layout.addWidget(self.plot_widget)
    
    # 2.1. 设置右键菜单
    def setup_context_menu(self):
        """设置自定义右键菜单"""
        # 获取 PlotItem 的 ViewBox
        view_box = self.plot_widget.getPlotItem().getViewBox()
        
        # 保存原始菜单
        self.original_menu = view_box.menu
        
        # 创建自定义菜单
        view_box.menu = None  # 先清空
        
        # 重写右键菜单
        def show_context_menu(ev):
            colors = self.theme_manager.get_colors()
            
            menu = QMenu()
            menu.setStyleSheet(f"""
                QMenu {{
                    background: {colors.BG_DARK};
                    border: 1px solid {colors.BORDER_MEDIUM};
                    border-radius: 4px;
                    padding: 4px;
                }}
                QMenu::item {{
                    color: {colors.TEXT_PRIMARY};
                    padding: 6px 20px;
                    border-radius: 2px;
                }}
                QMenu::item:selected {{
                    background: {colors.BORDER_MEDIUM};
                }}
            """)
            
            # 添加"复原视图"选项
            reset_action = QAction("复原视图", menu)
            reset_action.triggered.connect(self.reset_view)
            menu.addAction(reset_action)
            
            # 添加分隔线
            menu.addSeparator()
            
            # 添加"自动缩放"选项
            auto_range_action = QAction("自动缩放", menu)
            auto_range_action.triggered.connect(lambda: view_box.autoRange())
            menu.addAction(auto_range_action)
            
            # 显示菜单
            menu.exec(ev.screenPos().toPoint())
        
        # 绑定右键菜单
        view_box.raiseContextMenu = show_context_menu
    
    # 2.2. 复原视图
    def reset_view(self):
        """复原到初始视图"""
        if self.initial_x_range and self.initial_y_range:
            view_box = self.plot_widget.getPlotItem().getViewBox()
            view_box.setRange(xRange=self.initial_x_range, yRange=self.initial_y_range, padding=0)
        else:
            # 如果没有保存初始范围，则自动缩放
            self.plot_widget.getPlotItem().getViewBox().autoRange()
    
    # 2.3. 保存初始视图范围
    def save_initial_view(self):
        """保存当前视图范围为初始范围"""
        view_box = self.plot_widget.getPlotItem().getViewBox()
        self.initial_x_range = view_box.viewRange()[0]
        self.initial_y_range = view_box.viewRange()[1]
    
    # 3. 更新柱状图数据
    def update_data(self, labels: list[str], values: list[float]):
        """
        更新柱状图数据
        labels: X轴标签列表（批次号）
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
        
        # 在柱子上方显示数值
        colors = self.theme_manager.get_colors()
        for i, (label, value) in enumerate(zip(labels, values)):
            if value > 0:
                # 创建文本标签
                text_item = pg.TextItem(
                    text=f"{value:.1f}",
                    color=colors.TEXT_PRIMARY,
                    anchor=(0.5, 1.2)
                )
                text_item.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
                text_item.setPos(i, value)
                self.plot_widget.addItem(text_item)
        
        # 设置X轴刻度标签（批次号）
        x_dict = {i: label for i, label in enumerate(labels)}
        x_axis = self.plot_widget.getAxis('bottom')
        x_axis.setTicks([list(x_dict.items())])
        
        # 自动调整Y轴范围（留出空间显示数值）
        if values:
            max_val = max(values)
            self.plot_widget.setYRange(0, max_val * 1.2)
        
        # 复位视图（恢复初始缩放和平移）
        self.plot_widget.enableAutoRange()
        
        # 保存初始视图范围
        if self.enable_mouse:
            self.save_initial_view()
    
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
        
        # 保存初始视图范围
        if self.enable_mouse:
            self.save_initial_view()
    
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

