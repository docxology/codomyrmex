import http.server
import json
import socket
import threading
import time
from typing import Any

import pytest

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.core.parsers import (
    parse_json_response,
    parse_xml_tag,
    parse_code_blocks,
)
from codomyrmex.agents.llm_client import OllamaClient


class MockOllamaHandler(http.server.BaseHTTPRequestHandler):
    """Real HTTP handler for testing OllamaClient without mocks."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(body)

        if self.path == "/api/chat":
            messages = data.get("messages", [])
            user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")

            if "error" in user_msg.lower():
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
                return

            response_content = f"Echo: {user_msg}"
            if "json" in user_msg.lower():
                response_content = '{"result": "success", "data": 42}'
            elif "xml" in user_msg.lower():
                response_content = "<thought>I should echo</thought><action>echo</action>Hello"

            response_data = {
                "message": {"role": "assistant", "content": response_content},
                "done": True,
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        elif self.path == "/api/tags":
            response_data = {
                "models": [{"name": "llama3"}, {"name": "codellama"}]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence server logs
        pass


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def ollama_server():
    port = get_free_port()
    server = http.server.HTTPServer(("127.0.0.1", port), MockOllamaHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


class TestAgentLifecycleZeroMock:
    """Zero-mock tests for agent lifecycle, parsing, and error handling."""

    def test_ollama_client_execution_success(self, ollama_server):
        client = OllamaClient(base_url=ollama_server)
        request = AgentRequest(prompt="Hello Ollama")
        response = client.execute(request)

        assert response.is_success()
        assert "Echo: Hello Ollama" in response.content
        assert response.metadata["provider"] == "ollama"

    def test_ollama_client_error_handling(self, ollama_server):
        client = OllamaClient(base_url=ollama_server)
        request = AgentRequest(prompt="Trigger Error")
        response = client.execute(request)

        assert not response.is_success()
        assert "500" in response.error

    def test_response_parsing_json(self, ollama_server):
        client = OllamaClient(base_url=ollama_server)
        request = AgentRequest(prompt="Give me JSON")
        response = client.execute(request)

        assert response.is_success()
        parsed = parse_json_response(response.content)
        assert parsed.success
        assert parsed.data["result"] == "success"

    def test_response_parsing_xml(self, ollama_server):
        client = OllamaClient(base_url=ollama_server)
        request = AgentRequest(prompt="Give me XML")
        response = client.execute(request)

        assert response.is_success()
        thought = parse_xml_tag(response.content, "thought")
        action = parse_xml_tag(response.content, "action")
        assert thought == "I should echo"
        assert action == "echo"

    def test_complex_parsing_scenario(self):
        """Test parsing utilities with mixed content."""
        content = """
Here is the code you requested:

```python
def hello():
    print("world")
```

And the configuration:
```json
{"enabled": true}
```

<thought>User wants code and config</thought>
"""
        # Test code block parsing
        blocks = parse_code_blocks(content)
        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert "print" in blocks[0].code
        assert blocks[1].language == "json"

        # Test JSON parsing
        json_parsed = parse_json_response(content)
        assert json_parsed.success
        assert json_parsed.data["enabled"] is True

        # Test XML parsing
        thought = parse_xml_tag(content, "thought")
        assert thought == "User wants code and config"

    def test_ollama_unreachable(self):
        """Test handling of totally unreachable server (no port bound)."""
        client = OllamaClient(base_url="http://127.0.0.1:1")  # Port 1 is unlikely to be open
        request = AgentRequest(prompt="Hello")
        response = client.execute(request)

        assert not response.is_success()
        assert "Connection Failed" in response.error
