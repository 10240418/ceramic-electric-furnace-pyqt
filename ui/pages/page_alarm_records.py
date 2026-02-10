"""
报警记录页面 - 9宫格报警记录显示
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QHBoxLayout, QFrame, QScroller
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from datetime import datetime
from loguru import logger

from ui.styles.themes import ThemeManager
from ui.widgets.history_curve.dropdown_tech import DropdownTech
from ui.widgets.history_curve.widget_time_selector import WidgetTimeSelector
from backend.bridge.history_query import get_history_query_service


class PageAlarmRecords(QWidget):
    """报警记录页面 - 9宫格布局"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        # 批次号选择
        self.selected_batch_code = ""
        self.batch_options = []
        
        # 批次时间范围
        self.batch_start_time = None
        self.batch_end_time = None
        
        # 历史查询服务
        self.history_service = get_history_query_service()
        
        # 是否已查询过（点查询按钮后才显示数据）
        self.has_queried = False
        
        # 定义七个报警类型 + 2个预留位
        # has_phase: True=有相位列(4列), False=无相位列(3列)
        self.alarm_types = [
            {"title": "三相电流 (A)", "alarm_type": "arc_current", "param": "arc_current",
             "has_phase": True, "phases": ["1#", "2#", "3#"], "value_range": (6000, 8500), "threshold": 8000},
            {"title": "三相电压 (V)", "alarm_type": "arc_voltage", "param": "arc_voltage",
             "has_phase": True, "phases": ["1#", "2#", "3#"], "value_range": (95, 105), "threshold": 100},
            {"title": "三相电极深度 (mm)", "alarm_type": "electrode_depth", "param": "electrode_depth",
             "has_phase": True, "phases": ["1#", "2#", "3#"], "value_range": (1900, 2000), "threshold": 1960},
            {"title": "炉皮冷却水压 (kPa)", "alarm_type": "cooling_water", "param": "cooling_pressure_shell",
             "has_phase": False, "phases": ["-"], "value_range": (55, 65), "threshold": 60},
            {"title": "炉盖冷却水压 (kPa)", "alarm_type": "cooling_water", "param": "cooling_pressure_cover",
             "has_phase": False, "phases": ["-"], "value_range": (55, 65), "threshold": 60},
            {"title": "炉皮冷却水流速 (m\u00b3/h)", "alarm_type": "cooling_water_flow", "param": "cooling_flow_shell",
             "has_phase": False, "phases": ["-"], "value_range": (0, 50), "threshold": 0},
            {"title": "炉盖冷却水流速 (m\u00b3/h)", "alarm_type": "cooling_water_flow", "param": "cooling_flow_cover",
             "has_phase": False, "phases": ["-"], "value_range": (0, 50), "threshold": 0},
            {"title": "过滤器压差 (kPa)", "alarm_type": "filter", "param": "filter_pressure_diff",
             "has_phase": False, "phases": ["-"], "value_range": (45, 55), "threshold": 50},
            {"title": "高压紧急停电", "alarm_type": "emergency_stop", "param": "emergency_stop",
             "has_phase": False, "phases": ["-"], "value_range": (0, 1), "threshold": 8000},
        ]
        
        # 存储每个表格的引用
        self.tables = []
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 启用触摸手势支持
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
        # 顶部控制栏（参考 BarHistory 样式）
        self.toolbar = QWidget()
        self.toolbar.setObjectName("alarm_toolbar")
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(24)
        
        colors = self.theme_manager.get_colors()
        
        # 批次号下拉框
        self.batch_dropdown = DropdownTech(
            ["加载中..."],
            default_value="加载中...",
            accent_color=colors.GLOW_CYAN
        )
        self.batch_dropdown.selection_changed.connect(self.on_batch_changed)
        toolbar_layout.addWidget(self.batch_dropdown)
        
        # 时间选择器
        self.time_selector = WidgetTimeSelector(accent_color=colors.GLOW_CYAN)
        toolbar_layout.addWidget(self.time_selector)
        
        # 查询按钮
        self.query_btn = QPushButton("查询")
        self.query_btn.setObjectName("query_btn")
        self.query_btn.setFixedHeight(32)
        self.query_btn.setFixedWidth(80)
        self.query_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.query_btn.clicked.connect(self.on_query_clicked)
        toolbar_layout.addWidget(self.query_btn)
        
        toolbar_layout.addStretch()
        
        main_layout.addWidget(self.toolbar)
        
        # 9宫格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)
        
        # 创建9个报警记录卡片
        for i, alarm_config in enumerate(self.alarm_types):
            row = i // 3
            col = i % 3
            
            card = self.create_alarm_card(alarm_config)
            grid_layout.addWidget(card, row, col)
        
        main_layout.addLayout(grid_layout)
    
    def create_alarm_card(self, alarm_config: dict) -> QWidget:
        """创建单个报警记录卡片"""
        # 外层容器
        card = QFrame()
        card.setObjectName("alarm_card")
        card.setMinimumHeight(280)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(6)
        
        # 标题
        title_label = QLabel(alarm_config["title"])
        title_label.setObjectName("alarm_title")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        card_layout.addWidget(title_label)
        
        # 表格 (根据是否有相位决定列数)
        has_phase = alarm_config.get("has_phase", True)
        table = QTableWidget()
        table.setObjectName("alarm_table")
        
        if has_phase:
            # 有相位: 4列 (时间, 相位, 实际值, 报警值)
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["时间", "相位", "实际值", "报警值"])
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(1, 60)
            table.setColumnWidth(2, 80)
            table.setColumnWidth(3, 80)
        else:
            # 无相位: 3列 (时间, 实际值, 报警值)
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["时间", "实际值", "报警值"])
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(1, 90)
            table.setColumnWidth(2, 90)
        
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        # 启用触摸拖动滚动
        table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        QScroller.grabGesture(table.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        
        # 存储表格引用和配置
        table.setProperty("alarm_config", alarm_config)
        self.tables.append(table)
        
        card_layout.addWidget(table)
        
        return card
    
    # 加载批次列表
    def load_batch_list(self):
        try:
            batches = self.history_service.get_batch_list(limit=50)
            
            if batches:
                self.batch_options = [b["batch_code"] for b in batches]
                
                # 默认选中第一个（最新的）批次
                if not self.selected_batch_code or self.selected_batch_code not in self.batch_options:
                    self.selected_batch_code = self.batch_options[0]
                
                self.batch_dropdown.set_options(self.batch_options)
                self.batch_dropdown.set_value(self.selected_batch_code)
                
                # 加载该批次的时间范围
                self.query_batch_time_range(self.selected_batch_code)
                
                logger.info(f"报警页面加载 {len(self.batch_options)} 个批次，选中: {self.selected_batch_code}")
            else:
                logger.warning("报警页面未查询到批次数据")
                self.batch_options = []
                self.selected_batch_code = ""
                self.batch_dropdown.set_options(["无数据"])
                self.batch_dropdown.set_value("无数据")
        except Exception as e:
            logger.error(f"报警页面加载批次列表失败: {e}")
            self.batch_dropdown.set_options(["加载失败"])
            self.batch_dropdown.set_value("加载失败")
    
    # 查询批次时间范围
    def query_batch_time_range(self, batch_code: str):
        if not batch_code or batch_code in ("无数据", "加载失败", "加载中..."):
            return
        
        try:
            start_time, end_time = self.history_service.query_batch_time_range(batch_code)
            
            if start_time and end_time:
                self.batch_start_time = start_time
                self.batch_end_time = end_time
                
                # 更新时间选择器
                self.time_selector.set_batch_time_range(start_time, end_time, 0.0)
                
                logger.info(f"报警页面批次 {batch_code} 时间范围: {start_time} - {end_time}")
            else:
                logger.warning(f"报警页面批次 {batch_code} 没有时间范围")
                self.batch_start_time = None
                self.batch_end_time = None
        except Exception as e:
            logger.error(f"查询批次时间范围失败: {e}")
            self.batch_start_time = None
            self.batch_end_time = None
    
    # 批次号变化
    def on_batch_changed(self, batch_code: str):
        if batch_code in ("加载中...", "无数据", "加载失败"):
            return
        self.selected_batch_code = batch_code
        logger.info(f"报警页面切换批次: {batch_code}")
        
        # 查询该批次的时间范围，更新时间选择器
        self.query_batch_time_range(batch_code)
    
    # 查询按钮点击
    def on_query_clicked(self):
        logger.info(f"报警页面点击查询 - 批次: {self.selected_batch_code}")
        self.has_queried = True
        self.refresh_all_alarms()
    
    # 获取当前时间范围（从时间选择器读取，转为 datetime）
    def get_query_time_range(self):
        start_qdt, end_qdt = self.time_selector.get_time_range()
        start_dt = start_qdt.toPyDateTime()
        end_dt = end_qdt.toPyDateTime()
        return start_dt, end_dt
    
    # 刷新所有报警记录
    def refresh_all_alarms(self):
        if not self.has_queried:
            return
        
        logger.info("查询所有报警记录")
        
        start_dt, end_dt = self.get_query_time_range()
        batch_code = self.selected_batch_code or None
        
        try:
            for table in self.tables:
                alarm_config = table.property("alarm_config")
                if not alarm_config or not alarm_config["alarm_type"]:
                    continue
                
                filtered_alarms = self.history_service.query_alarm_records(
                    alarm_type=alarm_config["alarm_type"],
                    param_name=alarm_config["param"],
                    batch_code=batch_code,
                    start_time=start_dt,
                    end_time=end_dt,
                    limit=50
                )
                self.update_table(table, filtered_alarms)
        except Exception as e:
            logger.error(f"查询报警记录失败: {e}")
    
    def update_table(self, table: QTableWidget, alarms: list):
        """更新表格数据"""
        table.setRowCount(0)
        
        if not alarms:
            return
        
        # 判断是否有相位列 (4列=有相位, 3列=无相位)
        has_phase = table.columnCount() == 4
        
        # 按时间倒序排列（最新的在上面）
        alarms_sorted = sorted(alarms, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # 最多显示10条
        display_alarms = alarms_sorted[:10]
        
        for alarm in display_alarms:
            row = table.rowCount()
            table.insertRow(row)
            
            # 时间
            timestamp_str = alarm.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                time_str = dt.strftime("%m-%d %H:%M:%S")
            except:
                time_str = timestamp_str[:16] if len(timestamp_str) > 16 else timestamp_str
            
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, time_item)
            
            if has_phase:
                # 有相位列: 4列布局 (时间, 相位, 实际值, 报警值)
                if "phase" in alarm:
                    phase = alarm["phase"]
                else:
                    param_name = alarm.get("param_name", "")
                    phase = self.extract_phase(param_name)
                
                phase_item = QTableWidgetItem(phase)
                phase_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 1, phase_item)
                
                value = alarm.get("value", 0)
                value_item = QTableWidgetItem(f"{value:.2f}")
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 2, value_item)
                
                threshold = alarm.get("threshold", 0)
                threshold_item = QTableWidgetItem(f"{threshold:.2f}")
                threshold_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 3, threshold_item)
            else:
                # 无相位列: 3列布局 (时间, 实际值, 报警值)
                value = alarm.get("value", 0)
                value_item = QTableWidgetItem(f"{value:.2f}")
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 1, value_item)
                
                threshold = alarm.get("threshold", 0)
                threshold_item = QTableWidgetItem(f"{threshold:.2f}")
                threshold_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 2, threshold_item)
    
    def extract_phase(self, param_name: str) -> str:
        """从参数名中提取相位"""
        param_lower = param_name.lower()
        if "_u" in param_lower or "_1" in param_lower:
            return "1#"
        elif "_v" in param_lower or "_2" in param_lower:
            return "2#"
        elif "_w" in param_lower or "_3" in param_lower:
            return "3#"
        else:
            return "-"
    
    def apply_styles(self):
        """应用样式"""
        tm = self.theme_manager
        colors = tm.get_colors()
        
        self.setStyleSheet(f"""
            PageAlarmRecords {{
                background: {tm.bg_deep()};
            }}
            
            QWidget#alarm_toolbar {{
                background: {colors.BG_DARK};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
            }}
            
            QFrame#alarm_card {{
                background: {tm.card_bg()};
                border: 1px solid {tm.border_glow()};
                border-radius: 6px;
            }}
            
            QLabel#alarm_title {{
                color: {tm.text_primary()};
                background: transparent;
                border: none;
            }}
            
            QTableWidget#alarm_table {{
                background: {tm.bg_dark()};
                color: {tm.text_primary()};
                border: 1px solid {tm.border_dark()};
                border-radius: 4px;
                gridline-color: {tm.border_dark()};
            }}
            
            QTableWidget#alarm_table::item {{
                padding: 4px;
                border: none;
            }}
            
            QTableWidget#alarm_table::item:selected {{
                background: {tm.bg_medium()};
                color: {tm.text_primary()};
            }}
            
            QTableWidget#alarm_table::item:alternate {{
                background: {tm.bg_light()};
            }}
            
            QHeaderView::section {{
                background: {tm.bg_medium()};
                color: {tm.text_primary()};
                border: 1px solid {tm.border_dark()};
                padding: 6px;
                font-weight: bold;
                font-size: 11px;
            }}
            
            QScrollBar:vertical {{
                background: {tm.bg_medium()};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {tm.border_medium()};
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {tm.glow_cyan()};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # 查询按钮样式（与 BarHistory 一致）
        self.query_btn.setStyleSheet(f"""
            QPushButton#query_btn {{
                background: {colors.GLOW_CYAN};
                color: {colors.TEXT_ON_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#query_btn:hover {{
                background: {colors.GLOW_CYAN}CC;
            }}
            QPushButton#query_btn:pressed {{
                background: {colors.GLOW_CYAN}99;
            }}
        """)
    
    def showEvent(self, event):
        # 页面显示时加载批次列表（不自动查询，等用户点查询按钮）
        super().showEvent(event)
        self.load_batch_list()
    
    def hideEvent(self, event):
        super().hideEvent(event)
