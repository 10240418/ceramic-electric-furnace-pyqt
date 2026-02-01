"""
批次配置对话框 - 用于开始冶炼前配置批次编号
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QFrame, QSpinBox, QListView
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from ui.styles.themes import ThemeManager
from backend.bridge.history_query import HistoryQueryService
from loguru import logger


class DialogBatchConfig(QDialog):
    """批次配置对话框"""
    
    # 信号：确认批次配置（返回批次编号）
    batch_confirmed = pyqtSignal(str)
    
    # 1. 初始化对话框
    def __init__(self, furnace_number: int = 3, parent=None):
        super().__init__(parent)
        self.furnace_number = furnace_number
        self.theme_manager = ThemeManager.instance()
        self.history_service = HistoryQueryService.get_instance()
        
        self.setWindowTitle("开始记录")
        self.setModal(True)
        
        # 设置窗口标志，去除问号按钮
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # 初始化数据
        now = datetime.now()
        self.selected_year = now.year
        self.selected_month = now.month
        self.selected_batch_number = self.get_next_batch_number()
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(16)
        
        # 1. 年份行（带 +/- 按钮）
        year_layout = QHBoxLayout()
        year_layout.setSpacing(12)
        year_label = QLabel("年份:")
        year_label.setObjectName("rowLabel")
        year_label.setFixedWidth(80)
        year_layout.addWidget(year_label)
        
        btn_year_minus = QPushButton("-")
        btn_year_minus.setObjectName("btnMinus")
        btn_year_minus.setFixedSize(50, 44)
        btn_year_minus.clicked.connect(self.decrease_year)
        year_layout.addWidget(btn_year_minus)
        
        self.year_combo = self.create_year_selector()
        year_layout.addWidget(self.year_combo)
        
        btn_year_plus = QPushButton("+")
        btn_year_plus.setObjectName("btnPlus")
        btn_year_plus.setFixedSize(50, 44)
        btn_year_plus.clicked.connect(self.increase_year)
        year_layout.addWidget(btn_year_plus)
        
        main_layout.addLayout(year_layout)
        
        # 2. 月份行（带 +/- 按钮）
        month_layout = QHBoxLayout()
        month_layout.setSpacing(12)
        month_label = QLabel("月份:")
        month_label.setObjectName("rowLabel")
        month_label.setFixedWidth(80)
        month_layout.addWidget(month_label)
        
        btn_month_minus = QPushButton("-")
        btn_month_minus.setObjectName("btnMinus")
        btn_month_minus.setFixedSize(50, 44)
        btn_month_minus.clicked.connect(self.decrease_month)
        month_layout.addWidget(btn_month_minus)
        
        self.month_combo = self.create_month_selector()
        month_layout.addWidget(self.month_combo)
        
        btn_month_plus = QPushButton("+")
        btn_month_plus.setObjectName("btnPlus")
        btn_month_plus.setFixedSize(50, 44)
        btn_month_plus.clicked.connect(self.increase_month)
        month_layout.addWidget(btn_month_plus)
        
        main_layout.addLayout(month_layout)
        
        # 3. 炉次行
        batch_layout = QHBoxLayout()
        batch_layout.setSpacing(12)
        batch_label = QLabel("炉次:")
        batch_label.setObjectName("rowLabel")
        batch_label.setFixedWidth(80)
        batch_layout.addWidget(batch_label)
        
        btn_minus = QPushButton("-")
        btn_minus.setObjectName("btnMinus")
        btn_minus.setFixedSize(50, 44)
        btn_minus.clicked.connect(lambda: self.batch_spinbox.setValue(self.batch_spinbox.value() - 1))
        batch_layout.addWidget(btn_minus)
        
        self.batch_spinbox = self.create_batch_selector()
        batch_layout.addWidget(self.batch_spinbox)
        
        btn_plus = QPushButton("+")
        btn_plus.setObjectName("btnPlus")
        btn_plus.setFixedSize(50, 44)
        btn_plus.clicked.connect(lambda: self.batch_spinbox.setValue(self.batch_spinbox.value() + 1))
        batch_layout.addWidget(btn_plus)
        
        main_layout.addLayout(batch_layout)
        
        # 4. 批次编号行
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(12)
        preview_label = QLabel("批次编号:")
        preview_label.setObjectName("rowLabel")
        preview_label.setFixedWidth(80)
        preview_layout.addWidget(preview_label)
        
        self.batch_preview_label = QLabel()
        self.batch_preview_label.setObjectName("batchPreview")
        self.batch_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batch_preview_label.setFixedHeight(44)
        preview_layout.addWidget(self.batch_preview_label)
        self.update_batch_preview()
        
        main_layout.addLayout(preview_layout)
        
        main_layout.addSpacing(10)
        
        # 5. 按钮行
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.setFixedHeight(48)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_confirm = QPushButton("确认开始")
        btn_confirm.setObjectName("btnConfirm")
        btn_confirm.setFixedHeight(48)
        btn_confirm.clicked.connect(self.on_confirm)
        button_layout.addWidget(btn_confirm)
        
        main_layout.addLayout(button_layout)
    

    
    # 3. 创建年份选择器
    def create_year_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("yearCombo")
        combo.setFixedHeight(44)
        combo.setEditable(False)  # 禁止编辑
        
        # 设置下拉列表视图，增加行高
        list_view = QListView()
        combo.setView(list_view)
        
        # 添加年份选项（当前年份 ± 5 年）
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 6):
            combo.addItem(f"{year}年", year)
        
        # 设置当前年份
        combo.setCurrentText(f"{current_year}年")
        combo.currentIndexChanged.connect(self.on_year_changed)
        
        return combo
    
    # 4. 创建月份选择器
    def create_month_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("monthCombo")
        combo.setFixedHeight(44)
        combo.setEditable(False)  # 禁止编辑
        
        # 设置下拉列表视图，增加行高
        list_view = QListView()
        combo.setView(list_view)
        
        # 添加月份选项
        for month in range(1, 13):
            combo.addItem(f"{month}月", month)
        
        # 设置当前月份
        current_month = datetime.now().month
        combo.setCurrentIndex(current_month - 1)
        combo.currentIndexChanged.connect(self.on_month_changed)
        
        return combo
    
    # 5. 创建炉次选择器（显示两位数）
    def create_batch_selector(self) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setObjectName("batchSpinBox")
        spinbox.setFixedHeight(44)
        spinbox.setMinimum(1)
        spinbox.setMaximum(99)
        spinbox.setValue(self.selected_batch_number)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置前缀，使其显示为两位数
        spinbox.setPrefix("")
        spinbox.setSpecialValueText("01")
        
        # 连接信号
        spinbox.valueChanged.connect(self.on_batch_number_changed)
        
        # 自定义显示格式（两位数）
        spinbox.lineEdit().setText(f"{self.selected_batch_number:02d}")
        
        return spinbox
    

    

    
    # 6. 年份变化
    def on_year_changed(self, index: int):
        self.selected_year = self.year_combo.currentData()
        self.update_batch_preview()
        logger.debug(f"年份变化: {self.selected_year}")
    
    # 7. 月份变化
    def on_month_changed(self, index: int):
        self.selected_month = self.month_combo.currentData()
        self.update_batch_preview()
        logger.debug(f"月份变化: {self.selected_month}")
    
    # 6.1 增加年份
    def increase_year(self):
        current_index = self.year_combo.currentIndex()
        if current_index < self.year_combo.count() - 1:
            self.year_combo.setCurrentIndex(current_index + 1)
    
    # 6.2 减少年份
    def decrease_year(self):
        current_index = self.year_combo.currentIndex()
        if current_index > 0:
            self.year_combo.setCurrentIndex(current_index - 1)
    
    # 7.1 增加月份
    def increase_month(self):
        current_index = self.month_combo.currentIndex()
        if current_index < 11:  # 0-11 对应 1-12月
            self.month_combo.setCurrentIndex(current_index + 1)
        else:
            self.month_combo.setCurrentIndex(0)  # 循环到1月
    
    # 7.2 减少月份
    def decrease_month(self):
        current_index = self.month_combo.currentIndex()
        if current_index > 0:
            self.month_combo.setCurrentIndex(current_index - 1)
        else:
            self.month_combo.setCurrentIndex(11)  # 循环到12月
    
    # 8. 炉次变化（更新显示为两位数）
    def on_batch_number_changed(self, value: int):
        self.selected_batch_number = value
        # 更新 SpinBox 显示为两位数
        self.batch_spinbox.lineEdit().setText(f"{value:02d}")
        self.update_batch_preview()
        logger.debug(f"炉次变化: {value:02d}")
    
    # 9. 更新批次编号预览
    def update_batch_preview(self):
        batch_code = self.generate_batch_code()
        self.batch_preview_label.setText(batch_code)
    
    # 10. 生成批次编号
    def generate_batch_code(self) -> str:
        """
        生成批次编号
        格式: YYMMFFDD
        - YY: 年份后两位
        - MM: 月份（01-12）
        - FF: 炉号（固定 03）
        - DD: 当月第几炉（01-99）
        
        示例: 2026年12月3号炉第5炉 -> 26120305
        """
        year_suffix = self.selected_year % 100  # 年份后两位
        batch_code = f"{year_suffix:02d}{self.selected_month:02d}{self.furnace_number:02d}{self.selected_batch_number:02d}"
        return batch_code
    
    # 11. 从数据库获取下一个炉次编号
    def get_next_batch_number(self) -> int:
        """从数据库查询最新批次编号，返回下一个炉次
        
        逻辑：
        1. 查询所有批次号
        2. 筛选出当前年月的批次号（格式：YYMMFFDD）
        3. 提取最后两位数（DD），取最大值 + 1
        4. 如果没有数据，返回 1
        
        示例：
        - 最新批次：26020302 -> 返回 03
        - 最新批次：26020399 -> 返回 100（超出范围，返回 1）
        - 无数据 -> 返回 1
        """
        try:
            # 查询所有批次号
            batches = self.history_service.get_batch_list(limit=100)
            
            if not batches:
                logger.info("数据库无批次数据，默认炉次为 01")
                return 1
            
            # 当前年月前缀（YYMM）
            now = datetime.now()
            year_suffix = now.year % 100
            month = now.month
            prefix = f"{year_suffix:02d}{month:02d}{self.furnace_number:02d}"
            
            logger.debug(f"查询批次前缀: {prefix}")
            
            # 筛选当前年月的批次号
            current_month_batches = []
            for batch in batches:
                batch_code = batch.get("batch_code", "")
                if batch_code.startswith(prefix) and len(batch_code) == 8:
                    # 提取最后两位数
                    try:
                        batch_number = int(batch_code[-2:])
                        current_month_batches.append(batch_number)
                        logger.debug(f"找到批次: {batch_code}, 炉次: {batch_number}")
                    except ValueError:
                        continue
            
            if not current_month_batches:
                logger.info(f"当前月份无批次数据，默认炉次为 01")
                return 1
            
            # 取最大值 + 1
            max_batch = max(current_month_batches)
            next_batch = max_batch + 1
            
            # 防止超出范围
            if next_batch > 99:
                logger.warning(f"炉次超出范围 ({next_batch})，重置为 01")
                return 1
            
            logger.info(f"最新批次炉次: {max_batch:02d}, 下一炉次: {next_batch:02d}")
            return next_batch
            
        except Exception as e:
            logger.error(f"查询下一炉次失败: {e}")
            return 1
    
    # 12. 调整窗口大小（固定大小）
    def showEvent(self, event):
        """显示事件，调整窗口大小"""
        super().showEvent(event)
        
        # 固定窗口大小
        self.setFixedSize(450, 320)
        
        # 居中显示
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - 450) // 2
            y = parent_rect.y() + (parent_rect.height() - 320) // 2
            self.move(x, y)
    
    # 13. 确认按钮点击
    def on_confirm(self):
        batch_code = self.generate_batch_code()
        logger.info(f"批次配置确认: {batch_code}")
        
        # 发送信号
        self.batch_confirmed.emit(batch_code)
        
        # 关闭对话框
        self.accept()
    
    # 14. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_DARK};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 8px;
            }}
            
            QLabel#rowLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
            
            QLabel#batchPreview {{
                color: {colors.GLOW_PRIMARY};
                font-size: 20px;
                font-weight: bold;
                font-family: "Consolas", "Courier New", monospace;
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                background: {colors.BG_LIGHT};
                padding: 8px;
                letter-spacing: 2px;
            }}
            
            QComboBox {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 16px;
            }}
            
            QComboBox:hover {{
                border: 1px solid {colors.BORDER_GLOW};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid {colors.TEXT_PRIMARY};
                margin-right: 10px;
            }}
            
            QComboBox QAbstractItemView {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_GLOW};
                selection-background-color: {colors.GLOW_PRIMARY}33;
                selection-color: {colors.TEXT_PRIMARY};
                outline: none;
            }}
            
            QComboBox QAbstractItemView::item {{
                min-height: 45px;
                padding: 12px 16px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background: {colors.GLOW_PRIMARY}26;
            }}
            
            QSpinBox {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 18px;
                font-weight: bold;
                font-family: "Consolas", "Courier New", monospace;
            }}
            
            QSpinBox:hover {{
                border: 1px solid {colors.BORDER_GLOW};
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
            }}
            
            QPushButton#btnMinus, QPushButton#btnPlus {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                font-size: 20px;
                font-weight: bold;
            }}
            
            QPushButton#btnMinus:hover, QPushButton#btnPlus:hover {{
                border: 1px solid {colors.BORDER_GLOW};
                background: {colors.BG_MEDIUM};
            }}
            
            QPushButton#btnMinus:pressed, QPushButton#btnPlus:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QPushButton#btnCancel {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_SECONDARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                font-size: 16px;
            }}
            
            QPushButton#btnCancel:hover {{
                border: 1px solid {colors.BORDER_GLOW};
                color: {colors.TEXT_PRIMARY};
            }}
            
            QPushButton#btnConfirm {{
                background: {colors.GLOW_PRIMARY}33;
                color: {colors.GLOW_PRIMARY};
                border: 1px solid {colors.GLOW_PRIMARY};
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton#btnConfirm:hover {{
                background: {colors.GLOW_PRIMARY}4D;
            }}
            
            QPushButton#btnConfirm:pressed {{
                background: {colors.GLOW_PRIMARY}66;
            }}
        """)
    
    # 17. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

