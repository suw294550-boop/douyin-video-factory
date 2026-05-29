"""
无版权背景音乐生成 - ffmpeg 多层正弦波合成
"""
import os
import subprocess
from src.config import MUSIC_DIR


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=60).returncode == 0
    except Exception:
        return False


def generate_healing_piano(output_path, duration=60):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=261.63:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=329.63:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=392.00:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=523.25:duration={duration}:sample_rate=44100",
        "-filter_complex",
        "[0:a]volume=0.10,adelay=0:all=1[a0];"
        "[1:a]volume=0.06,adelay=3000:all=1[a1];"
        "[2:a]volume=0.04,adelay=6000:all=1[a2];"
        "[3:a]volume=0.03,adelay=9000:all=1[a3];"
        "[a0][a1][a2][a3]amix=inputs=4:duration=first,"
        f"afade=t=in:d=2,afade=t=out:st={duration-3}:d=3,"
        "lowpass=f=2200,aecho=0.8:0.6:50:0.3,volume=0.35",
        "-c:a", "libmp3lame", "-b:a", "128k",
        output_path,
    ]
    return _run(cmd)


def generate_ambient_pad(output_path, duration=60):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=220:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=330:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=550:duration={duration}:sample_rate=44100",
        "-filter_complex",
        "[0:a]volume=0.08[a0];[1:a]volume=0.06[a1];[2:a]volume=0.04[a2];[3:a]volume=0.03[a3];"
        "[a0][a1][a2][a3]amix=inputs=4:duration=first,"
        f"afade=t=in:d=2,afade=t=out:st={duration-3}:d=3,"
        "lowpass=f=1500,aecho=0.8:0.5:60:0.4,volume=0.25",
        "-c:a", "libmp3lame", "-b:a", "128k",
        output_path,
    ]
    return _run(cmd)


def generate_light_rhythm(output_path, duration=60):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=523.25:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=659.25:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=783.99:duration={duration}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency=1046.5:duration={duration}:sample_rate=44100",
        "-filter_complex",
        "[0:a]volume=0.08,adelay=0:all=1[a0];[1:a]volume=0.05,adelay=1500:all=1[a1];"
        "[2:a]volume=0.04,adelay=3000:all=1[a2];[3:a]volume=0.03,adelay=4500:all=1[a3];"
        "[a0][a1][a2][a3]amix=inputs=4:duration=first,"
        f"afade=t=in:d=1.5,afade=t=out:st={duration-2}:d=2,"
        "lowpass=f=3500,aecho=0.7:0.4:30:0.2,volume=0.3",
        "-c:a", "libmp3lame", "-b:a", "128k",
        output_path,
    ]
    return _run(cmd)


def generate_all():
    os.makedirs(str(MUSIC_DIR), exist_ok=True)
    print("Generating BGM library...")
    bgms = [
        ("healing_piano.mp3", "治愈钢琴", generate_healing_piano),
        ("ambient_pad.mp3", "氛围电子", generate_ambient_pad),
        ("light_rhythm.mp3", "轻快节奏", generate_light_rhythm),
    ]
    for filename, name, func in bgms:
        path = str(MUSIC_DIR / filename)
        if func(path):
            size_kb = os.path.getsize(path) / 1024
            print(f"  [{name}] {filename} ({size_kb:.0f}KB)")
        else:
            print(f"  [{name}] FAILED")
    print(f"Done! {len(os.listdir(str(MUSIC_DIR)))} files in music/")
