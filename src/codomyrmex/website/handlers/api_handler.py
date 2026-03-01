"""API endpoint handlers for WebsiteServer.

Handles /api/* routes for modules, agents, scripts, config,
docs, pipelines, tools, tests, PAI actions, and agent dispatch.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from typing import Any
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
                cwd=self.root_dir,  # Run from project root
                timeout=300  # 5 minute timeout safety
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

    def handle_tests_run(self) -> None:
        """Handle POST /api/tests -- run tests for a module.

        Runs tests in a background thread so the HTTP server stays
        responsive. Returns 202 Accepted immediately. Poll
        GET /api/tests/status to retrieve results.
        """
        # Import the server class to access class-level state
        from ..server import WebsiteServer

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
        """Handle GET /api/tests/status -- poll for test results."""
        from ..server import WebsiteServer

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
        """Handle POST /api/pai/action -- execute a PAI workflow action."""
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
        """Handle POST /api/agent/dispatch -- start an orchestrator run."""
        from ..server import WebsiteServer

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
        """Handle POST /api/agent/dispatch/stop -- stop orchestrator."""
        from ..server import WebsiteServer

        with self._dispatch_lock:
            if WebsiteServer._dispatch_orch:
                # Stop logic if supported by orchestrator
                WebsiteServer._dispatch_orch = None
            self.send_json_response({"success": True, "message": "Stop signal sent"})

    def handle_agent_dispatch_status(self) -> None:
        """Handle GET /api/agent/dispatch/status -- poll transcript."""
        from ..server import WebsiteServer

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
