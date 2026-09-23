# -*- mode: python ; coding: utf-8 -*-

import os
from glob import glob

from PyInstaller.building.build_main import Analysis, PYZ, EXE


# Collect Tesseract files prepared by GitHub Actions.
tesseract_binaries = []
tesseract_datas = []

for file_path in glob(
    os.path.join("tesseract", "**", "*"),
    recursive=True
):

    if not os.path.isfile(file_path):
        continue

    relative_path = os.path.relpath(
        file_path,
        "tesseract"
    )

    destination = os.path.dirname(
        os.path.join(
            "tesseract",
            relative_path
        )
    )

    filename = os.path.basename(file_path)

    if filename.lower().endswith(
        (".exe", ".dll")
    ):
        tesseract_binaries.append(
            (
                file_path,
                destination
            )
        )

    else:
        tesseract_datas.append(
            (
                file_path,
                destination
            )
        )


a = Analysis(
    ["Watcher.py"],
    pathex=[],
    binaries=tesseract_binaries,
    datas=[
        *tesseract_datas,
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
