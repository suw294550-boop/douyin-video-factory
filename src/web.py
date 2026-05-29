"""
Flask Web UI - 本地控制面板
"""
import os
import sys
import webbrowser
import threading
from flask import Flask, render_template

from src.api import api


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))
    app.register_blueprint(api)
    return app


def run_ui():
    app = create_app()

    @app.route("/")
    def index():
        return render_template("index.html")

    # 延迟打开浏览器
    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")

    threading.Timer(1.0, open_browser).start()

    print("\n  控制面板: http://127.0.0.1:5000")
    print("  按 Ctrl+C 退出\n")

    app.run(host="127.0.0.1", port=5000, debug=False)
