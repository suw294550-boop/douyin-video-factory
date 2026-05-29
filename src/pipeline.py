"""
视频合成主流水线 - 配音 + 字幕 + 背景 + BGM → 成品视频
"""
import os
import sys
import time
import json
import subprocess
from src.config import (
    OUTPUT_DIR, BACKGROUND_DIR, MUSIC_DIR, BGM_MAP, BGM_VOLUME,
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, FONT_PATH, FONT_SIZE,
    STROKE_COLOR, STROKE_WIDTH, SUBTITLE_MAX_CHARS_PER_LINE,
    VIDEO_TOPICS,
)
from src.scripts_gen import generate_scripts, generate_titles, generate_desc
from src.audio import tts_batch
from src.background import get_or_create_background


def _run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=180)
        stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
        stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
        return result.returncode, stdout, stderr
    except Exception as e:
        return -1, "", str(e)


def _get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", audio_path,
    ]
    code, out, _ = _run_cmd(cmd)
    try:
        return float(out.strip())
    except Exception:
        return 10.0


def _build_subtitle_filter(text):
    """生成 ffmpeg drawtext 字幕滤镜"""
    lines = []
    current = ""
    for char in text:
        current += char
        if len(current) >= SUBTITLE_MAX_CHARS_PER_LINE:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)

    total_h = len(lines) * 76
    y_start = int(VIDEO_HEIGHT * 0.68 - total_h / 2)
    font = FONT_PATH.replace("\\", "/").replace(":", "\\:")

    parts = []
    for i, line in enumerate(lines):
        y = y_start + i * 76
        safe_line = (
            line.replace("\\", "\\\\").replace(":", "\\:")
            .replace("'", "\\\\'").replace("%", "\\\\%")
            .replace("{", "\\\\{").replace("}", "\\\\}")
        )
        d = (
            f"drawtext=text='{safe_line}':fontfile='{font}':"
            f"fontsize={FONT_SIZE}:fontcolor=white@0.95:"
            f"x=(w-text_w)/2:y={y}:"
            f"bordercolor=black@0.55:borderw={STROKE_WIDTH}:"
            f"shadowcolor=black@0.35:shadowx=2:shadowy=2"
        )
        parts.append(d)
    return "," + ",".join(parts)


def _find_music(topic=""):
    music_dir = str(MUSIC_DIR)
    if not os.path.exists(music_dir):
        return None
    bgm_file = BGM_MAP.get(topic, "")
    bgm_path = os.path.join(music_dir, bgm_file)
    if bgm_file and os.path.exists(bgm_path):
        return bgm_path
    music_files = [
        f for f in os.listdir(music_dir)
        if f.endswith((".mp3", ".wav", ".m4a", ".ogg"))
    ]
    return os.path.join(music_dir, music_files[0]) if music_files else None


def _assemble_one(audio_path, script, bg_path, output_path, music_path=None):
    """合成一条视频: 背景 + 配音 + 字幕 + BGM"""
    duration = _get_audio_duration(audio_path)
    if duration < 3:
        duration = 10.0

    subtitle_vf = _build_subtitle_filter(script)
    bg_path_abs = os.path.abspath(bg_path)
    audio_path_abs = os.path.abspath(audio_path)
    output_path_abs = os.path.abspath(output_path)

    inputs = ["-i", bg_path_abs, "-i", audio_path_abs]

    if music_path and os.path.exists(music_path):
        music_path_abs = os.path.abspath(music_path)
        inputs.extend(["-i", music_path_abs])
        filter_complex = (
            f"[0:v]trim=0:{duration},setpts=PTS-STARTPTS{subtitle_vf}[v];"
            f"[2:a]volume={BGM_VOLUME},atrim=0:{duration},afade=t=out:st={duration-2}:d=2[bgm];"
            f"[1:a][bgm]amix=inputs=2:duration=first[a]"
        )
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            output_path_abs,
        ]
    else:
        filter_complex = f"[0:v]trim=0:{duration},setpts=PTS-STARTPTS{subtitle_vf}[v]"
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            output_path_abs,
        ]

    code, out, err = _run_cmd(cmd)
    if code != 0:
        print(f"  FAIL 合成失败")
        if err:
            err_lines = err.strip().split("\n")
            for line in err_lines[-3:]:
                if "error" in line.lower() or "Error" in line:
                    print(f"     {line.strip()[:200]}")
        return False
    return True


def run_pipeline(topic="emotional", count=10):
    """完整生产流水线"""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = str(OUTPUT_DIR)
    batch_dir = os.path.join(output_dir, f"batch_{topic}_{stamp}")
    os.makedirs(batch_dir, exist_ok=True)

    topic_name = VIDEO_TOPICS.get(topic, {}).get("name", topic)
    print("=" * 50)
    print(f"  短视频生产线")
    print(f"  赛道: {topic_name}  目标: {count} 条")
    print(f"  模型: Ollama (本地)")
    print("=" * 50)

    # 1. 生成文案
    print("\n[1/4] AI 生成文案...")
    scripts = generate_scripts(topic, count)

    # 1.5. 生成标题
    print("\n[2/4] AI 生成标题...")
    titles = generate_titles(scripts, topic)
    print(f"  生成 {len(titles)} 个标题")

    # 2. TTS 配音
    print("\n[3/4] TTS 配音...")
    audio_dir = os.path.join(batch_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    audio_data = tts_batch(scripts, audio_dir)

    # 3. 合成视频
    print("\n[4/4] 合成视频...")
    music = _find_music(topic)
    if music:
        print(f"[BGM] {os.path.basename(music)}")

    success = 0
    metadata_videos = []
    for i, (audio_path, script) in enumerate(audio_data):
        print(f"  [{i+1}/{len(audio_data)}] {script[:30]}", end=" ")
        bg_path = get_or_create_background(batch_dir, i)
        output_path = os.path.join(batch_dir, f"video_{i+1:03d}.mp4")

        if _assemble_one(audio_path, script, bg_path, output_path, music):
            size_mb = os.path.getsize(output_path) / 1024 / 1024
            print(f"OK ({size_mb:.1f}MB)")
            success += 1
            metadata_videos.append({
                "file": f"video_{i+1:03d}.mp4",
                "script": script,
                "title": titles[i] if i < len(titles) else "",
                "description": generate_desc(topic),
            })
        time.sleep(0.3)

    # 保存元数据
    meta_path = os.path.join(batch_dir, "metadata.json")
    metadata = {
        "topic": topic,
        "topic_name": topic_name,
        "generated_at": stamp,
        "videos": metadata_videos,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # 清理临时文件
    import shutil
    shutil.rmtree(audio_dir, ignore_errors=True)
    for f in os.listdir(batch_dir):
        if f.startswith("bg_") and f.endswith(".mp4"):
            os.remove(os.path.join(batch_dir, f))

    print()
    print("=" * 50)
    print(f"  完成! {success}/{len(audio_data)} 条视频")
    print(f"  输出: {batch_dir}")
    print("=" * 50)
    return batch_dir, success
