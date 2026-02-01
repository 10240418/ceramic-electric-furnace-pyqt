"""
设置料仓上限弹窗 - 二级弹窗，用于设置料仓上限
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator
from ui.styles.themes import ThemeManager
from loguru import logger


class DialogSetLimit(QDialog):
    """设置料仓上限弹窗"""
    
    # 信号：料仓上限设置完成
    limit_set = pyqtSignal(float)
    
    # 1. 初始化弹窗
    def __init__(self, current_limit: float, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.current_limit = current_limit
        
        self.setWindowTitle("设置料仓上限")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        # 设置窗口标志，去除问号按钮
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self.init_ui()
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("设置料仓上限")
        title_label.setObjectName("dialogTitle")
        main_layout.addWidget(title_label)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        
        input_label = QLabel("料仓上限:")
        input_label.setObjectName("inputLabel")
        input_layout.addWidget(input_label)
        
        self.limit_input = QLineEdit()
        self.limit_input.setObjectName("limitInput")
        self.limit_input.setPlaceholderText("请输入料仓上限")
        self.limit_input.setText(str(int(self.current_limit)))
        
        # 只允许输入数字
        validator = QDoubleValidator(0.0, 99999.0, 2)
        self.limit_input.setValidator(validator)
        
        input_layout.addWidget(self.limit_input, 1)
        
        unit_label = QLabel("kg")
        unit_label.setObjectName("unitLabel")
        input_layout.addWidget(unit_label)
        
        main_layout.addLayout(input_layout)
        
        main_layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_btn)
        
        main_layout.addLayout(button_layout)
    
    # 3. 确认设置
    def on_confirm(self):
        """确认设置料仓上限"""
        try:
            limit_text = self.limit_input.text().strip()
            if not limit_text:
                QMessageBox.warning(self, "警告", "请输入料仓上限")
                return
            
            limit_value = float(limit_text)
            
            if limit_value <= 0:
                QMessageBox.warning(self, "警告", "料仓上限必须大于0")
                return
            
            if limit_value > 10000:
                QMessageBox.warning(self, "警告", "料仓上限不能超过10000kg")
                return
            
            # 调用后端服务写入 PLC
            from backend.services.hopper.input_service import set_hopper_upper_limit
            
            logger.info(f"准备写入料仓上限值: {limit_value} kg")
            
            result = set_hopper_upper_limit(limit_value)
            
            if result['success']:
                # 写入成功，发射信号
                self.limit_set.emit(limit_value)
                
                logger.info(f"料仓上限设置成功: {limit_value} kg")
                
                QMessageBox.information(self, "成功", result['message'])
                
                self.accept()
            else:
                # 写入失败，显示错误信息
                logger.error(f"料仓上限设置失败: {result['message']}")
                
                QMessageBox.critical(self, "失败", result['message'])
        
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字")
        except Exception as e:
            logger.error(f"设置料仓上限异常: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"设置失败: {str(e)}")
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_DARK};
                border: 2px solid {colors.BORDER_GLOW};
                border-radius: 8px;
            }}
            
            QLabel#dialogTitle {{
                color: {colors.GLOW_PRIMARY};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QLabel#inputLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
            
            QLabel#unitLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
            
            QLineEdit#limitInput {{
                background: {colors.INPUT_BG};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.INPUT_BORDER};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: "Roboto Mono";
            }}
            QLineEdit#limitInput:focus {{
                border: 1px solid {colors.INPUT_BORDER_FOCUS};
            }}
            
            QPushButton#cancelBtn {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#cancelBtn:hover {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_MEDIUM};
            }}
            QPushButton#cancelBtn:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QPushButton#confirmBtn {{
                background: {colors.BUTTON_PRIMARY_BG};
                color: {colors.BUTTON_PRIMARY_TEXT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#confirmBtn:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton#confirmBtn:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 5. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

