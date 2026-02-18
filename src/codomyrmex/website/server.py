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

from codomyrmex.logging_monitoring import get_logger

from .data_provider import DataProvider
from .education_provider import EducationDataProvider

logger = get_logger(__name__)

# Port and allowed origins (configurable via environment)
_PORT = int(os.environ.get("CODOMYRMEX_PORT", "8787"))
_ALLOWED_ORIGINS = frozenset(
    {
        f"http://localhost:{_PORT}",
        f"http://127.0.0.1:{_PORT}",
    }
)


class WebsiteServer(http.server.SimpleHTTPRequestHandler):
    """
    Enhanced HTTP server that supports API endpoints for dynamic functionality.
    """

    # Class-level configuration to be set before starting the server
    root_dir: Path = Path(".")
    data_provider: DataProvider | None = None
    education_provider: EducationDataProvider | None = None
    _test_lock = threading.Lock()
    _test_running = False

    def __init__(self, *args, **kwargs):
        if WebsiteServer.education_provider is None:
            WebsiteServer.education_provider = EducationDataProvider(
                content_root=WebsiteServer.root_dir / "output"
            )
        super().__init__(*args, **kwargs)

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", f"http://localhost:{_PORT}")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
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
        elif parsed_path.path.startswith("/api/config"):
            self.handle_config_save()
        # Education POST routes
        elif parsed_path.path == "/api/education/curricula":
            self.handle_curriculum_create()
        elif parsed_path.path.startswith(
            "/api/education/curricula/"
        ) and parsed_path.path.endswith("/modules"):
            self.handle_module_add(parsed_path.path)
        elif parsed_path.path == "/api/education/sessions":
            self.handle_session_create()
        elif parsed_path.path == "/api/education/quiz":
            self.handle_quiz_generate()
        elif parsed_path.path == "/api/education/quiz/answer":
            self.handle_quiz_answer()
        elif parsed_path.path.startswith(
            "/api/education/exams"
        ) and parsed_path.path.endswith("/submit"):
            self.handle_exam_submit(parsed_path.path)
        elif parsed_path.path == "/api/education/exams":
            self.handle_exam_create()
        elif parsed_path.path == "/api/education/certificates":
            self.handle_certificate_generate()
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
        elif parsed_path.path == "/api/tools":
            self.handle_tools_list()
        # Education API routes
        elif parsed_path.path == "/api/education/curricula":
            self.handle_curricula_list()
        elif parsed_path.path == "/api/education/topics":
            self.handle_topics_list()
        elif parsed_path.path == "/api/education/certificates":
            self.handle_certificates_list()
        elif parsed_path.path.startswith("/api/education/curricula/"):
            self._dispatch_education_get(parsed_path.path, parsed_path.query)
        elif parsed_path.path.startswith("/api/education/sessions/"):
            self._dispatch_session_get(parsed_path.path)
        # Content API routes
        elif parsed_path.path == "/api/content/tree":
            self.handle_content_tree(parsed_path.query)
        elif parsed_path.path == "/api/content/file":
            self.handle_content_file(parsed_path.query)
        elif parsed_path.path == "/api/trust/status":
            self.handle_trust_status()
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

    def handle_tests_run(self) -> None:
        """Handle POST /api/tests — run tests for a module."""
        # Rate limiting: only one test run at a time
        with self._test_lock:
            if self._test_running:
                self.send_json_response(
                    {"error": "A test run is already in progress. Please wait."},
                    status=429,
                )
                return
            WebsiteServer._test_running = True

        try:
            try:
                content_length = int(self.headers.get("Content-Length", 0))
            except (TypeError, ValueError):
                content_length = 0
            module = None
            if content_length > 0:
                try:
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode("utf-8"))
                    module = data.get("module")
                except (json.JSONDecodeError, KeyError):
                    self.send_json_response({"error": "Invalid JSON"}, status=400)
                    return

            if self.data_provider:
                results = self.data_provider.run_tests(module)
                self.send_json_response(results)
            else:
                self.send_error(500, "Data provider missing")
        finally:
            with self._test_lock:
                WebsiteServer._test_running = False

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
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_error(400, "No content provided")
            return

        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))
        content = data.get("content")
        filename = data.get("filename")

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
        doc_path = path.replace("/api/docs/", "", 1)
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
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_error(400, "No content provided")
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return

        script_name = data.get("script")
        args = data.get("args", [])

        if not script_name:
            self.send_error(400, "Script name required")
            return

        # Security check: ensure script is within scripts dir
        script_path = (self.root_dir / "scripts" / script_name).resolve()
        scripts_root = (self.root_dir / "scripts").resolve()

        if (
            not str(script_path).startswith(str(scripts_root))
            or not script_path.exists()
        ):
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
                capture_output=True,
                text=True,
                env=env,
                cwd=self.root_dir,  # Run from project root
                timeout=300,  # 5 minute timeout safety
            )

            response = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

            self.send_json_response(response)

        except subprocess.TimeoutExpired:
            self.send_json_response(
                {
                    "success": False,
                    "error": "Script execution timed out after 300 seconds",
                    "stderr": "TimeoutExpired",
                },
                status=504,
            )
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, status=500)

    def handle_chat(self) -> None:
        """Proxy chat requests to Ollama."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response({"error": "No content provided"}, status=400)
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return

        ollama_url = "http://localhost:11434/api/chat"

        # Get the message from frontend
        user_message = data.get("message", "")
        # Use provided model or fall back to system default
        system_model = "llama3.1:latest"  # Fallback
        if self.data_provider:
            llm_config = self.data_provider.get_llm_config()
            system_model = llm_config.get("default_model", "llama3.1:latest")

        model = data.get("model") or system_model

        # Format for Ollama API
        ollama_payload = {
            "model": model,
            "messages": [{"role": "user", "content": user_message}],
            "stream": False,  # Non-streaming for simplicity
        }

        # If the frontend already sends proper format, use it
        if "messages" in data:
            ollama_payload = {
                "model": data.get("model") or system_model,
                "messages": data["messages"],
                "stream": False,
            }

        try:
            ollama_resp = requests.post(ollama_url, json=ollama_payload, timeout=60)

            if ollama_resp.status_code == 200:
                result = ollama_resp.json()
                # Extract the assistant's message
                response_text = result.get("message", {}).get("content", "No response")

                self.send_json_response(
                    {"response": response_text, "model": model, "success": True}
                )
            else:
                self.send_json_response(
                    {
                        "error": f"Ollama error: {ollama_resp.status_code} - {ollama_resp.text[:200]}"
                    },
                    status=502,
                )

        except requests.exceptions.ConnectionError:
            self.send_json_response(
                {"error": "Ollama service not reachable. Is it running?"}, status=503
            )
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
                "scripts": self.data_provider.get_available_scripts(),
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
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response({"error": "No content provided"}, status=400)
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return

        if self.data_provider:
            llm_config = self.data_provider.get_llm_config()
            system_model = llm_config.get("default_model", "llama3.1:latest")
        else:
            system_model = "llama3.1:latest"

        model = data.get("model") or system_model

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
                "http://localhost:11434/api/chat",
                json=ollama_payload,
                timeout=60,
            )
            if ollama_resp.status_code == 200:
                result = ollama_resp.json()
                summary_text = result.get("message", {}).get("content", "No response")
                self.send_json_response(
                    {
                        "summary": summary_text,
                        "model": model,
                        "success": True,
                    }
                )
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

    def do_PUT(self) -> None:
        """Handle PUT requests (module updates)."""
        if not self._validate_origin():
            self.send_json_response(
                {"status": "error", "message": "Origin not allowed"}, status=403
            )
            return

        parsed_path = urlparse(self.path)

        # PUT /api/education/curricula/<name>/modules/<mod>
        if (
            parsed_path.path.startswith("/api/education/curricula/")
            and "/modules/" in parsed_path.path
        ):
            self.handle_module_update(parsed_path.path)
        else:
            self.send_json_response(
                {"status": "error", "message": "Endpoint not found"}, status=404
            )

    # ── Helper: read JSON body ─────────────────────────────────────

    _MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB

    def _read_json_body(self) -> dict | None:
        """Read and parse JSON from the request body. Returns None on error (response already sent)."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response(
                {"status": "error", "message": "No content provided"}, status=400
            )
            return None
        if content_length > self._MAX_BODY_SIZE:
            self.send_json_response(
                {"status": "error", "message": "Request body too large"}, status=413
            )
            return None
        try:
            raw = self.rfile.read(content_length)
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json_response(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
            return None

    # ── Education GET dispatchers ──────────────────────────────────

    def _dispatch_education_get(self, path: str, query: str) -> None:
        """Route GET /api/education/curricula/<name>/... sub-paths."""
        from urllib.parse import parse_qs

        # Strip prefix: /api/education/curricula/<name>[/rest]
        rest = path.replace("/api/education/curricula/", "", 1)
        parts = rest.split("/", 1)
        name = parts[0]
        sub = parts[1] if len(parts) > 1 else ""

        if sub == "export":
            params = parse_qs(query)
            fmt = params.get("format", ["json"])[0]
            self.handle_curriculum_export(name, fmt)
        elif sub == "learning-path":
            params = parse_qs(query)
            level = params.get("level", ["beginner"])[0]
            self.handle_learning_path(name, level)
        elif sub == "":
            self.handle_curriculum_get(name)
        else:
            self.send_json_response(
                {"status": "error", "message": "Endpoint not found"}, status=404
            )

    def _dispatch_session_get(self, path: str) -> None:
        """Route GET /api/education/sessions/<id>/progress."""
        rest = path.replace("/api/education/sessions/", "", 1)
        parts = rest.split("/", 1)
        session_id = parts[0]
        sub = parts[1] if len(parts) > 1 else ""

        if sub == "progress":
            self.handle_session_progress(session_id)
        else:
            self.send_json_response(
                {"status": "error", "message": "Endpoint not found"}, status=404
            )

    # ── Curriculum handlers ────────────────────────────────────────

    def handle_curricula_list(self) -> None:
        """GET /api/education/curricula — list all curricula."""
        data = self.education_provider.list_curricula()
        self.send_json_response({"status": "ok", "data": data})

    def handle_curriculum_create(self) -> None:
        """POST /api/education/curricula — create a curriculum."""
        body = self._read_json_body()
        if body is None:
            return
        name = body.get("name")
        level = body.get("level")
        if not name:
            self.send_json_response(
                {"status": "error", "message": "Missing field: name"}, status=400
            )
            return
        if not level:
            self.send_json_response(
                {"status": "error", "message": "Missing field: level"}, status=400
            )
            return
        try:
            result = self.education_provider.create_curriculum(name, level)
            self.send_json_response({"status": "ok", "data": result})
        except ValueError as e:
            msg = str(e)
            code = 409 if "already exists" in msg else 400
            self.send_json_response({"status": "error", "message": msg}, status=code)

    def handle_curriculum_get(self, name: str) -> None:
        """GET /api/education/curricula/<name> — get curriculum details."""
        result = self.education_provider.get_curriculum(name)
        if result is None:
            self.send_json_response(
                {"status": "error", "message": f"Curriculum '{name}' not found"},
                status=404,
            )
        else:
            self.send_json_response({"status": "ok", "data": result})

    def handle_module_add(self, path: str) -> None:
        """POST /api/education/curricula/<name>/modules — add a module."""
        cur_name = path.replace("/api/education/curricula/", "", 1).replace(
            "/modules", ""
        )
        body = self._read_json_body()
        if body is None:
            return
        if not body.get("name"):
            self.send_json_response(
                {"status": "error", "message": "Missing field: name"}, status=400
            )
            return
        try:
            result = self.education_provider.add_module(cur_name, body)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)
        except ValueError as e:
            msg = str(e)
            code = 409 if "already exists" in msg else 400
            self.send_json_response({"status": "error", "message": msg}, status=code)

    def handle_module_update(self, path: str) -> None:
        """PUT /api/education/curricula/<name>/modules/<mod> — update a module."""
        rest = path.replace("/api/education/curricula/", "", 1)
        parts = rest.split("/modules/", 1)
        if len(parts) != 2:
            self.send_json_response(
                {"status": "error", "message": "Invalid path"}, status=400
            )
            return
        cur_name, mod_name = parts[0], parts[1]
        body = self._read_json_body()
        if body is None:
            return
        try:
            result = self.education_provider.update_module(cur_name, mod_name, body)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    def handle_curriculum_export(self, name: str, fmt: str) -> None:
        """GET /api/education/curricula/<name>/export?format=json — export curriculum."""
        try:
            result = self.education_provider.export_curriculum(name, fmt)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)
        except ValueError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=400)

    def handle_learning_path(self, name: str, level: str) -> None:
        """GET /api/education/curricula/<name>/learning-path?level=beginner."""
        try:
            result = self.education_provider.get_learning_path(name, level)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)
        except ValueError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=400)

    # ── Tutoring handlers ──────────────────────────────────────────

    def handle_topics_list(self) -> None:
        """GET /api/education/topics — list available topics."""
        topics = self.education_provider.list_topics()
        self.send_json_response({"status": "ok", "data": topics})

    def handle_session_create(self) -> None:
        """POST /api/education/sessions — create a tutoring session."""
        body = self._read_json_body()
        if body is None:
            return
        student_name = body.get("student_name")
        topic = body.get("topic")
        if not student_name:
            self.send_json_response(
                {"status": "error", "message": "Missing field: student_name"},
                status=400,
            )
            return
        if not topic:
            self.send_json_response(
                {"status": "error", "message": "Missing field: topic"}, status=400
            )
            return
        result = self.education_provider.create_session(student_name, topic)
        self.send_json_response({"status": "ok", "data": result})

    def handle_session_progress(self, session_id: str) -> None:
        """GET /api/education/sessions/<id>/progress — get session progress."""
        try:
            result = self.education_provider.get_session_progress(session_id)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    def handle_quiz_generate(self) -> None:
        """POST /api/education/quiz — generate quiz questions."""
        body = self._read_json_body()
        if body is None:
            return
        topic = body.get("topic")
        if not topic:
            self.send_json_response(
                {"status": "error", "message": "Missing field: topic"}, status=400
            )
            return
        difficulty = body.get("difficulty", "easy")
        valid_difficulties = {"easy", "medium", "hard"}
        if difficulty not in valid_difficulties:
            self.send_json_response(
                {
                    "status": "error",
                    "message": f"Invalid difficulty: must be one of {sorted(valid_difficulties)}",
                },
                status=400,
            )
            return
        count = body.get("count", 5)
        questions = self.education_provider.generate_quiz(topic, difficulty, count)
        self.send_json_response({"status": "ok", "data": questions})

    def handle_quiz_answer(self) -> None:
        """POST /api/education/quiz/answer — evaluate and optionally record an answer."""
        body = self._read_json_body()
        if body is None:
            return
        question_id = body.get("question_id")
        answer = body.get("answer")
        if not question_id:
            self.send_json_response(
                {"status": "error", "message": "Missing field: question_id"}, status=400
            )
            return
        if answer is None:
            self.send_json_response(
                {"status": "error", "message": "Missing field: answer"}, status=400
            )
            return

        session_id = body.get("session_id")
        try:
            if session_id:
                result = self.education_provider.record_answer(
                    session_id, question_id, answer
                )
            else:
                result = self.education_provider.evaluate_answer(question_id, answer)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    # ── Assessment handlers ────────────────────────────────────────

    def handle_exam_create(self) -> None:
        """POST /api/education/exams — create an exam."""
        body = self._read_json_body()
        if body is None:
            return
        curriculum_name = body.get("curriculum_name")
        if not curriculum_name:
            self.send_json_response(
                {"status": "error", "message": "Missing field: curriculum_name"},
                status=400,
            )
            return
        module_names = body.get("module_names")
        try:
            result = self.education_provider.create_exam(curriculum_name, module_names)
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    def handle_exam_submit(self, path: str) -> None:
        """POST /api/education/exams/<id>/submit — grade an exam submission."""
        rest = path.replace("/api/education/exams/", "", 1)
        exam_id = rest.replace("/submit", "")
        body = self._read_json_body()
        if body is None:
            return
        curriculum_name = body.get("curriculum_name")
        if not curriculum_name:
            self.send_json_response(
                {"status": "error", "message": "Missing field: curriculum_name"},
                status=400,
            )
            return
        answers = body.get("answers", {})
        try:
            result = self.education_provider.grade_submission(
                curriculum_name, exam_id, answers
            )
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    def handle_certificate_generate(self) -> None:
        """POST /api/education/certificates — generate a certificate."""
        body = self._read_json_body()
        if body is None:
            return
        student = body.get("student")
        curriculum_name = body.get("curriculum_name")
        score = body.get("score")
        if not student:
            self.send_json_response(
                {"status": "error", "message": "Missing field: student"}, status=400
            )
            return
        if not curriculum_name:
            self.send_json_response(
                {"status": "error", "message": "Missing field: curriculum_name"},
                status=400,
            )
            return
        if score is None:
            self.send_json_response(
                {"status": "error", "message": "Missing field: score"}, status=400
            )
            return
        try:
            result = self.education_provider.generate_certificate(
                student, curriculum_name, float(score)
            )
            self.send_json_response({"status": "ok", "data": result})
        except KeyError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)
        except (ValueError, TypeError) as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=400)

    def handle_certificates_list(self) -> None:
        """GET /api/education/certificates — list all certificates."""
        certs = self.education_provider.list_certificates()
        self.send_json_response({"status": "ok", "data": certs})

    # ── Content browser handlers ───────────────────────────────────

    def handle_content_tree(self, query: str) -> None:
        """GET /api/content/tree?path= — list output file tree."""
        from urllib.parse import parse_qs

        params = parse_qs(query)
        subpath = params.get("path", [""])[0]
        try:
            result = self.education_provider.list_output_files(subpath)
            self.send_json_response({"status": "ok", "data": result})
        except PermissionError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=403)
        except ValueError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=403)
        except FileNotFoundError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    def handle_content_file(self, query: str) -> None:
        """GET /api/content/file?path= — get file content or serve file."""
        from urllib.parse import parse_qs

        params = parse_qs(query)
        filepath = params.get("path", [""])[0]
        if not filepath:
            self.send_json_response(
                {"status": "error", "message": "Missing query parameter: path"},
                status=400,
            )
            return
        try:
            result = self.education_provider.get_file_content(filepath)
            self.send_json_response({"status": "ok", "data": result})
        except PermissionError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=403)
        except ValueError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=403)
        except FileNotFoundError as e:
            self.send_json_response({"status": "error", "message": str(e)}, status=404)

    def handle_trust_status(self) -> None:
        """Handle GET /api/trust/status — return trust gateway tool counts."""
        try:
            from codomyrmex.agents.pai.trust_gateway import get_trust_report

            report = get_trust_report()
            counts = report.get("counts", {})
            self.send_json_response(
                {
                    "counts": {
                        "untrusted": counts.get("untrusted", 0),
                        "verified": counts.get("verified", 0),
                        "trusted": counts.get("trusted", 0),
                    },
                    "total_tools": report.get("total_tools", 0),
                    "destructive_tools": report.get("destructive_tools", {}),
                }
            )
        except Exception as e:
            # Fallback if trust gateway not available
            self.send_json_response(
                {
                    "counts": {"untrusted": 0, "verified": 0, "trusted": 0},
                    "error": str(e),
                }
            )

    def handle_pai_action(self) -> None:
        """Handle POST /api/pai/action — execute a PAI workflow action."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response({"error": "No content provided"}, status=400)
            return
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
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
                    "modules": len(raw.get("modules", [])),
                    "tools_total": raw.get("tools", {}).get("total", 0),
                    "promoted": raw.get("trust", {}).get("promoted", 0),
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
                from codomyrmex.agents.pai.mcp_bridge import _tool_pai_status

                result = _tool_pai_status()
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

            self.send_json_response(
                {
                    "success": True,
                    "action": action,
                    "result": result,
                    "trust_counts": {
                        "untrusted": counts.get("untrusted", 0),
                        "verified": counts.get("verified", 0),
                        "trusted": counts.get("trusted", 0),
                    },
                }
            )
        except Exception as e:
            self.send_json_response(
                {"success": False, "error": str(e), "action": action},
                status=500,
            )

    def send_json_response(self, data: dict | list, status: int = 200) -> None:
        """Send a JSON response with the given data and HTTP status code."""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", f"http://localhost:{_PORT}")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Origin")
        self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
