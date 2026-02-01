"""
闪烁文本标签组件
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, pyqtProperty
from PyQt6.QtGui import QColor
from ui.styles.themes import ThemeManager


class LabelBlinking(QLabel):
    """闪烁文本标签组件（开关式）"""
    
    # 1. 初始化组件
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = ThemeManager.instance()
        self._is_blinking = False
        self._blink_visible = True
        self._blink_color = None
        self._normal_color = None
        
        # 闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_visibility)
        self.blink_timer.setInterval(500)  # 500ms 闪烁一次
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 设置是否闪烁
    def set_blinking(self, enabled: bool):
        self._is_blinking = enabled
        if enabled:
            self.blink_timer.start()
        else:
            self.blink_timer.stop()
            self._blink_visible = True
            self.update_style()
    
    # 3. 设置闪烁颜色
    def set_blink_color(self, color: str):
        self._blink_color = color
        self.update_style()
    
    # 4. 设置正常颜色
    def set_normal_color(self, color: str):
        self._normal_color = color
        self.update_style()
    
    # 5. 切换可见性
    def toggle_visibility(self):
        self._blink_visible = not self._blink_visible
        self.update_style()
    
    # 6. 更新样式
    def update_style(self):
        if not self._is_blinking:
            color = self._normal_color or self.theme_manager.text_primary()
            self.setStyleSheet(f"color: {color};")
            return
        
        if self._blink_visible:
            color = self._blink_color or self.theme_manager.glow_red()
            self.setStyleSheet(f"color: {color};")
        else:
            self.setStyleSheet(f"color: transparent;")
    
    # 7. 主题变化时更新
    def on_theme_changed(self):
        self.update_style()
    
    # 8. 清理资源
    def cleanup(self):
        """手动清理资源"""
        if hasattr(self, 'blink_timer') and self.blink_timer is not None:
            try:
                self.blink_timer.stop()
            except RuntimeError:
                pass  # Qt 对象已被删除
    
    def closeEvent(self, event):
        """窗口关闭时清理"""
        self.cleanup()
        super().closeEvent(event)


class LabelBlinkingFade(QLabel):
    """闪烁文本标签组件（渐变式）"""
    
    # 1. 初始化组件
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.theme_manager = ThemeManager.instance()
        self._is_blinking = False
        self._opacity = 1.0
        self._fade_in = False
        self._blink_color = None
        self._normal_color = None
        
        # 渐变定时器
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.update_opacity)
        self.fade_timer.setInterval(50)  # 50ms 更新一次
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 设置是否闪烁
    def set_blinking(self, enabled: bool):
        self._is_blinking = enabled
        if enabled:
            self.fade_timer.start()
        else:
            self.fade_timer.stop()
            self._opacity = 1.0
            self.update_style()
    
    # 3. 设置闪烁颜色
    def set_blink_color(self, color: str):
        self._blink_color = color
        self.update_style()
    
    # 4. 设置正常颜色
    def set_normal_color(self, color: str):
        self._normal_color = color
        self.update_style()
    
    # 5. 更新透明度
    def update_opacity(self):
        if self._fade_in:
            self._opacity += 0.1
            if self._opacity >= 1.0:
                self._opacity = 1.0
                self._fade_in = False
        else:
            self._opacity -= 0.1
            if self._opacity <= 0.3:
                self._opacity = 0.3
                self._fade_in = True
        
        self.update_style()
    
    # 6. 更新样式
    def update_style(self):
        if not self._is_blinking:
            # 正常状态：无边框
            color = self._normal_color or self.theme_manager.text_primary()
            self.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    border: none;
                    background: transparent;
                }}
            """)
            return
        
        # 报警状态：有边框并闪烁
        color = self._blink_color or self.theme_manager.glow_red()
        qcolor = QColor(color)
        qcolor.setAlphaF(self._opacity)
        rgba = f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {self._opacity})"
        
        # 边框也跟随透明度闪烁
        border_rgba = f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {self._opacity})"
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {rgba};
                border: 1px solid {border_rgba};
                border-radius: 4px;
                background: transparent;
                padding: 2px 4px;
            }}
        """)
    
    # 7. 主题变化时更新
    def on_theme_changed(self):
        self.update_style()
    
    # 8. 清理资源
    def cleanup(self):
        """手动清理资源"""
        if hasattr(self, 'fade_timer') and self.fade_timer is not None:
            try:
                self.fade_timer.stop()
            except RuntimeError:
                pass  # Qt 对象已被删除
    
    def closeEvent(self, event):
        """窗口关闭时清理"""
        self.cleanup()
        super().closeEvent(event)

