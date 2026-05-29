"""
打包脚本 - 创建可分发版本
生成 dist/DouyinFactory/ 目录，可直接分发
"""
import os
import sys
import shutil
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(BASE, "dist", "DouyinFactory")

# 需要分发的文件
INCLUDE_FILES = [
    "run.py",
    "requirements.txt",
    "README.md",
    "LICENSE",
    ".env.example",
    ".gitignore",
    "install.bat",
]

INCLUDE_DIRS = [
    "src",
    "scripts",
    "batch",
    "tests",
]

EXCLUDE_PATTERNS = [
    "__pycache__", "*.pyc", "*.pyo",
    "output", "browser_profile", "scripts_cache",
    "music", "backgrounds",
    "*.mp3", "*.mp4", "*.wav", "*.png",
    ".env", "douyin_cookies.json",
    "publish_log.json", "daily_log.txt",
    "*.log", ".git",
]


def should_exclude(path):
    for pat in EXCLUDE_PATTERNS:
        if pat.startswith("*"):
            if path.endswith(pat[1:]):
                return True
        elif pat in path:
            return True
    return False


def copytree(src, dst):
    for root, dirs, files in os.walk(src):
        # 过滤目录
        dirs[:] = [d for d in dirs if not should_exclude(d)]
        rel = os.path.relpath(root, src)
        target = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(target, exist_ok=True)
        for f in files:
            if should_exclude(f):
                continue
            src_path = os.path.join(root, f)
            dst_path = os.path.join(target, f)
            shutil.copy2(src_path, dst_path)


def build():
    print("=" * 50)
    print("  Building DouyinFactory package...")
    print("=" * 50)

    # 清理
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    # 创建必要空目录
    for d in ["output", "backgrounds", "music", "scripts_cache", "browser_profile"]:
        os.makedirs(os.path.join(DIST, d), exist_ok=True)

    # 复制文件
    for f in INCLUDE_FILES:
        src = os.path.join(BASE, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(DIST, f))
            print(f"  {f}")

    # 复制目录
    for d in INCLUDE_DIRS:
        src = os.path.join(BASE, d)
        if os.path.exists(src):
            copytree(src, os.path.join(DIST, d))
            print(f"  {d}/")

    print(f"\n  Package: {DIST}")
    print(f"  To install: run install.bat")
    print("=" * 50)

    # 创建 zip
    zip_path = os.path.join(BASE, "dist", "DouyinFactory.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(DIST):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, DIST)
                zf.write(full, os.path.join("DouyinFactory", rel))
    size_mb = os.path.getsize(zip_path) / 1024 / 1024
    print(f"  Zip: {zip_path} ({size_mb:.1f}MB)")
    return DIST


if __name__ == "__main__":
    build()
