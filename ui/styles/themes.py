"""
主题管理器 - 管理深色/浅色主题切换
"""
from enum import Enum
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .colors import DarkColors, LightColors, CommonColors


class Theme(Enum):
    """主题枚举"""
    DARK = "dark"
    LIGHT = "light"


class ThemeManager(QObject):
    """主题管理器（单例模式）"""
    
    # 主题变更信号
    theme_changed = pyqtSignal(Theme)
    
    _instance: Optional['ThemeManager'] = None
    _initialized: bool = False
    
    # 1. 单例模式实现
    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            # 必须先调用 QObject.__init__
            QObject.__init__(instance)
            instance._initialized = False
            instance._current_theme = Theme.DARK
            cls._instance = instance
        return cls._instance
    
    # 2. 初始化主题管理器（单例模式下只执行一次）
    def __init__(self):
        pass
    
    # 3. 获取单例实例
    @classmethod
    def instance(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    # 4. 获取当前主题
    def get_current_theme(self) -> Theme:
        return self._current_theme
    
    # 5. 设置主题
    def set_theme(self, theme: Theme):
        if self._current_theme != theme:
            self._current_theme = theme
            self.theme_changed.emit(theme)
    
    # 6. 切换主题
    def toggle_theme(self):
        new_theme = Theme.LIGHT if self._current_theme == Theme.DARK else Theme.DARK
        self.set_theme(new_theme)
    
    # 7. 是否为深色模式
    def is_dark_mode(self) -> bool:
        return self._current_theme == Theme.DARK
    
    # 8. 获取当前主题的颜色类
    def get_colors(self):
        return DarkColors if self.is_dark_mode() else LightColors
    
    # 9. 获取指定颜色
    def get_color(self, color_name: str) -> str:
        colors = self.get_colors()
        return getattr(colors, color_name, '#000000')
    
    # ===== 便捷访问方法 =====
    
    # 10. 背景色
    def bg_deep(self) -> str:
        return self.get_color('BG_DEEP')
    
    # 11. 背景色
    def bg_dark(self) -> str:
        return self.get_color('BG_DARK')
    
    # 12. 背景色
    def bg_medium(self) -> str:
        return self.get_color('BG_MEDIUM')
    
    # 13. 背景色
    def bg_light(self) -> str:
        return self.get_color('BG_LIGHT')
    
    # 14. 背景色
    def bg_surface(self) -> str:
        return self.get_color('BG_SURFACE')
    
    # 15. 背景色
    def bg_overlay(self) -> str:
        return self.get_color('BG_OVERLAY')
    
    # 16. 边框色
    def border_dark(self) -> str:
        return self.get_color('BORDER_DARK')
    
    # 17. 边框色
    def border_medium(self) -> str:
        return self.get_color('BORDER_MEDIUM')
    
    # 18. 边框色
    def border_light(self) -> str:
        return self.get_color('BORDER_LIGHT')
    
    # 19. 边框色
    def border_glow(self) -> str:
        return self.get_color('BORDER_GLOW')
    
    # 20. 边框色
    def border_accent(self) -> str:
        return self.get_color('BORDER_ACCENT')
    
    # 21. 网格线
    def grid_line(self) -> str:
        return self.get_color('GRID_LINE')
    
    # 22. 分割线
    def divider(self) -> str:
        return self.get_color('DIVIDER')
    
    # 23. 发光色
    def glow_primary(self) -> str:
        return self.get_color('GLOW_PRIMARY')
    
    # 24. 发光色
    def glow_secondary(self) -> str:
        return self.get_color('GLOW_SECONDARY')
    
    # 25. 发光色
    def glow_cyan(self) -> str:
        return self.get_color('GLOW_CYAN')
    
    # 26. 发光色
    def glow_cyan_light(self) -> str:
        return self.get_color('GLOW_CYAN_LIGHT')
    
    # 27. 发光色
    def glow_green(self) -> str:
        return self.get_color('GLOW_GREEN')
    
    # 28. 发光色
    def glow_orange(self) -> str:
        return self.get_color('GLOW_ORANGE')
    
    # 29. 发光色
    def glow_red(self) -> str:
        return self.get_color('GLOW_RED')
    
    # 30. 发光色
    def glow_blue(self) -> str:
        return self.get_color('GLOW_BLUE')
    
    # 31. 发光色
    def glow_yellow(self) -> str:
        return self.get_color('GLOW_YELLOW')
    
    # 32. 发光色
    def glow_purple(self) -> str:
        return self.get_color('GLOW_PURPLE')
    
    # 33. 文字色
    def text_primary(self) -> str:
        return self.get_color('TEXT_PRIMARY')
    
    # 34. 文字色
    def text_secondary(self) -> str:
        return self.get_color('TEXT_SECONDARY')
    
    # 35. 文字色
    def text_tertiary(self) -> str:
        return self.get_color('TEXT_TERTIARY')
    
    # 36. 文字色
    def text_muted(self) -> str:
        return self.get_color('TEXT_MUTED')
    
    # 37. 文字色
    def text_disabled(self) -> str:
        return self.get_color('TEXT_DISABLED')
    
    # 38. 文字色
    def text_inverse(self) -> str:
        return self.get_color('TEXT_INVERSE')
    
    # 39. 文字色
    def text_link(self) -> str:
        return self.get_color('TEXT_LINK')
    
    # 40. 文字色
    def text_accent(self) -> str:
        return self.get_color('TEXT_ACCENT')
    
    # 41. 状态色
    def status_normal(self) -> str:
        return self.get_color('STATUS_NORMAL')
    
    # 42. 状态色
    def status_success(self) -> str:
        return self.get_color('STATUS_SUCCESS')
    
    # 43. 状态色
    def status_warning(self) -> str:
        return self.get_color('STATUS_WARNING')
    
    # 44. 状态色
    def status_alarm(self) -> str:
        return self.get_color('STATUS_ALARM')
    
    # 45. 状态色
    def status_error(self) -> str:
        return self.get_color('STATUS_ERROR')
    
    # 46. 状态色
    def status_info(self) -> str:
        return self.get_color('STATUS_INFO')
    
    # 47. 状态色
    def status_offline(self) -> str:
        return self.get_color('STATUS_OFFLINE')
    
    # 48. 状态色
    def status_disabled(self) -> str:
        return self.get_color('STATUS_DISABLED')
    
    # 49. 按钮色
    def button_primary_bg(self) -> str:
        return self.get_color('BUTTON_PRIMARY_BG')
    
    # 50. 按钮色
    def button_primary_text(self) -> str:
        return self.get_color('BUTTON_PRIMARY_TEXT')
    
    # 51. 按钮色
    def button_primary_hover(self) -> str:
        return self.get_color('BUTTON_PRIMARY_HOVER')
    
    # 52. 输入框色
    def input_bg(self) -> str:
        return self.get_color('INPUT_BG')
    
    # 53. 输入框色
    def input_border(self) -> str:
        return self.get_color('INPUT_BORDER')
    
    # 54. 输入框色
    def input_border_focus(self) -> str:
        return self.get_color('INPUT_BORDER_FOCUS')
    
    # 55. 卡片色
    def card_bg(self) -> str:
        return self.get_color('CARD_BG')
    
    # 56. 卡片色
    def card_border(self) -> str:
        return self.get_color('CARD_BORDER')
    
    # 57. 卡片色
    def card_hover_border(self) -> str:
        return self.get_color('CARD_HOVER_BORDER')
    
    # 58. 表格色
    def table_bg(self) -> str:
        return self.get_color('TABLE_BG')
    
    # 59. 表格色
    def table_header_bg(self) -> str:
        return self.get_color('TABLE_HEADER_BG')
    
    # 60. 表格色
    def table_header_text(self) -> str:
        return self.get_color('TABLE_HEADER_TEXT')
    
    # 61. 图表色
    def chart_line_1(self) -> str:
        return self.get_color('CHART_LINE_1')
    
    # 62. 图表色
    def chart_line_2(self) -> str:
        return self.get_color('CHART_LINE_2')
    
    # 63. 图表色
    def chart_line_3(self) -> str:
        return self.get_color('CHART_LINE_3')
    
    # 64. 图表色
    def chart_line_4(self) -> str:
        return self.get_color('CHART_LINE_4')
    
    # 65. 图表色
    def chart_line_5(self) -> str:
        return self.get_color('CHART_LINE_5')
    
    # 66. 图表色
    def chart_line_6(self) -> str:
        return self.get_color('CHART_LINE_6')
    
    # 67. 图表色
    def chart_grid(self) -> str:
        return self.get_color('CHART_GRID')
    
    # 68. 图表色
    def chart_axis(self) -> str:
        return self.get_color('CHART_AXIS')
    
    # 69. 图表色
    def chart_bg(self) -> str:
        return self.get_color('CHART_BG')
    
    # 70. 下拉框色
    def dropdown_bg(self) -> str:
        return self.get_color('DROPDOWN_BG')
    
    # 71. 下拉框色
    def dropdown_border(self) -> str:
        return self.get_color('DROPDOWN_BORDER')
    
    # 72. 标签页色
    def tab_bg(self) -> str:
        return self.get_color('TAB_BG')
    
    # 73. 标签页色
    def tab_active_bg(self) -> str:
        return self.get_color('TAB_ACTIVE_BG')
    
    # 74. 标签页色
    def tab_active_border(self) -> str:
        return self.get_color('TAB_ACTIVE_BORDER')
    
    # 75. 阴影与发光
    def shadow_light(self) -> str:
        return self.get_color('SHADOW_LIGHT')
    
    # 76. 阴影与发光
    def shadow_medium(self) -> str:
        return self.get_color('SHADOW_MEDIUM')
    
    # 77. 阴影与发光
    def shadow_heavy(self) -> str:
        return self.get_color('SHADOW_HEAVY')
    
    # 78. 阴影与发光
    def glow_effect(self) -> str:
        return self.get_color('GLOW_EFFECT')
    
    # 79. 阴影与发光
    def overlay_light(self) -> str:
        return self.get_color('OVERLAY_LIGHT')
    
    # 80. 阴影与发光
    def overlay_medium(self) -> str:
        return self.get_color('OVERLAY_MEDIUM')
    
    # 81. 阴影与发光
    def overlay_heavy(self) -> str:
        return self.get_color('OVERLAY_HEAVY')
    
    # 82. 通用色
    @staticmethod
    def transparent() -> str:
        return CommonColors.TRANSPARENT
    
    # 83. 通用色
    @staticmethod
    def black() -> str:
        return CommonColors.BLACK
    
    # 84. 通用色
    @staticmethod
    def white() -> str:
        return CommonColors.WHITE


# 85. 全局单例访问函数
def get_theme_manager() -> ThemeManager:
    return ThemeManager.instance()

