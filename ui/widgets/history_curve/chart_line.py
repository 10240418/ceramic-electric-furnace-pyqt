"""
科技风格折线图组件（基于 PyQtGraph）
"""
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from ui.styles.themes import ThemeManager
from datetime import datetime


class TimeAxisItem(pg.AxisItem):
    """自定义时间轴"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def tickStrings(self, values, scale, spacing):
        """将时间戳转换为 HH:MM 格式"""
        strings = []
        for v in values:
            try:
                dt = datetime.fromtimestamp(v)
                strings.append(dt.strftime('%H:%M'))
            except:
                strings.append('')
        return strings


class ChartLine(QWidget):
    """科技风格折线图"""
    
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
        
        # 数据缓存
        self.data_series = []  # [(label, x_data, y_data, color), ...]
        
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
        
        # 创建 PyQtGraph 图表（使用自定义时间轴）
        axis_items = {'bottom': TimeAxisItem(orientation='bottom')}
        self.plot_widget = pg.PlotWidget(axisItems=axis_items)
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
        
        # 添加图例
        self.plot_widget.addLegend(offset=(10, 10))
        
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
    
    # 3. 更新单条曲线数据
    def update_data(self, x_data: list, y_data: list, label: str = "数据"):
        """更新单条曲线"""
        self.plot_widget.clear()
        
        if not x_data or not y_data:
            return
        
        # 绘制曲线
        pen = pg.mkPen(color=self.accent_color, width=2)
        self.plot_widget.plot(x_data, y_data, pen=pen, name=label)
        
        # 保存初始视图范围
        if self.enable_mouse:
            self.save_initial_view()
    
    # 3.1. 更新单条曲线数据（带时间轴）
    def update_data_with_time(self, x_data: list, y_data: list, label: str = "数据"):
        """更新单条曲线（X轴为时间戳）"""
        self.plot_widget.clear()
        
        if not x_data or not y_data:
            return
        
        # 绘制曲线
        pen = pg.mkPen(color=self.accent_color, width=2)
        self.plot_widget.plot(x_data, y_data, pen=pen, name=label)
        
        # 保存初始视图范围
        if self.enable_mouse:
            self.save_initial_view()
    
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
        
        # 保存初始视图范围
        if self.enable_mouse:
            self.save_initial_view()
    
    # 4.1. 更新多条曲线数据（带时间轴）
    def update_multi_data_with_time(self, data_list: list):
        """
        更新多条曲线（X轴为时间戳）
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
        
        # 保存初始视图范围
        if self.enable_mouse:
            self.save_initial_view()
    
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


