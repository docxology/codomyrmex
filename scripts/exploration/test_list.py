import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

from codomyrmex.agents.gemini.gemini_client import GeminiClient

client = GeminiClient()
models = client.list_models()
veo_models = [m['name'] for m in models if 'veo' in m['name'].lower()]
video_models = [m['name'] for m in models if 'video' in m['name'].lower()]
print("VEO MODELS:", veo_models)
print("VIDEO MODELS:", video_models)
