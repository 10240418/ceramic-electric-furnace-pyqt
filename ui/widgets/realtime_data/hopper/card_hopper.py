"""
料仓卡片组件 - 显示料仓重量和投料统计
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QSizePolicy, QWidget, QScroller
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer, QPoint, QTime
from ui.styles.themes import ThemeManager
from datetime import datetime


class CardHopper(QFrame):
    """料仓卡片组件"""
    
    # 信号：点击设置料仓上限按钮
    set_limit_clicked = pyqtSignal()
    
    # 1. 初始化卡片
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("hopperCard")
        
        # 数据
        self.hopper_weight = 0.0
        self.feeding_total = 0.0
        self.upper_limit = 5000.0
        self.state = 'idle'
        
        # 投料记录
        self.records = []
        
        # 上一次的投料累计值（用于检测变化）
        self.last_feeding_total = 0.0
        
        # 单击检测
        self.mouse_press_pos = None
        self.mouse_press_time = None
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 添加默认测试数据
        self.add_default_records()
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧 60%：投料记录表
        self.create_left_panel()
        main_layout.addWidget(self.left_panel, stretch=60)
        
        # 右侧 40%：数据面板
        self.create_right_panel()
        main_layout.addWidget(self.right_panel, stretch=40)
    
    # 3. 创建左侧面板（投料记录表）
    def create_left_panel(self):
        self.left_panel = QFrame()
        self.left_panel.setObjectName("leftPanel")
        
        layout = QVBoxLayout(self.left_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 记录容器
        self.records_container = QWidget()
        self.records_container.setObjectName("recordsContainer")
        self.records_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.records_layout = QVBoxLayout(self.records_container)
        self.records_layout.setContentsMargins(0, 0, 0, 0)
        self.records_layout.setSpacing(0)
        self.records_layout.addStretch()
        
        self.scroll_area.setWidget(self.records_container)
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        
        # 安装事件过滤器到 viewport，用于检测单击事件
        self.scroll_area.viewport().installEventFilter(self)
        
        layout.addWidget(self.scroll_area, stretch=1)
    
    # 4. 创建右侧面板（数据面板）
    def create_right_panel(self):
        self.right_panel = QFrame()
        self.right_panel.setObjectName("rightPanel")
        
        layout = QVBoxLayout(self.right_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 设置料仓上限按钮
        self.set_limit_btn = QPushButton("设置料仓上限")
        self.set_limit_btn.setObjectName("setLimitBtn")
        self.set_limit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_limit_btn.clicked.connect(self.on_set_limit_clicked)
        layout.addWidget(self.set_limit_btn)
        
        # 分割线
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # 料仓上限数据块
        self.upper_limit_block = self.create_data_block("料仓上限:", "5000", "kg")
        self.upper_limit_block.setObjectName("upperLimitBlock")
        layout.addWidget(self.upper_limit_block, stretch=1)
        
        # 投料状态数据块
        self.status_block = self.create_status_block()
        layout.addWidget(self.status_block, stretch=1)
        
        # 料仓重量数据块
        self.hopper_weight_block = self.create_data_block("料仓重量:", "0", "kg")
        layout.addWidget(self.hopper_weight_block, stretch=1)
        
        # 投料累计数据块
        self.feeding_total_block = self.create_data_block("投料累计:", "0", "kg")
        layout.addWidget(self.feeding_total_block, stretch=1)
        
        for block in (self.upper_limit_block, self.status_block, self.hopper_weight_block, self.feeding_total_block):
            block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            block.layout().setContentsMargins(0, 0, 0, 0)
            block.layout().setSpacing(2)
    
    # 5. 创建数据块
    def create_data_block(self, label: str, value: str, unit: str) -> QFrame:
        block = QFrame()
        block.setObjectName("dataBlock")
        
        layout = QVBoxLayout(block)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 标签（小字，左对齐）
        label_widget = QLabel(label)
        label_widget.setObjectName("blockLabel")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label_widget)
        
        # 数值 + 单位
        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(4)
        value_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setObjectName("blockValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_layout.addWidget(value_label)
        
        unit_label = QLabel(unit)
        unit_label.setObjectName("blockUnit")
        unit_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_layout.addWidget(unit_label)
        
        layout.addLayout(value_layout)
        
        return block
    
    # 6. 创建状态数据块
    def create_status_block(self) -> QFrame:
        block = QFrame()
        block.setObjectName("statusBlock")
        
        layout = QVBoxLayout(block)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 标签（小字，右对齐）
        label_widget = QLabel("投料状态:")
        label_widget.setObjectName("blockLabel")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label_widget)
        
        # 状态值
        self.status_value_label = QLabel("静止")
        self.status_value_label.setObjectName("statusValue")
        self.status_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.status_value_label)
        
        return block
    
    # 7. 更新数据
    def update_data(self, hopper_weight: float, feeding_total: float, 
                    upper_limit: float, state: str = 'idle', batch_code: str = ''):
        """
        更新料仓数据
        
        数据验证：如果料仓重量和投料累计都为0，不更新显示（保持上一次的有效数据）
        检测投料累计变化：如果投料累计值变化，触发投料记录查询
        
        Args:
            hopper_weight: 料仓重量（kg）
            feeding_total: 投料累计（kg）
            upper_limit: 料仓上限（kg）
            state: 料仓状态
                - 'idle': 静止
                - 'feeding': 上料中
                - 'waiting_feed': 排队等待上料
                - 'discharging': 排料中
            batch_code: 批次号（用于查询投料记录）
        """
        # 数据验证：如果料仓重量和投料累计都为0，跳过本次更新
        if hopper_weight == 0.0 and feeding_total == 0.0:
            if self.hopper_weight > 0.0 or self.feeding_total > 0.0:
                return
        
        # 检测投料累计是否变化（变化超过 0.1kg 才认为是真实变化）
        feeding_total_changed = abs(feeding_total - self.last_feeding_total) > 0.1
        
        self.hopper_weight = hopper_weight
        self.feeding_total = feeding_total
        self.upper_limit = upper_limit
        self.state = state
        
        # 如果投料累计变化且有批次号，触发投料记录查询
        if feeding_total_changed and batch_code:
            from loguru import logger
            logger.info(f"检测到投料累计变化: {self.last_feeding_total:.1f} -> {feeding_total:.1f} kg，触发投料记录查询")
            self.last_feeding_total = feeding_total
            self.load_feeding_records(batch_code)
        
        # 更新投料累计
        if feeding_total > 0.0:
            value_label = self.feeding_total_block.findChild(QLabel, "blockValue")
            if value_label:
                value_label.setText(str(int(feeding_total)))
        
        # 更新料仓重量
        if hopper_weight > 0.0:
            value_label = self.hopper_weight_block.findChild(QLabel, "blockValue")
            if value_label:
                value_label.setText(str(int(hopper_weight)))
        
        # 更新料仓上限
        value_label = self.upper_limit_block.findChild(QLabel, "blockValue")
        if value_label:
            value_label.setText(str(int(upper_limit)))
        
        # 更新投料状态
        state_text_map = {
            'idle': '静止',
            'feeding': '上料中',
            'waiting_feed': '排队等待上料',
            'discharging': '排料中'
        }
        self.status_value_label.setText(state_text_map.get(state, '静止'))
        
        # 根据状态设置颜色（使用主题变量）
        colors = self.theme_manager.get_colors()
        state_color_map = {
            'idle': colors.TEXT_PRIMARY,
            'feeding': colors.GLOW_PRIMARY,
            'waiting_feed': colors.GLOW_ORANGE,
            'discharging': colors.GLOW_GREEN
        }
        self.status_value_label.setStyleSheet(f"""
            QLabel#statusValue {{
                color: {state_color_map.get(state, colors.TEXT_PRIMARY)};
                font-size: 24px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
        """)
    
    # 8. 点击设置料仓上限按钮
    def on_set_limit_clicked(self):
        """点击设置料仓上限按钮，发射信号"""
        self.set_limit_clicked.emit()
    
    # 9. 添加投料记录
    def add_record(self, timestamp: datetime, weight: float):
        """
        添加投料记录
        
        Args:
            timestamp: 投料时间
            weight: 投料重量（kg）
        """
        record_item = self.create_record_item(timestamp, weight)
        
        # 插入到最前面（最新的在上面）
        self.records_layout.insertWidget(0, record_item, stretch=1)
        
        self.records.append({
            'timestamp': timestamp,
            'weight': weight
        })
    
    # 10. 创建记录项
    def create_record_item(self, timestamp: datetime, weight: float) -> QFrame:
        """创建单条记录项"""
        item = QFrame()
        item.setObjectName("recordItem")
        item.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        item.setMinimumHeight(42)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(12)
        
        time_container = QVBoxLayout()
        time_container.setContentsMargins(0, 0, 0, 0)
        time_container.setSpacing(0)
        date_label = QLabel(timestamp.strftime("%Y-%m-%d"))
        date_label.setObjectName("recordDate")
        date_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        date_label.setFixedHeight(16)
        time_label = QLabel(timestamp.strftime("%H:%M:%S"))
        time_label.setObjectName("recordTime")
        time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        time_label.setFixedHeight(16)
        time_container.addWidget(date_label)
        time_container.addWidget(time_label)
        layout.addLayout(time_container, stretch=3)
        
        weight_layout = QHBoxLayout()
        weight_layout.setContentsMargins(0, 0, 0, 0)
        weight_layout.setSpacing(4)
        weight_layout.addStretch()
        weight_value_label = QLabel(f"{weight:.1f}")
        weight_value_label.setObjectName("recordWeightValue")
        weight_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        weight_layout.addWidget(weight_value_label)
        unit_label = QLabel("kg")
        unit_label.setObjectName("recordUnit")
        unit_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        weight_layout.addWidget(unit_label)
        layout.addLayout(weight_layout, stretch=2)
        
        return item
    
    # 11. 清空记录
    def clear_records(self):
        """清空所有记录"""
        while self.records_layout.count():
            item = self.records_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.records.clear()
    
    # 12. 设置记录列表
    def set_records(self, records: list):
        """
        设置记录列表
        
        Args:
            records: 记录列表 [{'timestamp': datetime, 'weight': float}, ...]
        """
        self.clear_records()
        
        # 反转记录列表，让最新的记录显示在最上面
        for record in reversed(records):
            self.add_record(record['timestamp'], record['weight'])
        self.records_layout.addStretch()
    
    # 14. 加载投料记录（从数据库查询）
    def load_feeding_records(self, batch_code: str):
        """
        从数据库加载投料记录
        
        Args:
            batch_code: 批次号
        """
        from loguru import logger
        from backend.bridge.history_query import get_history_query_service
        from datetime import timezone, timedelta
        
        try:
            logger.info(f"开始查询批次 {batch_code} 的投料记录...")
            
            history_service = get_history_query_service()
            
            # 查询投料记录（最近 300 条）
            feeding_records_data = history_service.query_feeding_records(
                batch_code=batch_code,
                limit=300
            )
            
            if feeding_records_data:
                logger.info(f"查询到 {len(feeding_records_data)} 条投料记录")
                
                # 转换为前端需要的格式
                records = []
                beijing_tz = timezone(timedelta(hours=8))
                
                for record in feeding_records_data:
                    # 将 ISO 格式时间字符串转换为 datetime 对象
                    from dateutil import parser
                    utc_time = parser.isoparse(record['time'])
                    
                    # 确保是 UTC 时区
                    if utc_time.tzinfo is None:
                        utc_time = utc_time.replace(tzinfo=timezone.utc)
                    
                    # 转换为北京时间
                    beijing_time = utc_time.astimezone(beijing_tz)
                    
                    records.append({
                        'timestamp': beijing_time,
                        'weight': record['discharge_weight']
                    })
                
                # 更新投料记录表
                self.set_records(records)
                logger.info(f"投料记录表已更新，共 {len(records)} 条记录")
            else:
                logger.warning(f"批次 {batch_code} 没有投料记录")
                self.clear_records()
        
        except Exception as e:
            logger.error(f"加载投料记录失败: {e}", exc_info=True)
            self.clear_records()
    
    # 15. 初始化投料记录（批次开始时调用）
    def init_feeding_records(self, batch_code: str):
        """
        初始化投料记录（批次开始时调用）
        
        Args:
            batch_code: 批次号
        """
        from loguru import logger
        logger.info(f"初始化批次 {batch_code} 的投料记录")
        
        # 重置上一次的投料累计值
        self.last_feeding_total = 0.0
        
        # 加载投料记录
        self.load_feeding_records(batch_code)
    
    # 16. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#hopperCard {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 6px;
            }}
            
            QFrame#leftPanel {{
                background: transparent;
                border-left: 1px solid {colors.BORDER_DARK};
                border-top: 1px solid {colors.BORDER_DARK};
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-right: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
            
            QFrame#rightPanel {{
                background: transparent;
                border-top: 1px solid {colors.BORDER_DARK};
                border-right: 1px solid {colors.BORDER_DARK};
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-left: none;
                border-radius: 6px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                padding: 12px 10px 10px;
            }}
            
            QPushButton#setLimitBtn {{
                background: {colors.BUTTON_PRIMARY_BG};
                color: {colors.BUTTON_PRIMARY_TEXT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
                padding: 10px 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#setLimitBtn:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton#setLimitBtn:pressed {{
                background: {colors.BG_MEDIUM};
            }}
            
            QFrame#divider {{
                background: {colors.BORDER_ACCENT};
                border: none;
                margin: 10px 0px;
            }}
            
            QFrame#dataBlock {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {colors.BORDER_ACCENT};
                border-radius: 0px;
            }}
            
            QFrame#upperLimitBlock {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {colors.BORDER_ACCENT};
                border-radius: 0px;
            }}
            
            QFrame#statusBlock {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {colors.BORDER_ACCENT};
                border-radius: 0px;
            }}
            
            QLabel#blockLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
            
            QLabel#blockValue {{
                color: {colors.GLOW_PRIMARY};
                font-size: 28px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            QLabel#blockUnit {{
                color: {colors.TEXT_PRIMARY};
                font-size: 20px;
                border: none;
                background: transparent;
            }}
            
            QFrame#statusBlock {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-radius: 0px;
            }}
            
            QLabel#statusValue {{
                color: {colors.TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            
            QWidget#recordsContainer {{
                background: transparent;
                border: none;
            }}
            
            QFrame#recordItem {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {colors.DIVIDER};
                padding-right: 4px;
            }}
            QFrame#recordItem:last-child {{
                border-bottom: none;
            }}
            
            QLabel#recordDate {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0px;
            }}
            
            QLabel#recordTime {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0px;
            }}
            
            QLabel#recordWeightValue {{
                color: {colors.TEXT_PRIMARY};
                font-size: 20px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            QLabel#recordUnit {{
                color: {colors.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.BUTTON_PRIMARY_BG};
                border-radius: 4px;
                min-height: 60px;
                max-height: 120px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
    
    # 17. 添加默认测试记录
    def add_default_records(self):
        """添加默认测试记录（用于 UI 测试）"""
        from datetime import timedelta
        
        # 生成 10 条测试记录
        base_time = datetime.now()
        test_weights = [150.5, 200.3, 175.8, 220.1, 190.6, 165.4, 210.9, 185.2, 195.7, 205.3]
        
        for i, weight in enumerate(test_weights):
            # 每条记录间隔 5 分钟
            record_time = base_time - timedelta(minutes=i * 5)
            self.add_record(record_time, weight)
    
    # 18. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        # 强制刷新所有投料记录的颜色
        self._refresh_record_colors()
    
    # 19. 强制刷新投料记录颜色
    def _refresh_record_colors(self):
        """强制刷新所有投料记录的日期和时间颜色"""
        colors = self.theme_manager.get_colors()
        
        # 查找所有记录项中的日期和时间标签
        for record_item in self.records_container.findChildren(QFrame):
            if record_item.objectName() == "recordItem":
                for label in record_item.findChildren(QLabel):
                    obj_name = label.objectName()
                    if obj_name == "recordDate" or obj_name == "recordTime":
                        label.setStyleSheet(f"""
                            QLabel {{
                                color: {colors.TEXT_PRIMARY};
                                font-size: 14px;
                                font-weight: 600;
                                border: none;
                                background: transparent;
                                padding: 0px;
                            }}
                        """)
                    elif obj_name == "recordWeightValue":
                        label.setStyleSheet(f"""
                            QLabel {{
                                color: {colors.TEXT_PRIMARY};
                                font-size: 20px;
                                font-weight: bold;
                                font-family: "Roboto Mono";
                                border: none;
                                background: transparent;
                            }}
                        """)
                    elif obj_name == "recordUnit":
                        label.setStyleSheet(f"""
                            QLabel {{
                                color: {colors.TEXT_PRIMARY};
                                font-size: 18px;
                                font-weight: bold;
                                border: none;
                                background: transparent;
                            }}
                        """)
    
    # 20. 事件过滤器（检测单击事件）
    def eventFilter(self, obj, event):
        """事件过滤器，用于检测滚动区域的单击事件"""
        if obj == self.scroll_area.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.mouse_press_pos = event.pos()
                    self.mouse_press_time = QTime.currentTime()
                    return False
            
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    if self.mouse_press_pos and self.mouse_press_time:
                        # 检查是否是单击（移动距离小于5像素，且时间小于300ms）
                        move_distance = (event.pos() - self.mouse_press_pos).manhattanLength()
                        elapsed_time = self.mouse_press_time.msecsTo(QTime.currentTime())
                        
                        if move_distance < 5 and elapsed_time < 300:
                            # 单击事件，打开详情弹窗
                            from loguru import logger
                            logger.info("检测到单击事件，打开料仓详情弹窗")
                            self.open_detail_dialog()
                        
                        self.mouse_press_pos = None
                        self.mouse_press_time = None
                    return False
        
        return super().eventFilter(obj, event)
    
    # 21. 打开详情弹窗
    def open_detail_dialog(self):
        """打开投料详情弹窗 - 使用延迟调用避免事件冲突"""
        # 使用 QTimer.singleShot 延迟打开，让当前事件处理完成
        QTimer.singleShot(50, self._do_open_detail_dialog)
    
    # 21.1 实际打开弹窗
    def _do_open_detail_dialog(self):
        """实际打开弹窗的方法"""
        from .dialog_hopper_detail import DialogHopperDetail
        
        dialog = DialogHopperDetail(self.window())
        
        # 更新弹窗数据
        dialog.update_data(
            feeding_total=self.feeding_total,
            hopper_weight=self.hopper_weight,
            upper_limit=self.upper_limit,
            state=self.state
        )
        
        # 连接料仓上限设置信号
        dialog.upper_limit_set.connect(self.on_detail_limit_set)
        
        dialog.exec()
    
    # 22. 详情弹窗中设置了料仓上限
    def on_detail_limit_set(self, limit: float):
        """详情弹窗中设置了料仓上限，更新主卡片显示"""
        self.upper_limit = limit
        value_label = self.upper_limit_block.findChild(QLabel, "blockValue")
        if value_label:
            value_label.setText(str(int(limit)))
