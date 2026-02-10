"""
颜色常量定义 - 深色/浅色/多色主题配色方案
"""


class DarkColors:
    """深色主题颜色（科技风格）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0d1117'      # 最深背景
    BG_DARK = '#161b22'      # 深色背景
    BG_MEDIUM = '#21262d'    # 中等背景
    BG_LIGHT = '#30363d'     # 浅色背景
    BG_CARD = '#1c2128'      # 卡片背景
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#30363d4D'  # 按钮正常背景（30%透明）
    BTN_BG_HOVER = '#30363d80'   # 按钮悬停背景（50%透明）
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#30363d'   # 深色边框
    BORDER_MEDIUM = '#444c56' # 中等边框
    BORDER_LIGHT = '#6e7681'  # 浅色边框
    BORDER_GLOW = '#00d4ff'   # 发光边框（青色）
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#00d4ff'      # 主要发光（青色）
    GLOW_CYAN = '#00d4ff'         # 青色发光
    GLOW_GREEN = '#00ff88'        # 绿色发光
    GLOW_ORANGE = '#ff9500'       # 橙色发光
    GLOW_RED = '#ff3b30'          # 红色发光
    GLOW_BLUE = '#0088ff'         # 蓝色发光
    GLOW_YELLOW = '#ffcc00'       # 黄色发光
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#e6edf3'    # 主要文字
    TEXT_SECONDARY = '#8b949e'  # 次要文字
    TEXT_MUTED = '#484f58'      # 弱化文字
    TEXT_DISABLED = '#3d444d'   # 禁用文字
    TEXT_ACCENT = '#38bdf8'     # 强调文字（天蓝）
    TEXT_ON_PRIMARY = '#0d1117' # 主色背景上的文字
    TEXT_SELECTED = '#00d4ff'   # 选中状态文字
    TEXT_BUTTERFLY_LEFT = '#e6edf3'  # 蝶阀左侧文字
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#00ff88'   # 成功状态（绿色）
    STATUS_WARNING = '#ffcc00'   # 警告状态（黄色）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）
    STATUS_ERROR = '#ff0000'     # 错误状态
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#F9A620'    # 警告色（橙色）
    COLOR_SUCCESS = '#11C900'    # 成功色（绿色）
    COLOR_ERROR = '#D20000'      # 错误色（红色）
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#00d4ff'       # 主要按钮背景
    BUTTON_PRIMARY_TEXT = '#0d1117'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#00f0ff'    # 主要按钮悬停
    BUTTON_SECOND_TEXT = '#e6edf3'      # 次要按钮文字
    BUTTON_SECONDARY_BG = '#21262d'     # 次要按钮背景
    BUTTON_SECONDARY_HOVER = '#30363d'  # 次要按钮悬停
    BUTTON_DANGER_BG = '#da3633'        # 危险按钮背景
    BUTTON_DANGER_TEXT = '#ffffff'      # 危险按钮文字
    BUTTON_DANGER_HOVER = '#ff5544'     # 危险按钮悬停
    BUTTON_DISABLED_BG = '#21262d'      # 禁用按钮背景
    BUTTON_DISABLED_TEXT = '#484f58'    # 禁用按钮文字
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#30363d'           # 输入框背景
    INPUT_BORDER = '#444c56'       # 输入框边框
    INPUT_BORDER_FOCUS = '#00d4ff' # 输入框聚焦边框
    
    # ===== 卡片颜色 =====
    CARD_BG = '#21262d'            # 卡片背景
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#00d4ff'    # 图表线条1（亮青色）
    CHART_LINE_2 = '#ff3b8e'    # 图表线条2（粉红色）
    CHART_LINE_3 = '#ffcc00'    # 图表线条3（亮黄色）
    CHART_LINE_4 = '#0088ff'    # 图表线条4（蓝色）
    CHART_LINE_5 = '#bf5af2'    # 图表线条5（紫色）
    CHART_LINE_6 = '#00ff88'    # 图表线条6（绿色）
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#00d4ff'        # 1#电极颜色（青色）
    ELECTRODE_2 = '#ffb84d'        # 2#电极颜色（橙黄）
    ELECTRODE_3 = '#ff3b30'        # 3#电极颜色（红色）
    ELECTRODE_CARD_BG_1 = '#0d2a1a'    # 1#电极卡片背景（深绿色调）
    ELECTRODE_CARD_BG_2 = '#2a2510'    # 2#电极卡片背景（深琥珀色调）
    ELECTRODE_CARD_BG_3 = '#2a1010'    # 3#电极卡片背景（深红色调）
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'      # 浅色覆盖层
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'     # 中等覆盖层


class LightColors:
    """浅色主题颜色（绿色系，基于 #E9EEA8）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#e9eea8'      # 最深背景（主色调）
    BG_DARK = '#f2fedc'      # 深色背景（浅绿）
    BG_MEDIUM = '#fafbe7'    # 中等背景（米白）
    BG_LIGHT = '#ffffff'     # 浅色背景（纯白）
    BG_CARD = '#F2FEDC'      # 卡片背景（浅绿色）
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'    # 按钮正常背景（白色）
    BTN_BG_HOVER = '#fafbe7'     # 按钮悬停背景（米白）
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#d5a339'   # 深色边框（金棕色）
    BORDER_MEDIUM = '#8e7344' # 中等边框（棕色）
    BORDER_LIGHT = '#acac9a'  # 浅色边框（灰绿）
    BORDER_GLOW = '#007663'   # 发光边框（深绿色）
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#007663'      # 主要发光（深绿）
    GLOW_CYAN = '#007663'         # 青色发光（深绿）
    GLOW_GREEN = '#008b67'        # 绿色发光
    GLOW_ORANGE = '#d5a339'       # 橙色发光（金棕）
    GLOW_RED = '#b95d3b'          # 红色发光（棕红）
    GLOW_BLUE = '#00ced4'         # 蓝色发光（青蓝）
    GLOW_YELLOW = '#859a00'       # 黄色发光（橄榄绿）
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#1b3d2f'    # 主要文字（深绿）
    TEXT_SECONDARY = '#474838'  # 次要文字（深灰绿）
    TEXT_MUTED = '#8b949e'      # 弱化文字（灰色）
    TEXT_DISABLED = '#acac9a'   # 禁用文字（浅灰）
    TEXT_ACCENT = '#008b67'     # 强调文字（中绿）
    TEXT_ON_PRIMARY = '#ffffff' # 主色背景上的文字
    TEXT_SELECTED = '#007663'   # 选中状态文字（深绿）
    TEXT_BUTTERFLY_LEFT = '#1b3d2f'  # 蝶阀左侧文字
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#008b67'   # 成功状态（绿色）
    STATUS_WARNING = '#d5a339'   # 警告状态（金棕）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）
    STATUS_ERROR = '#ff0000'     # 错误状态（鲜红色）
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#F9A620'    # 警告色（橙色）
    COLOR_SUCCESS = '#11C900'    # 成功色（绿色）
    COLOR_ERROR = '#D20000'      # 错误色（红色）
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#007663'       # 主要按钮背景（深绿）
    BUTTON_PRIMARY_TEXT = '#ffffff'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#008b67'    # 主要按钮悬停（中绿）
    BUTTON_SECOND_TEXT = '#1b3d2f'      # 次要按钮文字（深绿）
    BUTTON_SECONDARY_BG = '#e9eea8'     # 次要按钮背景（浅绿）
    BUTTON_SECONDARY_HOVER = '#008b67'  # 次要按钮悬停（中绿）
    BUTTON_DANGER_BG = '#c53030'        # 危险按钮背景
    BUTTON_DANGER_TEXT = '#ffffff'      # 危险按钮文字
    BUTTON_DANGER_HOVER = '#c76d4b'     # 危险按钮悬停
    BUTTON_DISABLED_BG = '#e0e0d0'      # 禁用按钮背景
    BUTTON_DISABLED_TEXT = '#acac9a'    # 禁用按钮文字
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'           # 输入框背景
    INPUT_BORDER = '#acac9a'       # 输入框边框
    INPUT_BORDER_FOCUS = '#007663' # 输入框聚焦边框（深绿）
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'            # 卡片背景
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#007663'    # 图表线条1（深绿）
    CHART_LINE_2 = '#008b67'    # 图表线条2（中绿）
    CHART_LINE_3 = '#d5a339'    # 图表线条3（金棕）
    CHART_LINE_4 = '#00ced4'    # 图表线条4（青蓝）
    CHART_LINE_5 = '#95b0b1'    # 图表线条5（灰蓝）
    CHART_LINE_6 = '#859a00'    # 图表线条6（橄榄绿）
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#007663'        # 1#电极颜色（深绿）
    ELECTRODE_2 = '#d4a017'        # 2#电极颜色（金黄）
    ELECTRODE_3 = '#b95d3b'        # 3#电极颜色（棕红）
    ELECTRODE_CARD_BG_1 = '#E5FFDF'    # 1#电极卡片背景（浅绿）
    ELECTRODE_CARD_BG_2 = '#FCFFE0'    # 2#电极卡片背景（浅黄）
    ELECTRODE_CARD_BG_3 = '#FDE6E0'    # 3#电极卡片背景（浅粉）
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'# 浅色覆盖层
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'# 中等覆盖层


