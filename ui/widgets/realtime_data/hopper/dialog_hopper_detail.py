"""
投料详情弹窗 - 显示料仓详细信息、投料记录和统计
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles.themes import ThemeManager
from .table_feeding_record import TableFeedingRecord
from .chart_feeding_stats import ChartFeedingStats
from .dialog_set_limit import DialogSetLimit
from backend.bridge.history_query import get_history_query_service
from backend.bridge.data_cache import DataCache
from loguru import logger
from datetime import datetime, timedelta


class DialogHopperDetail(QDialog):
    """投料详情弹窗"""
    
    # 信号：料仓上限设置完成
    upper_limit_set = pyqtSignal(float)
    
    # 1. 初始化弹窗
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 数据
        self.feeding_total = 0.0
        self.hopper_weight = 0.0
        self.upper_limit = 5000.0
        self.is_feeding = False
        
        # 历史查询服务
        self.history_service = get_history_query_service()
        self.data_cache = DataCache()  # DataCache 使用 __new__ 实现单例，直接实例化即可
        
        self.setWindowTitle("投料详情")
        self.setModal(True)
        
        # 设置窗口标志，去除问号按钮
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # 顶部：投料详情标题 + 投料状态
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        
        # 左侧：投料详情标题
        title_label = QLabel("投料详情")
        title_label.setObjectName("titleLabel")
        title_label.setFixedHeight(40)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 右侧：投料状态（减小宽度，右对齐）
        status_label = QLabel("投料状态: 未投料")
        status_label.setObjectName("statusLabel")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setFixedHeight(40)
        status_label.setFixedWidth(200)
        header_layout.addWidget(status_label)
        self.status_label = status_label
        
        main_layout.addLayout(header_layout)
        
        # 三行数据
        data_layout = QHBoxLayout()
        data_layout.setSpacing(16)
        
        # 投料累计
        self.feeding_total_widget = self.create_data_card("投料累计", "0", "kg")
        data_layout.addWidget(self.feeding_total_widget, 1)
        
        # 料仓重量
        self.hopper_weight_widget = self.create_data_card("料仓重量", "0", "kg")
        data_layout.addWidget(self.hopper_weight_widget, 1)
        
        # 料仓上限（带按钮）
        self.upper_limit_widget = self.create_limit_card()
        data_layout.addWidget(self.upper_limit_widget, 1)
        
        main_layout.addLayout(data_layout)
        
        # 下方：投料记录表 + 投料统计图（占据76%高度）
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)
        
        # 投料记录表
        self.feeding_record_table = TableFeedingRecord()
        charts_layout.addWidget(self.feeding_record_table, 1)
        
        # 投料统计折线图
        self.feeding_stats_chart = ChartFeedingStats()
        charts_layout.addWidget(self.feeding_stats_chart, 1)
        
        main_layout.addLayout(charts_layout, 3)
    
    # 3. 创建数据卡片
    def create_data_card(self, label: str, value: str, unit: str) -> QFrame:
        """创建数据卡片"""
        card = QFrame()
        card.setObjectName("dataCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setObjectName("dataLabel")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)
        
        # 数值 + 单位
        value_layout = QHBoxLayout()
        value_layout.setSpacing(4)
        value_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setObjectName("dataValue")
        value_layout.addWidget(value_label)
        
        unit_label = QLabel(unit)
        unit_label.setObjectName("dataUnit")
        value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        return card
    
    # 4. 创建料仓上限卡片（带设置按钮）
    def create_limit_card(self) -> QFrame:
        """创建料仓上限卡片"""
        card = QFrame()
        card.setObjectName("dataCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 标签
        label_widget = QLabel("料仓上限")
        label_widget.setObjectName("dataLabel")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)
        
        # 数值 + 单位 + 设置按钮
        value_layout = QHBoxLayout()
        value_layout.setSpacing(4)
        value_layout.addStretch()
        
        self.limit_value_label = QLabel("5000")
        self.limit_value_label.setObjectName("dataValue")
        value_layout.addWidget(self.limit_value_label)
        
        unit_label = QLabel("kg")
        unit_label.setObjectName("dataUnit")
        value_layout.addWidget(unit_label)
        
        # 设置按钮
        set_btn = QPushButton("设置")
        set_btn.setObjectName("setLimitBtn")
        set_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_btn.clicked.connect(self.on_set_limit_clicked)
        value_layout.addWidget(set_btn)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        return card
    
    # 5. 点击设置料仓上限按钮
    def on_set_limit_clicked(self):
        """打开设置料仓上限弹窗"""
        dialog = DialogSetLimit(self.upper_limit, self)
        dialog.limit_set.connect(self.on_limit_set)
        dialog.exec()
    
    # 6. 料仓上限设置完成
    def on_limit_set(self, limit: float):
        """料仓上限设置完成"""
        self.upper_limit = limit
        self.limit_value_label.setText(str(int(limit)))
        
        # 发射信号
        self.upper_limit_set.emit(limit)
        
        logger.info(f"料仓上限已更新: {limit} kg")
    
    # 7. 更新数据
    def update_data(self, feeding_total: float, hopper_weight: float, 
                    upper_limit: float, is_feeding: bool):
        """
        更新数据
        
        Args:
            feeding_total: 投料累计（kg）
            hopper_weight: 料仓重量（kg）
            upper_limit: 料仓上限（kg）
            is_feeding: 是否正在投料
        """
        self.feeding_total = feeding_total
        self.hopper_weight = hopper_weight
        self.upper_limit = upper_limit
        self.is_feeding = is_feeding
        
        # 更新状态
        status_text = "投料状态: 投料中" if is_feeding else "投料状态: 未投料"
        self.status_label.setText(status_text)
        
        colors = self.theme_manager.get_colors()
        if is_feeding:
            self.status_label.setStyleSheet(f"""
                QLabel#statusLabel {{
                    background: {colors.BG_LIGHT};
                    color: {colors.GLOW_PRIMARY};
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid {colors.BORDER_GLOW};
                    border-radius: 6px;
                }}
            """)
        else:
            self.status_label.setStyleSheet(f"""
                QLabel#statusLabel {{
                    background: {colors.BG_LIGHT};
                    color: {colors.TEXT_SECONDARY};
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid {colors.BORDER_DARK};
                    border-radius: 6px;
                }}
            """)
        
        # 更新投料累计
        feeding_value_label = self.feeding_total_widget.findChild(QLabel, "dataValue")
        if feeding_value_label:
            feeding_value_label.setText(str(int(feeding_total)))
        
        # 更新料仓重量
        weight_value_label = self.hopper_weight_widget.findChild(QLabel, "dataValue")
        if weight_value_label:
            weight_value_label.setText(str(int(hopper_weight)))
        
        # 更新料仓上限
        self.limit_value_label.setText(str(int(upper_limit)))
    
    # 8. 添加投料记录
    def add_feeding_record(self, timestamp: datetime, weight: float):
        """
        添加投料记录
        
        Args:
            timestamp: 投料时间
            weight: 投料重量（kg）
        """
        self.feeding_record_table.add_record(timestamp, weight)
        self.feeding_stats_chart.add_data_point(timestamp, weight)
    
    # 9. 设置投料记录列表
    def set_feeding_records(self, records: list):
        """
        设置投料记录列表
        
        Args:
            records: 记录列表 [{'timestamp': datetime, 'weight': float}, ...]
        """
        self.feeding_record_table.set_records(records)
    
    # 10. 调整窗口大小（78%宽 × 80%高）
    def showEvent(self, event):
        """显示事件，调整窗口大小并加载历史数据"""
        super().showEvent(event)
        
        # 获取父窗口大小
        if self.parent():
            parent_size = self.parent().size()
            width = int(parent_size.width() * 0.78)
            height = int(parent_size.height() * 0.8)
            self.resize(width, height)
            
            # 居中显示
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - width) // 2
            y = parent_rect.y() + (parent_rect.height() - height) // 2
            self.move(x, y)
        
        # 加载历史投料数据
        self.load_feeding_history()
    
    # 11. 加载历史投料数据
    def load_feeding_history(self):
        """从数据库加载当前批次的历史投料数据"""
        try:
            # 获取当前批次号（从批次服务中获取）
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            batch_code = batch_service.batch_code
            
            if not batch_code:
                logger.warning("未获取到当前批次号，无法加载历史投料数据")
                return
            
            logger.info(f"开始加载批次 {batch_code} 的历史投料数据...")
            
            # 查询当前批次的投料累计历史数据（无聚合，原始数据）
            feeding_data = self.history_service.query_feeding_total_raw(batch_code)
            
            if not feeding_data:
                logger.warning(f"批次 {batch_code} 没有历史投料数据")
                return
            
            logger.info(f"查询到 {len(feeding_data)} 条投料累计数据")
            
            # 提取时间和累计值
            timestamps = [d['time'] for d in feeding_data]
            cumulative_values = [d['value'] for d in feeding_data]
            
            # 更新投料累计曲线
            self.feeding_stats_chart.set_data(timestamps, cumulative_values)
            
            # 计算投料记录（差值法）
            feeding_records = self.calculate_feeding_records(feeding_data)
            
            logger.info(f"计算出 {len(feeding_records)} 条投料记录")
            
            # 更新投料记录表
            self.set_feeding_records(feeding_records)
            
        except Exception as e:
            logger.error(f"加载历史投料数据失败: {e}", exc_info=True)
    
    # 12. 计算投料记录（差值法）
    def calculate_feeding_records(self, feeding_data: list) -> list:
        """
        根据投料累计数据计算每次投料记录
        
        算法：
        1. 遍历投料累计数据，计算相邻两点的差值
        2. 如果差值 > 阈值（如50kg），认为发生了一次投料
        3. 记录投料时间和投料重量
        
        Args:
            feeding_data: 投料累计数据 [{'time': datetime, 'value': float}, ...]
            
        Returns:
            投料记录列表 [{'timestamp': datetime, 'weight': float}, ...]
        """
        if len(feeding_data) < 2:
            return []
        
        records = []
        threshold = 50.0  # 投料阈值（kg），小于此值的变化忽略
        
        for i in range(1, len(feeding_data)):
            prev_value = feeding_data[i - 1]['value']
            curr_value = feeding_data[i]['value']
            curr_time = feeding_data[i]['time']
            
            # 计算差值
            diff = curr_value - prev_value
            
            # 如果差值大于阈值，认为发生了投料
            if diff > threshold:
                records.append({
                    'timestamp': curr_time,
                    'weight': diff
                })
                logger.debug(f"检测到投料: 时间={curr_time}, 重量={diff:.1f}kg")
        
        return records
    
    # 13. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_DARK};
                border: 2px solid {colors.BORDER_GLOW};
                border-radius: 8px;
            }}
            
            QLabel#titleLabel {{
                background: transparent;
                color: {colors.TEXT_PRIMARY};
                font-size: 20px;
                font-weight: bold;
                border: none;
            }}
            
            QLabel#statusLabel {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_SECONDARY};
                font-size: 16px;
                font-weight: bold;
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QFrame#dataCard {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QLabel#dataLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
            
            QLabel#dataValue {{
                color: {colors.GLOW_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            QLabel#dataUnit {{
                color: {colors.TEXT_SECONDARY};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
            
            QPushButton#setLimitBtn {{
                background: {colors.BUTTON_PRIMARY_BG};
                color: {colors.BUTTON_PRIMARY_TEXT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton#setLimitBtn:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton#setLimitBtn:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 14. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
