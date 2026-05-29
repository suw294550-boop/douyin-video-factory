"""
发布追踪器 - 记录已发布的视频
"""
import json
import os
import time
from src.config import TRACKER_FILE


def load_log():
    if os.path.exists(str(TRACKER_FILE)):
        with open(str(TRACKER_FILE), "r", encoding="utf-8") as f:
            return json.load(f)
    return {"published": [], "stats": {"total": 0, "last_run": ""}}


def save_log(log):
    with open(str(TRACKER_FILE), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def mark_published(video_file, topic, title):
    log = load_log()
    log["published"].append({
        "file": video_file,
        "topic": topic,
        "title": title,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    log["stats"]["total"] += 1
    log["stats"]["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_log(log)


def get_stats():
    log = load_log()
    return log["stats"]


def report():
    log = load_log()
    stats = log["stats"]
    print(f"总发布: {stats['total']} 条")
    print(f"最近发布: {stats.get('last_run', 'N/A')}")
    recent = log["published"][-10:]
    if recent:
        print("\n最近10条:")
        for r in recent:
            print(f"  [{r['time']}] {r['topic']} - {r['title'][:30]}")
