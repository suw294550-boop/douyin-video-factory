"""
生成无版权 BGM 库
用法: python scripts/generate_bgm.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.music import generate_all

if __name__ == "__main__":
    generate_all()
