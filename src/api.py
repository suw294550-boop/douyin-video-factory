"""
REST API - Flask 路由，封装 pipeline/uploader/config 模块
"""
import os
import re
import json
import glob
import time
import threading
import requests
from flask import Blueprint, jsonify, request, Response

from src.config import (
    PROJECT_ROOT, OUTPUT_DIR, OLLAMA_BASE_URL, OLLAMA_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, VIDEO_TOPICS,
    BROWSER_PROFILE, COOKIE_FILE,
)

api = Blueprint("api", __name__)

# 后台任务状态
_jobs = {}
_lock = threading.Lock()


def _get_job(job_id):
    with _lock:
        return _jobs.get(job_id, {})


def _update_job(job_id, **kwargs):
    with _lock:
        if job_id not in _jobs:
            _jobs[job_id] = {}
        _jobs[job_id].update(kwargs)


# ── 系统状态 ──

@api.route("/api/status")
def get_status():
    logged_in = os.path.exists(str(COOKIE_FILE)) or os.path.exists(str(BROWSER_PROFILE))
    return jsonify({
        "model": OLLAMA_MODEL,
        "logged_in": logged_in,
        "ollama_url": OLLAMA_BASE_URL,
    })


# ── 模型管理 ──

@api.route("/api/models")
def list_models():
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        models = ["qwen3:8b (Ollama 未连接)"]
    return jsonify({"models": models, "current": OLLAMA_MODEL})


@api.route("/api/models/switch", methods=["POST"])
def switch_model():
    data = request.get_json()
    model = data.get("model", "")
    if not model:
        return jsonify({"ok": False, "error": "model is required"}), 400

    # 写入 .env
    env_path = PROJECT_ROOT / ".env"
    lines = []
    if os.path.exists(str(env_path)):
        with open(str(env_path), encoding="utf-8") as f:
            lines = f.read().split("\n")
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("OLLAMA_MODEL="):
            new_lines.append(f"OLLAMA_MODEL={model}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"OLLAMA_MODEL={model}")
    with open(str(env_path), "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    # 运行时更新
    import src.config
    src.config.OLLAMA_MODEL = model

    return jsonify({"ok": True, "model": model})


# ── 生产 ──

@api.route("/api/produce", methods=["POST"])
def start_produce():
    data = request.get_json()
    topics = data.get("topics", [{"topic": "emotional", "count": 3}])

    job_id = f"produce_{int(time.time())}"
    _update_job(job_id, status="running", progress=0, log="", topics=topics)

    def _run():
        from src.pipeline import run_pipeline
        total = 0
        results = []
        for i, t in enumerate(topics):
            topic = t.get("topic", "emotional")
            count = int(t.get("count", 3))
            _update_job(job_id, log=f"[{i+1}/{len(topics)}] {topic} x{count} ...", progress=int(100 * i / len(topics)))
            try:
                batch_dir, ok = run_pipeline(topic, count)
                total += ok
                results.append({"topic": topic, "count": ok, "dir": batch_dir})
            except Exception as e:
                _update_job(job_id, log=f"错误: {e}", status="error")
                return
        _update_job(job_id, status="done", progress=100, log=f"完成 {total} 条", results=results, total=total)

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    return jsonify({"ok": True, "job_id": job_id})


@api.route("/api/produce/status/<job_id>")
def produce_status(job_id):
    job = _get_job(job_id)
    if not job:
        return jsonify({"status": "not_found"}), 404
    return jsonify(job)


# ── 发布 ──

@api.route("/api/batches")
def list_batches():
    od = str(OUTPUT_DIR)
    if not os.path.exists(od):
        return jsonify({"batches": []})

    batches = []
    for d in sorted(os.listdir(od), reverse=True):
        full = os.path.join(od, d)
        if not os.path.isdir(full):
            continue
        meta_path = os.path.join(full, "metadata.json")
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        videos = sorted(glob.glob(os.path.join(full, "video_*.mp4")))
        batches.append({
            "dir": d,
            "topic": meta.get("topic_name", "未知"),
            "count": len(videos),
            "generated": meta.get("generated_at", ""),
            "videos": meta.get("videos", []),
        })
    return jsonify({"batches": batches[:20]})


@api.route("/api/publish", methods=["POST"])
def start_publish():
    data = request.get_json()
    batch_dir_name = data.get("dir", "")
    if not batch_dir_name:
        return jsonify({"ok": False, "error": "dir is required"}), 400

    batch_dir = str(OUTPUT_DIR / batch_dir_name)
    if not os.path.exists(batch_dir):
        return jsonify({"ok": False, "error": "batch not found"}), 404

    job_id = f"publish_{int(time.time())}"
    _update_job(job_id, status="running", progress=0, log="", batch=batch_dir_name)

    def _run():
        from src.uploader import publish_batch
        import asyncio
        meta_path = os.path.join(batch_dir, "metadata.json")
        topic_name = "短视频"
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
                topic_name = meta.get("topic_name", "短视频")
        _update_job(job_id, log=f"开始发布 {topic_name} ...")
        try:
            n = asyncio.run(publish_batch(batch_dir, topic_name))
            _update_job(job_id, status="done", progress=100, log=f"发布完成 {n} 条", total=n)
        except Exception as e:
            _update_job(job_id, log=f"错误: {e}", status="error")

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    return jsonify({"ok": True, "job_id": job_id})


@api.route("/api/publish/status/<job_id>")
def publish_status(job_id):
    job = _get_job(job_id)
    if not job:
        return jsonify({"status": "not_found"}), 404
    return jsonify(job)


# ── 定时调度 ──

SCHEDULE_FILE = PROJECT_ROOT / "schedule.json"


def _load_schedule():
    if os.path.exists(str(SCHEDULE_FILE)):
        with open(str(SCHEDULE_FILE), encoding="utf-8") as f:
            return json.load(f)
    return {"enabled": False, "time": "09:50", "auto_publish": True, "topics": [
        {"topic": "emotional", "count": 3},
        {"topic": "cold_knowledge", "count": 3},
        {"topic": "motivation", "count": 3},
    ]}


def _save_schedule(data):
    with open(str(SCHEDULE_FILE), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@api.route("/api/schedule")
def get_schedule():
    return jsonify(_load_schedule())


@api.route("/api/schedule", methods=["POST"])
def set_schedule():
    data = request.get_json()
    _save_schedule(data)
    return jsonify({"ok": True})


# ── 登录 ──

@api.route("/api/login", methods=["POST"])
def start_login():
    job_id = f"login_{int(time.time())}"
    _update_job(job_id, status="running", log="请在浏览器弹出的窗口中扫码...")

    def _run():
        from src.uploader import login_only
        try:
            login_only()
            _update_job(job_id, status="done", log="登录完成")
        except Exception as e:
            _update_job(job_id, log=f"登录失败: {e}", status="error")

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    return jsonify({"ok": True, "job_id": job_id})


@api.route("/api/login/status/<job_id>")
def login_status(job_id):
    job = _get_job(job_id)
    if not job:
        return jsonify({"status": "not_found"}), 404
    return jsonify(job)
