"""
PyInstaller runtime hook for snap7
"""
import os
import sys

# 1. 获取 _internal 目录路径
if hasattr(sys, '_MEIPASS'):
    # PyInstaller 打包后的路径
    base_path = sys._MEIPASS
else:
    # 开发环境路径
    base_path = os.path.dirname(os.path.abspath(__file__))

# 2. 添加 snap7/lib 目录到 DLL 搜索路径
snap7_lib_path = os.path.join(base_path, 'snap7', 'lib')

if os.path.exists(snap7_lib_path):
    # Windows 10+ 使用 os.add_dll_directory
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(snap7_lib_path)
    
    # 同时添加到 PATH 环境变量（兼容旧版本）
    os.environ['PATH'] = snap7_lib_path + os.pathsep + os.environ.get('PATH', '')

