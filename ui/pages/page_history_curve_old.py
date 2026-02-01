"""
历史曲线页面 - 重构版（只保留折线图模式）
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.history_curve.chart_line import ChartLine
from ui.widgets.history_curve.dropdown_tech import DropdownTech, DropdownMultiSelect
from ui.widgets.history_curve.widget_time_selector import WidgetTimeSelector
from ui.pages.page_batch_compare import PageBatchCompare
import random


class PageHistoryCurve(QWidget):
    """历史曲线页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 状态变量
        self.is_history_mode = False  # 是否为历史轮次查询模式
        self.selected_batch = "20260128001"
        self.selected_batches = ["20260128001"]
        
        # 下拉选项
        self.batch_options = ["20260128001", "20260128002", "20260128003", "20260127001"]
        
        # 弧压/流/电极选项
        self.arc_options = ["弧流", "弧压", "电极高度"]
        
        # 功率/能耗选项
        self.power_options = ["功率", "能耗"]
        
        # 料仓选项
        self.hopper_options = ["蝶阀开度", "投料量"]
        
        # 冷却水选项
        self.cooling_options = ["炉皮冷却水流量", "炉皮冷却水流速", "炉盖冷却水流量", "炉盖冷却水流速", "过滤器压差"]
        
        # 当前选择
        self.arc_select = "弧流"
        self.power_select = "功率"
        self.hopper_select = "蝶阀开度"
        self.cooling_select = "炉皮冷却水流量"
        
        # 模拟数据
        self.generate_mock_data()
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 启动数据更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_charts)
        self.update_timer.start(2000)
    
    # 2. 生成模拟数据
    def generate_mock_data(self):
        # 折线图模拟数据（时间序列）
        self.mock_time_labels = [f"{i:02d}:00" for i in range(0, 24, 2)]
        
        # 弧流数据（3条线）
        self.mock_arc_current_data = {
            "电极1": [2800 + random.randint(-200, 200) for _ in range(12)],
            "电极2": [2900 + random.randint(-200, 200) for _ in range(12)],
            "电极3": [2850 + random.randint(-200, 200) for _ in range(12)],
        }
        
        # 弧压数据（3条线）
        self.mock_arc_voltage_data = {
            "电极1": [140 + random.randint(-10, 10) for _ in range(12)],
            "电极2": [145 + random.randint(-10, 10) for _ in range(12)],
            "电极3": [142 + random.randint(-10, 10) for _ in range(12)],
        }
        
        # 电极高度数据（3条线）
        self.mock_electrode_height_data = {
            "电极1": [-150 + random.randint(-20, 20) for _ in range(12)],
            "电极2": [-155 + random.randint(-20, 20) for _ in range(12)],
            "电极3": [-148 + random.randint(-20, 20) for _ in range(12)],
        }
        
        # 功率数据
        self.mock_power_data = [1500 + random.randint(-100, 100) for _ in range(12)]
        
        # 能耗数据
        self.mock_energy_data = [3200 + random.randint(-200, 200) for _ in range(12)]
        
        # 蝶阀开度数据（4条线）
        self.mock_valve_data = {
            "蝶阀1": [75 + random.randint(-5, 5) for _ in range(12)],
            "蝶阀2": [70 + random.randint(-5, 5) for _ in range(12)],
            "蝶阀3": [80 + random.randint(-5, 5) for _ in range(12)],
            "蝶阀4": [72 + random.randint(-5, 5) for _ in range(12)],
        }
        
        # 投料量数据
        self.mock_feed_data = [1200 + random.randint(-100, 100) for _ in range(12)]
        
        # 冷却水数据
        self.mock_cooling_data = {
            "炉皮冷却水流量": [3.5 + random.uniform(-0.5, 0.5) for _ in range(12)],
            "炉皮冷却水流速": [2.8 + random.uniform(-0.4, 0.4) for _ in range(12)],
            "炉盖冷却水流量": [2.2 + random.uniform(-0.3, 0.3) for _ in range(12)],
            "炉盖冷却水流速": [1.8 + random.uniform(-0.2, 0.2) for _ in range(12)],
            "过滤器压差": [0.5 + random.uniform(-0.1, 0.1) for _ in range(12)],
        }
        
        # 柱状图模拟数据（批次对比）
        self.mock_batch_data = {
            'batches': self.batch_options,
            'feed_weight': {
                "20260128001": 3580,
                "20260128002": 3620,
                "20260128003": 3550,
                "20260127001": 3600,
            },
            'shell_water': {
                "20260128001": 125.5,
                "20260128002": 130.2,
                "20260128003": 122.8,
                "20260127001": 128.0,
            },
            'cover_water': {
                "20260128001": 98.3,
                "20260128002": 102.5,
                "20260128003": 95.7,
                "20260127001": 100.1,
            }
        }
    
    # 3. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 顶部控制栏
        self.create_control_bar()
        main_layout.addWidget(self.control_bar)
        
        # 内容区域（可滚动）
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        
        # 创建折线图模式布局
        self.create_line_chart_mode()
        
        # 创建批次对比页面
        self.batch_compare_page = PageBatchCompare()
        self.batch_compare_page.hide()
        self.content_layout.addWidget(self.batch_compare_page)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        main_layout.addWidget(scroll_area)
    
    # 4. 创建控制栏
    def create_control_bar(self):
        self.control_bar = QWidget()
        layout = QHBoxLayout(self.control_bar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(24)
        
        colors = self.theme_manager.get_colors()
        
        # 历史轮次查询按钮
        self.history_mode_btn = QPushButton("历史轮次查询")
        self.history_mode_btn.setFixedHeight(32)
        self.history_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_mode_btn.clicked.connect(self.toggle_history_mode)
        layout.addWidget(self.history_mode_btn)
        
        # 批次选择器（单选/多选切换）
        self.batch_dropdown = DropdownTech(
            self.batch_options, 
            self.selected_batch,
            accent_color=colors.GLOW_CYAN
        )
        self.batch_dropdown.selection_changed.connect(self.on_batch_changed)
        layout.addWidget(self.batch_dropdown)
        
        self.batch_multi_dropdown = DropdownMultiSelect(
            self.batch_options,
            self.selected_batches,
            accent_color=colors.GLOW_CYAN
        )
        self.batch_multi_dropdown.selection_changed.connect(self.on_batches_changed)
        self.batch_multi_dropdown.hide()
        layout.addWidget(self.batch_multi_dropdown)
        
        # 时间选择器（合并版）
        self.time_selector = WidgetTimeSelector(accent_color=colors.GLOW_CYAN)
        self.time_selector.time_range_changed.connect(self.on_time_range_changed)
        layout.addWidget(self.time_selector)
        
        layout.addStretch()
    
    # 5. 创建折线图模式布局
    def create_line_chart_mode(self):
        self.line_chart_container = QWidget()
        layout = QVBoxLayout(self.line_chart_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        colors = self.theme_manager.get_colors()
        
        # 第一行：弧压/流/电极 | 功率/能耗
        row1 = QWidget()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(8)
        
        # 弧压/流/电极面板
        self.arc_panel = PanelTech("弧压/流/电极")
        self.arc_panel.setMinimumHeight(300)
        
        # 弧压/流/电极下拉选择器
        self.arc_dropdown = DropdownTech(
            self.arc_options,
            self.arc_select,
            accent_color=colors.GLOW_CYAN
        )
        self.arc_dropdown.selection_changed.connect(self.on_arc_changed)
        self.arc_panel.add_header_action(self.arc_dropdown)
        
        # 弧压/流/电极图表
        self.arc_chart = ChartLine(y_label="A", accent_color=colors.GLOW_CYAN)
        arc_layout = QVBoxLayout()
        arc_layout.setContentsMargins(0, 0, 0, 0)
        arc_layout.addWidget(self.arc_chart)
        self.arc_panel.set_content_layout(arc_layout)
        
        row1_layout.addWidget(self.arc_panel, stretch=1)
        
        # 功率/能耗面板
        self.power_panel = PanelTech("功率/能耗")
        self.power_panel.setMinimumHeight(300)
        
        # 功率/能耗下拉选择器
        self.power_dropdown = DropdownTech(
            self.power_options,
            self.power_select,
            accent_color=colors.GLOW_ORANGE
        )
        self.power_dropdown.selection_changed.connect(self.on_power_changed)
        self.power_panel.add_header_action(self.power_dropdown)
        
        # 功率/能耗图表
        self.power_chart = ChartLine(y_label="kW", accent_color=colors.GLOW_ORANGE)
        power_layout = QVBoxLayout()
        power_layout.setContentsMargins(0, 0, 0, 0)
        power_layout.addWidget(self.power_chart)
        self.power_panel.set_content_layout(power_layout)
        
        row1_layout.addWidget(self.power_panel, stretch=1)
        
        layout.addWidget(row1)
        
        # 第二行：料仓 | 冷却水
        row2 = QWidget()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(8)
        
        # 料仓面板
        self.hopper_panel = PanelTech("料仓")
        self.hopper_panel.setMinimumHeight(300)
        
        # 料仓下拉选择器
        self.hopper_dropdown = DropdownTech(
            self.hopper_options,
            self.hopper_select,
            accent_color=colors.GLOW_BLUE
        )
        self.hopper_dropdown.selection_changed.connect(self.on_hopper_changed)
        self.hopper_panel.add_header_action(self.hopper_dropdown)
        
        # 料仓图表
        self.hopper_chart = ChartLine(y_label="%", accent_color=colors.GLOW_BLUE)
        hopper_layout = QVBoxLayout()
        hopper_layout.setContentsMargins(0, 0, 0, 0)
        hopper_layout.addWidget(self.hopper_chart)
        self.hopper_panel.set_content_layout(hopper_layout)
        
        row2_layout.addWidget(self.hopper_panel, stretch=1)
        
        # 冷却水面板
        self.cooling_panel = PanelTech("冷却水")
        self.cooling_panel.setMinimumHeight(300)
        
        # 冷却水下拉选择器
        self.cooling_dropdown = DropdownTech(
            self.cooling_options,
            self.cooling_select,
            accent_color=colors.GLOW_GREEN
        )
        self.cooling_dropdown.selection_changed.connect(self.on_cooling_changed)
        self.cooling_panel.add_header_action(self.cooling_dropdown)
        
        # 冷却水图表
        self.cooling_chart = ChartLine(y_label="m³/h", accent_color=colors.GLOW_GREEN)
        cooling_layout = QVBoxLayout()
        cooling_layout.setContentsMargins(0, 0, 0, 0)
        cooling_layout.addWidget(self.cooling_chart)
        self.cooling_panel.set_content_layout(cooling_layout)
        
        row2_layout.addWidget(self.cooling_panel, stretch=1)
        
        layout.addWidget(row2)
        
        self.content_layout.addWidget(self.line_chart_container)
    
    # 6. 切换历史模式
    def toggle_history_mode(self):
        self.is_history_mode = not self.is_history_mode
        
        if self.is_history_mode:
            # 切换到批次对比模式
            self.line_chart_container.hide()
            self.batch_compare_page.show()
            self.batch_dropdown.hide()
            self.batch_multi_dropdown.show()
            self.time_selector.hide()
            
            # 更新批次对比数据
            self.update_batch_compare()
        else:
            # 切换到折线图模式
            self.batch_compare_page.hide()
            self.line_chart_container.show()
            self.batch_multi_dropdown.hide()
            self.batch_dropdown.show()
            self.time_selector.show()
            
            self.update_line_charts()
        
        # 更新按钮样式
        self.update_history_mode_button()
    
    # 7. 更新历史模式按钮样式
    def update_history_mode_button(self):
        colors = self.theme_manager.get_colors()
        is_dark = self.theme_manager.is_dark_mode()
        
        if self.is_history_mode:
            # 选中状态
            if is_dark:
                selected_text = colors.GLOW_CYAN
            else:
                selected_text = colors.TEXT_INVERSE
            
            self.history_mode_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {colors.GLOW_CYAN}33;
                    color: {selected_text};
                    border: 1.5px solid {colors.GLOW_CYAN};
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {colors.GLOW_CYAN}4D;
                }}
            """)
        else:
            # 未选中状态
            if is_dark:
                bg_normal = f"{colors.BG_LIGHT}4D"
                bg_hover = f"{colors.BG_LIGHT}80"
            else:
                bg_normal = colors.BG_LIGHT
                bg_hover = colors.BG_MEDIUM
            
            self.history_mode_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg_normal};
                    color: {colors.TEXT_PRIMARY};
                    border: 1px solid {colors.BORDER_MEDIUM};
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {bg_hover};
                    border: 1px solid {colors.GLOW_CYAN};
                }}
            """)
    
    # 8. 更新折线图
    def update_line_charts(self):
        colors = self.theme_manager.get_colors()
        
        # 更新弧压/流/电极图表
        if self.arc_select == "弧流":
            data_list = [
                ("电极1", list(range(12)), self.mock_arc_current_data["电极1"], colors.CHART_LINE_1),
                ("电极2", list(range(12)), self.mock_arc_current_data["电极2"], colors.CHART_LINE_2),
                ("电极3", list(range(12)), self.mock_arc_current_data["电极3"], colors.CHART_LINE_3),
            ]
            self.arc_chart.plot_widget.setLabel('left', "电流 (A)")
        elif self.arc_select == "弧压":
            data_list = [
                ("电极1", list(range(12)), self.mock_arc_voltage_data["电极1"], colors.CHART_LINE_1),
                ("电极2", list(range(12)), self.mock_arc_voltage_data["电极2"], colors.CHART_LINE_2),
                ("电极3", list(range(12)), self.mock_arc_voltage_data["电极3"], colors.CHART_LINE_3),
            ]
            self.arc_chart.plot_widget.setLabel('left', "电压 (V)")
        else:
            data_list = [
                ("电极1", list(range(12)), self.mock_electrode_height_data["电极1"], colors.CHART_LINE_1),
                ("电极2", list(range(12)), self.mock_electrode_height_data["电极2"], colors.CHART_LINE_2),
                ("电极3", list(range(12)), self.mock_electrode_height_data["电极3"], colors.CHART_LINE_3),
            ]
            self.arc_chart.plot_widget.setLabel('left', "高度 (mm)")
        
        self.arc_chart.update_multi_data(data_list)
        
        # 更新功率/能耗图表
        x_data = list(range(12))
        if self.power_select == "功率":
            self.power_chart.update_data(x_data, self.mock_power_data, "功率")
            self.power_chart.plot_widget.setLabel('left', "功率 (kW)")
        else:
            self.power_chart.update_data(x_data, self.mock_energy_data, "能耗")
            self.power_chart.plot_widget.setLabel('left', "能耗 (kWh)")
        
        # 更新料仓图表
        if self.hopper_select == "蝶阀开度":
            data_list = [
                ("蝶阀1", x_data, self.mock_valve_data["蝶阀1"], colors.CHART_LINE_1),
                ("蝶阀2", x_data, self.mock_valve_data["蝶阀2"], colors.CHART_LINE_2),
                ("蝶阀3", x_data, self.mock_valve_data["蝶阀3"], colors.CHART_LINE_3),
                ("蝶阀4", x_data, self.mock_valve_data["蝶阀4"], colors.CHART_LINE_4),
            ]
            self.hopper_chart.update_multi_data(data_list)
            self.hopper_chart.plot_widget.setLabel('left', "开度 (%)")
        else:
            self.hopper_chart.update_data(x_data, self.mock_feed_data, "投料量")
            self.hopper_chart.plot_widget.setLabel('left', "投料量 (kg)")
        
        # 更新冷却水图表
        if self.cooling_select in self.mock_cooling_data:
            self.cooling_chart.update_data(x_data, self.mock_cooling_data[self.cooling_select], self.cooling_select)
            
            if "流量" in self.cooling_select:
                self.cooling_chart.plot_widget.setLabel('left', "流量 (m³/h)")
            elif "流速" in self.cooling_select:
                self.cooling_chart.plot_widget.setLabel('left', "流速 (m/s)")
            elif "压差" in self.cooling_select:
                self.cooling_chart.plot_widget.setLabel('left', "压差 (kPa)")
    
    # 9. 更新批次对比
    def update_batch_compare(self):
        # 筛选选中的批次
        selected_batches = [b for b in self.batch_options if b in self.selected_batches]
        
        # 准备批次数据
        batch_data = {
            'batches': selected_batches,
            'feed_weight': {b: self.mock_batch_data['feed_weight'].get(b, 0) for b in selected_batches},
            'shell_water': {b: self.mock_batch_data['shell_water'].get(b, 0) for b in selected_batches},
            'cover_water': {b: self.mock_batch_data['cover_water'].get(b, 0) for b in selected_batches}
        }
        
        self.batch_compare_page.update_batch_data(batch_data)
    
    # 10. 更新图表（定时器调用）
    def update_charts(self):
        # 模拟数据变化
        for key in self.mock_arc_current_data:
            for i in range(len(self.mock_arc_current_data[key])):
                self.mock_arc_current_data[key][i] += random.randint(-50, 50)
                self.mock_arc_current_data[key][i] = max(2000, min(3500, self.mock_arc_current_data[key][i]))
        
        for i in range(len(self.mock_power_data)):
            self.mock_power_data[i] += random.randint(-20, 20)
            self.mock_power_data[i] = max(1200, min(1800, self.mock_power_data[i]))
        
        # 更新当前模式的图表
        if self.is_history_mode:
            self.update_batch_compare()
        else:
            self.update_line_charts()
    
    # 11. 批次选择变化
    def on_batch_changed(self, batch: str):
        self.selected_batch = batch
        self.update_line_charts()
    
    # 12. 批次多选变化
    def on_batches_changed(self, batches: list[str]):
        self.selected_batches = batches
        self.update_batch_compare()
    
    # 13. 时间范围变化
    def on_time_range_changed(self, start, end):
        print(f"时间范围变化: {start.toString()} - {end.toString()}")
        self.update_line_charts()
    
    # 14. 弧压/流/电极选择变化
    def on_arc_changed(self, option: str):
        self.arc_select = option
        self.update_line_charts()
    
    # 15. 功率/能耗选择变化
    def on_power_changed(self, option: str):
        self.power_select = option
        self.update_line_charts()
    
    # 16. 料仓选择变化
    def on_hopper_changed(self, option: str):
        self.hopper_select = option
        self.update_line_charts()
    
    # 17. 冷却水选择变化
    def on_cooling_changed(self, option: str):
        self.cooling_select = option
        self.update_line_charts()
    
    # 18. 刷新数据
    def refresh_data(self):
        print("刷新数据")
        self.generate_mock_data()
        self.update_charts()
    
    # 19. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            PageHistoryCurve {{
                background: {colors.BG_DEEP};
            }}
            QScrollArea {{
                background: {colors.BG_DEEP};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {colors.BG_MEDIUM};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.BORDER_MEDIUM};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors.GLOW_CYAN};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.control_bar.setStyleSheet(f"""
            QWidget {{
                background: {colors.BG_DARK};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
            }}
        """)
        
        self.update_history_mode_button()
    
    # 20. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
