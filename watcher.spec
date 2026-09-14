# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


hiddenimports = collect_submodules("pytesseract")


a = Analysis(
    ["Watcher.py"],
    pathex=[],
    binaries=[
        (
            "tesseract/tesseract.exe",
            "tesseract"
        ),
        (
            "tesseract/*.dll",
            "tesseract"
        ),
    ],
    datas=[
        (
            "tesseract/tessdata",
            "tesseract/tessdata"
        ),
        (
            "W_logo.png",
            "."
        ),
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
    a.binaries,
    a.datas,
    [],
    name="watcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)