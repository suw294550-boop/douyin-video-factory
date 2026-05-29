"""
AI 文案和标题生成 - 使用本地 Ollama 模型
"""
import json
import os
import random
import time
from src.config import VIDEO_TOPICS, SCRIPTS_CACHE, TITLE_TEMPLATES, DESC_TEMPLATES, TRENDING_TAGS
from src.llm import call_llm

# 备用文案 - 断网或 Ollama 不可用时使用
FALLBACK_SCRIPTS = {
    "emotional": [
        "有些路只能一个人走，有些话只能说给自己听",
        "成年人的世界，就是把哭声调成静音的过程",
        "你以为是错过，其实是躲过一劫",
        "时间从来不语，却回答了所有问题",
        "生活不是等待暴风雨过去，而是学会在雨中跳舞",
        "你以为的极限，可能只是别人的起点",
        "温柔的一半是知识，另一半是经历",
        "山海自有归期，风雨自有相逢",
        "世界上最美的相遇，是久别重逢",
        "那些杀不死你的，终将使你更强大",
    ],
    "cold_knowledge": [
        "人的胃酸强度足以溶解刀片，但胃黏膜每3天更新一次",
        "考拉的指纹和人类的极其相似，连专家都难区分",
        "闪电的温度是太阳表面的5倍，达到3万摄氏度",
        "蜗牛可以连续睡3年不醒来",
        "人的鼻子可以记住5万种不同的气味",
        "章鱼有3个心脏，血液是蓝色的",
        "蜜蜂的翅膀每分钟可以扇动11400次",
        "企鹅的膝盖藏在羽毛里面看不到",
        "香蕉其实是有辐射的，因为富含钾元素",
        "爱因斯坦小时候说话晚，父母以为他有问题",
    ],
    "motivation": [
        "乾坤未定，你我皆是黑马",
        "半山腰太挤了，去山顶看看吧",
        "你只管努力，剩下的交给时间",
        "今天不想跑，所以才去跑",
        "星光不负赶路人",
        "做自己的太阳，无需凭借谁的光",
        "慢也好，步子小也好，是在往前走就好",
        "所有的惊艳，都来自长久的准备",
        "不逼自己一把，你永远不知道自己有多优秀",
        "你的压力来源于无法自律",
    ],
}


def generate_scripts(topic="emotional", count=10):
    """用本地 LLM 生成短视频文案"""
    topic_config = VIDEO_TOPICS.get(topic, VIDEO_TOPICS["emotional"])
    topic_name = topic_config["name"]
    print(f"[脚本生成] 赛道: {topic_name}, 目标: {count} 条, 模型: Ollama")

    try:
        raw = call_llm(
            system_prompt="你是一个专业的短视频文案写手，输出简洁有力的中文文案。",
            user_prompt=topic_config["prompt"],
            temperature=0.8,
            max_tokens=2000,
        )
        lines = [
            l.strip().lstrip("0123456789.、)） -")
            for l in raw.split("\n") if l.strip()
        ]
        scripts = [l for l in lines if len(l) >= 5][:count]

        # 兜底: 不够用备用填满
        if len(scripts) < count:
            fallback = FALLBACK_SCRIPTS.get(topic, FALLBACK_SCRIPTS["emotional"])
            need = count - len(scripts)
            scripts.extend(fallback[:need])

        # 缓存
        os.makedirs(str(SCRIPTS_CACHE), exist_ok=True)
        cache_file = str(SCRIPTS_CACHE / f"{topic}_{int(time.time())}.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(scripts, f, ensure_ascii=False, indent=2)

        print(f"[脚本生成] 成功 {len(scripts)} 条")
        return scripts[:count]

    except Exception as e:
        print(f"[脚本生成] Ollama 调用失败: {e}")
        fallback = FALLBACK_SCRIPTS.get(topic, FALLBACK_SCRIPTS["emotional"])
        scripts = fallback[:count]
        print(f"[脚本生成] 使用备用文案 {len(scripts)} 条")
        return scripts


def generate_titles(scripts, topic):
    """用 LLM 为每条视频生成吸引人的标题"""
    topic_name = VIDEO_TOPICS.get(topic, {}).get("name", topic)
    prompts_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(scripts)])

    try:
        raw = call_llm(
            system_prompt="你是一个抖音爆款标题写手。每条视频文案配一个吸引人的标题，5-12个字，有情绪和好奇心。输出格式：每行一个标题，不要编号，不要任何解释。",
            user_prompt=f"为以下{topic_name}短视频文案写标题：\n\n{prompts_text}",
            temperature=0.8,
            max_tokens=800,
        )
        titles = [
            l.strip().lstrip("0123456789.、)） -")
            for l in raw.split("\n") if l.strip()
        ]
        while len(titles) < len(scripts):
            templates = TITLE_TEMPLATES.get(topic, TITLE_TEMPLATES["emotional"])
            titles.append(templates[len(titles) % len(templates)])
        return titles[:len(scripts)]
    except Exception:
        templates = TITLE_TEMPLATES.get(topic, TITLE_TEMPLATES["emotional"])
        return [templates[i % len(templates)] for i in range(len(scripts))]


def generate_desc(topic):
    """生成一条视频描述（含随机热门标签）"""
    templates = DESC_TEMPLATES.get(topic, DESC_TEMPLATES["emotional"])
    desc = random.choice(templates)
    all_tags = TRENDING_TAGS.get(topic, [])
    extra_tags = random.sample(all_tags, min(3, len(all_tags)))
    return desc + " " + " ".join(extra_tags)
