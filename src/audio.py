"""
TTS 语音合成 - 使用 Microsoft Edge TTS (免费)
"""
import asyncio
import os
from src.config import TTS_VOICE, TTS_RATE, TTS_PITCH


async def _generate(script, output_path):
    import edge_tts
    communicate = edge_tts.Communicate(
        text=script, voice=TTS_VOICE, rate=TTS_RATE, pitch=TTS_PITCH
    )
    await communicate.save(output_path)
    return output_path


def tts_single(script, output_path):
    return asyncio.run(_generate(script, output_path))


def tts_batch(scripts, output_dir):
    audio_files = []
    for i, script in enumerate(scripts):
        mp3_path = os.path.join(output_dir, f"audio_{i:03d}.mp3")
        print(f"[TTS] {i+1}/{len(scripts)}: {script[:20]}...")
        try:
            tts_single(script, mp3_path)
            audio_files.append((mp3_path, script))
        except Exception as e:
            print(f"[TTS] 失败: {e}")
    return audio_files
