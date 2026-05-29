"""
LLM 抽象层 - 默认使用本地 Ollama，可选 DeepSeek 兜底
"""
import sys
from src.config import (
    LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
)


def call_llm(system_prompt, user_prompt, temperature=0.8, max_tokens=2000):
    """
    统一 LLM 调用接口。
    默认走 Ollama 本地模型，设置 DEEPSEEK_API_KEY 环境变量后自动切 DeepSeek。
    """
    if LLM_PROVIDER == "deepseek" and DEEPSEEK_API_KEY:
        return _call_deepseek(system_prompt, user_prompt, temperature, max_tokens)
    return _call_ollama(system_prompt, user_prompt, temperature, max_tokens)


def _call_ollama(system_prompt, user_prompt, temperature, max_tokens):
    import requests
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


def _call_deepseek(system_prompt, user_prompt, temperature, max_tokens):
    import requests
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers=headers, json=payload, timeout=OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
