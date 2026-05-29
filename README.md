# Douyin Video Factory

全自动抖音短视频生产线 — AI 写文案 → TTS 配音 → ffmpeg 合成 → 浏览器自动发布。

**零 API 费用**，全部使用本地 Ollama 模型 + 开源工具。

## 功能

- **AI 文案生成** — 本地 Ollama (qwen3:8b) 自动生成情感语录/冷知识/励志语录/书摘文案
- **智能标题** — 每条视频自动配吸引人的标题和热门标签
- **TTS 配音** — Microsoft Edge TTS (免费)
- **视频合成** — ffmpeg 字幕渲染 + 无版权 BGM 混音
- **自动发布** — Playwright 浏览器自动化发布到抖音创作者平台
- **持久化登录** — 扫码一次，长期有效

## 环境要求

- Windows 10/11 + Python 3.10+
- [ffmpeg](https://ffmpeg.org/download.html) (需在 PATH 中)
- [Ollama](https://ollama.com/) 运行中 + qwen3:8b 模型
- 抖音创作者账号

## 快速开始

```bash
# 1. 克隆
git clone <repo-url> douyin-video-factory
cd douyin-video-factory

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 拉取本地模型 (5.2GB, 仅首次)
ollama pull qwen3:8b

# 4. 生成 BGM 库
python scripts/generate_bgm.py

# 5. 登录抖音 (打开浏览器扫码)
python run.py login

# 6. 生产 + 发布
python run.py all
```

或双击 `batch/setup.bat` 一键安装，再双击 `batch/login.bat` 登录。

## 使用方法

```bash
# 生产视频
python run.py produce --topic emotional --count 10    # 单赛道
python run.py produce --all                            # 全部赛道

# 发布视频
python run.py publish --latest                         # 发布最新批次
python run.py publish --dir output/batch_xxx           # 发布指定批次

# 一键全流程
python run.py all

# 查看统计
python run.py report
```

## 赛道说明

| 赛道 | 说明 | 时长 |
|------|------|------|
| `emotional` | 情感语录 | 15-25字/条 |
| `cold_knowledge` | 冷知识科普 | 15-30字/条 |
| `motivation` | 励志语录 | 10-20字/条 |
| `book_review` | 书摘推荐 | 15-25字/条 |

## 配置

复制 `.env.example` 为 `.env` 可按需修改：

```bash
# 默认使用 Ollama
OLLAMA_MODEL=qwen3:8b

# 可选: 使用 DeepSeek API (设置后自动切换)
# DEEPSEEK_API_KEY=sk-your-key
```

`src/config.py` 中可调整视频参数、字幕样式、TTS 音色等。

## 项目结构

```
douyin-video-factory/
├── src/                    # Python 包
│   ├── config.py           # 配置 (相对路径, .env)
│   ├── llm.py              # LLM 抽象 (Ollama/DeepSeek)
│   ├── scripts_gen.py      # 文案+标题生成
│   ├── pipeline.py         # 视频合成流水线
│   ├── audio.py            # TTS 语音合成
│   ├── background.py       # 背景视频生成
│   ├── music.py            # 无版权 BGM 生成
│   ├── uploader.py         # 抖音自动发布
│   └── tracker.py          # 发布统计
├── scripts/                # 工具脚本
├── batch/                  # Windows 批处理
├── run.py                  # CLI 入口
└── README.md
```

## Ollama 模型推荐

| 模型 | 显存 | 中文质量 |
|------|------|----------|
| `qwen3:8b` | ~6GB | 优秀 (推荐) |
| `deepseek-r1:8b` | ~6GB | 优秀 (推理强) |
| `llama3.1:8b` | ~6GB | 中等 |

RTX 4060 8GB 可以流畅运行以上所有模型。

## License

MIT
