# PyInstaller 自定义钩子 - pyqtgraph
# 用于避免收集 pyqtgraph.opengl 和 pyqtgraph.canvas 导致的崩溃

from PyInstaller.utils.hooks import collect_submodules

# 只收集核心模块，排除会导致崩溃的模块
hiddenimports = [
    'pyqtgraph.graphicsItems',
    'pyqtgraph.graphicsItems.PlotItem',
    'pyqtgraph.graphicsItems.ViewBox',
    'pyqtgraph.graphicsItems.AxisItem',
    'pyqtgraph.graphicsItems.PlotDataItem',
    'pyqtgraph.graphicsItems.ScatterPlotItem',
    'pyqtgraph.graphicsItems.LegendItem',
    'pyqtgraph.exporters',
]

# 排除会导致崩溃的模块
excludedimports = [
    'pyqtgraph.opengl',
    'pyqtgraph.canvas',
    'pyqtgraph.examples',
]






