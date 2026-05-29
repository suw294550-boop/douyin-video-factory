"""
背景视频生成 - ffmpeg 纯色渐变
"""
import os
import random
import subprocess
from src.config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, BACKGROUND_DIR


def _run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode
    except Exception:
        return -1


def create_gradient_bg(output_path, color="0x1a1a2e", duration=60):
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c={color}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d={duration}:r={FPS}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    _run_cmd(cmd)
    return output_path


def get_or_create_background(output_dir, index=0):
    bg_dir = str(BACKGROUND_DIR)
    existing = [
        f for f in os.listdir(bg_dir)
        if f.endswith((".mp4", ".mov", ".webm", ".mkv"))
    ] if os.path.exists(bg_dir) else []

    if existing:
        return os.path.join(bg_dir, random.choice(existing))

    colors = [
        "0x1a1a2e", "0x0f3460", "0x130f40",
        "0x2d3436", "0x0c0c0c", "0x1b1b2f",
    ]
    color = colors[index % len(colors)]
    bg_path = os.path.join(output_dir, f"bg_{index:03d}.mp4")
    create_gradient_bg(bg_path, color)
    return bg_path
