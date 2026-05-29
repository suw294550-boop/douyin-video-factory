#!/usr/bin/env python3
"""
抖音短视频工厂 - CLI 入口
    python run.py produce --topic emotional --count 10
    python run.py produce --all
    python run.py publish --dir output/batch_xxx
    python run.py publish --latest
    python run.py login
    python run.py all
    python run.py report
"""
import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_produce(args):
    """生产视频"""
    from src.pipeline import run_pipeline

    if hasattr(args, "all") and args.all:
        topics = [
            ("emotional", 5, "情感语录"),
            ("cold_knowledge", 5, "冷知识"),
            ("motivation", 5, "励志语录"),
        ]
        total = 0
        for topic, count, name in topics:
            print(f"\n>>> 生产 {name} x{count}")
            _, ok = run_pipeline(topic, count)
            total += ok
        print(f"\n全部完成! 共 {total} 条视频")
        return

    topic = getattr(args, "topic", "emotional")
    count = int(getattr(args, "count", 10))
    run_pipeline(topic, count)


def cmd_publish(args):
    """发布视频"""
    from src.uploader import publish_batch
    import asyncio

    if hasattr(args, "dir") and args.dir:
        video_dir = args.dir
        topic = getattr(args, "topic", "短视频")
    elif hasattr(args, "latest") and args.latest:
        from src.config import OUTPUT_DIR
        output_dir = str(OUTPUT_DIR)
        dirs = sorted([
            d for d in os.listdir(output_dir)
            if os.path.isdir(os.path.join(output_dir, d))
        ])
        if not dirs:
            print("没有找到视频目录")
            return
        video_dir = os.path.join(output_dir, dirs[-1])
        topic_map = {
            "emotional": "情感语录", "cold_knowledge": "冷知识",
            "motivation": "励志语录", "book_review": "书摘推荐",
        }
        topic = "短视频"
        for k, v in topic_map.items():
            if k in dirs[-1]:
                topic = v
                break
    else:
        print("请指定 --dir <目录> 或 --latest")
        return

    n = asyncio.run(publish_batch(video_dir, topic))
    print(f"\n发布完成: {n} 条")


def cmd_login(_args):
    """扫码登录"""
    from src.uploader import login_only
    login_only()


def cmd_all(_args):
    """生产 + 发布全流程"""
    from src.pipeline import run_pipeline
    from src.uploader import publish_batch
    import asyncio

    topics = [
        ("emotional", 3, "情感语录"),
        ("cold_knowledge", 3, "冷知识"),
        ("motivation", 3, "励志语录"),
    ]
    batch_dirs = []
    total = 0

    print("\n" + "=" * 50)
    print("  一键全流程: 生产 + 发布")
    print("=" * 50)

    for topic, count, name in topics:
        print(f"\n>>> {name} x{count}")
        batch_dir, ok = run_pipeline(topic, count)
        batch_dirs.append(batch_dir)
        total += ok

    print(f"\n生产完成: {total} 条\n")

    published = 0
    for batch_dir in batch_dirs:
        n = asyncio.run(publish_batch(batch_dir))
        published += n

    print(f"\n{'=' * 50}")
    print(f"  全流程完成! 生产: {total} | 发布: {published}")
    print(f"{'=' * 50}")


def cmd_report(_args):
    """查看发布统计"""
    from src.tracker import report
    report()


def cmd_ui(_args):
    """启动 Web 控制面板"""
    from src.web import run_ui
    run_ui()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="抖音短视频工厂")
    sub = parser.add_subparsers(dest="command", help="命令")

    p = sub.add_parser("produce", help="生产视频")
    p.add_argument("--topic", default="emotional",
                   choices=["emotional", "cold_knowledge", "book_review", "motivation"])
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--all", action="store_true")

    p = sub.add_parser("publish", help="发布视频")
    p.add_argument("--dir", type=str)
    p.add_argument("--topic", type=str, default="短视频")
    p.add_argument("--latest", action="store_true")

    sub.add_parser("login", help="扫码登录抖音")
    sub.add_parser("all", help="生产+发布全流程")
    sub.add_parser("report", help="查看发布统计")
    sub.add_parser("ui", help="启动 Web 控制面板")

    args = parser.parse_args()

    if args.command == "produce":
        cmd_produce(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "login":
        cmd_login(args)
    elif args.command == "all":
        cmd_all(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "ui":
        cmd_ui(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