class LightChange:
    """强浅色主题颜色（绿色系，基于 #E9EEA8）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#FFFFFF'      # 最深背景（主色调）
    BG_DARK = '#F2FEDC'      # 深色背景（浅绿）
    BG_MEDIUM = '#fafbe7'    # 中等背景（米白）
    BG_LIGHT = '#ffffff'     # 浅色背景（纯白）
    BG_CARD = '#F2FEDC'      # 卡片背景
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'    # 按钮正常背景（白色）
    BTN_BG_HOVER = '#fafbe7'     # 按钮悬停背景（米白）
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#000000'   # 深色边框
    BORDER_MEDIUM = '#8e7344' # 中等边框（棕色）
    BORDER_LIGHT = '#acac9a'  # 浅色边框（灰绿）
    BORDER_GLOW = '#00d4ff'   # 发光边框（青色）
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#007663'      # 主要发光（深绿）
    GLOW_CYAN = '#007663'         # 青色发光（深绿）
    GLOW_GREEN = '#008b67'        # 绿色发光
    GLOW_ORANGE = '#d5a339'       # 橙色发光（金棕）
    GLOW_RED = '#b95d3b'          # 红色发光（棕红）
    GLOW_BLUE = '#00ced4'         # 蓝色发光（青蓝）
    GLOW_YELLOW = '#859a00'       # 黄色发光（橄榄绿）
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#00014D'    # 主要文字（深蓝）
    TEXT_SECONDARY = '#474838'  # 次要文字（深灰绿）
    TEXT_MUTED = '#8b949e'      # 弱化文字（灰色）
    TEXT_DISABLED = '#acac9a'   # 禁用文字（浅灰）
    TEXT_ACCENT = '#1610F6'     # 强调文字（蓝紫）
    TEXT_ON_PRIMARY = '#ffffff' # 主色背景上的文字
    TEXT_SELECTED = '#007663'   # 选中状态文字（深绿）
    TEXT_BUTTERFLY_LEFT = '#1b3d2f'  # 蝶阀左侧文字
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#008b67'   # 成功状态（绿色）
    STATUS_WARNING = '#d5a339'   # 警告状态（金棕）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）
    STATUS_ERROR = '#ff0000'     # 错误状态（鲜红色）
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = "#E8C60A9D"    # 警告色（橙黄半透明）
    COLOR_SUCCESS = '#11C900'    # 成功色（绿色）
    COLOR_ERROR = '#D20000'      # 错误色（红色）
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#00014D'       # 主要按钮背景（蓝色）
    BUTTON_PRIMARY_TEXT = '#ffffff'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#008b67'    # 主要按钮悬停（中绿）
    BUTTON_SECOND_TEXT = '#00014D'      # 次要按钮文字（蓝色）
    BUTTON_SECONDARY_BG = "#e9eea8"     # 次要按钮背景（浅绿）
    BUTTON_SECONDARY_HOVER = '#008b67'  # 次要按钮悬停（中绿）
    BUTTON_DANGER_BG = '#c53030'        # 危险按钮背景
    BUTTON_DANGER_TEXT = '#ffffff'      # 危险按钮文字
    BUTTON_DANGER_HOVER = "#ed3960"     # 危险按钮悬停
    BUTTON_DISABLED_BG = '#e0e0d0'      # 禁用按钮背景
    BUTTON_DISABLED_TEXT = '#acac9a'    # 禁用按钮文字
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'           # 输入框背景
    INPUT_BORDER = '#acac9a'       # 输入框边框
    INPUT_BORDER_FOCUS = '#007663' # 输入框聚焦边框（深绿）
    
    # ===== 卡片颜色 =====
    CARD_BG = '#F2FEDC'            # 卡片背景
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#007663'    # 图表线条1（深绿）
    CHART_LINE_2 = '#008b67'    # 图表线条2（中绿）
    CHART_LINE_3 = '#d5a339'    # 图表线条3（金棕）
    CHART_LINE_4 = '#00ced4'    # 图表线条4（青蓝）
    CHART_LINE_5 = '#95b0b1'    # 图表线条5（灰蓝）
    CHART_LINE_6 = '#859a00'    # 图表线条6（橄榄绿）
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#15FF00'        # 1#电极颜色（绿色）
    ELECTRODE_2 = "#F8A500"        # 2#电极颜色（黄色）
    ELECTRODE_3 = '#FF0000'        # 3#电极颜色（红色）
    ELECTRODE_CARD_BG_1 = '#E5FFDF'    # 1#电极卡片背景（浅绿）
    ELECTRODE_CARD_BG_2 = '#FCFFE0'    # 2#电极卡片背景（浅黄）
    ELECTRODE_CARD_BG_3 = '#FDE6E0'    # 3#电极卡片背景（浅粉）
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'# 浅色覆盖层
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'# 中等覆盖层

class OceanBlue:
    """深海蓝主题（深色，深邃海洋 + 电光蓝）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0a1628'
    BG_DARK = '#0f1f3d'
    BG_MEDIUM = '#162a4a'
    BG_LIGHT = '#1e3a5f'
    BG_CARD = '#122240'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#1e3a5f4D'
    BTN_BG_HOVER = '#1e3a5f80'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#1e3a5f'
    BORDER_MEDIUM = '#2b5278'
    BORDER_LIGHT = '#3a6b8f'
    BORDER_GLOW = '#00b4d8'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#00b4d8'
    GLOW_CYAN = '#00b4d8'
    GLOW_GREEN = '#00e5a0'
    GLOW_ORANGE = '#f4a261'
    GLOW_RED = '#e76f51'
    GLOW_BLUE = '#0077b6'
    GLOW_YELLOW = '#e9c46a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#caf0f8'
    TEXT_SECONDARY = '#90cad7'
    TEXT_MUTED = '#4a7a8a'
    TEXT_DISABLED = '#2b5278'
    TEXT_ACCENT = '#48cae4'
    TEXT_ON_PRIMARY = '#0a1628'
    TEXT_SELECTED = '#00b4d8'
    TEXT_BUTTERFLY_LEFT = '#caf0f8'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#00e5a0'
    STATUS_WARNING = '#e9c46a'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#f4a261'
    COLOR_SUCCESS = '#00e5a0'
    COLOR_ERROR = '#e76f51'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#00b4d8'
    BUTTON_PRIMARY_TEXT = '#0a1628'
    BUTTON_PRIMARY_HOVER = '#48cae4'
    BUTTON_SECOND_TEXT = '#caf0f8'
    BUTTON_SECONDARY_BG = '#162a4a'
    BUTTON_SECONDARY_HOVER = '#1e3a5f'
    BUTTON_DANGER_BG = '#e76f51'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#f4845f'
    BUTTON_DISABLED_BG = '#162a4a'
    BUTTON_DISABLED_TEXT = '#2b5278'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#1e3a5f'
    INPUT_BORDER = '#2b5278'
    INPUT_BORDER_FOCUS = '#00b4d8'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#162a4a'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#00b4d8'
    CHART_LINE_2 = '#e76f51'
    CHART_LINE_3 = '#e9c46a'
    CHART_LINE_4 = '#48cae4'
    CHART_LINE_5 = '#a8dadc'
    CHART_LINE_6 = '#00e5a0'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#00b4d8'
    ELECTRODE_2 = '#e9c46a'
    ELECTRODE_3 = '#e76f51'
    ELECTRODE_CARD_BG_1 = '#0a2535'
    ELECTRODE_CARD_BG_2 = '#2a2510'
    ELECTRODE_CARD_BG_3 = '#2a1510'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class RoseGold:
    """玫瑰金主题（浅色，暖粉 + 玫瑰金）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#fdf2f0'
    BG_DARK = '#fff5f3'
    BG_MEDIUM = '#fff9f8'
    BG_LIGHT = '#ffffff'
    BG_CARD = '#fff5f3'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'
    BTN_BG_HOVER = '#fff5f3'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#d4a08a'
    BORDER_MEDIUM = '#c49080'
    BORDER_LIGHT = '#e0c0b0'
    BORDER_GLOW = '#b76e79'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#b76e79'
    GLOW_CYAN = '#b76e79'
    GLOW_GREEN = '#6b9e78'
    GLOW_ORANGE = '#d4a373'
    GLOW_RED = '#c0392b'
    GLOW_BLUE = '#7e92a5'
    GLOW_YELLOW = '#d4a373'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#3d2022'
    TEXT_SECONDARY = '#6b4c4e'
    TEXT_MUTED = '#a08585'
    TEXT_DISABLED = '#c8b0b0'
    TEXT_ACCENT = '#b76e79'
    TEXT_ON_PRIMARY = '#ffffff'
    TEXT_SELECTED = '#b76e79'
    TEXT_BUTTERFLY_LEFT = '#3d2022'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#6b9e78'
    STATUS_WARNING = '#d4a373'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#d4a373'
    COLOR_SUCCESS = '#6b9e78'
    COLOR_ERROR = '#c0392b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#b76e79'
    BUTTON_PRIMARY_TEXT = '#ffffff'
    BUTTON_PRIMARY_HOVER = '#cc8891'
    BUTTON_SECOND_TEXT = '#3d2022'
    BUTTON_SECONDARY_BG = '#fdf2f0'
    BUTTON_SECONDARY_HOVER = '#cc8891'
    BUTTON_DANGER_BG = '#c0392b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#e74c3c'
    BUTTON_DISABLED_BG = '#f0e0dd'
    BUTTON_DISABLED_TEXT = '#c8b0b0'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'
    INPUT_BORDER = '#e0c0b0'
    INPUT_BORDER_FOCUS = '#b76e79'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#b76e79'
    CHART_LINE_2 = '#6b9e78'
    CHART_LINE_3 = '#d4a373'
    CHART_LINE_4 = '#7e92a5'
    CHART_LINE_5 = '#a0748c'
    CHART_LINE_6 = '#8b6e5a'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#b76e79'
    ELECTRODE_2 = '#d4a373'
    ELECTRODE_3 = '#c0392b'
    ELECTRODE_CARD_BG_1 = '#fce8ea'
    ELECTRODE_CARD_BG_2 = '#fef3e0'
    ELECTRODE_CARD_BG_3 = '#fce0dc'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'


class EmeraldNight:
    """翡翠夜主题（深色，暗森林 + 翡翠发光）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0a1a12'
    BG_DARK = '#0f2518'
    BG_MEDIUM = '#163020'
    BG_LIGHT = '#1e4030'
    BG_CARD = '#122a1c'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#1e40304D'
    BTN_BG_HOVER = '#1e403080'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#1e4030'
    BORDER_MEDIUM = '#2a5a40'
    BORDER_LIGHT = '#3a7a55'
    BORDER_GLOW = '#00d68f'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#00d68f'
    GLOW_CYAN = '#00d68f'
    GLOW_GREEN = '#34ebc6'
    GLOW_ORANGE = '#f0a050'
    GLOW_RED = '#f05050'
    GLOW_BLUE = '#50b0f0'
    GLOW_YELLOW = '#f0d050'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#d0f0e0'
    TEXT_SECONDARY = '#80c0a0'
    TEXT_MUTED = '#406050'
    TEXT_DISABLED = '#2a5a40'
    TEXT_ACCENT = '#34ebc6'
    TEXT_ON_PRIMARY = '#0a1a12'
    TEXT_SELECTED = '#00d68f'
    TEXT_BUTTERFLY_LEFT = '#d0f0e0'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#34ebc6'
    STATUS_WARNING = '#f0d050'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#f0a050'
    COLOR_SUCCESS = '#34ebc6'
    COLOR_ERROR = '#f05050'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#00d68f'
    BUTTON_PRIMARY_TEXT = '#0a1a12'
    BUTTON_PRIMARY_HOVER = '#34ebc6'
    BUTTON_SECOND_TEXT = '#d0f0e0'
    BUTTON_SECONDARY_BG = '#163020'
    BUTTON_SECONDARY_HOVER = '#1e4030'
    BUTTON_DANGER_BG = '#f05050'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#ff6666'
    BUTTON_DISABLED_BG = '#163020'
    BUTTON_DISABLED_TEXT = '#2a5a40'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#1e4030'
    INPUT_BORDER = '#2a5a40'
    INPUT_BORDER_FOCUS = '#00d68f'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#163020'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#00d68f'
    CHART_LINE_2 = '#f05050'
    CHART_LINE_3 = '#f0d050'
    CHART_LINE_4 = '#50b0f0'
    CHART_LINE_5 = '#a080d0'
    CHART_LINE_6 = '#34ebc6'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#00d68f'
    ELECTRODE_2 = '#f0d050'
    ELECTRODE_3 = '#f05050'
    ELECTRODE_CARD_BG_1 = '#0a2a18'
    ELECTRODE_CARD_BG_2 = '#2a2510'
    ELECTRODE_CARD_BG_3 = '#2a1010'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class SunsetAmber:
    """日落琥珀主题（浅色，暖杏 + 琥珀金）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#fef6ee'
    BG_DARK = '#fff8f0'
    BG_MEDIUM = '#fffbf5'
    BG_LIGHT = '#ffffff'
    BG_CARD = '#fff8f0'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'
    BTN_BG_HOVER = '#fff8f0'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#c9956a'
    BORDER_MEDIUM = '#b8845a'
    BORDER_LIGHT = '#ddb896'
    BORDER_GLOW = '#c06014'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#c06014'
    GLOW_CYAN = '#c06014'
    GLOW_GREEN = '#5a8a50'
    GLOW_ORANGE = '#e07020'
    GLOW_RED = '#c0392b'
    GLOW_BLUE = '#4a80a0'
    GLOW_YELLOW = '#b09000'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#3a2010'
    TEXT_SECONDARY = '#6a4530'
    TEXT_MUTED = '#a08070'
    TEXT_DISABLED = '#c8b0a0'
    TEXT_ACCENT = '#c06014'
    TEXT_ON_PRIMARY = '#ffffff'
    TEXT_SELECTED = '#c06014'
    TEXT_BUTTERFLY_LEFT = '#3a2010'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#5a8a50'
    STATUS_WARNING = '#e07020'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#e07020'
    COLOR_SUCCESS = '#5a8a50'
    COLOR_ERROR = '#c0392b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#c06014'
    BUTTON_PRIMARY_TEXT = '#ffffff'
    BUTTON_PRIMARY_HOVER = '#d07024'
    BUTTON_SECOND_TEXT = '#3a2010'
    BUTTON_SECONDARY_BG = '#fef6ee'
    BUTTON_SECONDARY_HOVER = '#d07024'
    BUTTON_DANGER_BG = '#c0392b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#e74c3c'
    BUTTON_DISABLED_BG = '#f0e0d0'
    BUTTON_DISABLED_TEXT = '#c8b0a0'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'
    INPUT_BORDER = '#ddb896'
    INPUT_BORDER_FOCUS = '#c06014'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#c06014'
    CHART_LINE_2 = '#5a8a50'
    CHART_LINE_3 = '#b09000'
    CHART_LINE_4 = '#4a80a0'
    CHART_LINE_5 = '#a07060'
    CHART_LINE_6 = '#8a6040'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#c06014'
    ELECTRODE_2 = '#b09000'
    ELECTRODE_3 = '#c0392b'
    ELECTRODE_CARD_BG_1 = '#fef0e0'
    ELECTRODE_CARD_BG_2 = '#fef5d8'
    ELECTRODE_CARD_BG_3 = '#fce0dc'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'


class VioletDream:
    """紫罗兰梦主题（深色，深紫 + 霓虹紫红）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0e0a1a'
    BG_DARK = '#150f28'
    BG_MEDIUM = '#1e1635'
    BG_LIGHT = '#2a2048'
    BG_CARD = '#18122c'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#2a20484D'
    BTN_BG_HOVER = '#2a204880'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#2a2048'
    BORDER_MEDIUM = '#3d3060'
    BORDER_LIGHT = '#554080'
    BORDER_GLOW = '#a855f7'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#a855f7'
    GLOW_CYAN = '#a855f7'
    GLOW_GREEN = '#34d399'
    GLOW_ORANGE = '#fb923c'
    GLOW_RED = '#f43f5e'
    GLOW_BLUE = '#60a5fa'
    GLOW_YELLOW = '#fbbf24'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#e8ddf5'
    TEXT_SECONDARY = '#a090c0'
    TEXT_MUTED = '#554080'
    TEXT_DISABLED = '#3d3060'
    TEXT_ACCENT = '#c084fc'
    TEXT_ON_PRIMARY = '#0e0a1a'
    TEXT_SELECTED = '#a855f7'
    TEXT_BUTTERFLY_LEFT = '#e8ddf5'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#34d399'
    STATUS_WARNING = '#fbbf24'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#fb923c'
    COLOR_SUCCESS = '#34d399'
    COLOR_ERROR = '#f43f5e'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#a855f7'
    BUTTON_PRIMARY_TEXT = '#0e0a1a'
    BUTTON_PRIMARY_HOVER = '#c084fc'
    BUTTON_SECOND_TEXT = '#e8ddf5'
    BUTTON_SECONDARY_BG = '#1e1635'
    BUTTON_SECONDARY_HOVER = '#2a2048'
    BUTTON_DANGER_BG = '#f43f5e'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#fb7185'
    BUTTON_DISABLED_BG = '#1e1635'
    BUTTON_DISABLED_TEXT = '#3d3060'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#2a2048'
    INPUT_BORDER = '#3d3060'
    INPUT_BORDER_FOCUS = '#a855f7'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#1e1635'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#a855f7'
    CHART_LINE_2 = '#f43f5e'
    CHART_LINE_3 = '#fbbf24'
    CHART_LINE_4 = '#60a5fa'
    CHART_LINE_5 = '#c084fc'
    CHART_LINE_6 = '#34d399'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#a855f7'
    ELECTRODE_2 = '#fbbf24'
    ELECTRODE_3 = '#f43f5e'
    ELECTRODE_CARD_BG_1 = '#1a102a'
    ELECTRODE_CARD_BG_2 = '#2a2510'
    ELECTRODE_CARD_BG_3 = '#2a1018'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class ArcticFrost:
    """极地霜白主题（浅色，冰蓝白 + 冰蓝强调）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#eef4f8'
    BG_DARK = '#f2f8fc'
    BG_MEDIUM = '#f7fbfd'
    BG_LIGHT = '#ffffff'
    BG_CARD = '#f2f8fc'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'
    BTN_BG_HOVER = '#f2f8fc'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#8aaec0'
    BORDER_MEDIUM = '#7a9eb0'
    BORDER_LIGHT = '#b0ccd8'
    BORDER_GLOW = '#2563eb'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#2563eb'
    GLOW_CYAN = '#2563eb'
    GLOW_GREEN = '#16a34a'
    GLOW_ORANGE = '#ea880a'
    GLOW_RED = '#dc2626'
    GLOW_BLUE = '#0284c7'
    GLOW_YELLOW = '#ca8a04'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#1e2a3a'
    TEXT_SECONDARY = '#4a6070'
    TEXT_MUTED = '#8aaec0'
    TEXT_DISABLED = '#b0ccd8'
    TEXT_ACCENT = '#2563eb'
    TEXT_ON_PRIMARY = '#ffffff'
    TEXT_SELECTED = '#2563eb'
    TEXT_BUTTERFLY_LEFT = '#1e2a3a'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#16a34a'
    STATUS_WARNING = '#ea880a'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#ea880a'
    COLOR_SUCCESS = '#16a34a'
    COLOR_ERROR = '#dc2626'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#2563eb'
    BUTTON_PRIMARY_TEXT = '#ffffff'
    BUTTON_PRIMARY_HOVER = '#3b82f6'
    BUTTON_SECOND_TEXT = '#1e2a3a'
    BUTTON_SECONDARY_BG = '#eef4f8'
    BUTTON_SECONDARY_HOVER = '#3b82f6'
    BUTTON_DANGER_BG = '#dc2626'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#ef4444'
    BUTTON_DISABLED_BG = '#e0eaf0'
    BUTTON_DISABLED_TEXT = '#b0ccd8'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'
    INPUT_BORDER = '#b0ccd8'
    INPUT_BORDER_FOCUS = '#2563eb'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#2563eb'
    CHART_LINE_2 = '#dc2626'
    CHART_LINE_3 = '#ca8a04'
    CHART_LINE_4 = '#0284c7'
    CHART_LINE_5 = '#7c3aed'
    CHART_LINE_6 = '#16a34a'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#2563eb'
    ELECTRODE_2 = '#ca8a04'
    ELECTRODE_3 = '#dc2626'
    ELECTRODE_CARD_BG_1 = '#e0eeff'
    ELECTRODE_CARD_BG_2 = '#fef5d8'
    ELECTRODE_CARD_BG_3 = '#fee0e0'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'


class IronForge:
    """铁锻主题（深色，高对比度文字）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0b0f12'
    BG_DARK = '#11161b'
    BG_MEDIUM = '#1a222a'
    BG_LIGHT = '#252f38'
    BG_CARD = '#141a20'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#252f384D'
    BTN_BG_HOVER = '#252f3880'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#2b3946'
    BORDER_MEDIUM = '#3a4c5c'
    BORDER_LIGHT = '#5c7184'
    BORDER_GLOW = '#f0c75e'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#f0c75e'
    GLOW_CYAN = '#f0c75e'
    GLOW_GREEN = '#6ac48f'
    GLOW_ORANGE = '#f0c75e'
    GLOW_RED = '#ff3b30'
    GLOW_BLUE = '#4aa3d8'
    GLOW_YELLOW = '#ffd98a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#eaf0f5'
    TEXT_SECONDARY = '#b7c2cc'
    TEXT_MUTED = '#6b7b88'
    TEXT_DISABLED = '#3a4652'
    TEXT_ACCENT = '#f0c75e'
    TEXT_ON_PRIMARY = '#0b0f12'
    TEXT_SELECTED = '#f0c75e'
    TEXT_BUTTERFLY_LEFT = '#eaf0f5'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#6ac48f'
    STATUS_WARNING = '#f0c75e'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#f0c75e'
    COLOR_SUCCESS = '#6ac48f'
    COLOR_ERROR = '#d14b4b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#f0c75e'
    BUTTON_PRIMARY_TEXT = '#0b0f12'
    BUTTON_PRIMARY_HOVER = '#ffd98a'
    BUTTON_SECOND_TEXT = '#eaf0f5'
    BUTTON_SECONDARY_BG = '#1a222a'
    BUTTON_SECONDARY_HOVER = '#252f38'
    BUTTON_DANGER_BG = '#d14b4b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#e25c5c'
    BUTTON_DISABLED_BG = '#1a222a'
    BUTTON_DISABLED_TEXT = '#3a4652'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#252f38'
    INPUT_BORDER = '#3a4c5c'
    INPUT_BORDER_FOCUS = '#f0c75e'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#1a222a'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#f0c75e'
    CHART_LINE_2 = '#6ac48f'
    CHART_LINE_3 = '#4aa3d8'
    CHART_LINE_4 = '#ff8a3d'
    CHART_LINE_5 = '#a0b0bd'
    CHART_LINE_6 = '#d14b4b'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#f0c75e'
    ELECTRODE_2 = '#6ac48f'
    ELECTRODE_3 = '#d14b4b'
    ELECTRODE_CARD_BG_1 = '#1a1f18'
    ELECTRODE_CARD_BG_2 = '#18201a'
    ELECTRODE_CARD_BG_3 = '#241516'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class ControlRoom:
    """中控室主题（深色，高对比度文字）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0a1016'
    BG_DARK = '#101821'
    BG_MEDIUM = '#17212c'
    BG_LIGHT = '#213041'
    BG_CARD = '#121b24'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#2130414D'
    BTN_BG_HOVER = '#21304180'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#2a3a4b'
    BORDER_MEDIUM = '#3a4e63'
    BORDER_LIGHT = '#5a7088'
    BORDER_GLOW = '#e85d4a'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#e85d4a'
    GLOW_CYAN = '#e85d4a'
    GLOW_GREEN = '#6fbf6b'
    GLOW_ORANGE = '#d8934a'
    GLOW_RED = '#c73b3b'
    GLOW_BLUE = '#6b8fbf'
    GLOW_YELLOW = '#d9c26a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#e6f0fa'
    TEXT_SECONDARY = '#b4c6d6'
    TEXT_MUTED = '#6a7c8c'
    TEXT_DISABLED = '#3b4a59'
    TEXT_ACCENT = '#e85d4a'
    TEXT_ON_PRIMARY = '#0a1016'
    TEXT_SELECTED = '#e85d4a'
    TEXT_BUTTERFLY_LEFT = '#e6f0fa'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#6fbf6b'
    STATUS_WARNING = '#d8934a'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#d8934a'
    COLOR_SUCCESS = '#6fbf6b'
    COLOR_ERROR = '#c73b3b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#e85d4a'
    BUTTON_PRIMARY_TEXT = '#0a1016'
    BUTTON_PRIMARY_HOVER = '#f07a6a'
    BUTTON_SECOND_TEXT = '#e6f0fa'
    BUTTON_SECONDARY_BG = '#17212c'
    BUTTON_SECONDARY_HOVER = '#213041'
    BUTTON_DANGER_BG = '#c73b3b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#d64a4a'
    BUTTON_DISABLED_BG = '#17212c'
    BUTTON_DISABLED_TEXT = '#3b4a59'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#213041'
    INPUT_BORDER = '#3a4e63'
    INPUT_BORDER_FOCUS = '#e85d4a'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#17212c'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#e85d4a'
    CHART_LINE_2 = '#6fbf6b'
    CHART_LINE_3 = '#d8934a'
    CHART_LINE_4 = '#6b8fbf'
    CHART_LINE_5 = '#a0aab3'
    CHART_LINE_6 = '#c73b3b'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#e85d4a'
    ELECTRODE_2 = '#d8934a'
    ELECTRODE_3 = '#c73b3b'
    ELECTRODE_CARD_BG_1 = '#10202a'
    ELECTRODE_CARD_BG_2 = '#201d12'
    ELECTRODE_CARD_BG_3 = '#241414'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class NightShift:
    """夜班主题（深色，高对比度文字）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0a0c0d'
    BG_DARK = '#111416'
    BG_MEDIUM = '#1b2023'
    BG_LIGHT = '#262d31'
    BG_CARD = '#15191c'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#262d314D'
    BTN_BG_HOVER = '#262d3180'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#2b3236'
    BORDER_MEDIUM = '#3b444a'
    BORDER_LIGHT = '#56626a'
    BORDER_GLOW = '#c9956a'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#c9956a'
    GLOW_CYAN = '#c9956a'
    GLOW_GREEN = '#8fbf6a'
    GLOW_ORANGE = '#c9956a'
    GLOW_RED = '#c73b3b'
    GLOW_BLUE = '#6b86b8'
    GLOW_YELLOW = '#d9b06a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#f2f5f7'
    TEXT_SECONDARY = '#c3cbd0'
    TEXT_MUTED = '#7d8a92'
    TEXT_DISABLED = '#3c454b'
    TEXT_ACCENT = '#c9956a'
    TEXT_ON_PRIMARY = '#0a0c0d'
    TEXT_SELECTED = '#c9956a'
    TEXT_BUTTERFLY_LEFT = '#f2f5f7'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#8fbf6a'
    STATUS_WARNING = '#c9956a'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#c9956a'
    COLOR_SUCCESS = '#8fbf6a'
    COLOR_ERROR = '#c73b3b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#c9956a'
    BUTTON_PRIMARY_TEXT = '#0a0c0d'
    BUTTON_PRIMARY_HOVER = '#d8a980'
    BUTTON_SECOND_TEXT = '#f2f5f7'
    BUTTON_SECONDARY_BG = '#1b2023'
    BUTTON_SECONDARY_HOVER = '#262d31'
    BUTTON_DANGER_BG = '#c73b3b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#d64a4a'
    BUTTON_DISABLED_BG = '#1b2023'
    BUTTON_DISABLED_TEXT = '#3c454b'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#262d31'
    INPUT_BORDER = '#3b444a'
    INPUT_BORDER_FOCUS = '#c9956a'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#1b2023'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#c9956a'
    CHART_LINE_2 = '#8fbf6a'
    CHART_LINE_3 = '#6b86b8'
    CHART_LINE_4 = '#c73b3b'
    CHART_LINE_5 = '#9aa7af'
    CHART_LINE_6 = '#d9b06a'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#c9956a'
    ELECTRODE_2 = '#d9b06a'
    ELECTRODE_3 = '#c73b3b'
    ELECTRODE_CARD_BG_1 = '#172019'
    ELECTRODE_CARD_BG_2 = '#201c14'
    ELECTRODE_CARD_BG_3 = '#241414'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class SteelLine:
    """钢线主题（浅色，高对比度边框与分割线）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#f2f4f6'
    BG_DARK = '#e7ebef'
    BG_MEDIUM = '#f5f7f9'
    BG_LIGHT = '#ffffff'
    BG_CARD = '#f0f3f6'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'
    BTN_BG_HOVER = '#f5f7f9'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#1e2a33'
    BORDER_MEDIUM = '#2a3a45'
    BORDER_LIGHT = '#3a4b58'
    BORDER_GLOW = '#455a64'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#455a64'
    GLOW_CYAN = '#455a64'
    GLOW_GREEN = '#2e7d32'
    GLOW_ORANGE = '#a07a52'
    GLOW_RED = '#c0392b'
    GLOW_BLUE = '#5f7480'
    GLOW_YELLOW = '#b59b2a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#1e2a33'
    TEXT_SECONDARY = '#394a58'
    TEXT_MUTED = '#6b7b86'
    TEXT_DISABLED = '#9aa7af'
    TEXT_ACCENT = '#455a64'
    TEXT_ON_PRIMARY = '#ffffff'
    TEXT_SELECTED = '#455a64'
    TEXT_BUTTERFLY_LEFT = '#1e2a33'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#2e7d32'
    STATUS_WARNING = '#a07a52'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#a07a52'
    COLOR_SUCCESS = '#2e7d32'
    COLOR_ERROR = '#c0392b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#455a64'
    BUTTON_PRIMARY_TEXT = '#ffffff'
    BUTTON_PRIMARY_HOVER = '#566b76'
    BUTTON_SECOND_TEXT = '#1e2a33'
    BUTTON_SECONDARY_BG = '#f0f3f6'
    BUTTON_SECONDARY_HOVER = '#e7ebef'
    BUTTON_DANGER_BG = '#c0392b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#e04c3c'
    BUTTON_DISABLED_BG = '#e7ebef'
    BUTTON_DISABLED_TEXT = '#9aa7af'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'
    INPUT_BORDER = '#2a3a45'
    INPUT_BORDER_FOCUS = '#455a64'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#455a64'
    CHART_LINE_2 = '#2e7d32'
    CHART_LINE_3 = '#a07a52'
    CHART_LINE_4 = '#5f7480'
    CHART_LINE_5 = '#6b7b86'
    CHART_LINE_6 = '#c0392b'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#455a64'
    ELECTRODE_2 = '#a07a52'
    ELECTRODE_3 = '#c0392b'
    ELECTRODE_CARD_BG_1 = '#e7f2fc'
    ELECTRODE_CARD_BG_2 = '#f6efe6'
    ELECTRODE_CARD_BG_3 = '#f7e6e2'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'


class SlateGrid:
    """石墨网格主题（深色，高对比度边框与分割线）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#1c2126'
    BG_DARK = '#242b31'
    BG_MEDIUM = '#2d363d'
    BG_LIGHT = '#364149'
    BG_CARD = '#22292f'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#3641494D'
    BTN_BG_HOVER = '#36414980'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#0f1418'
    BORDER_MEDIUM = '#3f4c56'
    BORDER_LIGHT = '#dfe5ea'
    BORDER_GLOW = '#8899a6'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#8899a6'
    GLOW_CYAN = '#8899a6'
    GLOW_GREEN = '#6fa27f'
    GLOW_ORANGE = '#b9895a'
    GLOW_RED = '#c73b3b'
    GLOW_BLUE = '#708499'
    GLOW_YELLOW = '#c9b06a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#eef2f5'
    TEXT_SECONDARY = '#c4cbd1'
    TEXT_MUTED = '#7a8791'
    TEXT_DISABLED = '#3f4c56'
    TEXT_ACCENT = '#8899a6'
    TEXT_ON_PRIMARY = '#1c2126'
    TEXT_SELECTED = '#8899a6'
    TEXT_BUTTERFLY_LEFT = '#eef2f5'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#6fa27f'
    STATUS_WARNING = '#b9895a'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#b9895a'
    COLOR_SUCCESS = '#6fa27f'
    COLOR_ERROR = '#c73b3b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#8899a6'
    BUTTON_PRIMARY_TEXT = '#1c2126'
    BUTTON_PRIMARY_HOVER = '#9aa9b4'
    BUTTON_SECOND_TEXT = '#eef2f5'
    BUTTON_SECONDARY_BG = '#2d363d'
    BUTTON_SECONDARY_HOVER = '#364149'
    BUTTON_DANGER_BG = '#c73b3b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#d64a4a'
    BUTTON_DISABLED_BG = '#2d363d'
    BUTTON_DISABLED_TEXT = '#3f4c56'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#364149'
    INPUT_BORDER = '#3f4c56'
    INPUT_BORDER_FOCUS = '#8899a6'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#2d363d'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#8899a6'
    CHART_LINE_2 = '#6fa27f'
    CHART_LINE_3 = '#b9895a'
    CHART_LINE_4 = '#708499'
    CHART_LINE_5 = '#a9b3ba'
    CHART_LINE_6 = '#c73b3b'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#8899a6'
    ELECTRODE_2 = '#b9895a'
    ELECTRODE_3 = '#c73b3b'
    ELECTRODE_CARD_BG_1 = '#1c2730'
    ELECTRODE_CARD_BG_2 = '#262118'
    ELECTRODE_CARD_BG_3 = '#241414'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'


