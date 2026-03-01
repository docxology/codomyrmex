"""Proxy and pass-through handlers for WebsiteServer.

Handles /api/chat (Ollama proxy) and /api/awareness/summary
(Ollama-powered AI summary generation).
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests

from codomyrmex.config_management.defaults import (
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_OLLAMA_URL = os.getenv("CODOMYRMEX_OLLAMA_URL", DEFAULT_OLLAMA_URL)
_DEFAULT_MODEL = os.getenv("CODOMYRMEX_DEFAULT_MODEL", DEFAULT_OLLAMA_MODEL)


class ProxyHandler:
    """Mixin providing Ollama proxy endpoint handlers.

    Expects the host class to provide:
    - self.data_provider: DataProvider instance
    - self.headers: HTTP request headers
    - self.rfile: request input stream
    - self.send_json_response(data, status): JSON response sender
    """

    def handle_chat(self) -> None:
        """Proxy chat requests to Ollama."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response({"error": "No content provided"}, status=400)
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return

        ollama_url = f"{_OLLAMA_URL}/api/chat"

        # Get the message from frontend
        user_message = data.get('message', '')
        # Use provided model or fall back to system default
        system_model = _DEFAULT_MODEL
        if self.data_provider:
            llm_config = self.data_provider.get_llm_config()
            system_model = llm_config.get("default_model", _DEFAULT_MODEL)

        model = data.get('model') or system_model

        # Format for Ollama API
        ollama_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "stream": False  # Non-streaming for simplicity
        }

            # If the frontend already sends proper format, use it
        if 'messages' in data:
            ollama_payload = {
                "model": data.get('model') or system_model,
                "messages": data['messages'],
                "stream": False
            }

        try:
            ollama_resp = requests.post(ollama_url, json=ollama_payload, timeout=60)

            if ollama_resp.status_code == 200:
                result = ollama_resp.json()
                # Extract the assistant's message
                response_text = result.get('message', {}).get('content', 'No response')

                self.send_json_response({
                    "response": response_text,
                    "model": model,
                    "success": True
                })
            else:
                self.send_json_response({
                    "error": f"Ollama error: {ollama_resp.status_code} - {ollama_resp.text[:200]}"
                }, status=502)

        except requests.exceptions.ConnectionError:
            self.send_json_response({"error": "Ollama service not reachable. Is it running?"}, status=503)
        except requests.exceptions.Timeout:
            self.send_json_response({"error": "Ollama request timed out"}, status=504)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_awareness_summary(self) -> None:
        """Handle POST /api/awareness/summary -- generate Ollama AI summary."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response({"error": "No content provided"}, status=400)
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return

        if self.data_provider:
            llm_config = self.data_provider.get_llm_config()
            system_model = llm_config.get("default_model", _DEFAULT_MODEL)
        else:
            system_model = _DEFAULT_MODEL

        model = data.get('model') or system_model

        if not self.data_provider:
            self.send_json_response({"error": "Data provider missing"}, status=500)
            return

        awareness = self.data_provider.get_pai_awareness_data()
        metrics = awareness.get("metrics", {})
        missions_summary = ", ".join(
            f"{m['title']} ({m['status']})" for m in awareness.get("missions", [])
        )
        projects_summary = ", ".join(
            f"{p['title']} ({p['completion_percentage']}%)"
            for p in awareness.get("projects", [])
        )

        prompt = (
            f"Here is the current PAI ecosystem state:\n"
            f"- Missions ({metrics.get('mission_count', 0)}): {missions_summary or 'none'}\n"
            f"- Projects ({metrics.get('project_count', 0)}): {projects_summary or 'none'}\n"
            f"- Tasks: {metrics.get('completed_tasks', 0)}/{metrics.get('total_tasks', 0)} completed\n"
            f"- Overall completion: {metrics.get('overall_completion', 0)}%\n\n"
            f"Provide: 1) Overall assessment, 2) Key priorities, "
            f"3) Potential blockers, 4) Recommended actions."
        )

        ollama_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

        try:
            ollama_resp = requests.post(
                f"{_OLLAMA_URL}/api/chat",
                json=ollama_payload,
                timeout=60,
            )
            if ollama_resp.status_code == 200:
                result = ollama_resp.json()
                summary_text = result.get("message", {}).get("content", "No response")
                self.send_json_response({
                    "summary": summary_text,
                    "model": model,
                    "success": True,
                })
            else:
                self.send_json_response(
                    {"error": f"Ollama error: {ollama_resp.status_code}"},
                    status=502,
                )
        except requests.exceptions.ConnectionError:
            self.send_json_response(
                {"error": "Ollama service not reachable. Is it running?"},
                status=503,
            )
        except requests.exceptions.Timeout:
            self.send_json_response(
                {"error": "Ollama request timed out"},
                status=504,
            )
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
