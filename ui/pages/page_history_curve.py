"""
历史曲线页面 - 重构版（只保留折线图模式）
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QScrollArea, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QThread, pyqtSignal
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.history_curve.chart_line import ChartLine
from ui.widgets.history_curve.bar_history import BarHistory
from ui.widgets.history_curve.button_export import ButtonExport
from ui.pages.page_batch_compare import PageBatchCompare
from backend.bridge.history_query import get_history_query_service
from backend.services.data_exporter import get_data_exporter
from datetime import datetime, timedelta
from loguru import logger
import random


# ============================================================
# 历史数据查询线程（后台执行，避免阻塞 UI）
# ============================================================
class HistoryQueryThread(QThread):
    """历史数据查询线程"""
    
    # 查询完成信号
    query_finished = pyqtSignal(dict)
    # 查询失败信号
    query_failed = pyqtSignal(str)
    
    def __init__(self, history_service, batch_code: str, start_time: datetime, end_time: datetime, interval: str):
        super().__init__()
        self.history_service = history_service
        self.batch_code = batch_code
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
    
    def run(self):
        """在后台线程中执行查询"""
        try:
            logger.info(f"后台线程开始查询批次 {self.batch_code} 的历史数据")
            
            # 1. 查询弧流弧压数据
            arc_data = self.history_service.query_arc_data(
                self.batch_code, self.start_time, self.end_time, self.interval
            )
            
            # 2. 查询电极深度数据
            electrode_data = self.history_service.query_electrode_depth(
                self.batch_code, self.start_time, self.end_time, self.interval
            )
            
            # 3. 查询功率能耗数据
            power_data = self.history_service.query_power_energy(
                self.batch_code, self.start_time, self.end_time, self.interval
            )
            
            # 4. 查询料仓数据
            hopper_data = self.history_service.query_hopper_data(
                self.batch_code, self.start_time, self.end_time, self.interval
            )
            
            # 5. 查询冷却水数据
            cooling_data = self.history_service.query_cooling_water(
                self.batch_code, self.start_time, self.end_time, self.interval
            )
            
            # 汇总结果
            result = {
                "arc_data": arc_data,
                "electrode_data": electrode_data,
                "power_data": power_data,
                "hopper_data": hopper_data,
                "cooling_data": cooling_data
            }
            
            logger.info("后台线程查询完成，发送结果到主线程")
            self.query_finished.emit(result)
            
        except Exception as e:
            logger.error(f"后台线程查询失败: {e}", exc_info=True)
            self.query_failed.emit(str(e))


class PageHistoryCurve(QWidget):
    """历史曲线页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 后端查询服务
        self.history_service = get_history_query_service()
        self.data_exporter = get_data_exporter()
        
        # 状态变量
        self.is_history_mode = False
        self.selected_batch = ""
        self.selected_batches = []
        
        # 当前查询的时间范围（用于导出）
        self.current_start_time = None
        self.current_end_time = None
        
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
        
        # 标记是否已经初始化过
        self.is_initialized = False
        
        # 查询线程
        self.query_thread = None
    
        # 重试计数器
        self.load_retry_count = 0
        self.max_retry_count = 10  # 最大重试次数
    
    # 2. 加载初始数据
    def load_initial_data(self):
        """页面加载时等待批次列表加载完成即可，时间范围加载完成后会自动触发查询"""
        logger.info("开始加载初始数据...")
        
        # 等待 bar_history 加载完批次列表
        if not self.bar_history.get_selected_batch():
            # 检查重试次数
            self.load_retry_count += 1
            if self.load_retry_count > self.max_retry_count:
                logger.error(f"批次列表加载失败，已重试 {self.max_retry_count} 次，停止重试")
                logger.error("可能原因: InfluxDB 连接失败或认证失败，请检查配置")
                return
            
            logger.warning(f"批次列表尚未加载，延迟重试... (第 {self.load_retry_count}/{self.max_retry_count} 次)")
            QTimer.singleShot(1000, self.load_initial_data)
            return
        
        # 重置重试计数器
        self.load_retry_count = 0
        
        # 获取最新批次
        self.selected_batch = self.bar_history.get_selected_batch()
        logger.info(f"使用最新批次: {self.selected_batch}")
        
        # 注意：不需要在这里查询数据，批次时间范围加载完成后会自动触发 on_batch_time_range_loaded
        logger.info("等待批次时间范围加载完成...")
    
    # 3. 查询所有数据（使用后台线程）
    def query_all_data(self, batch_code: str, start_time: datetime, end_time: datetime):
        """查询所有图表的历史数据（后台线程执行）"""
        if not batch_code:
            logger.warning("批次号为空，无法查询")
            return
        
        # 保存当前查询的时间范围（用于导出）
        self.current_start_time = start_time
        self.current_end_time = end_time
        
        logger.info(f"开始查询批次 {batch_code} 的历史数据，时间范围: {start_time} - {end_time}")
        
        # 所有时间范围统一使用 100 个数据点
        target_points = 100
        
        # 计算最佳聚合间隔
        interval = self.history_service.calculate_optimal_interval(start_time, end_time, target_points=target_points)
        logger.info(f"使用聚合间隔: {interval}")
        
        # 如果已有查询线程在运行，先停止
        if self.query_thread and self.query_thread.isRunning():
            logger.warning("上一次查询尚未完成，等待完成...")
            self.query_thread.wait()
        
        # 创建后台查询线程
        self.query_thread = HistoryQueryThread(
            self.history_service,
            batch_code,
            start_time,
            end_time,
            interval
        )
        
        # 连接信号
        self.query_thread.query_finished.connect(self.on_query_finished)
        self.query_thread.query_failed.connect(self.on_query_failed)
        
        # 启动线程
        self.query_thread.start()
        logger.info("后台查询线程已启动")
    
    # 3.1. 查询完成回调
    def on_query_finished(self, result: dict):
        """查询完成后更新缓存和图表（主线程）"""
        try:
            logger.info("收到后台查询结果，开始更新缓存")
            
            # 更新缓存
            arc_data = result.get("arc_data", {})
            self.cached_data["arc_current"] = arc_data.get("arc_current", {"U": [], "V": [], "W": []})
            self.cached_data["arc_voltage"] = arc_data.get("arc_voltage", {"U": [], "V": [], "W": []})
            
            # 转换为 1/2/3 编号
            self.cached_data["arc_current"]["1"] = self.cached_data["arc_current"].pop("U", [])
            self.cached_data["arc_current"]["2"] = self.cached_data["arc_current"].pop("V", [])
            self.cached_data["arc_current"]["3"] = self.cached_data["arc_current"].pop("W", [])
            
            self.cached_data["arc_voltage"]["1"] = self.cached_data["arc_voltage"].pop("U", [])
            self.cached_data["arc_voltage"]["2"] = self.cached_data["arc_voltage"].pop("V", [])
            self.cached_data["arc_voltage"]["3"] = self.cached_data["arc_voltage"].pop("W", [])
            
            # 电极深度
            electrode_data = result.get("electrode_data", {})
            self.cached_data["electrode_depth"] = electrode_data
            
            # 功率能耗
            power_data = result.get("power_data", {})
            self.cached_data["power"] = power_data.get("power", [])
            self.cached_data["energy"] = power_data.get("energy", [])
            
            # 料仓
            hopper_data = result.get("hopper_data", {})
            self.cached_data["feeding_total"] = hopper_data.get("feeding_total", [])
            
            # 冷却水
            cooling_data = result.get("cooling_data", {})
            self.cached_data["shell_water"] = cooling_data.get("shell_water", [])
            self.cached_data["cover_water"] = cooling_data.get("cover_water", [])
            
            logger.info("缓存更新完成，开始更新图表")
            
            # 更新所有图表
            self.update_line_charts()
            
        except Exception as e:
            logger.error(f"处理查询结果失败: {e}", exc_info=True)
    
    # 3.2. 查询失败回调
    def on_query_failed(self, error_msg: str):
        """查询失败时显示错误（主线程）"""
        logger.error(f"历史数据查询失败: {error_msg}")
        QMessageBox.critical(self, "查询失败", f"查询历史数据失败:\n{error_msg}")
    
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
        self.bar_history.batch_time_range_loaded.connect(self.on_batch_time_range_loaded)  # 监听批次时间范围加载完成
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
        
        # 创建下拉框和导出按钮的容器
        arc_controls = QWidget()
        arc_controls_layout = QHBoxLayout(arc_controls)
        arc_controls_layout.setContentsMargins(0, 0, 0, 0)
        arc_controls_layout.setSpacing(8)
        
        # 弧压/流/电极下拉选择器
        from ui.widgets.history_curve.dropdown_tech import DropdownTech
        arc_options = ["弧流", "弧压", "电极高度"]
        self.arc_dropdown = DropdownTech(
            arc_options,
            self.arc_select,
            accent_color=colors.GLOW_CYAN
        )
        self.arc_dropdown.selection_changed.connect(self.on_arc_changed)
        arc_controls_layout.addWidget(self.arc_dropdown)
        
        # 弧压/流/电极导出按钮
        self.arc_export_btn = ButtonExport(accent_color=colors.GLOW_CYAN)
        self.arc_export_btn.export_clicked.connect(self.on_arc_export_clicked)
        arc_controls_layout.addWidget(self.arc_export_btn)
        
        self.arc_panel.add_header_action(arc_controls)
        
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
        
        # 创建下拉框和导出按钮的容器
        power_controls = QWidget()
        power_controls_layout = QHBoxLayout(power_controls)
        power_controls_layout.setContentsMargins(0, 0, 0, 0)
        power_controls_layout.setSpacing(8)
        
        # 功率/能耗下拉选择器
        power_options = ["功率", "能耗"]
        self.power_dropdown = DropdownTech(
            power_options,
            self.power_select,
            accent_color=colors.GLOW_ORANGE
        )
        self.power_dropdown.selection_changed.connect(self.on_power_changed)
        power_controls_layout.addWidget(self.power_dropdown)
        
        # 功率/能耗导出按钮
        self.power_export_btn = ButtonExport(accent_color=colors.GLOW_ORANGE)
        self.power_export_btn.export_clicked.connect(self.on_power_export_clicked)
        power_controls_layout.addWidget(self.power_export_btn)
        
        self.power_panel.add_header_action(power_controls)
        
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
        
        # 创建下拉框和导出按钮的容器
        hopper_controls = QWidget()
        hopper_controls_layout = QHBoxLayout(hopper_controls)
        hopper_controls_layout.setContentsMargins(0, 0, 0, 0)
        hopper_controls_layout.setSpacing(8)
        
        # 料仓下拉选择器
        hopper_options = ["投料量"]
        self.hopper_dropdown = DropdownTech(
            hopper_options,
            self.hopper_select,
            accent_color=colors.GLOW_BLUE
        )
        self.hopper_dropdown.selection_changed.connect(self.on_hopper_changed)
        hopper_controls_layout.addWidget(self.hopper_dropdown)
        
        # 料仓导出按钮
        self.hopper_export_btn = ButtonExport(accent_color=colors.GLOW_BLUE)
        self.hopper_export_btn.export_clicked.connect(self.on_hopper_export_clicked)
        hopper_controls_layout.addWidget(self.hopper_export_btn)
        
        self.hopper_panel.add_header_action(hopper_controls)
        
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
        
        # 创建下拉框和导出按钮的容器
        cooling_controls = QWidget()
        cooling_controls_layout = QHBoxLayout(cooling_controls)
        cooling_controls_layout.setContentsMargins(0, 0, 0, 0)
        cooling_controls_layout.setSpacing(8)
        
        # 冷却水下拉选择器
        cooling_options = ["炉皮冷却水累计", "炉盖冷却水累计"]
        self.cooling_dropdown = DropdownTech(
            cooling_options,
            self.cooling_select,
            accent_color=colors.GLOW_GREEN
        )
        self.cooling_dropdown.selection_changed.connect(self.on_cooling_changed)
        cooling_controls_layout.addWidget(self.cooling_dropdown)
        
        # 冷却水导出按钮
        self.cooling_export_btn = ButtonExport(accent_color=colors.GLOW_GREEN)
        self.cooling_export_btn.export_clicked.connect(self.on_cooling_export_clicked)
        cooling_controls_layout.addWidget(self.cooling_export_btn)
        
        self.cooling_panel.add_header_action(cooling_controls)
        
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
        """批次选择变化时，清空缓存，等待时间范围加载完成"""
        logger.info(f"批次选择变化: {batch}")
        self.selected_batch = batch
        
        # 清空缓存
        self.clear_cache()
        
        # 注意：不在这里查询数据，等待 on_batch_time_range_loaded 信号
    
    # 7.1. 批次时间范围加载完成
    def on_batch_time_range_loaded(self, batch_code: str, start_time, end_time):
        """批次时间范围加载完成后，自动查询完整时间范围的数据"""
        logger.info(f"批次 {batch_code} 时间范围加载完成: {start_time} - {end_time}")
        
        # 自动查询完整时间范围的数据
        self.query_all_data(batch_code, start_time, end_time)
    
    # 8. 批次多选变化
    def on_batches_changed(self, batches: list):
        """批次多选变化"""
        self.selected_batches = batches
        self.update_batch_compare()
    
    # 9. 时间范围变化（自动查询）
    def on_time_range_changed(self, start: QDateTime, end: QDateTime):
        """时间范围变化时自动查询"""
        logger.info(f"时间范围变化: {start.toString()} - {end.toString()}")
        
        # 清空缓存
        self.clear_cache()
        
        # 自动触发查询
        self.on_query_clicked()
    
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
                # 使用时间戳作为X轴
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in data_1]
                y_data_1 = [d["value"] for d in data_1]
                y_data_2 = [d["value"] for d in data_2]
                y_data_3 = [d["value"] for d in data_3]
                
                data_list = [
                    ("1#电极 (A)", x_data, y_data_1, colors.CHART_LINE_1),
                    ("2#电极 (A)", x_data, y_data_2, colors.CHART_LINE_2),
                    ("3#电极 (A)", x_data, y_data_3, colors.CHART_LINE_3),
                ]
                self.arc_chart.update_multi_data_with_time(data_list)
                self.arc_chart.plot_widget.setLabel('left', "")
            
        elif self.arc_select == "弧压":
            data_1 = self.cached_data["arc_voltage"]["1"]
            data_2 = self.cached_data["arc_voltage"]["2"]
            data_3 = self.cached_data["arc_voltage"]["3"]
            
            if data_1 and data_2 and data_3:
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in data_1]
                y_data_1 = [d["value"] for d in data_1]
                y_data_2 = [d["value"] for d in data_2]
                y_data_3 = [d["value"] for d in data_3]
                
                data_list = [
                    ("1#电极 (V)", x_data, y_data_1, colors.CHART_LINE_1),
                    ("2#电极 (V)", x_data, y_data_2, colors.CHART_LINE_2),
                    ("3#电极 (V)", x_data, y_data_3, colors.CHART_LINE_3),
                ]
                self.arc_chart.update_multi_data_with_time(data_list)
                self.arc_chart.plot_widget.setLabel('left', "")
        
        else:  # 电极高度
            data_1 = self.cached_data["electrode_depth"]["1"]
            data_2 = self.cached_data["electrode_depth"]["2"]
            data_3 = self.cached_data["electrode_depth"]["3"]
            
            if data_1 and data_2 and data_3:
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in data_1]
                y_data_1 = [d["value"] for d in data_1]
                y_data_2 = [d["value"] for d in data_2]
                y_data_3 = [d["value"] for d in data_3]
                
                data_list = [
                    ("1#电极 (mm)", x_data, y_data_1, colors.CHART_LINE_1),
                    ("2#电极 (mm)", x_data, y_data_2, colors.CHART_LINE_2),
                    ("3#电极 (mm)", x_data, y_data_3, colors.CHART_LINE_3),
                ]
                self.arc_chart.update_multi_data_with_time(data_list)
                self.arc_chart.plot_widget.setLabel('left', "")
        
        # 更新功率/能耗图表
        if self.power_select == "功率":
            power_data = self.cached_data["power"]
            if power_data:
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in power_data]
                y_data = [d["value"] for d in power_data]
                self.power_chart.update_data_with_time(x_data, y_data, "功率 (kW)")
                self.power_chart.plot_widget.setLabel('left', "")
        else:
            energy_data = self.cached_data["energy"]
            if energy_data:
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in energy_data]
                y_data = [d["value"] for d in energy_data]
                self.power_chart.update_data_with_time(x_data, y_data, "能耗 (kWh)")
                self.power_chart.plot_widget.setLabel('left', "")
        
        # 更新料仓图表
        feeding_data = self.cached_data["feeding_total"]
        if feeding_data:
            x_data = [self._parse_time_to_timestamp(d["time"]) for d in feeding_data]
            y_data = [d["value"] for d in feeding_data]
            self.hopper_chart.update_data_with_time(x_data, y_data, "投料累计 (kg)")
            self.hopper_chart.plot_widget.setLabel('left', "")
        
        # 更新冷却水图表
        if self.cooling_select == "炉皮冷却水累计":
            shell_data = self.cached_data["shell_water"]
            if shell_data:
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in shell_data]
                y_data = [d["value"] for d in shell_data]
                self.cooling_chart.update_data_with_time(x_data, y_data, "炉皮冷却水累计 (m³)")
                self.cooling_chart.plot_widget.setLabel('left', "")
        else:
            cover_data = self.cached_data["cover_water"]
            if cover_data:
                x_data = [self._parse_time_to_timestamp(d["time"]) for d in cover_data]
                y_data = [d["value"] for d in cover_data]
                self.cooling_chart.update_data_with_time(x_data, y_data, "炉盖冷却水累计 (m³)")
                self.cooling_chart.plot_widget.setLabel('left', "")
    
    # 12.1. 解析时间字符串为时间戳
    def _parse_time_to_timestamp(self, time_str: str) -> float:
        """将ISO格式时间字符串转换为时间戳（秒）"""
        from dateutil import parser
        dt = parser.isoparse(time_str)
        return dt.timestamp()
    
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
    
    # 19.1. 页面显示事件（每次显示时重新加载批次列表）
    def showEvent(self, event):
        """页面显示时重新加载批次列表"""
        super().showEvent(event)
        
        if not self.is_initialized:
            # 首次显示，延迟加载数据（等待 UI 渲染完成）
            # 重置重试计数器
            self.load_retry_count = 0
            QTimer.singleShot(500, self.load_initial_data)
            self.is_initialized = True
        else:
            # 非首次显示，立即重新加载批次列表
            logger.info("页面显示，重新加载批次列表...")
            self.bar_history.load_batch_list()
    
    def hideEvent(self, event):
        """页面隐藏时停止查询线程"""
        super().hideEvent(event)
        
        # 停止查询线程
        if self.query_thread and self.query_thread.isRunning():
            logger.info("页面隐藏，停止查询线程...")
            self.query_thread.quit()
            self.query_thread.wait()
    
    # 20. 弧压/流/电极导出
    def on_arc_export_clicked(self):
        """导出弧压/流/电极数据"""
        if not self.selected_batch:
            QMessageBox.warning(self, "导出失败", "请先选择批次并查询数据")
            return
        
        if not self.current_start_time or not self.current_end_time:
            QMessageBox.warning(self, "导出失败", "请先查询数据")
            return
        
        # 根据当前选择获取数据
        if self.arc_select == "弧流":
            data_type_map = {
                "1": "1#弧流",
                "2": "2#弧流",
                "3": "3#弧流"
            }
            data_source = self.cached_data["arc_current"]
        elif self.arc_select == "弧压":
            data_type_map = {
                "1": "1#弧压",
                "2": "2#弧压",
                "3": "3#弧压"
            }
            data_source = self.cached_data["arc_voltage"]
        else:  # 电极高度
            data_type_map = {
                "1": "1#电极高度",
                "2": "2#电极高度",
                "3": "3#电极高度"
            }
            data_source = self.cached_data["electrode_depth"]
        
        # 弹出文件保存对话框
        default_filename = f"{self.selected_batch}_{self.arc_select}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            default_filename,
            "Excel 文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # 导出三相数据（分别导出）
        try:
            # 创建工作簿
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
            
            wb = openpyxl.Workbook()
            sheet_created = False
            
            # 为每相创建一个工作表
            for phase_id, data_type in data_type_map.items():
                data_list = data_source.get(phase_id, [])
                
                if not data_list:
                    logger.warning(f"{data_type} 数据为空，跳过")
                    continue
                
                # 创建工作表
                if sheet_created:
                    ws = wb.create_sheet(title=data_type)
                else:
                    ws = wb.active
                    ws.title = data_type
                    sheet_created = True
                
                # 设置列宽
                ws.column_dimensions['A'].width = 20
                ws.column_dimensions['B'].width = 22
                ws.column_dimensions['C'].width = 22
                ws.column_dimensions['D'].width = 20
                ws.column_dimensions['E'].width = 15
                
                # 表头样式
                header_font = Font(name='Microsoft YaHei', size=12, bold=True, color='FFFFFF')
                header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                header_alignment = Alignment(horizontal='center', vertical='center')
                border = Border(
                    left=Side(style='thin', color='000000'),
                    right=Side(style='thin', color='000000'),
                    top=Side(style='thin', color='000000'),
                    bottom=Side(style='thin', color='000000')
                )
                
                # 写入表头
                headers = ['批次编号', '起始时间', '截止时间', '数据类型', '数据值']
                for col_idx, header in enumerate(headers, start=1):
                    cell = ws.cell(row=1, column=col_idx, value=header)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                    cell.border = border
                
                # 数据样式
                data_font = Font(name='Microsoft YaHei', size=11)
                data_alignment = Alignment(horizontal='center', vertical='center')
                
                # 格式化时间
                start_time_str = self.current_start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = self.current_end_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 写入数据
                for row_idx, data_point in enumerate(data_list, start=2):
                    # 批次编号
                    cell = ws.cell(row=row_idx, column=1, value=self.selected_batch)
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = border
                    
                    # 起始时间
                    cell = ws.cell(row=row_idx, column=2, value=start_time_str)
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = border
                    
                    # 截止时间
                    cell = ws.cell(row=row_idx, column=3, value=end_time_str)
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = border
                    
                    # 数据类型
                    cell = ws.cell(row=row_idx, column=4, value=data_type)
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = border
                    
                    # 数据值
                    value = data_point.get('value', 0)
                    cell = ws.cell(row=row_idx, column=5, value=round(value, 2))
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = border
            
            # 检查是否创建了任何工作表
            if not sheet_created:
                QMessageBox.warning(self, "导出失败", "没有可导出的数据")
                return
            
            # 保存文件
            wb.save(file_path)
            logger.info(f"数据导出成功: {file_path}")
            QMessageBox.information(self, "导出成功", f"数据已导出到:\n{file_path}")
            
        except Exception as e:
            logger.error(f"导出数据失败: {e}", exc_info=True)
            QMessageBox.critical(self, "导出失败", f"导出数据时发生错误:\n{str(e)}")
    
    # 21. 功率/能耗导出
    def on_power_export_clicked(self):
        """导出功率/能耗数据"""
        if not self.selected_batch:
            QMessageBox.warning(self, "导出失败", "请先选择批次并查询数据")
            return
        
        if not self.current_start_time or not self.current_end_time:
            QMessageBox.warning(self, "导出失败", "请先查询数据")
            return
        
        # 根据当前选择获取数据
        if self.power_select == "功率":
            data_type = "功率"
            data_list = self.cached_data["power"]
        else:
            data_type = "能耗"
            data_list = self.cached_data["energy"]
        
        if not data_list:
            QMessageBox.warning(self, "导出失败", f"{data_type}数据为空")
            return
        
        # 弹出文件保存对话框
        default_filename = f"{self.selected_batch}_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            default_filename,
            "Excel 文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # 导出数据
        success = self.data_exporter.export_to_excel(
            file_path,
            self.selected_batch,
            self.current_start_time,
            self.current_end_time,
            data_type,
            data_list
        )
        
        if success:
            QMessageBox.information(self, "导出成功", f"数据已导出到:\n{file_path}")
        else:
            QMessageBox.critical(self, "导出失败", "导出数据时发生错误，请查看日志")
    
    # 22. 料仓导出
    def on_hopper_export_clicked(self):
        """导出料仓数据"""
        if not self.selected_batch:
            QMessageBox.warning(self, "导出失败", "请先选择批次并查询数据")
            return
        
        if not self.current_start_time or not self.current_end_time:
            QMessageBox.warning(self, "导出失败", "请先查询数据")
            return
        
        data_type = "投料量"
        data_list = self.cached_data["feeding_total"]
        
        if not data_list:
            QMessageBox.warning(self, "导出失败", f"{data_type}数据为空")
            return
        
        # 弹出文件保存对话框
        default_filename = f"{self.selected_batch}_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            default_filename,
            "Excel 文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # 导出数据
        success = self.data_exporter.export_to_excel(
            file_path,
            self.selected_batch,
            self.current_start_time,
            self.current_end_time,
            data_type,
            data_list
        )
        
        if success:
            QMessageBox.information(self, "导出成功", f"数据已导出到:\n{file_path}")
        else:
            QMessageBox.critical(self, "导出失败", "导出数据时发生错误，请查看日志")
    
    # 23. 冷却水导出
    def on_cooling_export_clicked(self):
        """导出冷却水数据"""
        if not self.selected_batch:
            QMessageBox.warning(self, "导出失败", "请先选择批次并查询数据")
            return
        
        if not self.current_start_time or not self.current_end_time:
            QMessageBox.warning(self, "导出失败", "请先查询数据")
            return
        
        # 根据当前选择获取数据
        if self.cooling_select == "炉皮冷却水累计":
            data_type = "炉皮冷却水累计"
            data_list = self.cached_data["shell_water"]
        else:
            data_type = "炉盖冷却水累计"
            data_list = self.cached_data["cover_water"]
        
        if not data_list:
            QMessageBox.warning(self, "导出失败", f"{data_type}数据为空")
            return
        
        # 弹出文件保存对话框
        default_filename = f"{self.selected_batch}_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            default_filename,
            "Excel 文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # 导出数据
        success = self.data_exporter.export_to_excel(
            file_path,
            self.selected_batch,
            self.current_start_time,
            self.current_end_time,
            data_type,
            data_list
        )
        
        if success:
            QMessageBox.information(self, "导出成功", f"数据已导出到:\n{file_path}")
        else:
            QMessageBox.critical(self, "导出失败", "导出数据时发生错误，请查看日志")
