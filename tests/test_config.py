"""验证配置加载"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_project_root():
    from src.config import PROJECT_ROOT
    assert PROJECT_ROOT.exists(), f"Root not found: {PROJECT_ROOT}"

def test_output_dir():
    from src.config import OUTPUT_DIR
    assert "output" in str(OUTPUT_DIR)

def test_default_model():
    from src.config import OLLAMA_MODEL
    assert OLLAMA_MODEL in ("qwen3:8b", "deepseek-r1:8b", "llama3.1:8b")

def test_video_topics():
    from src.config import VIDEO_TOPICS
    assert len(VIDEO_TOPICS) >= 4
    assert "emotional" in VIDEO_TOPICS

if __name__ == "__main__":
    test_project_root()
    test_output_dir()
    test_default_model()
    test_video_topics()
    print("All config tests passed!")
