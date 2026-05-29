# -*- mode: python ; coding: utf-8 -*-
import sys, os
from PyInstaller.utils.hooks import collect_data_files

datas = [('D:/桌面/short-video-factory/src/templates', 'src/templates')]

a = Analysis(
    ['run.py'],
    pathex=['D:/桌面/short-video-factory'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'flask','flask.cli','flask.json','flask.blueprints',
        'edge_tts','edge_tts.communicate','edge_tts.util',
        'playwright','playwright.async_api','playwright.sync_api',
        'requests','urllib3','certifi',
        'dotenv','asyncio','threading','json','glob','subprocess',
        'src','src.config','src.llm','src.scripts_gen',
        'src.pipeline','src.audio','src.background','src.music',
        'src.uploader','src.tracker','src.api','src.web',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter','matplotlib','numpy','pandas','scipy','PIL','cv2'],
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
    name='DouyinFactory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
