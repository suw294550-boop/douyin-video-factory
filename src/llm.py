"""
LLM 抽象层 - 本地 Ollama（免费）
"""
import requests
import sys
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


def call_llm(system_prompt, user_prompt, temperature=0.8, max_tokens=2000):
    """调用本地 Ollama 模型"""
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[Ollama] 调用失败: {e}", file=sys.stderr)
        print("[Ollama] 请确认 Ollama 正在运行: ollama serve", file=sys.stderr)
        raise
