import os

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("all_models.txt", "w") as f:
    try:
        f.writelines(f"{m.name}\n" for m in client.models.list())
    except Exception as e:
        f.write(f"Error: {e}\n")
