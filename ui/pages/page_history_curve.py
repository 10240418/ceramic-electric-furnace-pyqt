"""
历史曲线页面 - 重构版（只保留折线图模式）
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.history_curve.chart_line import ChartLine
from ui.widgets.history_curve.bar_history import BarHistory
from ui.pages.page_batch_compare import PageBatchCompare
from backend.bridge.history_query import get_history_query_service
from datetime import datetime, timedelta
from loguru import logger
import random


class PageHistoryCurve(QWidget):
    """历史曲线页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 后端查询服务
        self.history_service = get_history_query_service()
        
        # 状态变量
        self.is_history_mode = False
        self.selected_batch = ""
        self.selected_batches = []
        
        # 当前选择
        self.arc_select = "弧流"
        self.power_select = "功率"
        self.hopper_select = "投料量"
        self.cooling_select = "炉皮冷却水累计"
        
        # 数据缓存
        self.cached_data = {
            "arc_current": {"1": [], "2": [], "3": []},
            "arc_voltage": {"1": [], "2": [], "3": []},
            "electrode_depth": {"1": [], "2": [], "3": []},
            "power": [],
            "energy": [],
            "feeding_total": [],
            "shell_water": [],
            "cover_water": []
        }
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 延迟加载数据（等待 UI 渲染完成）
        QTimer.singleShot(500, self.load_initial_data)
    
    # 2. 加载初始数据
    def load_initial_data(self):
        """页面加载时自动查询最新批次的24h数据"""
        logger.info("开始加载初始数据...")
        
        # 等待 bar_history 加载完批次列表
        if not self.bar_history.get_selected_batch():
            logger.warning("批次列表尚未加载，延迟重试...")
            QTimer.singleShot(1000, self.load_initial_data)
            return
        
        # 获取最新批次
        self.selected_batch = self.bar_history.get_selected_batch()
        logger.info(f"使用最新批次: {self.selected_batch}")
        
        # 设置默认时间范围为24小时
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # 查询所有图表数据
        self.query_all_data(self.selected_batch, start_time, end_time)
    
    # 3. 查询所有数据
    def query_all_data(self, batch_code: str, start_time: datetime, end_time: datetime):
        """查询所有图表的历史数据"""
        if not batch_code:
            logger.warning("批次号为空，无法查询")
            return
        
        logger.info(f"开始查询批次 {batch_code} 的历史数据，时间范围: {start_time} - {end_time}")
        
        # 计算最佳聚合间隔
        interval = self.history_service.calculate_optimal_interval(start_time, end_time, target_points=100)
        logger.info(f"使用聚合间隔: {interval}")
        
        try:
            # 1. 查询弧流弧压数据
            arc_data = self.history_service.query_arc_data(batch_code, start_time, end_time, interval)
            self.cached_data["arc_current"] = arc_data.get("arc_current", {"U": [], "V": [], "W": []})
            self.cached_data["arc_voltage"] = arc_data.get("arc_voltage", {"U": [], "V": [], "W": []})
            
            # 转换为 1/2/3 编号
            self.cached_data["arc_current"]["1"] = self.cached_data["arc_current"].pop("U", [])
            self.cached_data["arc_current"]["2"] = self.cached_data["arc_current"].pop("V", [])
            self.cached_data["arc_current"]["3"] = self.cached_data["arc_current"].pop("W", [])
            
            self.cached_data["arc_voltage"]["1"] = self.cached_data["arc_voltage"].pop("U", [])
            self.cached_data["arc_voltage"]["2"] = self.cached_data["arc_voltage"].pop("V", [])
            self.cached_data["arc_voltage"]["3"] = self.cached_data["arc_voltage"].pop("W", [])
            
            # 2. 查询电极深度数据
            electrode_data = self.history_service.query_electrode_depth(batch_code, start_time, end_time, interval)
            self.cached_data["electrode_depth"] = electrode_data
            
            # 3. 查询功率能耗数据
            power_data = self.history_service.query_power_energy(batch_code, start_time, end_time, interval)
            self.cached_data["power"] = power_data.get("power", [])
            self.cached_data["energy"] = power_data.get("energy", [])
            
            # 4. 查询料仓数据
            hopper_data = self.history_service.query_hopper_data(batch_code, start_time, end_time, interval)
            self.cached_data["feeding_total"] = hopper_data.get("feeding_total", [])
            
            # 5. 查询冷却水数据
            cooling_data = self.history_service.query_cooling_water(batch_code, start_time, end_time, interval)
            self.cached_data["shell_water"] = cooling_data.get("shell_water", [])
            self.cached_data["cover_water"] = cooling_data.get("cover_water", [])
            
            logger.info("历史数据查询完成，开始更新图表")
            
            # 更新所有图表
            self.update_line_charts()
            
        except Exception as e:
            logger.error(f"查询历史数据失败: {e}", exc_info=True)
    
    # 4. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 顶部控制栏（使用 BarHistory 组件）
        self.bar_history = BarHistory()
        self.bar_history.mode_changed.connect(self.on_mode_changed)
        self.bar_history.batch_changed.connect(self.on_batch_changed)
        self.bar_history.batches_changed.connect(self.on_batches_changed)
        self.bar_history.time_range_changed.connect(self.on_time_range_changed)
        self.bar_history.query_clicked.connect(self.on_query_clicked)
        main_layout.addWidget(self.bar_history)
        
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
        self.arc_panel = PanelTech("弧压/流/电极 (A/V/mm)")
        self.arc_panel.setMinimumHeight(300)
        
        # 弧压/流/电极下拉选择器
        from ui.widgets.history_curve.dropdown_tech import DropdownTech
        arc_options = ["弧流", "弧压", "电极高度"]
        self.arc_dropdown = DropdownTech(
            arc_options,
            self.arc_select,
            accent_color=colors.GLOW_CYAN
        )
        self.arc_dropdown.selection_changed.connect(self.on_arc_changed)
        self.arc_panel.add_header_action(self.arc_dropdown)
        
        # 弧压/流/电极图表
        self.arc_chart = ChartLine(y_label="", accent_color=colors.GLOW_CYAN)
        arc_layout = QVBoxLayout()
        arc_layout.setContentsMargins(0, 0, 0, 0)
        arc_layout.addWidget(self.arc_chart)
        self.arc_panel.set_content_layout(arc_layout)
        
        row1_layout.addWidget(self.arc_panel, stretch=1)
        
        # 功率/能耗面板
        self.power_panel = PanelTech("功率/能耗 (kW/kWh)")
        self.power_panel.setMinimumHeight(300)
        
        # 功率/能耗下拉选择器
        power_options = ["功率", "能耗"]
        self.power_dropdown = DropdownTech(
            power_options,
            self.power_select,
            accent_color=colors.GLOW_ORANGE
        )
        self.power_dropdown.selection_changed.connect(self.on_power_changed)
        self.power_panel.add_header_action(self.power_dropdown)
        
        # 功率/能耗图表
        self.power_chart = ChartLine(y_label="", accent_color=colors.GLOW_ORANGE)
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
        self.hopper_panel = PanelTech("料仓 (kg)")
        self.hopper_panel.setMinimumHeight(300)
        
        # 料仓下拉选择器
        hopper_options = ["投料量"]
        self.hopper_dropdown = DropdownTech(
            hopper_options,
            self.hopper_select,
            accent_color=colors.GLOW_BLUE
        )
        self.hopper_dropdown.selection_changed.connect(self.on_hopper_changed)
        self.hopper_panel.add_header_action(self.hopper_dropdown)
        
        # 料仓图表
        self.hopper_chart = ChartLine(y_label="", accent_color=colors.GLOW_BLUE)
        hopper_layout = QVBoxLayout()
        hopper_layout.setContentsMargins(0, 0, 0, 0)
        hopper_layout.addWidget(self.hopper_chart)
        self.hopper_panel.set_content_layout(hopper_layout)
        
        row2_layout.addWidget(self.hopper_panel, stretch=1)
        
        # 冷却水面板
        self.cooling_panel = PanelTech("冷却水累计用量 (m³)")
        self.cooling_panel.setMinimumHeight(300)
        
        # 冷却水下拉选择器
        cooling_options = ["炉皮冷却水累计", "炉盖冷却水累计"]
        self.cooling_dropdown = DropdownTech(
            cooling_options,
            self.cooling_select,
            accent_color=colors.GLOW_GREEN
        )
        self.cooling_dropdown.selection_changed.connect(self.on_cooling_changed)
        self.cooling_panel.add_header_action(self.cooling_dropdown)
        
        # 冷却水图表
        self.cooling_chart = ChartLine(y_label="", accent_color=colors.GLOW_GREEN)
        cooling_layout = QVBoxLayout()
        cooling_layout.setContentsMargins(0, 0, 0, 0)
        cooling_layout.addWidget(self.cooling_chart)
        self.cooling_panel.set_content_layout(cooling_layout)
        
        row2_layout.addWidget(self.cooling_panel, stretch=1)
        
        layout.addWidget(row2)
        
        self.content_layout.addWidget(self.line_chart_container)
    
    # 6. 模式切换
    def on_mode_changed(self, is_history_mode: bool):
        """历史轮次查询模式切换"""
        self.is_history_mode = is_history_mode
        
        if is_history_mode:
            self.line_chart_container.hide()
            self.batch_compare_page.show()
            self.update_batch_compare()
        else:
            self.batch_compare_page.hide()
            self.line_chart_container.show()
            self.update_line_charts()
    
    # 7. 批次选择变化（清空缓存）
    def on_batch_changed(self, batch: str):
        """批次选择变化时清空缓存"""
        logger.info(f"批次选择变化: {batch}")
        self.selected_batch = batch
        # 清空缓存，等待用户点击查询按钮
        self.clear_cache()
    
    # 8. 批次多选变化
    def on_batches_changed(self, batches: list):
        """批次多选变化"""
        self.selected_batches = batches
        self.update_batch_compare()
    
    # 9. 时间范围变化（清空缓存）
    def on_time_range_changed(self, start: QDateTime, end: QDateTime):
        """时间范围变化时清空缓存"""
        logger.info(f"时间范围变化: {start.toString()} - {end.toString()}")
        # 清空缓存，等待用户点击查询按钮
        self.clear_cache()
    
    # 10. 查询按钮点击
    def on_query_clicked(self):
        """点击查询按钮，从数据库查询数据"""
        batch_code = self.bar_history.get_selected_batch()
        
        if not batch_code or batch_code in ["无数据", "加载失败"]:
            logger.warning("未选择有效批次")
            return
        
        # 获取时间范围
        start_qdt, end_qdt = self.bar_history.get_time_range()
        start_time = start_qdt.toPyDateTime()
        end_time = end_qdt.toPyDateTime()
        
        logger.info(f"查询按钮点击 - 批次: {batch_code}, 时间: {start_time} - {end_time}")
        
        # 查询所有数据
        self.query_all_data(batch_code, start_time, end_time)
    
    # 11. 清空缓存
    def clear_cache(self):
        """清空数据缓存"""
        self.cached_data = {
            "arc_current": {"1": [], "2": [], "3": []},
            "arc_voltage": {"1": [], "2": [], "3": []},
            "electrode_depth": {"1": [], "2": [], "3": []},
            "power": [],
            "energy": [],
            "feeding_total": [],
            "shell_water": [],
            "cover_water": []
        }
        logger.info("数据缓存已清空")
    
    # 12. 更新折线图（使用缓存数据）
    def update_line_charts(self):
        """使用缓存数据更新图表"""
        colors = self.theme_manager.get_colors()
        
        # 更新弧压/流/电极图表
        if self.arc_select == "弧流":
            data_1 = self.cached_data["arc_current"]["1"]
            data_2 = self.cached_data["arc_current"]["2"]
            data_3 = self.cached_data["arc_current"]["3"]
            
            if data_1 and data_2 and data_3:
                x_data = list(range(len(data_1)))
                y_data_1 = [d["value"] for d in data_1]
                y_data_2 = [d["value"] for d in data_2]
                y_data_3 = [d["value"] for d in data_3]
                
                data_list = [
                    ("1#电极 (A)", x_data, y_data_1, colors.CHART_LINE_1),
                    ("2#电极 (A)", x_data, y_data_2, colors.CHART_LINE_2),
                    ("3#电极 (A)", x_data, y_data_3, colors.CHART_LINE_3),
                ]
                self.arc_chart.update_multi_data(data_list)
                self.arc_chart.plot_widget.setLabel('left', "")
            
        elif self.arc_select == "弧压":
            data_1 = self.cached_data["arc_voltage"]["1"]
            data_2 = self.cached_data["arc_voltage"]["2"]
            data_3 = self.cached_data["arc_voltage"]["3"]
            
            if data_1 and data_2 and data_3:
                x_data = list(range(len(data_1)))
                y_data_1 = [d["value"] for d in data_1]
                y_data_2 = [d["value"] for d in data_2]
                y_data_3 = [d["value"] for d in data_3]
                
                data_list = [
                    ("1#电极 (V)", x_data, y_data_1, colors.CHART_LINE_1),
                    ("2#电极 (V)", x_data, y_data_2, colors.CHART_LINE_2),
                    ("3#电极 (V)", x_data, y_data_3, colors.CHART_LINE_3),
                ]
                self.arc_chart.update_multi_data(data_list)
                self.arc_chart.plot_widget.setLabel('left', "")
        
        else:  # 电极高度
            data_1 = self.cached_data["electrode_depth"]["1"]
            data_2 = self.cached_data["electrode_depth"]["2"]
            data_3 = self.cached_data["electrode_depth"]["3"]
            
            if data_1 and data_2 and data_3:
                x_data = list(range(len(data_1)))
                y_data_1 = [d["value"] for d in data_1]
                y_data_2 = [d["value"] for d in data_2]
                y_data_3 = [d["value"] for d in data_3]
                
                data_list = [
                    ("1#电极 (mm)", x_data, y_data_1, colors.CHART_LINE_1),
                    ("2#电极 (mm)", x_data, y_data_2, colors.CHART_LINE_2),
                    ("3#电极 (mm)", x_data, y_data_3, colors.CHART_LINE_3),
                ]
                self.arc_chart.update_multi_data(data_list)
                self.arc_chart.plot_widget.setLabel('left', "")
        
        # 更新功率/能耗图表
        if self.power_select == "功率":
            power_data = self.cached_data["power"]
            if power_data:
                x_data = list(range(len(power_data)))
                y_data = [d["value"] for d in power_data]
                self.power_chart.update_data(x_data, y_data, "功率 (kW)")
                self.power_chart.plot_widget.setLabel('left', "")
        else:
            energy_data = self.cached_data["energy"]
            if energy_data:
                x_data = list(range(len(energy_data)))
                y_data = [d["value"] for d in energy_data]
                self.power_chart.update_data(x_data, y_data, "能耗 (kWh)")
                self.power_chart.plot_widget.setLabel('left', "")
        
        # 更新料仓图表
        feeding_data = self.cached_data["feeding_total"]
        if feeding_data:
            x_data = list(range(len(feeding_data)))
            y_data = [d["value"] for d in feeding_data]
            self.hopper_chart.update_data(x_data, y_data, "投料累计 (kg)")
            self.hopper_chart.plot_widget.setLabel('left', "")
        
        # 更新冷却水图表
        if self.cooling_select == "炉皮冷却水累计":
            shell_data = self.cached_data["shell_water"]
            if shell_data:
                x_data = list(range(len(shell_data)))
                y_data = [d["value"] for d in shell_data]
                self.cooling_chart.update_data(x_data, y_data, "炉皮冷却水累计 (m³)")
                self.cooling_chart.plot_widget.setLabel('left', "")
        else:
            cover_data = self.cached_data["cover_water"]
            if cover_data:
                x_data = list(range(len(cover_data)))
                y_data = [d["value"] for d in cover_data]
                self.cooling_chart.update_data(x_data, y_data, "炉盖冷却水累计 (m³)")
                self.cooling_chart.plot_widget.setLabel('left', "")
    
    # 13. 更新批次对比
    def update_batch_compare(self):
        """更新批次对比页面"""
        if not self.selected_batches:
            logger.warning("未选择批次，无法更新批次对比")
            return
        
        logger.info(f"开始查询批次对比数据: {self.selected_batches}")
        
        # 查询每个批次的统计数据
        batch_data = {
            'batches': [],
            'energy_total': {},
            'feeding_total': {},
            'shell_water_total': {},
            'cover_water_total': {},
            'duration_hours': {}
        }
        
        for batch_code in self.selected_batches:
            try:
                stats = self.history_service.query_batch_statistics(batch_code)
                
                batch_data['batches'].append(batch_code)
                batch_data['energy_total'][batch_code] = stats['energy_total']
                batch_data['feeding_total'][batch_code] = stats['feeding_total']
                batch_data['shell_water_total'][batch_code] = stats['shell_water_total']
                batch_data['cover_water_total'][batch_code] = stats['cover_water_total']
                batch_data['duration_hours'][batch_code] = stats['duration_hours']
                
            except Exception as e:
                logger.error(f"查询批次 {batch_code} 统计数据失败: {e}")
        
        # 更新批次对比页面
        self.batch_compare_page.update_batch_data(batch_data)
    
    # 14. 弧压/流/电极选择变化
    def on_arc_changed(self, option: str):
        """切换弧流/弧压/电极高度时，使用缓存数据更新图表"""
        self.arc_select = option
        self.update_line_charts()
    
    # 15. 功率/能耗选择变化
    def on_power_changed(self, option: str):
        """切换功率/能耗时，使用缓存数据更新图表"""
        self.power_select = option
        self.update_line_charts()
    
    # 16. 料仓选择变化
    def on_hopper_changed(self, option: str):
        """切换料仓选项时，使用缓存数据更新图表"""
        self.hopper_select = option
        self.update_line_charts()
    
    # 17. 冷却水选择变化
    def on_cooling_changed(self, option: str):
        """切换冷却水选项时，使用缓存数据更新图表"""
        self.cooling_select = option
        self.update_line_charts()
    
    # 18. 应用样式
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
    
    # 19. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
