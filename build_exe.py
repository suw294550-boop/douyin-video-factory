"""
PyInstaller 打包为独立 .exe
输出: dist/DouyinFactory.exe (单文件)
"""
import os
import sys
import subprocess
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE, "src", "templates")

def build():
    # 先写 spec 文件
    spec = f"""# -*- mode: python ; coding: utf-8 -*-
import sys, os
from PyInstaller.utils.hooks import collect_data_files

datas = [('{TEMPLATE_DIR.replace(chr(92),'/')}', 'src/templates')]

a = Analysis(
    ['run.py'],
    pathex=['{BASE.replace(chr(92),'/')}'],
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
    hooksconfig={{}},
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
"""

    spec_path = os.path.join(BASE, "DouyinFactory.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec)

    print("Building DouyinFactory.exe ...")
    print("This may take 3-5 minutes...")
    print()

    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean", "--noconfirm",
        spec_path,
    ], cwd=BASE, timeout=600)

    if result.returncode != 0:
        print("\nBuild FAILED!")
        return None

    # 检查输出
    exe_path = os.path.join(BASE, "dist", "DouyinFactory.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / 1_048_576
        print(f"\n  Build OK: DouyinFactory.exe ({size_mb:.1f}MB)")
        print(f"  Location: {exe_path}")
        return exe_path
    else:
        print("\n  Build FAILED: exe not found")
        return None


if __name__ == "__main__":
    build()
