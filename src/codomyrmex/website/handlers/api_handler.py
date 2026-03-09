"""API endpoint handlers for WebsiteServer.

Handles /api/* routes for modules, agents, scripts, config,
docs, pipelines, tools, tests, PAI actions, and agent dispatch.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
from urllib.parse import urlparse

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class APIHandler:
    """Mixin providing /api/* endpoint handlers for WebsiteServer.

    Expects the host class to provide:
    - self.data_provider: DataProvider instance
    - self.root_dir: Path to project root
    - self.headers: HTTP request headers
    - self.rfile: request input stream
    - self.path: request path
    - self.send_json_response(data, status): JSON response sender
    - self.send_error(code, msg): error response sender
    """

    # Store latest test results for async retrieval
    _test_results: dict | None = None

    # Config files must carry one of these extensions to be readable/writable.
    _ALLOWED_CONFIG_EXTENSIONS: frozenset[str] = frozenset(
        {
            ".json",
            ".toml",
            ".yaml",
            ".yml",
        }
    )

    # ── shared helpers ───────────────────────────────────────────────────

    def _read_json_body(self) -> dict | None:
        """Parse JSON from POST body.

        Returns the parsed dict on success, or ``None`` after sending an
        appropriate error response to the client.
        """
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0
        if content_length == 0:
            self.send_json_response({"error": "No content provided"}, status=400)
            return None
        try:
            raw = self.rfile.read(content_length)
            payload = raw.decode("utf-8").strip()
            if not payload:
                self.send_json_response({"error": "No content provided"}, status=400)
                return None
            return json.loads(payload)
        except (json.JSONDecodeError, KeyError):
            self.send_json_response({"error": "Invalid JSON"}, status=400)
            return None

    def _is_allowed_config_file(self, filename: str) -> bool:
        """Return True if *filename* has an allowed config file extension.

        Uses a static extension whitelist so the check does not depend on the
        data provider being present — callers must separately guard against a
        missing data provider before invoking this method.
        """
        _, ext = os.path.splitext(filename)
        return ext.lower() in self._ALLOWED_CONFIG_EXTENSIONS

    def handle_modules_list(self) -> None:
        """Handle GET /api/modules -- return all modules."""
        if self.data_provider:
            modules = self.data_provider.get_modules()
            self.send_json_response(modules)
        else:
            self.send_error(500, "Data provider missing")

    def handle_module_detail(self, path: str) -> None:
        """Handle GET /api/modules/{name} -- return single module detail."""
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
        """Handle GET /api/tools -- return all MCP tools, resources, and prompts."""
        if not self.data_provider:
            self.send_error(500, "Data provider missing")
            return
        tools_data = self.data_provider.get_mcp_tools()
        self.send_json_response(tools_data)

    def handle_agents_list(self) -> None:
        """Handle GET /api/agents -- return actual AI agents."""
        if self.data_provider:
            agents = self.data_provider.get_actual_agents()
            self.send_json_response(agents)
        else:
            self.send_error(500, "Data provider missing")

    def handle_scripts_list(self) -> None:
        """Handle GET /api/scripts -- return available scripts."""
        if self.data_provider:
            scripts = self.data_provider.get_available_scripts()
            self.send_json_response(scripts)
        else:
            self.send_error(500, "Data provider missing")

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
        if not self.data_provider:
            self.send_json_response({"error": "Data provider missing"}, status=500)
            return
        if not self._is_allowed_config_file(filename):
            self.send_json_response(
                {"error": f"Config file '{filename}' is not in the allowed list"},
                status=403,
            )
            return
        try:
            content = self.data_provider.get_config_content(filename)
            self.send_json_response({"content": content})
        except FileNotFoundError as e:
            self.send_json_response({"error": str(e)}, status=404)
        except ValueError as e:
            self.send_json_response({"error": str(e)}, status=403)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)

    def handle_config_save(self) -> None:
        """Handle config save request."""
        data = self._read_json_body()
        if data is None:
            return

        content = data.get("content")
        filename = data.get("filename")

        if not filename:
            # Extract from URL path
            parsed_path = urlparse(self.path)
            filename = parsed_path.path.replace("/api/config/", "")

        if not content or not filename:
            self.send_error(400, "Missing filename or content")
            return

        if not self.data_provider:
            self.send_error(500, "Data provider missing")
            return

        if not self._is_allowed_config_file(filename):
            self.send_json_response(
                {"error": f"Config file '{filename}' is not in the allowed list"},
                status=403,
            )
            return

        try:
            self.data_provider.save_config_content(filename, content)
            self.send_json_response({"success": True, "filename": filename})
        except ValueError as e:
            self.send_json_response({"success": False, "error": str(e)}, status=403)
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, status=500)

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
        """Handle GET /api/docs/{path} -- return doc file content."""
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

    def handle_execute(self) -> None:
        """Execute a script from the scripts directory."""
        data = self._read_json_body()
        if data is None:
            return

        script_name = data.get("script")
        raw_args = data.get("args", [])

        if not script_name:
            self.send_error(400, "Script name required")
            return

        # CWE-78: Validate args are plain strings with no shell metacharacters
        if not isinstance(raw_args, list):
            self.send_error(400, "args must be a list of strings")
            return
        _SHELL_META = set(";&|`$(){}\n\r")
        sanitized_args: list[str] = []
        for arg in raw_args:
            if not isinstance(arg, str):
                self.send_error(400, f"Invalid arg type: {type(arg).__name__}")
                return
            if any(ch in _SHELL_META for ch in arg):
                self.send_error(400, f"Arg contains forbidden characters: {arg!r}")
                return
            sanitized_args.append(arg)

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
            cmd = [sys.executable, str(script_path), *sanitized_args]
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

    def handle_tests_run(self) -> None:
        """Handle POST /api/tests -- run tests for a module.

        Runs tests in a background thread so the HTTP server stays
        responsive. Returns 202 Accepted immediately. Poll
        GET /api/tests/status to retrieve results.
        """
        # Import the server class to access class-level state
        from codomyrmex.website.server import WebsiteServer

        with self._test_lock:
            if self._test_running:
                self.send_json_response(
                    {"error": "A test run is already in progress. Please wait."},
                    status=429,
                )
                return
            WebsiteServer._test_running = True

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
        """Handle GET /api/tests/status -- poll for test results."""
        from codomyrmex.website.server import WebsiteServer

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

    def handle_trust_status(self) -> None:
        """Handle GET /api/trust/status -- return trust gateway tool counts."""
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

    # ── PAI action sub-handlers ───────────────────────────────────────

    def _pai_verify(self, _data: dict) -> dict:
        """Execute PAI verify action."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        raw = verify_capabilities()
        return {
            "modules": raw.get("modules", {}).get("total", 0),
            "tools_total": raw.get("tools", {}).get("total", 0),
            "promoted": len(
                raw.get("trust", {}).get("promoted_to_verified", [])
            ),
        }

    def _pai_trust(self, _data: dict) -> dict:
        """Execute PAI trust-all action."""
        from codomyrmex.agents.pai.trust_gateway import trust_all

        return trust_all()

    def _pai_reset(self, _data: dict) -> dict:
        """Execute PAI trust reset action."""
        from codomyrmex.agents.pai.trust_gateway import reset_trust

        reset_trust()
        return {"message": "Trust levels reset to UNTRUSTED"}

    def _pai_status(self, _data: dict) -> dict:
        """Execute PAI status check."""
        try:
            from codomyrmex.agents.pai.mcp_bridge import tool_pai_status

            return tool_pai_status()
        except Exception as exc:
            return {
                "status": "degraded",
                "error": str(exc),
                "available": False,
            }

    def _pai_analyze(self, _data: dict) -> dict:
        """Execute PAI system analysis."""
        modules = self.data_provider.get_modules() if self.data_provider else []
        summary = (
            self.data_provider.get_system_summary()
            if self.data_provider
            else {}
        )
        active = sum(1 for m in modules if m.get("status") == "Active")
        error_count = sum(
            1 for m in modules if m.get("status") not in ("Active", "Unknown")
        )
        return {
            "total_modules": len(modules),
            "active_modules": active,
            "error_modules": error_count,
            "system": summary,
        }

    def _pai_search(self, data: dict) -> dict | None:
        """Execute PAI module search.

        Returns None after sending an error response when the query is empty.
        """
        query = data.get("query", "").strip()
        if not query:
            self.send_json_response(
                {"error": "search requires 'query' field", "success": False},
                status=400,
            )
            return None
        # CWE-1333: Escape user input to prevent regex injection / ReDoS
        escaped_query = re.escape(query)
        pattern = re.compile(escaped_query, re.IGNORECASE)
        modules = self.data_provider.get_modules() if self.data_provider else []
        hits = [
            m
            for m in modules
            if pattern.search(m.get("name", ""))
            or pattern.search(m.get("description", ""))
        ]
        return {"query": query, "hits": hits, "count": len(hits)}

    def _pai_docs(self, data: dict) -> dict | None:
        """Execute PAI docs lookup.

        Returns None after sending an error response when the module is missing.
        """
        module_name = data.get("module", "").strip()
        if not module_name:
            self.send_json_response(
                {"error": "docs requires 'module' field", "success": False},
                status=400,
            )
            return None
        detail = (
            self.data_provider.get_module_detail(module_name)
            if self.data_provider
            else None
        )
        if detail is None:
            self.send_json_response(
                {
                    "error": f"Module '{module_name}' not found",
                    "success": False,
                },
                status=404,
            )
            return None
        return detail

    def _pai_add_memory(self, data: dict) -> dict | None:
        """Execute PAI add-memory action.

        Returns None after sending an error response when content is empty.
        """
        from codomyrmex.agentic_memory.mcp_tools import memory_put

        content = data.get("content", "")
        if not content:
            self.send_json_response(
                {
                    "error": "Content is required for add_memory",
                    "success": False,
                },
                status=400,
            )
            return None
        return memory_put(content=content)

    # Dispatch table mapping action names to handler methods.
    _PAI_ACTION_DISPATCH: dict[str, str] = {
        "verify": "_pai_verify",
        "trust": "_pai_trust",
        "reset": "_pai_reset",
        "status": "_pai_status",
        "analyze": "_pai_analyze",
        "search": "_pai_search",
        "docs": "_pai_docs",
        "add_memory": "_pai_add_memory",
    }

    def handle_pai_action(self) -> None:
        """Handle POST /api/pai/action -- execute a PAI workflow action."""
        data = self._read_json_body()
        if data is None:
            return

        action = data.get("action", "")
        handler_name = self._PAI_ACTION_DISPATCH.get(action)

        if handler_name is None:
            self.send_json_response(
                {"error": f"Unknown action: {action}", "success": False},
                status=400,
            )
            return

        try:
            handler_fn = getattr(self, handler_name)
            result = handler_fn(data)

            # Sub-handlers return None when they've already sent an error
            if result is None:
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

    def handle_agent_dispatch(self) -> None:
        """Handle POST /api/agent/dispatch -- start an orchestrator run."""
        from codomyrmex.website.server import WebsiteServer

        data = self._read_json_body()
        if data is None:
            return

        seed_prompt = data.get("prompt", "Analyze the current context.")
        todo_path = data.get("todo", "")
        agents = data.get("agents")

        with self._dispatch_lock:
            if (
                WebsiteServer._dispatch_thread
                and WebsiteServer._dispatch_thread.is_alive()
            ):
                self.send_json_response(
                    {"error": "A dispatch run is already in progress"}, status=429
                )
                return

            try:

                from codomyrmex.agents.orchestrator import ConversationOrchestrator

                if todo_path:
                    WebsiteServer._dispatch_orch = ConversationOrchestrator.dev_loop(
                        todo_path=todo_path,
                        channel=f"dispatch-{int(time.time())}",
                        agents=agents,
                    )
                else:
                    default_agents = [
                        {
                            "identity": "architect",
                            "persona": "system planner",
                            "provider": "ollama",
                        },
                        {
                            "identity": "reviewer",
                            "persona": "code executor",
                            "provider": "antigravity",
                        },
                    ]
                    WebsiteServer._dispatch_orch = ConversationOrchestrator(
                        channel=f"dispatch-{int(time.time())}",
                        seed_prompt=seed_prompt,
                        agents=agents or default_agents,
                    )

                def run_orch():
                    try:
                        WebsiteServer._dispatch_orch.run(rounds=3)
                    except Exception as e:
                        logger.error("Dispatch error: %s", e)

                WebsiteServer._dispatch_thread = threading.Thread(
                    target=run_orch, daemon=True
                )
                WebsiteServer._dispatch_thread.start()

                self.send_json_response(
                    {
                        "success": True,
                        "message": "Dispatch started",
                        "channel": WebsiteServer._dispatch_orch.channel_id,
                    }
                )
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)

    def handle_agent_dispatch_stop(self) -> None:
        """Handle POST /api/agent/dispatch/stop -- stop orchestrator."""
        from codomyrmex.website.server import WebsiteServer

        with self._dispatch_lock:
            if WebsiteServer._dispatch_orch:
                # Stop logic if supported by orchestrator
                WebsiteServer._dispatch_orch = None
            self.send_json_response({"success": True, "message": "Stop signal sent"})

    def handle_agent_dispatch_status(self) -> None:
        """Handle GET /api/agent/dispatch/status -- poll transcript."""
        from codomyrmex.website.server import WebsiteServer

        with self._dispatch_lock:
            if not WebsiteServer._dispatch_orch:
                self.send_json_response({"active": False, "turns": []})
                return

            try:
                from dataclasses import asdict

                log = WebsiteServer._dispatch_orch.get_log()
                turns = [asdict(t) for t in log.turns]

                is_active = (
                    WebsiteServer._dispatch_thread
                    and WebsiteServer._dispatch_thread.is_alive()
                )

                self.send_json_response(
                    {"active": is_active, "summary": log.summary(), "turns": turns}
                )
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)
