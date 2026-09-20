# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["Watcher.py"],
    pathex=[],
    binaries=[
        ("tesseract/tesseract.exe", "tesseract"),
        ("tesseract/*.dll", "tesseract"),
    ],
    datas=[
        ("tesseract/tessdata/eng.traineddata", "tesseract/tessdata"),
        ("w_logo.png", "."),
        ("start_sound.wav", "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
    ],
    noarchive=False,
    optimize=2,
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