class PolarFrame:
    """极光框架主题（浅色，高对比度边框与分割线）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#f7f9fb'
    BG_DARK = '#eef3f7'
    BG_MEDIUM = '#f9fbfd'
    BG_LIGHT = '#ffffff'
    BG_CARD = '#f1f5f9'
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'
    BTN_BG_HOVER = '#f1f5f9'
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#0b1f2a'
    BORDER_MEDIUM = '#1b2f3a'
    BORDER_LIGHT = '#2c4a5c'
    BORDER_GLOW = '#0d9488'
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#0d9488'
    GLOW_CYAN = '#0d9488'
    GLOW_GREEN = '#2e7d32'
    GLOW_ORANGE = '#a07a52'
    GLOW_RED = '#c0392b'
    GLOW_BLUE = '#4a7a80'
    GLOW_YELLOW = '#b59b2a'
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#0b1f2a'
    TEXT_SECONDARY = '#334a58'
    TEXT_MUTED = '#6b7d87'
    TEXT_DISABLED = '#9aa7af'
    TEXT_ACCENT = '#0d9488'
    TEXT_ON_PRIMARY = '#ffffff'
    TEXT_SELECTED = '#0d9488'
    TEXT_BUTTERFLY_LEFT = '#0b1f2a'
    
    # ===== 状态色 =====
    STATUS_SUCCESS = '#2e7d32'
    STATUS_WARNING = '#a07a52'
    STATUS_ALARM = '#ff0000'
    STATUS_ERROR = '#ff0000'
    
    # ===== 自定义状态色 =====
    COLOR_WARNING = '#a07a52'
    COLOR_SUCCESS = '#2e7d32'
    COLOR_ERROR = '#c0392b'
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#0d9488'
    BUTTON_PRIMARY_TEXT = '#ffffff'
    BUTTON_PRIMARY_HOVER = '#20b7aa'
    BUTTON_SECOND_TEXT = '#0b1f2a'
    BUTTON_SECONDARY_BG = '#f1f5f9'
    BUTTON_SECONDARY_HOVER = '#e3ebf2'
    BUTTON_DANGER_BG = '#c0392b'
    BUTTON_DANGER_TEXT = '#ffffff'
    BUTTON_DANGER_HOVER = '#e04c3c'
    BUTTON_DISABLED_BG = '#e3ebf2'
    BUTTON_DISABLED_TEXT = '#9aa7af'
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'
    INPUT_BORDER = '#1b2f3a'
    INPUT_BORDER_FOCUS = '#0d9488'
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#0d9488'
    CHART_LINE_2 = '#2e7d32'
    CHART_LINE_3 = '#a07a52'
    CHART_LINE_4 = '#4a7a80'
    CHART_LINE_5 = '#6b7d87'
    CHART_LINE_6 = '#c0392b'
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_1 = '#0d9488'
    ELECTRODE_2 = '#a07a52'
    ELECTRODE_3 = '#c0392b'
    ELECTRODE_CARD_BG_1 = '#e4f3fb'
    ELECTRODE_CARD_BG_2 = '#f6efe6'
    ELECTRODE_CARD_BG_3 = '#f7e6e2'
    
    # ===== 阴影与发光效果 =====
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'


# ===== 通用颜色（不随主题变化）=====
class CommonColors:
    """通用颜色常量"""
    TRANSPARENT = 'transparent'
    BLACK = '#000000'
    WHITE = '#ffffff'
