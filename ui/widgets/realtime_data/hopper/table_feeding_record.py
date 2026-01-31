"""
投料记录表组件 - 显示投料历史记录列表
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager
from datetime import datetime


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
        
        # 标题
        title_label = QLabel("投料记录")
        title_label.setObjectName("tableTitle")
        title_label.setFixedHeight(36)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 记录容器
        self.records_container = QWidget()
        self.records_container.setObjectName("recordsContainer")
        self.records_layout = QVBoxLayout(self.records_container)
        self.records_layout.setContentsMargins(8, 8, 8, 8)
        self.records_layout.setSpacing(6)
        self.records_layout.addStretch()
        
        scroll_area.setWidget(self.records_container)
        main_layout.addWidget(scroll_area)
    
    # 3. 添加记录
    def add_record(self, timestamp: datetime, weight: float):
        """
        添加投料记录
        
        Args:
            timestamp: 投料时间
            weight: 投料重量（kg）
        """
        record_item = self.create_record_item(timestamp, weight)
        
        # 插入到最前面（最新的在上面）
        self.records_layout.insertWidget(0, record_item)
        
        self.records.append({
            'timestamp': timestamp,
            'weight': weight
        })
    
    # 4. 创建记录项
    def create_record_item(self, timestamp: datetime, weight: float) -> QFrame:
        """创建单条记录项"""
        item = QFrame()
        item.setObjectName("recordItem")
        item.setFixedHeight(48)
        
        layout = QVBoxLayout(item)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # 时间
        time_label = QLabel(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        time_label.setObjectName("recordTime")
        layout.addWidget(time_label)
        
        # 重量
        weight_label = QLabel(f"投料重量: {weight:.1f} kg")
        weight_label.setObjectName("recordWeight")
        layout.addWidget(weight_label)
        
        return item
    
    # 5. 清空记录
    def clear_records(self):
        """清空所有记录"""
        while self.records_layout.count() > 1:
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
        self.clear_records()
        
        for record in records:
            self.add_record(record['timestamp'], record['weight'])
    
    # 7. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#feedingRecordTable {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QLabel#tableTitle {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-radius: 6px 6px 0 0;
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
                background: {colors.BG_DARK};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
            }}
            QFrame#recordItem:hover {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_MEDIUM};
            }}
            
            QLabel#recordTime {{
                color: {colors.TEXT_SECONDARY};
                font-size: 12px;
                border: none;
                background: transparent;
            }}
            
            QLabel#recordWeight {{
                color: {colors.GLOW_PRIMARY};
                font-size: 13px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                background: {colors.BG_DARK};
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {colors.BORDER_MEDIUM};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors.BORDER_GLOW};
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

