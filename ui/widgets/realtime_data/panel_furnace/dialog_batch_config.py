"""
批次配置对话框 - 用于开始冶炼前配置批次编号
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QMouseEvent
from datetime import datetime
from ui.styles.themes import ThemeManager
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
        
        # 无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(450, 380)
        
        # 用于拖动窗口
        self.drag_position = QPoint()
        
        # 初始化数据
        now = datetime.now()
        self.selected_year = now.year
        self.selected_month = now.month
        self.selected_batch_number = 1
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.apply_styles)
    
    # 2. 初始化 UI
    def init_ui(self):
        # 主容器（带边框和背景）
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        container.setGeometry(0, 0, 450, 380)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # 内容区域
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(16)
        
        # 年份选择
        self.year_combo = self.create_year_selector()
        content_layout.addLayout(self.create_field_layout("年份", self.year_combo))
        
        # 月份选择
        self.month_combo = self.create_month_selector()
        content_layout.addLayout(self.create_field_layout("月份", self.month_combo))
        
        # 炉次选择（使用 SpinBox + 按钮）
        self.batch_spinbox = self.create_batch_selector()
        content_layout.addLayout(self.create_batch_field_layout())
        
        # 批次编号预览
        self.batch_preview_label = QLabel()
        self.batch_preview_label.setObjectName("batchPreview")
        self.batch_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batch_preview_label.setFixedHeight(50)
        content_layout.addWidget(self.batch_preview_label)
        self.update_batch_preview()
        
        content_layout.addStretch()
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.setFixedSize(100, 36)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_confirm = QPushButton("确认")
        btn_confirm.setObjectName("btnConfirm")
        btn_confirm.setFixedSize(100, 36)
        btn_confirm.clicked.connect(self.on_confirm)
        button_layout.addWidget(btn_confirm)
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
    
    # 3. 创建自定义标题栏
    def create_title_bar(self) -> QFrame:
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(50)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 10, 0)
        
        # 图标
        icon_label = QLabel("📝")
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel("批次配置")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 关闭按钮
        btn_close = QPushButton("✕")
        btn_close.setObjectName("btnClose")
        btn_close.setFixedSize(40, 40)
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)
        
        return title_bar
    
    # 4. 鼠标事件（拖动窗口）
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # 只在标题栏区域允许拖动
            if event.position().y() < 50:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_position = QPoint()
    
    # 5. 创建字段布局
    def create_field_layout(self, label: str, widget) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        label_widget = QLabel(label)
        label_widget.setObjectName("fieldLabel")
        layout.addWidget(label_widget)
        
        layout.addWidget(widget)
        
        return layout
    
    # 6. 创建年份选择器
    def create_year_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("yearCombo")
        combo.setFixedHeight(40)
        
        # 添加年份选项（当前年份 ± 5 年）
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 6):
            combo.addItem(f"{year}年", year)
        
        # 设置当前年份
        combo.setCurrentText(f"{current_year}年")
        combo.currentIndexChanged.connect(self.on_year_changed)
        
        return combo
    
    # 7. 创建月份选择器
    def create_month_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("monthCombo")
        combo.setFixedHeight(40)
        
        # 添加月份选项
        for month in range(1, 13):
            combo.addItem(f"{month}月", month)
        
        # 设置当前月份
        current_month = datetime.now().month
        combo.setCurrentIndex(current_month - 1)
        combo.currentIndexChanged.connect(self.on_month_changed)
        
        return combo
    
    # 8. 创建炉次选择器（显示两位数）
    def create_batch_selector(self) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setObjectName("batchSpinBox")
        spinbox.setFixedHeight(40)
        spinbox.setMinimum(1)
        spinbox.setMaximum(99)
        spinbox.setValue(1)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置前缀，使其显示为两位数
        spinbox.setPrefix("")
        spinbox.setSpecialValueText("01")
        
        # 连接信号
        spinbox.valueChanged.connect(self.on_batch_number_changed)
        
        # 自定义显示格式（两位数）
        spinbox.lineEdit().setText("01")
        
        return spinbox
    
    # 9. 创建炉次字段布局（带 +1/-1 按钮）
    def create_batch_field_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        label = QLabel("当月第几炉")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        
        # 水平布局：-1 按钮 + SpinBox + +1 按钮
        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        
        btn_minus = QPushButton("-1")
        btn_minus.setObjectName("btnMinus")
        btn_minus.setFixedSize(60, 40)
        btn_minus.clicked.connect(lambda: self.batch_spinbox.setValue(self.batch_spinbox.value() - 1))
        h_layout.addWidget(btn_minus)
        
        h_layout.addWidget(self.batch_spinbox, stretch=1)
        
        btn_plus = QPushButton("+1")
        btn_plus.setObjectName("btnPlus")
        btn_plus.setFixedSize(60, 40)
        btn_plus.clicked.connect(lambda: self.batch_spinbox.setValue(self.batch_spinbox.value() + 1))
        h_layout.addWidget(btn_plus)
        
        layout.addLayout(h_layout)
        
        return layout
    
    # 10. 年份变化
    def on_year_changed(self, index: int):
        self.selected_year = self.year_combo.currentData()
        self.update_batch_preview()
        logger.debug(f"年份变化: {self.selected_year}")
    
    # 11. 月份变化
    def on_month_changed(self, index: int):
        self.selected_month = self.month_combo.currentData()
        self.update_batch_preview()
        logger.debug(f"月份变化: {self.selected_month}")
    
    # 12. 炉次变化（更新显示为两位数）
    def on_batch_number_changed(self, value: int):
        self.selected_batch_number = value
        # 更新 SpinBox 显示为两位数
        self.batch_spinbox.lineEdit().setText(f"{value:02d}")
        self.update_batch_preview()
        logger.debug(f"炉次变化: {value:02d}")
    
    # 13. 更新批次编号预览
    def update_batch_preview(self):
        batch_code = self.generate_batch_code()
        self.batch_preview_label.setText(f"批次编号: {batch_code}")
    
    # 14. 生成批次编号
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
    
    # 15. 确认按钮点击
    def on_confirm(self):
        batch_code = self.generate_batch_code()
        logger.info(f"批次配置确认: {batch_code}")
        
        # 发送信号
        self.batch_confirmed.emit(batch_code)
        
        # 关闭对话框
        self.accept()
    
    # 16. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: transparent;
            }}
            
            QFrame#dialogContainer {{
                background: {colors.BG_DEEP};
                border: 2px solid {colors.BORDER_GLOW};
                border-radius: 12px;
            }}
            
            QFrame#titleBar {{
                background: {colors.BG_DARK};
                border-bottom: 1px solid {colors.BORDER_GLOW};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
            
            QLabel#titleLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 20px;
                font-weight: bold;
            }}
            
            QPushButton#btnClose {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }}
            
            QPushButton#btnClose:hover {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
            }}
            
            QPushButton#btnClose:pressed {{
                background: {colors.BG_MEDIUM};
            }}
            
            QFrame#contentFrame {{
                background: transparent;
            }}
            
            QLabel#fieldLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 16px;
            }}
            
            QComboBox {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 16px;
                min-height: 40px;
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
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors.TEXT_PRIMARY};
                margin-right: 10px;
            }}
            
            QComboBox QAbstractItemView {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_GLOW};
                selection-background-color: {colors.GLOW_PRIMARY};
                selection-color: {colors.TEXT_PRIMARY};
            }}
            
            QSpinBox {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 24px;
                font-weight: bold;
                min-height: 40px;
            }}
            
            QSpinBox:hover {{
                border: 1px solid {colors.BORDER_GLOW};
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
            }}
            
            QPushButton#btnMinus, QPushButton#btnPlus {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }}
            
            QPushButton#btnMinus:hover, QPushButton#btnPlus:hover {{
                border: 1px solid {colors.BORDER_GLOW};
                background: {colors.BG_LIGHT};
            }}
            
            QPushButton#btnMinus:pressed, QPushButton#btnPlus:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QLabel#batchPreview {{
                color: {colors.GLOW_PRIMARY};
                font-size: 28px;
                font-weight: bold;
                background: {colors.BG_DARK};
                border: 2px solid {colors.GLOW_PRIMARY};
                border-radius: 8px;
                padding: 12px;
            }}
            
            QPushButton#btnCancel {{
                background: {colors.BG_MEDIUM};
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

