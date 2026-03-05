"""HTTP server with REST API endpoints for the Codomyrmex website.

Provides WebsiteServer, an enhanced HTTP request handler that serves
static files and exposes API endpoints for modules, agents, scripts,
configuration, documentation, pipelines, health monitoring, test
execution, and Ollama chat proxy.

Endpoint handler logic is split into focused handler mixins:
- APIHandler   -- /api/* routes for modules, agents, scripts, config, etc.
- HealthHandler -- /health, /status, /telemetry, /security/posture
- ProxyHandler -- Ollama chat proxy and awareness summary
"""

import http.server
import json
import os
import threading
from pathlib import Path
from urllib.parse import urlparse

from codomyrmex.config_management.defaults import (
    DEFAULT_CORS_ORIGINS,
)
from codomyrmex.logging_monitoring import get_logger

from .data_provider import DataProvider
from .handlers import APIHandler, HealthHandler, ProxyHandler

logger = get_logger(__name__)

# Configuration from environment variables
_CORS_ORIGINS = os.getenv(
    "CODOMYRMEX_CORS_ORIGINS",
    DEFAULT_CORS_ORIGINS
    + ",http://127.0.0.1:8787,http://localhost:8888,http://127.0.0.1:8888,http://localhost:8889,http://127.0.0.1:8889",
)

# Allowed origins for CORS/CSRF validation
_ALLOWED_ORIGINS = frozenset(
    origin.strip() for origin in _CORS_ORIGINS.split(",") if origin.strip()
)


class WebsiteServer(
    APIHandler,
    HealthHandler,
    ProxyHandler,
    http.server.SimpleHTTPRequestHandler,
):
    """
    Enhanced HTTP server that supports API endpoints for dynamic functionality.

    Method implementations are provided by handler mixins:
    - APIHandler: modules, agents, scripts, config, docs, tests, PAI, dispatch
    - HealthHandler: status, health, telemetry, security posture, awareness, LLM config
    - ProxyHandler: Ollama chat proxy, awareness summary
    """

    # Class-level configuration to be set before starting the server
    root_dir: Path = Path()
    data_provider: DataProvider | None = None
    _test_lock = threading.Lock()
    _test_running = False
    _dispatch_lock = threading.Lock()
    _dispatch_orch = None
    _dispatch_thread = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _cors_origin(self) -> str:
        """Return the matching CORS origin for the current request, or the first allowed origin.

        CWE-113: Sanitizes output by stripping CR/LF to prevent HTTP response splitting.
        """
        origin = self.headers.get("Origin", "")
        # Strip any CR/LF to prevent HTTP response splitting (CWE-113)
        clean_origin = origin.replace("\r", "").replace("\n", "")
        if clean_origin in _ALLOWED_ORIGINS:
            return clean_origin
        return next(iter(_ALLOWED_ORIGINS))

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Origin")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def _validate_origin(self) -> bool:
        """Check Origin or Referer header matches allowed origins."""
        origin = self.headers.get("Origin", "")
        referer = self.headers.get("Referer", "")
        if origin:
            return origin in _ALLOWED_ORIGINS
        if referer:
            parsed = urlparse(referer)
            referer_origin = f"{parsed.scheme}://{parsed.netloc}"
            return referer_origin in _ALLOWED_ORIGINS
        # No Origin/Referer = same-origin request or curl — allow
        return True

    def do_POST(self) -> None:
        """Handle POST requests -- dispatch to handler mixins."""
        if not self._validate_origin():
            self.send_json_response({"error": "Origin not allowed"}, status=403)
            return

        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/execute":
            self.handle_execute()
        elif parsed_path.path == "/api/chat":
            self.handle_chat()
        elif parsed_path.path == "/api/refresh":
            self.handle_refresh()
        elif parsed_path.path == "/api/tests":
            self.handle_tests_run()
        elif parsed_path.path == "/api/awareness/summary":
            self.handle_awareness_summary()
        elif parsed_path.path == "/api/pai/action":
            self.handle_pai_action()
        elif parsed_path.path == "/api/agent/dispatch":
            self.handle_agent_dispatch()
        elif parsed_path.path == "/api/agent/dispatch/stop":
            self.handle_agent_dispatch_stop()
        elif parsed_path.path == "/api/telemetry/seed":
            self.handle_telemetry_seed()
        elif parsed_path.path.startswith("/api/config"):
            self.handle_config_save()
        else:
            self.send_error(404, "Endpoint not found")

    def do_GET(self) -> None:
        """Handle GET requests -- dispatch to handler mixins."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/status":
            self.handle_status()
        elif parsed_path.path == "/api/health":
            self.handle_health()
        elif parsed_path.path == "/api/config":
            self.handle_config_list()
        elif parsed_path.path.startswith("/api/config/"):
            self.handle_config_get(parsed_path.path)
        elif parsed_path.path == "/api/docs":
            self.handle_docs_list()
        elif parsed_path.path.startswith("/api/docs/"):
            self.handle_docs_get(parsed_path.path)
        elif parsed_path.path == "/api/modules":
            self.handle_modules_list()
        elif parsed_path.path.startswith("/api/modules/"):
            self.handle_module_detail(parsed_path.path)
        elif parsed_path.path == "/api/agents":
            self.handle_agents_list()
        elif parsed_path.path == "/api/scripts":
            self.handle_scripts_list()
        elif parsed_path.path == "/api/pipelines":
            self.handle_pipelines_list()
        elif parsed_path.path == "/api/awareness":
            self.handle_awareness()
        elif parsed_path.path == "/api/llm/config":
            self.handle_llm_config()
        elif parsed_path.path == "/api/agent/dispatch/status":
            self.handle_agent_dispatch_status()
        elif parsed_path.path == "/api/tools":
            self.handle_tools_list()
        elif parsed_path.path == "/api/trust/status":
            self.handle_trust_status()
        elif parsed_path.path == "/api/tests/status":
            self.handle_tests_status()
        elif parsed_path.path == "/api/telemetry":
            self.handle_telemetry()
        elif parsed_path.path == "/api/security/posture":
            self.handle_security_posture()
        else:
            super().do_GET()

    def send_json_response(self, data: dict | list, status: int = 200) -> None:
        """Send a JSON response with the given data and HTTP status code."""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Origin")
        self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        """Override to suppress high-frequency access logs like /api/health."""
        if len(args) > 0 and type(args[0]) is str:
            req = args[0]
            if "GET /api/health" in req or "GET /api/status" in req:
                return  # Suppress
        super().log_message(format, *args)
