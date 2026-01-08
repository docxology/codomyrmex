"""Verification script for Gemini API Integration."""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import os
import sys
import logging
from typing import Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from codomyrmex.agents.gemini.gemini_client import GeminiClient
from codomyrmex.agents.core import AgentRequest

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VERIFY")

def print_result(step: str, success: bool, details: Any = ""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {step}")
    if details and not success:
        print(f"    Error: {details}")
    if details and success:
        print(f"    Output: {str(details)[:100]}...")

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ SKIPPING: GEMINI_API_KEY not found in environment.")
        return

    print("🚀 Starting Gemini API Verification...")
    
    # 1. Initialize
    try:
        client = GeminiClient()
        print_result("Initialize Client", True)
    except Exception as e:
        print_result("Initialize Client", False, e)
        return

    # 2. List Models
    try:
        models = client.list_models()
        if models:
            print_result("List Models", True, f"Found {len(models)} models. First: {models[0].get('name')}")
            # Find a valid generation model
            gen_model = next((m['name'] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])), "gemini-2.0-flash")
        else:
             print_result("List Models", False, "No models returned")
             gen_model = "gemini-2.0-flash"
    except Exception as e:
        print_result("List Models", False, e)
        gen_model = "gemini-2.0-flash"

    # 3. Generate Content
    try:
        # Standard
        req = AgentRequest(prompt="Say 'Hello, Verification!'", context={"model": gen_model})
        resp = client.execute(req)
        if resp.is_success() and "Hello" in resp.content:
             print_result("Generate Content (Basic)", True, resp.content)
        else:
             print_result("Generate Content (Basic)", False, f"Content mismatch: {resp.content}")

        # System Instruction Test
        req_sys = AgentRequest(
            prompt="Hello", 
            context={
                "model": gen_model,
                "system_instruction": "You are a pirate."
            }
        )
        resp_sys = client.execute(req_sys)
        if resp_sys.is_success() and ("Arr" in resp_sys.content or "Ahoy" in resp_sys.content):
             print_result("Generate Content (System Instruct)", True, resp_sys.content)
        else:
             print_result("Generate Content (System Instruct)", False, f"Pirate check failed: {resp_sys.content}")

    except Exception as e:
        print_result("Generate Content", False, e)

    # 4. Count Tokens
    try:
        count = client.count_tokens("Hello world", model=gen_model)
        if count > 0:
             print_result("Count Tokens", True, f"{count} tokens")
        else:
             print_result("Count Tokens", False, "Returned 0 tokens")
    except Exception as e:
        print_result("Count Tokens", False, e)

    # 5. Embed Content
    try:
        emb = client.embed_content("Hello world")
        if emb and len(emb) > 0:
             print_result("Embed Content", True, f"Vector dim: {len(emb[0])}")
        else:
             print_result("Embed Content", False, "Empty embedding")
    except Exception as e:
         print_result("Embed Content", False, e)

    # 6. Files API
    try:
        # Create dummy file
        dummy_path = "temp_verify.txt"
        with open(dummy_path, "w") as f:
            f.write("This is a test file for Gemini API verification.")
            
        # Upload
        upload_resp = client.upload_file(dummy_path, mime_type="text/plain")
        if upload_resp and "name" in upload_resp:
             file_name = upload_resp["name"]
             print_result("Upload File", True, file_name)
             
             # List (check if present)
             files = client.list_files()
             found = any(f["name"] == file_name for f in files)
             print_result("List Files", found, f"File {file_name} found in list")
             
             # Delete
             del_success = client.delete_file(file_name)
             print_result("Delete File", del_success)
        else:
             print_result("Upload File", False, "No response or name")
             
        os.remove(dummy_path)
    except Exception as e:
        print_result("Files API", False, e)
        if os.path.exists("temp_verify.txt"): os.remove("temp_verify.txt")

    print("🏁 Verification Complete.")

if __name__ == "__main__":
    main()