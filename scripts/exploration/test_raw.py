import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))
from codomyrmex.agents.gemini.gemini_client import GeminiClient

client = GeminiClient()
models = client.list_models()
for m in models:
    if "veo" in m.get("name", "").lower() or "video" in m.get("name", "").lower():
        print(m.get("name"))
