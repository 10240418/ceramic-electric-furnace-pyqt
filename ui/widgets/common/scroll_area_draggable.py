"""
支持鼠标拖拽滚动的滚动区域
"""
from PyQt6.QtWidgets import QScrollArea, QScrollBar, QWidget, QAbstractSpinBox, QPushButton
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QMouseEvent


class ScrollAreaDraggable(QScrollArea):
    """支持鼠标拖拽滚动的滚动区域"""
    
    # 1. 初始化
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 拖拽状态
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._scroll_start_value = 0
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
        
        # 设置滚动条策略
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    
    # 2. 判断是否为可交互控件
    def _is_interactive_widget(self, widget: QWidget) -> bool:
        if widget is None:
            return False
        
        # 检查是否为按钮、输入框等可交互控件
        if isinstance(widget, (QPushButton, QAbstractSpinBox, QScrollBar)):
            return True
        
        # 检查父级是否为可交互控件
        parent = widget.parent()
        while parent and parent != self:
            if isinstance(parent, (QPushButton, QAbstractSpinBox)):
                return True
            parent = parent.parent()
        
        return False
    
    # 3. 鼠标按下事件
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取鼠标位置的控件
            widget_at_pos = self.childAt(event.position().toPoint())
            
            # 如果点击的是可交互控件，不启动拖拽
            if self._is_interactive_widget(widget_at_pos):
                super().mousePressEvent(event)
                return
            
            # 开始拖拽
            self._dragging = True
            self._drag_start_pos = event.position().toPoint()
            self._scroll_start_value = self.verticalScrollBar().value()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    # 4. 鼠标移动事件
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            # 计算移动距离
            delta = event.position().toPoint() - self._drag_start_pos
            
            # 更新滚动条位置
            new_value = self._scroll_start_value - delta.y()
            self.verticalScrollBar().setValue(new_value)
        
        super().mouseMoveEvent(event)
    
    # 5. 鼠标释放事件
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    # 6. 离开事件
    def leaveEvent(self, event: QEvent):
        self._dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
