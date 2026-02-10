"""
投料记录表组件 - 显示投料历史记录列表
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QScroller, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from ui.styles.themes import ThemeManager
from datetime import datetime
from loguru import logger


class TableFeedingRecord(QFrame):
    """投料记录表组件"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("feedingRecordTable")
        
        self.records = []
        
        self.init_ui()
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏（和投料累计图表一样的样式）
        title_widget = QWidget()
        title_widget.setObjectName("titleBar")
        title_widget.setFixedHeight(36)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(12, 0, 12, 0)
        title_layout.setSpacing(0)
        
        title_label = QLabel("投料记录")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_label)
        
        main_layout.addWidget(title_widget)
        
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
        self.records_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.records_layout = QVBoxLayout(self.records_container)
        self.records_layout.setContentsMargins(12, 2, 12, 2)
        self.records_layout.setSpacing(0)
        self.records_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.records_container)
        
        # 注意：QScroller 在 showEvent 中延迟注册，避免和父组件的 QScroller 冲突
        
        main_layout.addWidget(self.scroll_area)
    
    # 2.5 显示事件 - 延迟注册 QScroller
    def showEvent(self, event):
        super().showEvent(event)
        # 延迟 100ms 注册 QScroller，确保父组件的事件处理完成
        QTimer.singleShot(100, self._register_scroller)
    
    # 2.6 注册 QScroller
    def _register_scroller(self):
        """注册 QScroller，启用拖动滚动"""
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
    
    # 3. 添加记录
    def add_record(self, timestamp: datetime, weight: float):
        """
        添加单条投料记录（实时新增，插入到最前面）
        
        Args:
            timestamp: 投料时间
            weight: 投料重量（kg）
        """
        # 如果已有记录，先插入分割线
        has_existing = self.records_layout.count() > 0
        
        record_item = self.create_record_item(timestamp, weight)
        self.records_layout.insertWidget(0, record_item)
        
        if has_existing:
            divider_container = QWidget()
            divider_layout = QHBoxLayout(divider_container)
            divider_layout.setContentsMargins(0, 0, 0, 0)
            divider_layout.setSpacing(0)
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setObjectName("dataDivider")
            divider.setFixedHeight(1)
            divider_layout.addWidget(divider)
            self.records_layout.insertWidget(1, divider_container)
        else:
            # 第一条记录，底部也加分割线
            self._append_bottom_divider()
        
        self.records.append({
            'timestamp': timestamp,
            'weight': weight
        })
    
    # 4. 创建记录项（参考 CardHopper 的紧凑水平布局）
    def create_record_item(self, timestamp: datetime, weight: float) -> QFrame:
        """创建单条记录项"""
        item = QFrame()
        item.setObjectName("recordItem")
        item.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        item.setFixedHeight(42)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(12)
        
        # 左侧：日期 + 时间（上下堆叠）
        time_container = QVBoxLayout()
        time_container.setContentsMargins(0, 0, 0, 0)
        time_container.setSpacing(0)
        
        date_label = QLabel(timestamp.strftime("%Y-%m-%d"))
        date_label.setObjectName("recordDate")
        date_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        date_label.setFixedHeight(16)
        time_container.addWidget(date_label)
        
        time_label = QLabel(timestamp.strftime("%H:%M:%S"))
        time_label.setObjectName("recordTime")
        time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        time_label.setFixedHeight(16)
        time_container.addWidget(time_label)
        
        layout.addLayout(time_container, stretch=3)
        
        # 右侧：重量 + 单位
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
    
    # 4.5 添加底部分割线
    def _append_bottom_divider(self):
        divider_container = QWidget()
        divider_container.setObjectName("bottomDivider")
        divider_layout = QHBoxLayout(divider_container)
        divider_layout.setContentsMargins(0, 0, 0, 0)
        divider_layout.setSpacing(0)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("dataDivider")
        divider.setFixedHeight(1)
        divider_layout.addWidget(divider)
        self.records_layout.addWidget(divider_container)
    
    # 5. 清空记录
    def clear_records(self):
        """清空所有记录"""
        while self.records_layout.count() > 0:
            item = self.records_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.records.clear()
    
    # 6. 设置记录列表
    def set_records(self, records: list):
        """
        设置记录列表
        
        Args:
            records: 记录列表 [{'timestamp': datetime, 'weight': float}, ...]
        """
        logger.info(f"TableFeedingRecord.set_records: 收到 {len(records)} 条记录")
        self.clear_records()
        
        # 按时间降序排列（最新的在上面）
        sorted_records = sorted(records, key=lambda r: r['timestamp'], reverse=True)
        
        for i, record in enumerate(sorted_records):
            # 记录之间添加分割线
            if i > 0:
                divider_container = QWidget()
                divider_layout = QHBoxLayout(divider_container)
                divider_layout.setContentsMargins(0, 0, 0, 0)
                divider_layout.setSpacing(0)
                divider = QFrame()
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setObjectName("dataDivider")
                divider.setFixedHeight(1)
                divider_layout.addWidget(divider)
                self.records_layout.addWidget(divider_container)
            
            record_item = self.create_record_item(record['timestamp'], record['weight'])
            self.records_layout.addWidget(record_item)
            self.records.append(record)
        
        # 最后一条记录下方也添加分割线
        if sorted_records:
            self._append_bottom_divider()
        
        logger.info(f"TableFeedingRecord: 添加完成，当前 records_layout.count()={self.records_layout.count()}")
    
    # 7. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#feedingRecordTable {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QWidget#titleBar {{
                background: {colors.BG_LIGHT};
                border: none;
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-radius: 6px 6px 0 0;
            }}
            
            QLabel#titleLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
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
            }}
            
            QFrame#dataDivider {{
                background: {colors.BORDER_DARK};
                border: none;
                max-height: 1px;
                min-height: 1px;
            }}
            
            QLabel#recordDate {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0px;
            }}
            
            QLabel#recordTime {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0px;
            }}
            
            QLabel#recordWeightValue {{
                color: {colors.TEXT_ACCENT};
                font-size: 26px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            QLabel#recordUnit {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
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
    
    # 8. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
    


