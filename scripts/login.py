"""
抖音扫码登录 - 独立脚本
用法: python scripts/login.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.uploader import login_only

if __name__ == "__main__":
    login_only()
