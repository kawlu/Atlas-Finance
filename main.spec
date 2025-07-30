# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\lucas\\Documents\\Programação\\Faculdade\\Desenvolvimento de Softwares\\Atlas Finance\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\lucas\\Documents\\Programação\\Faculdade\\Desenvolvimento de Softwares\\Atlas Finance\\data\\translations_pt_BR.qm', 'data'), ('C:\\Users\\lucas\\Documents\\Programação\\Faculdade\\Desenvolvimento de Softwares\\Atlas Finance\\src\\util\\data_util.json', 'src/util'), ('C:\\Users\\lucas\\Documents\\Programação\\Faculdade\\Desenvolvimento de Softwares\\Atlas Finance\\ui', 'ui')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\lucas\\Documents\\Programação\\Faculdade\\Desenvolvimento de Softwares\\Atlas Finance\\assets\\icon.ico'],
)
