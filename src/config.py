"""
统一配置 - 基于项目根目录的相对路径
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录 = 本文件向上两级
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# === LLM 配置 ===
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# === 路径 ===
OUTPUT_DIR = PROJECT_ROOT / "output"
BACKGROUND_DIR = PROJECT_ROOT / "backgrounds"
MUSIC_DIR = PROJECT_ROOT / "music"
SCRIPTS_CACHE = PROJECT_ROOT / "scripts_cache"
BROWSER_PROFILE = PROJECT_ROOT / "browser_profile"
COOKIE_FILE = PROJECT_ROOT / "douyin_cookies.json"
TRACKER_FILE = PROJECT_ROOT / "publish_log.json"
DAILY_LOG_FILE = PROJECT_ROOT / "daily_log.txt"
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

# === 视频参数 ===
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
VIDEO_DURATION_MIN = 30
VIDEO_DURATION_MAX = 60

# === 字幕参数 ===
FONT_SIZE = 52
FONT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 3
SUBTITLE_MAX_CHARS_PER_LINE = 18

# === TTS ===
TTS_VOICE = "zh-CN-XiaoxiaoNeural"
TTS_RATE = "+10%"
TTS_PITCH = "+0Hz"

# === 背景音乐 ===
BGM_MAP = {
    "emotional": "healing_piano.mp3",
    "cold_knowledge": "ambient_pad.mp3",
    "motivation": "light_rhythm.mp3",
    "book_review": "healing_piano.mp3",
}
BGM_VOLUME = 0.10

# === 视频赛道 ===
VIDEO_TOPICS = {
    "emotional": {
        "name": "情感语录",
        "prompt": """你是一个情感类短视频文案写手。请生成10条情感语录短视频文案。
每条文案要求：
- 15-25个字
- 温暖治愈或扎心共鸣
- 适合配风景/城市延时背景
- 不要网络烂梗
- 每行一条，不要编号
- 纯中文，不要任何标点符号外的特殊字符
- 直接输出文案，不要任何解释""",
    },
    "cold_knowledge": {
        "name": "冷知识",
        "prompt": """你是一个科普短视频文案写手。请生成10条有趣的冷知识短视频文案。
每条文案要求：
- 15-30个字
- 出人意料但真实的知识
- 适合图文展示
- 每行一条，不要编号
- 纯中文
- 直接输出文案，不要任何解释""",
    },
    "book_review": {
        "name": "书摘推荐",
        "prompt": """你是一个读书博主。请生成10条好书推荐/书摘短视频文案。
每条文案要求：
- 15-25个字
- 来自经典书籍的金句或感悟
- 标注书名
- 每行一条
- 纯中文
- 直接输出文案，不要任何解释""",
    },
    "motivation": {
        "name": "励志语录",
        "prompt": """你是一个励志文案写手。请生成10条励志短视频文案。
每条文案要求：
- 10-20个字
- 简短有力、适合作为手机壁纸的文字
- 积极向上但不鸡汤
- 每行一条
- 纯中文
- 直接输出文案，不要任何解释""",
    },
}

# === 标题模板 ===
TITLE_TEMPLATES = {
    "emotional": [
        "这句话说到心坎里了",
        "多少人看哭了",
        "成年人的世界没有容易二字",
        "听完这段话我沉默了",
        "说中了多少人的心事",
        "深夜emo的时候看看这段话",
        "有些话只能说给自己听",
        "懂的人自然懂",
        "听完你会释怀很多",
        "致所有在深夜里崩溃过的人",
        "这世界总有人偷偷爱着你",
        "希望这条视频能治愈你",
    ],
    "cold_knowledge": [
        "99%的人都不知道的冷知识",
        "这个冷知识太颠覆了",
        "活了这么多年才知道",
        "长知识了！转给朋友看",
        "第3个真的没想到",
        "颠覆认知的冷知识",
        "学到就是赚到",
        "原来这么多年都理解错了",
        "让人惊掉下巴的知识点",
    ],
    "book_review": [
        "这本书改变了我的一生",
        "值得反复读的一本书",
        "书里最戳我的一句话",
        "豆瓣高分神作推荐",
        "读完后久久不能平静",
        "后悔没早点读到这本书",
        "这本书治好了我的精神内耗",
        "强烈推荐给所有人",
    ],
    "motivation": [
        "这句话支撑我走了很长的路",
        "送给正在努力变好的你",
        "别放弃，再坚持一下",
        "今天也要加油呀",
        "刷到就是在提醒你",
        "你不努力谁也给不了你想要的生活",
        "收藏起来，emo的时候看",
        "30秒打满鸡血",
        "致每一个不甘平庸的你",
    ],
}

# === 描述模板 ===
DESC_TEMPLATES = {
    "emotional": [
        "有些话只说给懂的人听\n你最近过得好吗？评论区说说吧\n#情感语录 #深夜文案 #治愈系 #生活感悟 #扎心语录",
        "这个世界没那么糟，总有人偷偷爱着你\n#情感语录 #暖心文案 #治愈 #成年人的崩溃 #共鸣",
    ],
    "cold_knowledge": [
        "每天一个冷知识，让你成为人群中最有趣的人\n你还知道哪些冷知识？评论区分享\n#冷知识 #涨知识 #科普 #有趣 #知识点",
        "涨知识了！收藏起来以后用\n关注我，每天更新冷知识~ #冷知识 #科普 #涨知识 #冷门知识 #每天学习一点点",
    ],
    "book_review": [
        "书中自有黄金屋\n你最近在读什么书？评论区推荐给我\n#好书推荐 #书摘 #读书笔记 #阅读 #每日读书",
        "每天推荐一本好书，陪你一起阅读成长\n#书摘 #好书推荐 #读书 #阅读打卡 #精神食粮",
    ],
    "motivation": [
        "星光不负赶路人\n你正在为什么而努力？评论区告诉我\n#励志 #正能量 #努力变好 #自律 #成长",
        "别让未来的你，讨厌现在的自己\n关注我，每天给你一点力量~ #励志语录 #正能量 #努力 #奋斗 #成为更好的自己",
    ],
}

# === 热门标签 ===
TRENDING_TAGS = {
    "emotional": ["#情感语录", "#深夜文案", "#治愈系", "#扎心语录", "#共鸣", "#成年人的世界",
                   "#情感共鸣", "#emo文案", "#走心文案", "#晚安语录"],
    "cold_knowledge": ["#冷知识", "#涨知识", "#科普", "#有趣冷知识", "#冷门知识",
                       "#每日知识", "#学到了", "#知识分享", "#万物知识", "#趣味科普"],
    "book_review": ["#好书推荐", "#书摘", "#读书笔记", "#阅读", "#每日读书",
                    "#书单", "#推荐书单", "#读书人", "#阅读分享", "#书籍推荐"],
    "motivation": ["#励志", "#正能量", "#努力变好", "#自律", "#成长",
                   "#加油", "#梦想", "#人生感悟", "#奋斗", "#成为更好的自己"],
}
