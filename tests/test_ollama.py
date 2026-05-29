"""验证 Ollama 连接和中文生成"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ollama_connectivity():
    """Ollama 能正常连接并生成中文内容"""
    from src.llm import _call_ollama
    result = _call_ollama(
        system_prompt="你是一个有用的助手。",
        user_prompt="用一句话介绍你自己。",
        temperature=0.5,
        max_tokens=100,
    )
    assert isinstance(result, str), f"Expected string, got {type(result)}"
    assert len(result) > 0, "Empty response"
    print(f"Ollama response: {result[:100]}")

if __name__ == "__main__":
    test_ollama_connectivity()
    print("Ollama test passed!")
