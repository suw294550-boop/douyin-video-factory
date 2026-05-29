"""
Flask Web UI - 本地控制面板 + 后台定时调度
"""
import os
import sys
import time
import json
import webbrowser
import threading
import subprocess
from flask import Flask, render_template

from src.api import api


def _scheduler_loop():
    """后台线程：每分钟检查一次定时任务"""
    schedule_file = "D:/桌面/short-video-factory/schedule.json"
    last_run_date = ""

    while True:
        time.sleep(60)
        try:
            if not os.path.exists(schedule_file):
                continue
            with open(schedule_file, encoding="utf-8") as f:
                sched = json.load(f)
            if not sched.get("enabled"):
                continue

            now = time.strftime("%H:%M")
            today = time.strftime("%Y%m%d")
            if now == sched.get("time", "09:50") and today != last_run_date:
                last_run_date = today
                print(f"\n[Scheduler] Running scheduled task: {now}")
                topics = sched.get("topics", [{"topic": "emotional", "count": 3}])
                py = sys.executable
                script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "run.py")
                for t in topics:
                    topic = t.get("topic", "emotional")
                    count = int(t.get("count", 3))
                    subprocess.Popen(
                        [py, script, "produce", "--topic", topic, "--count", str(count)],
                        cwd=os.path.dirname(os.path.dirname(__file__)),
                    ).wait()
                if sched.get("auto_publish"):
                    latest_dir = max(
                        [d for d in os.listdir("D:/桌面/short-video-factory/output")
                         if os.path.isdir(os.path.join("D:/桌面/short-video-factory/output", d))],
                        key=lambda d: os.path.getmtime(os.path.join("D:/桌面/short-video-factory/output", d))
                    )
                    subprocess.Popen(
                        [py, script, "publish", "--dir", os.path.join("D:/桌面/short-video-factory/output", latest_dir)],
                        cwd=os.path.dirname(os.path.dirname(__file__)),
                    ).wait()
                print(f"[Scheduler] Task complete")
        except Exception as e:
            print(f"[Scheduler] Error: {e}")


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))
    app.register_blueprint(api)
    return app


def run_ui():
    app = create_app()

    @app.route("/")
    def index():
        return render_template("index.html")

    # 启动后台调度线程
    threading.Thread(target=_scheduler_loop, daemon=True).start()
    print("[Scheduler] Background scheduler started")

    # 延迟打开浏览器
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")

    threading.Timer(1.0, open_browser).start()

    print("\n  控制面板: http://127.0.0.1:5000")
    print("  按 Ctrl+C 退出\n")

    app.run(host="127.0.0.1", port=5000, debug=False)
