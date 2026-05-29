"""
抖音创作者平台自动发布 - Playwright 浏览器自动化
"""
import os
import json
import glob
import asyncio
from src.config import BROWSER_PROFILE, COOKIE_FILE

UPLOAD_URL = "https://creator.douyin.com/creator-micro/content/upload"


def load_metadata(video_dir):
    meta_path = os.path.join(video_dir, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


async def _save_cookies(context):
    cookies = await context.cookies()
    with open(str(COOKIE_FILE), "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


async def _load_cookies(context):
    if not os.path.exists(str(COOKIE_FILE)):
        return False
    with open(str(COOKIE_FILE), "r", encoding="utf-8") as f:
        cookies = json.load(f)
    await context.add_cookies(cookies)
    return True


async def login_douyin(page):
    """扫码登录抖音创作者平台"""
    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║  请用抖音 APP 扫描浏览器二维码  ║")
    print("  ╚══════════════════════════════════╝")
    print()

    await page.goto("https://creator.douyin.com/login", wait_until="domcontentloaded")
    await asyncio.sleep(5)

    if "login" not in page.url.lower():
        print("[Login] 已有登录态, 跳过扫码")
        return True

    for i in range(300):
        await asyncio.sleep(1)
        if "login" not in page.url.lower() and "creator.douyin.com" in page.url:
            print("[Login] 扫码成功!")
            return True
        if i == 10:
            print("  >>> 请在浏览器窗口中扫码 <<<")
        if i > 30 and i % 30 == 0:
            print(f"  等待中... ({i}秒)")

    print("[Login] 扫码超时")
    return False


async def upload_one(page, video_path, title, description=""):
    """上传并发布一条视频"""
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        print(f"  [X] 文件不存在: {video_path}")
        return False

    try:
        await page.goto(UPLOAD_URL, wait_until="domcontentloaded")
        await asyncio.sleep(5)

        # 上传视频文件
        file_input = page.locator('input[type="file"]').first
        if await file_input.count() == 0:
            print("  [X] 找不到上传入口")
            return False

        await file_input.set_input_files(video_path)
        print("  上传中...")

        # 等待编辑页加载
        title_input = None
        for _ in range(80):
            await asyncio.sleep(2)
            title_input = page.locator('[placeholder*="标题"]').first
            if await title_input.count() > 0:
                break

        if not title_input or await title_input.count() == 0:
            print("  [X] 编辑页未加载")
            return False

        # 填标题
        await asyncio.sleep(2)
        await title_input.click()
        await asyncio.sleep(0.3)
        await title_input.fill("")
        await asyncio.sleep(0.3)
        await title_input.type(title[:55], delay=20)
        print(f"  标题: {title[:40]}")

        # 填描述
        if description:
            await asyncio.sleep(1)
            try:
                desc_sel = page.locator('[placeholder*="描述"]').first
                if await desc_sel.count() == 0:
                    if await page.locator("textarea").count() > 1:
                        desc_sel = page.locator("textarea").nth(1)
                if await desc_sel.count() > 0:
                    await desc_sel.click()
                    await asyncio.sleep(0.3)
                    await desc_sel.fill(description[:500])
                    print("  描述已填写")
            except Exception:
                pass

        await asyncio.sleep(2)

        # 点击发布
        published = False
        all_btns = page.locator("button")
        for idx in range(await all_btns.count()):
            try:
                btn = all_btns.nth(idx)
                text = (await btn.text_content() or "").strip()
                if "发布" in text and "视频" not in text:
                    await btn.click()
                    published = True
                    break
            except Exception:
                continue

        if not published:
            pub_btn = page.locator('button:has-text("发布")').first
            if await pub_btn.count() > 0:
                await pub_btn.click()
                published = True

        await asyncio.sleep(5)
        return published

    except Exception as e:
        print(f"  [异常] {e}")
        return False


async def publish_batch(video_dir, topic_name=""):
    """发布一个目录下的所有视频"""
    if not os.path.exists(video_dir):
        print(f"目录不存在: {video_dir}")
        return 0

    videos = sorted(glob.glob(os.path.join(video_dir, "video_*.mp4")))
    if not videos:
        print(f"无视频文件: {video_dir}")
        return 0

    # 加载元数据
    metadata = load_metadata(video_dir)
    video_meta = {}
    if metadata:
        for v in metadata.get("videos", []):
            video_meta[v["file"]] = v
        topic_name = topic_name or metadata.get("topic_name", "短视频")
        print(f"[元数据] 加载 {len(video_meta)} 条视频信息")
    topic_name = topic_name or "短视频"

    print(f"\n[批量发布] {topic_name} - {len(videos)} 条视频")
    os.makedirs(str(BROWSER_PROFILE), exist_ok=True)

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE),
            headless=False,
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            args=["--disable-blink-features=AutomationControlled", "--no-first-run"],
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        # 检查登录态
        await page.goto(UPLOAD_URL, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        if "login" in page.url.lower():
            if not await login_douyin(page):
                await browser.close()
                return 0
            await _save_cookies(browser)

        success = 0
        for i, video in enumerate(videos):
            fname = os.path.basename(video)
            meta = video_meta.get(fname, {})
            title = meta.get("title", f"#{topic_name}")
            desc = meta.get("description", f"关注我，每天更新~ #{topic_name}")

            print(f"\n[{i+1}/{len(videos)}] {title[:30]}")
            if await upload_one(page, video, title, desc):
                print(f"  OK 发布成功")
                success += 1
            else:
                print(f"  FAIL 发布失败")

            if i < len(videos) - 1:
                wait = 60 + (i % 3) * 15
                for s in range(wait, 0, -5):
                    print(f"  下一条等待 {s} 秒...", end="\r")
                    await asyncio.sleep(5)
                print(" " * 30, end="\r")

        await _save_cookies(browser)
        await browser.close()
        return success


def login_only():
    """独立登录功能"""
    async def _login():
        # 清除旧登录态
        if os.path.exists(str(COOKIE_FILE)):
            os.remove(str(COOKIE_FILE))
        import shutil
        if os.path.exists(str(BROWSER_PROFILE)):
            shutil.rmtree(str(BROWSER_PROFILE), ignore_errors=True)
        os.makedirs(str(BROWSER_PROFILE), exist_ok=True)

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE),
                headless=False,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                args=["--disable-blink-features=AutomationControlled", "--no-first-run"],
            )
            page = browser.pages[0] if browser.pages else await browser.new_page()
            ok = await login_douyin(page)
            if ok:
                await _save_cookies(browser)
            await browser.close()

    asyncio.run(_login())
