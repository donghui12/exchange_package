# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 获取操作系统类型
is_windows = sys.platform.startswith('win')
is_macos = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# 设置可执行文件名称
if is_windows:
    exe_name = '秒转助手'
    console_mode = False  # Windows下使用窗口模式
elif is_macos:
    exe_name = '秒转助手'
    console_mode = False  # macOS下使用窗口模式
else:
    exe_name = '秒转助手'
    console_mode = True   # Linux下使用控制台模式

a = Analysis(
    ['../main.py'],
    pathex=['../'],
    binaries=[],
    datas=[
        ('../src', 'src'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'requests',
        'openpyxl',
        'psutil',
        'json',
        'os',
        'sys',
        'threading',
        'queue',
        're',
        'urllib.parse',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console_mode,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)