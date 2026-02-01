"""
批次配置对话框 - 用于开始冶炼前配置批次编号
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QFrame, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
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
        
        self.setWindowTitle("批次配置")
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
        self.selected_batch_number = 1
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 顶部：标题
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # 图标
        icon_label = QLabel("📝")
        icon_label.setStyleSheet("font-size: 28px;")
        header_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel("批次配置")
        title_label.setObjectName("titleLabel")
        title_label.setFixedHeight(40)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # 内容区域
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # 年份选择卡片
        self.year_combo = self.create_year_selector()
        year_card = self.create_field_card("年份", self.year_combo)
        content_layout.addWidget(year_card)
        
        # 月份选择卡片
        self.month_combo = self.create_month_selector()
        month_card = self.create_field_card("月份", self.month_combo)
        content_layout.addWidget(month_card)
        
        # 炉次选择卡片（使用 SpinBox + 按钮）
        self.batch_spinbox = self.create_batch_selector()
        batch_card = self.create_batch_field_card()
        content_layout.addWidget(batch_card)
        
        # 批次编号预览卡片
        preview_card = self.create_preview_card()
        content_layout.addWidget(preview_card)
        
        main_layout.addLayout(content_layout)
        
        main_layout.addStretch()
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.setFixedSize(120, 42)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_confirm = QPushButton("确认开始")
        btn_confirm.setObjectName("btnConfirm")
        btn_confirm.setFixedSize(120, 42)
        btn_confirm.clicked.connect(self.on_confirm)
        button_layout.addWidget(btn_confirm)
        
        main_layout.addLayout(button_layout)
    
    # 3. 创建字段卡片
    def create_field_card(self, label: str, widget) -> QFrame:
        """创建字段卡片"""
        card = QFrame()
        card.setObjectName("fieldCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setObjectName("fieldLabel")
        layout.addWidget(label_widget)
        
        # 控件
        layout.addWidget(widget)
        
        return card
    
    # 4. 创建年份选择器
    def create_year_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("yearCombo")
        combo.setFixedHeight(44)
        
        # 添加年份选项（当前年份 ± 5 年）
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 6):
            combo.addItem(f"{year}年", year)
        
        # 设置当前年份
        combo.setCurrentText(f"{current_year}年")
        combo.currentIndexChanged.connect(self.on_year_changed)
        
        return combo
    
    # 5. 创建月份选择器
    def create_month_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("monthCombo")
        combo.setFixedHeight(44)
        
        # 添加月份选项
        for month in range(1, 13):
            combo.addItem(f"{month}月", month)
        
        # 设置当前月份
        current_month = datetime.now().month
        combo.setCurrentIndex(current_month - 1)
        combo.currentIndexChanged.connect(self.on_month_changed)
        
        return combo
    
    # 6. 创建炉次选择器（显示两位数）
    def create_batch_selector(self) -> QSpinBox:
        spinbox = QSpinBox()
        spinbox.setObjectName("batchSpinBox")
        spinbox.setFixedHeight(44)
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
    
    # 7. 创建炉次字段卡片（带 +1/-1 按钮）
    def create_batch_field_card(self) -> QFrame:
        """创建炉次字段卡片"""
        card = QFrame()
        card.setObjectName("fieldCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)
        
        # 标签
        label = QLabel("当月第几炉")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        
        # 水平布局：-1 按钮 + SpinBox + +1 按钮
        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        
        btn_minus = QPushButton("-1")
        btn_minus.setObjectName("btnMinus")
        btn_minus.setFixedSize(70, 44)
        btn_minus.clicked.connect(lambda: self.batch_spinbox.setValue(self.batch_spinbox.value() - 1))
        h_layout.addWidget(btn_minus)
        
        h_layout.addWidget(self.batch_spinbox, stretch=1)
        
        btn_plus = QPushButton("+1")
        btn_plus.setObjectName("btnPlus")
        btn_plus.setFixedSize(70, 44)
        btn_plus.clicked.connect(lambda: self.batch_spinbox.setValue(self.batch_spinbox.value() + 1))
        h_layout.addWidget(btn_plus)
        
        layout.addLayout(h_layout)
        
        return card
    
    # 8. 创建批次编号预览卡片
    def create_preview_card(self) -> QFrame:
        """创建批次编号预览卡片"""
        card = QFrame()
        card.setObjectName("previewCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # 标签
        label = QLabel("批次编号预览")
        label.setObjectName("previewLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # 批次编号
        self.batch_preview_label = QLabel()
        self.batch_preview_label.setObjectName("batchPreview")
        self.batch_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batch_preview_label.setFixedHeight(60)
        layout.addWidget(self.batch_preview_label)
        self.update_batch_preview()
        
        return card
    
    # 9. 年份变化
    def on_year_changed(self, index: int):
        self.selected_year = self.year_combo.currentData()
        self.update_batch_preview()
        logger.debug(f"年份变化: {self.selected_year}")
    
    # 10. 月份变化
    def on_month_changed(self, index: int):
        self.selected_month = self.month_combo.currentData()
        self.update_batch_preview()
        logger.debug(f"月份变化: {self.selected_month}")
    
    # 11. 炉次变化（更新显示为两位数）
    def on_batch_number_changed(self, value: int):
        self.selected_batch_number = value
        # 更新 SpinBox 显示为两位数
        self.batch_spinbox.lineEdit().setText(f"{value:02d}")
        self.update_batch_preview()
        logger.debug(f"炉次变化: {value:02d}")
    
    # 12. 更新批次编号预览
    def update_batch_preview(self):
        batch_code = self.generate_batch_code()
        self.batch_preview_label.setText(batch_code)
    
    # 13. 生成批次编号
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
    
    # 14. 调整窗口大小（50%宽 × 60%高）
    def showEvent(self, event):
        """显示事件，调整窗口大小"""
        super().showEvent(event)
        
        # 获取父窗口大小
        if self.parent():
            parent_size = self.parent().size()
            width = int(parent_size.width() * 0.5)
            height = int(parent_size.height() * 0.6)
            self.resize(width, height)
            
            # 居中显示
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - width) // 2
            y = parent_rect.y() + (parent_rect.height() - height) // 2
            self.move(x, y)
    
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
                background: {colors.BG_DARK};
                border: 2px solid {colors.BORDER_GLOW};
                border-radius: 8px;
            }}
            
            QLabel#titleLabel {{
                background: transparent;
                color: {colors.TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                border: none;
            }}
            
            QFrame#fieldCard {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QFrame#previewCard {{
                background: {colors.BG_LIGHT};
                border: 2px solid {colors.GLOW_PRIMARY};
                border-radius: 8px;
            }}
            
            QLabel#fieldLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 15px;
                border: none;
                background: transparent;
            }}
            
            QLabel#previewLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
            
            QLabel#batchPreview {{
                color: {colors.GLOW_PRIMARY};
                font-size: 32px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            
            QComboBox {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 18px;
                min-height: 44px;
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
                font-size: 28px;
                font-weight: bold;
                font-family: "Roboto Mono";
                min-height: 44px;
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
            
            QPushButton#btnCancel {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_SECONDARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
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

