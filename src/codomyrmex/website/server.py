"""HTTP server with REST API endpoints for the Codomyrmex website.

Provides WebsiteServer, an enhanced HTTP request handler that serves
static files and exposes API endpoints for modules, agents, scripts,
configuration, documentation, pipelines, health monitoring, test
execution, and Ollama chat proxy.
"""

import http.server
import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

import requests

from codomyrmex.config_management.defaults import (
    DEFAULT_CORS_ORIGINS,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
)
from codomyrmex.logging_monitoring import get_logger

from .data_provider import DataProvider

logger = get_logger(__name__)

# Configuration from environment variables
_CORS_ORIGINS = os.getenv(
    "CODOMYRMEX_CORS_ORIGINS",
    DEFAULT_CORS_ORIGINS + ",http://127.0.0.1:8787,http://localhost:8888,http://127.0.0.1:8888,http://localhost:8889,http://127.0.0.1:8889",
)
_OLLAMA_URL = os.getenv("CODOMYRMEX_OLLAMA_URL", DEFAULT_OLLAMA_URL)
_DEFAULT_MODEL = os.getenv("CODOMYRMEX_DEFAULT_MODEL", DEFAULT_OLLAMA_MODEL)

# Allowed origins for CORS/CSRF validation
_ALLOWED_ORIGINS = frozenset(origin.strip() for origin in _CORS_ORIGINS.split(",") if origin.strip())


