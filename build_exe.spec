# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 1. 收集所有需要的数据文件
import os
import snap7

# 获取 snap7.dll 的路径
snap7_lib_path = os.path.join(os.path.dirname(snap7.__file__), 'lib', 'snap7.dll')

datas = [
    ('assets', 'assets'),  # 图标、图片、音频
    ('backend/configs', 'backend/configs'),  # YAML 配置文件
    ('backend/data', 'backend/data'),  # valve_config.json
    ('data', 'data'),  # alarm_thresholds.json, batch_state.json
]

# 2. 收集二进制文件（DLL）
binaries = [
    (snap7_lib_path, 'snap7/lib'),  # 添加 snap7.dll
]

# 3. 收集所有需要的隐藏导入
hiddenimports = [
    # PyQt6 核心
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtCharts',
    'PyQt6.QtSvg',
    'PyQt6.QtSvgWidgets',
    
    # pyqtgraph - 只导入核心模块，避免子进程崩溃
    'pyqtgraph',
    'pyqtgraph.graphicsItems',
    'pyqtgraph.graphicsItems.PlotItem',
    'pyqtgraph.graphicsItems.ViewBox',
    'pyqtgraph.graphicsItems.AxisItem',
    'pyqtgraph.graphicsItems.PlotDataItem',
    'pyqtgraph.graphicsItems.ScatterPlotItem',
    'pyqtgraph.graphicsItems.LegendItem',
    'pyqtgraph.exporters',
    
    # 后端模块
    'backend',
    'backend.bridge',
    'backend.bridge.data_bridge',
    'backend.bridge.data_cache',
    'backend.bridge.service_manager',
    'backend.core',
    'backend.core.influxdb',
    'backend.plc',
    'backend.plc.plc_manager',
    'backend.services',
    'backend.services.polling_service',
    'backend.tools',
    
    # InfluxDB
    'influxdb_client',
    'influxdb_client.client',
    'influxdb_client.client.write_api',
    
    # Snap7
    'snap7',
    'snap7.client',
    'snap7.util',
    
    # Modbus
    'pymodbus',
    'pymodbus.client',
    'pymodbus.client.sync',
    
    # 其他依赖
    'numpy',
    'yaml',
    'pydantic',
    'pydantic_core',
    'loguru',
    'openpyxl',
    'psutil',
    'playsound',  # 报警声音播放
]

# 4. 分析阶段
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],  # 使用自定义钩子目录
    hooksconfig={},
    runtime_hooks=['rthooks/pyi_rth_snap7.py'],
    excludes=[
        'fastapi',  # 已移除
        'uvicorn',  # 已移除
        'matplotlib',  # 不需要
        'pandas',  # 不需要
        'scipy',  # 不需要
        'PIL',  # 不需要
        'tkinter',  # 不需要
        'PyQt5',  # 排除 PyQt5 (与 PyQt6 冲突)
        'pyqtgraph.opengl',  # 排除 OpenGL 模块（会导致崩溃）
        'pyqtgraph.examples',  # 排除示例
        'OpenGL',  # 排除 OpenGL
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 5. 打包阶段
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='3号电炉',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# 6. 收集所有文件到 dist 目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='3号电炉',
)

