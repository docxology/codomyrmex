"""Unified LLM Client for Real Agent Integration.

Provides a factory to get a real LLM client (Claude or Ollama) for use in
autonomous agents, CLI tools, and skills.
"""

import os
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Any, Optional
from dataclasses import dataclass

from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL

logger = logging.getLogger(__name__)

@dataclass
class AgentRequest:
    """Functional component: AgentRequest."""
    prompt: str
    metadata: Optional[dict[str, Any]] = None

class OllamaClient:
    """Client for local Ollama instance (REST API).
    
    Implements a robust interface compatible with ClaudeClient
    for use in ClaudeCodeEndpoint, using real LLM inference.
    """
    def __init__(self, model: str = "llama3", base_url: str = DEFAULT_OLLAMA_URL):
        """Execute   Init   operations natively."""
        self.model = model
        self.base_url = base_url
        self.session_manager = None # dummy for interface compatibility

    def create_session(self, session_id: str) -> None: 
        """Execute Create Session operations natively."""
        # Ollama manages context internally via /api/chat if messages are sent
        # For this simple client, we rely on prompt context or stateless calls
        return None

    def execute_with_session(self, request: AgentRequest, session: Any = None, session_id: Any = None) -> Any:
        """Execute request using Ollama /api/chat for real conversation."""
        url = f"{self.base_url}/api/chat"
        
        # Construct chat messages
        messages = [{"role": "user", "content": request.prompt}]
        
        # Check if system prompt is embedded in context or prompt
        if "System:" in request.prompt:
            parts = request.prompt.split("System:", 1)
            if len(parts) > 1:
                sys_instruction, user_msg = parts[1].split("\n", 1) if "\n" in parts[1] else (parts[1], "")
                messages = [
                    {"role": "system", "content": sys_instruction.strip()},
                    {"role": "user", "content": user_msg.strip() or "Proceed."}
                ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        start_time = time.monotonic()
        content = ""
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    msg = data.get("message", {})
                    content = msg.get("content", "")
                else:
                    raise RuntimeError(f"Ollama returned {response.status}")
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            # Propagate error with context
            try:
                # Try to list models to help debugging
                with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=1.0) as resp:
                     if resp.status == 200:
                         tags = json.loads(resp.read().decode("utf-8"))
                         models = [m.get("name") for m in tags.get("models", [])]
                         print(f"DEBUG: Available models: {models}")
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
                pass
            raise RuntimeError(f"Real Ollama Connection Failed: {e}")

        elapsed = time.monotonic() - start_time

        class Response:
            """Functional component: Response."""
            def is_success(self): return True
            pass
        
        resp = Response()
        resp.content = content
        resp.tokens_used = 0 
        resp.execution_time = elapsed
        return resp

def get_llm_client(identity: str = "agent") -> Any:
    """Factory to get the best available REAL LLM client.
    
    Priority:
    1. ClaudeClient (if ANTHROPIC_API_KEY set)
    2. OllamaClient (if reachable)
    
    Raises RuntimeError if no real client is available.
    """
    # 1. Check Claude
    try:
        from codomyrmex.agents.claude.claude_client import ClaudeClient
        if os.environ.get("ANTHROPIC_API_KEY"):
            logger.info(f"[{identity}] Using real ClaudeClient (API Key found)")
            return ClaudeClient()
    except ImportError:
        pass
    
    # 2. Check Ollama
    try:
        # Quick health check
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.0) as resp:
            if resp.status == 200:
                # Use configured model or default
                model = os.environ.get("OLLAMA_MODEL", "codellama:latest")
                logger.info(f"[{identity}] Using real OllamaClient (Localhost reachable, model={model})")
                return OllamaClient(model=model) 
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
        pass
        
    raise RuntimeError(
        f"[{identity}] CRITICAL: No Real LLM Available.\n"
        "Please set ANTHROPIC_API_KEY for Claude,\n"
        "OR ensure Ollama is running at http://localhost:11434.\n"
        "Mocks are strictly forbidden."
    )
