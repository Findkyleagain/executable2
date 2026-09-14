# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


hiddenimports = collect_submodules("pytesseract")


a = Analysis(
    ["Watcher.py"],
    pathex=[],
    binaries=[
        ("tesseract/tesseract.exe", "tesseract"),
        ("tesseract/*.dll", "tesseract"),
    ],
    datas=[
        ("tesseract/tessdata", "tesseract/tessdata"),
        ("w_logo.png", "."),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="watcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="watcher",
)