class WebsiteServer(http.server.SimpleHTTPRequestHandler):
    """
    Enhanced HTTP server that supports API endpoints for dynamic functionality.
    """

    # Class-level configuration to be set before starting the server
    root_dir: Path = Path(".")
    data_provider: DataProvider | None = None
    _test_lock = threading.Lock()
    _test_running = False
    _dispatch_lock = threading.Lock()
    _dispatch_orch = None
    _dispatch_thread = None

    def __init__(self, *args, **kwargs):
        """Execute   Init   operations natively."""
        super().__init__(*args, **kwargs)

    def _cors_origin(self) -> str:
        """Return the matching CORS origin for the current request, or the first allowed origin."""
        origin = self.headers.get("Origin", "")
        if origin in _ALLOWED_ORIGINS:
            return origin
        return next(iter(_ALLOWED_ORIGINS))

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', self._cors_origin())
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Origin')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Vary', 'Origin')
        self.end_headers()

    def _validate_origin(self) -> bool:
        """Check Origin or Referer header matches allowed origins."""
        origin = self.headers.get("Origin", "")
        referer = self.headers.get("Referer", "")
        if origin:
            if origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:"):
                return True
            return origin in _ALLOWED_ORIGINS
        if referer:
            if referer.startswith("http://localhost:") or referer.startswith("http://127.0.0.1:"):
                return True
            return any(referer.startswith(o) for o in _ALLOWED_ORIGINS)
        # Allow requests with no origin (e.g. same-origin, curl)
        return True

    def do_POST(self) -> None:
        """Handle POST requests."""
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
        """Handle GET requests."""
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

    def handle_status(self) -> None:
        """Handle /api/status — quick system status."""
        if self.data_provider:
            summary = self.data_provider.get_system_summary()
            self.send_json_response(summary)
        else:
            self.send_error(500, "Data provider missing")

    def handle_health(self) -> None:
        """Handle /api/health — comprehensive health data."""
        if self.data_provider:
            health = self.data_provider.get_health_status()
            self.send_json_response(health)
        else:
            self.send_error(500, "Data provider missing")

    # Store latest test results for async retrieval
    _test_results: dict | None = None

    def handle_tests_run(self) -> None:
        """Handle POST /api/tests — run tests for a module.

        Runs tests in a background thread so the HTTP server stays
        responsive. Returns 202 Accepted immediately. Poll
        GET /api/tests/status to retrieve results.
        """
        with self._test_lock:
            if self._test_running:
                self.send_json_response(
                    {"error": "A test run is already in progress. Please wait."},
                    status=429,
                )
                return
            WebsiteServer._test_running = True

        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (TypeError, ValueError):
            content_length = 0
        module = None
        if content_length > 0:
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                module = data.get('module')
            except (json.JSONDecodeError, KeyError):
                with self._test_lock:
                    WebsiteServer._test_running = False
                self.send_json_response({"error": "Invalid JSON"}, status=400)
                return

        if not self.data_provider:
            with self._test_lock:
                WebsiteServer._test_running = False
            self.send_error(500, "Data provider missing")
            return

        dp = self.data_provider

        def _run_tests_bg(mod: str | None) -> None:
            try:
                WebsiteServer._test_results = dp.run_tests(mod)
            except Exception as exc:
                WebsiteServer._test_results = {"error": str(exc)}
            finally:
                with WebsiteServer._test_lock:
                    WebsiteServer._test_running = False

        t = threading.Thread(target=_run_tests_bg, args=(module,), daemon=True)
        t.start()
        self.send_json_response(
            {"status": "running", "message": "Test run started in background."},
            status=202,
        )

    def handle_tests_status(self) -> None:
        """Handle GET /api/tests/status — poll for test results."""
        with self._test_lock:
            running = self._test_running
        if running:
            self.send_json_response({"status": "running"})
        elif WebsiteServer._test_results is not None:
            self.send_json_response(
                {"status": "done", "results": WebsiteServer._test_results}
            )
        else:
            self.send_json_response({"status": "idle"})

    def handle_config_list(self) -> None:
        """Handle config list request."""
        if self.data_provider:
            configs = self.data_provider.get_config_files()
            self.send_json_response(configs)
        else:
            self.send_error(500, "Data provider missing")

    def handle_config_get(self, path: str) -> None:
        """Handle config get request."""
        filename = path.replace("/api/config/", "")
        if self.data_provider:
            try:
                content = self.data_provider.get_config_content(filename)
                self.send_json_response({"content": content})
            except FileNotFoundError as e:
                self.send_json_response({"error": str(e)}, status=404)
            except ValueError as e:
                self.send_json_response({"error": str(e)}, status=403)
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)
        else:
            self.send_json_response({"error": "Data provider missing"}, status=500)

    def handle_config_save(self) -> None:
        """Handle config save request."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "No content provided")
            return

        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        content = data.get('content')
        filename = data.get('filename')

        if not filename:
            # Extract from URL path
            parsed_path = urlparse(self.path)
            filename = parsed_path.path.replace("/api/config/", "")

        if not content or not filename:
            self.send_error(400, "Missing filename or content")
            return

        if self.data_provider:
            try:
                self.data_provider.save_config_content(filename, content)
                self.send_json_response({"success": True, "filename": filename})
            except ValueError as e:
                self.send_json_response({"success": False, "error": str(e)}, status=403)
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)}, status=500)
        else:
            self.send_error(500, "Data provider missing")

    def handle_docs_list(self) -> None:
        """Handle docs list request."""
        if self.data_provider:
            data = self.data_provider.get_doc_tree()
            self.send_json_response(data)
        else:
            self.send_error(500)

    def handle_pipelines_list(self) -> None:
        """Handle pipelines list request."""
        if self.data_provider:
            status = self.data_provider.get_pipeline_status()
            self.send_json_response(status)
        else:
            self.send_error(500)

    def handle_docs_get(self, path: str) -> None:
        """Handle GET /api/docs/{path} — return doc file content."""
        from urllib.parse import unquote
        doc_path = unquote(path.replace("/api/docs/", "", 1))
        if not self.data_provider:
            self.send_error(500, "Data provider missing")
            return
        try:
            content = self.data_provider.get_doc_content(doc_path)
            self.send_json_response({"content": content})
        except ValueError as e:
            self.send_json_response({"error": str(e)}, status=403)
        except FileNotFoundError as e:
            self.send_json_response({"error": str(e)}, status=404)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_modules_list(self) -> None:
        """Handle GET /api/modules — return all modules."""
        if self.data_provider:
            modules = self.data_provider.get_modules()
            self.send_json_response(modules)
        else:
            self.send_error(500, "Data provider missing")

    def handle_module_detail(self, path: str) -> None:
        """Handle GET /api/modules/{name} — return single module detail."""
        name = path.replace("/api/modules/", "", 1)
        if not self.data_provider:
            self.send_error(500, "Data provider missing")
            return
        detail = self.data_provider.get_module_detail(name)
        if detail is None:
            self.send_json_response({"error": f"Module '{name}' not found"}, status=404)
        else:
            self.send_json_response(detail)

    def handle_tools_list(self) -> None:
        """Handle GET /api/tools — return all MCP tools, resources, and prompts."""
        if not self.data_provider:
            self.send_error(500, "Data provider missing")
            return
        tools_data = self.data_provider.get_mcp_tools()
        self.send_json_response(tools_data)

    def handle_agents_list(self) -> None:
        """Handle GET /api/agents — return actual AI agents."""
        if self.data_provider:
            agents = self.data_provider.get_actual_agents()
            self.send_json_response(agents)
        else:
            self.send_error(500, "Data provider missing")

    def handle_scripts_list(self) -> None:
        """Handle GET /api/scripts — return available scripts."""
        if self.data_provider:
            scripts = self.data_provider.get_available_scripts()
            self.send_json_response(scripts)
        else:
            self.send_error(500, "Data provider missing")

    def handle_execute(self) -> None:
        """Execute a script from the scripts directory."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_error(400, "No content provided")
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return

        script_name = data.get('script')
        args = data.get('args', [])

        if not script_name:
            self.send_error(400, "Script name required")
            return

        # Security check: ensure script is within scripts dir
        script_path = (self.root_dir / "scripts" / script_name).resolve()
        scripts_root = (self.root_dir / "scripts").resolve()

        if not str(script_path).startswith(str(scripts_root)) or not script_path.exists():
            self.send_error(403, f"Invalid script path: {script_name}")
            return

        try:
            # Run the script using the current python executable
            cmd = [sys.executable, str(script_path)] + args
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            # Ensure we capture both stdout and stderr
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=self.root_dir, # Run from project root
                timeout=300 # 5 minute timeout safety
            )

            response = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

            self.send_json_response(response)

        except subprocess.TimeoutExpired:
            self.send_json_response({
                "success": False,
                "error": "Script execution timed out after 300 seconds",
                "stderr": "TimeoutExpired"
            }, status=504)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, status=500)

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

    def handle_refresh(self) -> None:
        """Refresh system data."""
        if self.data_provider:
            data = {
                "system": self.data_provider.get_system_summary(),
                "modules": self.data_provider.get_modules(),
                "agents": self.data_provider.get_actual_agents(),
                "scripts": self.data_provider.get_available_scripts()
            }
            self.send_json_response(data)
        else:
            self.send_error(500, "Data provider not initialized")

    def handle_awareness(self) -> None:
        """Handle GET /api/awareness — PAI ecosystem data."""
        if self.data_provider:
            data = self.data_provider.get_pai_awareness_data()
            self.send_json_response(data)
        else:
            self.send_json_response({"error": "Data provider missing"}, status=500)

    def handle_llm_config(self) -> None:
        """Handle GET /api/llm/config — return LLM configuration."""
        if self.data_provider:
            config = self.data_provider.get_llm_config()
            self.send_json_response(config)
        else:
            self.send_json_response({"error": "Data provider missing"}, status=500)

    def handle_awareness_summary(self) -> None:
        """Handle POST /api/awareness/summary — generate Ollama AI summary."""
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

    def handle_trust_status(self) -> None:
        """Handle GET /api/trust/status — return trust gateway tool counts."""
        try:
            from codomyrmex.agents.pai.trust_gateway import get_trust_report
            report = get_trust_report()
            counts = report.get("counts", {})
            self.send_json_response({
                "counts": {
                    "untrusted": counts.get("untrusted", 0),
                    "verified": counts.get("verified", 0),
                    "trusted": counts.get("trusted", 0),
                },
                "total_tools": report.get("total_tools", 0),
                "destructive_tools": report.get("destructive_tools", {}),
            })
        except Exception as e:
            # Fallback if trust gateway not available
            self.send_json_response({
                "counts": {"untrusted": 0, "verified": 0, "trusted": 0},
                "error": str(e),
            })

    def handle_pai_action(self) -> None:
        """Handle POST /api/pai/action — execute a PAI workflow action."""
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

        action = data.get("action", "")
        result: dict = {}

        try:
            if action == "verify":
                from codomyrmex.agents.pai.trust_gateway import verify_capabilities
                raw = verify_capabilities()
                result = {
                    "modules": raw.get("modules", {}).get("total", 0),
                    "tools_total": raw.get("tools", {}).get("total", 0),
                    "promoted": len(raw.get("trust", {}).get("promoted_to_verified", [])),
                }
            elif action == "trust":
                from codomyrmex.agents.pai.trust_gateway import trust_all
                raw = trust_all()
                result = raw
            elif action == "reset":
                from codomyrmex.agents.pai.trust_gateway import reset_trust
                reset_trust()
                result = {"message": "Trust levels reset to UNTRUSTED"}
            elif action == "status":
                try:
                    from codomyrmex.agents.pai.mcp_bridge import _tool_pai_status
                    result = _tool_pai_status()
                except Exception as _status_err:
                    result = {
                        "status": "degraded",
                        "error": str(_status_err),
                        "available": False,
                    }
            elif action == "analyze":
                modules = self.data_provider.get_modules() if self.data_provider else []
                summary = self.data_provider.get_system_summary() if self.data_provider else {}
                active = sum(1 for m in modules if m.get("status") == "Active")
                error_count = sum(1 for m in modules if m.get("status") not in ("Active", "Unknown"))
                result = {
                    "total_modules": len(modules),
                    "active_modules": active,
                    "error_modules": error_count,
                    "system": summary,
                }
            elif action == "search":
                import re
                query = data.get("query", "").strip()
                if not query:
                    self.send_json_response({"error": "search requires 'query' field", "success": False}, status=400)
                    return
                try:
                    pattern = re.compile(query, re.IGNORECASE)
                except re.error as exc:
                    self.send_json_response({"error": f"Invalid regex: {exc}", "success": False}, status=400)
                    return
                modules = self.data_provider.get_modules() if self.data_provider else []
                hits = [
                    m for m in modules
                    if pattern.search(m.get("name", "")) or pattern.search(m.get("description", ""))
                ]
                result = {"query": query, "hits": hits, "count": len(hits)}
            elif action == "docs":
                module_name = data.get("module", "").strip()
                if not module_name:
                    self.send_json_response({"error": "docs requires 'module' field", "success": False}, status=400)
                    return
                detail = self.data_provider.get_module_detail(module_name) if self.data_provider else None
                if detail is None:
                    self.send_json_response({"error": f"Module '{module_name}' not found", "success": False}, status=404)
                    return
                result = detail
            elif action == "add_memory":
                from codomyrmex.agentic_memory.mcp_tools import memory_put
                content = data.get("content", "")
                if not content:
                    self.send_json_response({"error": "Content is required for add_memory", "success": False}, status=400)
                    return
                # memory_put expects **kwargs, so we pass content=content directly
                result = memory_put(content=content)
            else:
                self.send_json_response(
                    {"error": f"Unknown action: {action}", "success": False},
                    status=400,
                )
                return

            # After any trust-changing action, include updated counts
            from codomyrmex.agents.pai.trust_gateway import get_trust_report
            report = get_trust_report()
            counts = report.get("counts", {})

            self.send_json_response({
                "success": True,
                "action": action,
                "result": result,
                "trust_counts": {
                    "untrusted": counts.get("untrusted", 0),
                    "verified": counts.get("verified", 0),
                    "trusted": counts.get("trusted", 0),
                },
            })
        except Exception as e:
            self.send_json_response(
                {"success": False, "error": str(e), "action": action},
                status=500,
            )

    def handle_agent_dispatch(self) -> None:
        """Handle POST /api/agent/dispatch — start an orchestrator run."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (TypeError, ValueError):
            content_length = 0

        data = {}
        if content_length > 0:
            try:
                post_data = self.rfile.read(content_length)
                payload = post_data.decode('utf-8').strip()
                if not payload:
                    self.send_json_response({"error": "No content provided"}, status=400)
                    return
                data = json.loads(payload)
            except (json.JSONDecodeError, KeyError):
                self.send_json_response({"error": "Invalid JSON"}, status=400)
                return
        else:
            self.send_json_response({"error": "No content provided"}, status=400)
            return

        seed_prompt = data.get("prompt", "Analyze the current context.")
        todo_path = data.get("todo", "")
        agents = data.get("agents")

        with self._dispatch_lock:
            if WebsiteServer._dispatch_thread and WebsiteServer._dispatch_thread.is_alive():
                self.send_json_response({"error": "A dispatch run is already in progress"}, status=429)
                return

            try:
                import time

                from codomyrmex.agents.orchestrator import ConversationOrchestrator

                if todo_path:
                    WebsiteServer._dispatch_orch = ConversationOrchestrator.dev_loop(
                        todo_path=todo_path,
                        channel=f"dispatch-{int(time.time())}",
                        agents=agents
                    )
                else:
                    default_agents = [
                        {"identity": "architect", "persona": "system planner", "provider": "ollama"},
                        {"identity": "reviewer", "persona": "code executor", "provider": "antigravity"}
                    ]
                    WebsiteServer._dispatch_orch = ConversationOrchestrator(
                        channel=f"dispatch-{int(time.time())}",
                        seed_prompt=seed_prompt,
                        agents=agents if agents else default_agents
                    )

                def run_orch():
                    """Execute Run Orch operations natively."""
                    try:
                        WebsiteServer._dispatch_orch.run(rounds=3)
                    except Exception as e:
                        logger.error(f"Dispatch error: {e}")

                WebsiteServer._dispatch_thread = threading.Thread(target=run_orch, daemon=True)
                WebsiteServer._dispatch_thread.start()

                self.send_json_response({
                    "success": True,
                    "message": "Dispatch started",
                    "channel": WebsiteServer._dispatch_orch.channel_id
                })
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)

    def handle_agent_dispatch_stop(self) -> None:
        """Handle POST /api/agent/dispatch/stop — stop orchestrator."""
        with self._dispatch_lock:
            if WebsiteServer._dispatch_orch:
                # Stop logic if supported by orchestrator
                WebsiteServer._dispatch_orch = None
            self.send_json_response({"success": True, "message": "Stop signal sent"})

    def handle_agent_dispatch_status(self) -> None:
        """Handle GET /api/agent/dispatch/status — poll transcript."""
        with self._dispatch_lock:
            if not WebsiteServer._dispatch_orch:
                self.send_json_response({"active": False, "turns": []})
                return

            try:
                from dataclasses import asdict
                log = WebsiteServer._dispatch_orch.get_log()
                turns = [asdict(t) for t in log.turns]

                is_active = WebsiteServer._dispatch_thread and WebsiteServer._dispatch_thread.is_alive()

                self.send_json_response({
                    "active": is_active,
                    "summary": log.summary(),
                    "turns": turns
                })
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)

    # Persistent telemetry collector shared across requests
    _telemetry_collector = None
    _telemetry_dm = None

    @classmethod
    def _ensure_telemetry(cls):
        """Lazily initialise the shared MetricCollector and DashboardManager.

        Returns:
            Tuple of (collector, dashboard_manager, MetricType) for callers.
        """
        from codomyrmex.telemetry.dashboard import (
            DashboardManager,
            MetricCollector,
            MetricType,
            Panel,
            PanelType,
        )

        if cls._telemetry_collector is None:
            cls._telemetry_collector = MetricCollector()
            cls._telemetry_dm = DashboardManager(cls._telemetry_collector)
            dash = cls._telemetry_dm.create(
                "System Overview",
                description="Baseline system metrics",
                tags=["system", "auto"],
            )
            dash.add_panel(Panel(
                id="modules", title="Module Count",
                panel_type=PanelType.STAT, metrics=["module_count"],
            ))
            dash.add_panel(Panel(
                id="tools", title="MCP Tool Count",
                panel_type=PanelType.STAT, metrics=["tool_count"],
            ))
            dash.add_panel(Panel(
                id="agents", title="Agent Count",
                panel_type=PanelType.STAT, metrics=["agent_count"],
            ))

        return cls._telemetry_collector, cls._telemetry_dm, MetricType

    def handle_telemetry(self) -> None:
        """Handle GET /api/telemetry — metric series and dashboard registry.

        Uses a persistent MetricCollector that seeds baseline system
        metrics on first access and refreshes them on each request.
        """
        try:
            collector, dm, MetricType = self._ensure_telemetry()

            # Seed / refresh baseline metrics from DataProvider
            if self.data_provider:
                modules = self.data_provider.get_modules()
                collector.record("module_count", float(len(modules)),
                                metric_type=MetricType.GAUGE)
                agents = self.data_provider.get_actual_agents()
                collector.record("agent_count", float(len(agents)),
                                metric_type=MetricType.GAUGE)
                try:
                    tools_data = self.data_provider.get_mcp_tools()
                    collector.record("tool_count",
                                    float(len(tools_data.get("tools", []))),
                                    metric_type=MetricType.GAUGE)
                except Exception:
                    pass

            # Build latest_values dict for the frontend
            latest_values = {}
            for name in collector._metrics:
                latest = collector.get_latest(name)
                if latest is not None:
                    latest_values[name] = latest.value

            data = {
                "status": "ok",
                "dashboards": [d.to_dict() for d in dm.list()],
                "metric_names": list(collector._metrics.keys()),
                "total_metrics": sum(
                    len(v) for v in collector._metrics.values()
                ),
                "latest_values": latest_values,
            }
        except Exception as exc:
            data = {"status": "error", "error": str(exc)}
        self.send_json_response(data)

    def handle_telemetry_seed(self) -> None:
        """Handle POST /api/telemetry/seed — seed baseline system metrics.

        Triggers a fresh telemetry snapshot capturing module count,
        tool count, agent count, and Python version.
        """
        try:
            collector, _dm, MetricType = self._ensure_telemetry()
            seeded = []

            if self.data_provider:
                modules = self.data_provider.get_modules()
                collector.record("module_count", float(len(modules)),
                                metric_type=MetricType.GAUGE)
                seeded.append("module_count")

                agents = self.data_provider.get_actual_agents()
                collector.record("agent_count", float(len(agents)),
                                metric_type=MetricType.GAUGE)
                seeded.append("agent_count")

                try:
                    tools_data = self.data_provider.get_mcp_tools()
                    collector.record("tool_count",
                                    float(len(tools_data.get("tools", []))),
                                    metric_type=MetricType.GAUGE)
                    seeded.append("tool_count")
                except Exception:
                    pass

                # Additional useful metrics
                import platform
                collector.record("python_version_minor",
                                float(sys.version_info.minor),
                                metric_type=MetricType.GAUGE)
                seeded.append("python_version_minor")

                scripts = self.data_provider.get_available_scripts()
                collector.record("script_count",
                                float(len(scripts)),
                                metric_type=MetricType.GAUGE)
                seeded.append("script_count")

            self.send_json_response({
                "status": "ok",
                "seeded_metrics": seeded,
                "count": len(seeded),
            })
        except Exception as exc:
            self.send_json_response(
                {"status": "error", "error": str(exc)}, status=500
            )

    def handle_security_posture(self) -> None:
        """Handle GET /api/security/posture — aggregate security posture."""
        try:
            from codomyrmex.security.dashboard import SecurityDashboard
            sd = SecurityDashboard()
            posture = sd.posture()
            data = {
                "status": "ok",
                "risk_score": posture.risk_score,
                "compliance_rate": posture.compliance_pass_rate,
                "secret_findings_count": posture.secret_findings_count,
                "total_checks": posture.total_checks,
                "markdown": sd.to_markdown(),
            }
        except Exception as exc:
            data = {"status": "error", "error": str(exc)}
        self.send_json_response(data)

    def send_json_response(self, data: dict | list, status: int = 200) -> None:
        """Send a JSON response with the given data and HTTP status code."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', self._cors_origin())
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Origin')
        self.send_header('Vary', 'Origin')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
