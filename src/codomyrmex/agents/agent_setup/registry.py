"""Agent Registry — declarative catalog and live health probes.

Every known agent is described by an ``AgentDescriptor`` that captures its
type (``api``, ``cli``, or ``local``), environment variable for the primary
credential, and a probe function that returns a ``ProbeResult``.
"""

from __future__ import annotations

import os
import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ProbeResult:
    """Result of probing a single agent's availability."""

    name: str
    status: str  # "operative" | "key_missing" | "unreachable" | "unavailable"
    detail: str
    latency_ms: float | None = None

    @property
    def is_operative(self) -> bool:
        return self.status == "operative"


@dataclass
class AgentDescriptor:
    """Declarative description of a known agent."""

    name: str
    display_name: str
    agent_type: str  # "api" | "cli" | "local"
    env_var: str  # primary env var (API key, or informational for CLI)
    config_key: str  # AgentConfig field for the key/url
    default_model: str
    probe: Callable[[], ProbeResult] = field(repr=False)


# ---------------------------------------------------------------------------
# Probe helpers (real network / process checks — zero mocks)
# ---------------------------------------------------------------------------

def _probe_api_key_env(name: str, env_var: str) -> ProbeResult:
    """Check if an API key env var is set (basic reachability)."""
    start = time.time()
    key = os.environ.get(env_var)
    elapsed = (time.time() - start) * 1000
    if key:
        return ProbeResult(
            name=name, status="operative",
            detail=f"Key present ({env_var}={key[:4]}...)",
            latency_ms=round(elapsed, 2),
        )
    return ProbeResult(
        name=name, status="key_missing",
        detail=f"Set {env_var} to enable",
    )


def _probe_cli_binary(name: str, binary: str) -> ProbeResult:
    """Check if a CLI binary is on PATH."""
    start = time.time()
    path = shutil.which(binary)
    elapsed = (time.time() - start) * 1000
    if path:
        return ProbeResult(
            name=name, status="operative",
            detail=f"Found at {path}",
            latency_ms=round(elapsed, 2),
        )
    return ProbeResult(
        name=name, status="unavailable",
        detail=f"Binary '{binary}' not found on PATH",
    )


def _probe_ollama(base_url: str = "") -> ProbeResult:
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)
    """Check Ollama server reachability and list models."""
    import json as _json
    import urllib.error
    import urllib.request

    start = time.time()
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = _json.loads(resp.read().decode())
        elapsed = (time.time() - start) * 1000
        models = [m.get("name", "?") for m in data.get("models", [])]
        count = len(models)
        summary = ", ".join(models[:5])
        if count > 5:
            summary += f" … (+{count - 5} more)"
        return ProbeResult(
            name="ollama", status="operative",
            detail=f"{count} model(s): {summary}" if count else "Server up, no models pulled",
            latency_ms=round(elapsed, 2),
        )
    except (urllib.error.URLError, OSError, Exception) as exc:
        elapsed = (time.time() - start) * 1000
        return ProbeResult(
            name="ollama", status="unreachable",
            detail=f"Cannot reach {base_url}: {exc}",
            latency_ms=round(elapsed, 2),
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """Central catalog of all known agents with live probing."""

    def __init__(self, ollama_base_url: str = ""):
        ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)
        self._ollama_base_url = ollama_base_url
        self._descriptors: list[AgentDescriptor] = self._build_catalog()

    # -- public API ---------------------------------------------------------

    def list_agents(self) -> list[AgentDescriptor]:
        """Return all known agent descriptors."""
        return list(self._descriptors)

    def probe_agent(self, name: str) -> ProbeResult:
        """Probe a single agent by name."""
        for desc in self._descriptors:
            if desc.name == name:
                return desc.probe()
        return ProbeResult(name=name, status="unavailable", detail="Unknown agent")

    def probe_all(self) -> list[ProbeResult]:
        """Probe every registered agent and return results."""
        results = []
        for desc in self._descriptors:
            try:
                results.append(desc.probe())
            except Exception as exc:
                logger.warning("Probe failed for %s: %s", desc.name, exc)
                results.append(ProbeResult(
                    name=desc.name, status="unreachable",
                    detail=f"Probe error: {exc}",
                ))
        return results

    def get_operative(self) -> list[str]:
        """Return names of agents that are currently operative."""
        return [r.name for r in self.probe_all() if r.is_operative]

    # -- catalog construction -----------------------------------------------

    def _build_catalog(self) -> list[AgentDescriptor]:
        url = self._ollama_base_url
        return [
            # ── API agents ────────────────────────────────────────────
            AgentDescriptor(
                name="claude", display_name="Claude (Anthropic)",
                agent_type="api", env_var="ANTHROPIC_API_KEY",
                config_key="claude_api_key", default_model="claude-3-opus-20240229",
                probe=lambda: _probe_api_key_env("claude", "ANTHROPIC_API_KEY"),
            ),
            AgentDescriptor(
                name="codex", display_name="Codex (OpenAI)",
                agent_type="api", env_var="OPENAI_API_KEY",
                config_key="codex_api_key", default_model="code-davinci-002",
                probe=lambda: _probe_api_key_env("codex", "OPENAI_API_KEY"),
            ),
            AgentDescriptor(
                name="o1", display_name="O1/O3 (OpenAI)",
                agent_type="api", env_var="OPENAI_API_KEY",
                config_key="o1_api_key", default_model="o1",
                probe=lambda: _probe_api_key_env("o1", "OPENAI_API_KEY"),
            ),
            AgentDescriptor(
                name="deepseek", display_name="DeepSeek Coder",
                agent_type="api", env_var="DEEPSEEK_API_KEY",
                config_key="deepseek_api_key", default_model="deepseek-coder",
                probe=lambda: _probe_api_key_env("deepseek", "DEEPSEEK_API_KEY"),
            ),
            AgentDescriptor(
                name="qwen", display_name="Qwen-Coder (Alibaba)",
                agent_type="api", env_var="DASHSCOPE_API_KEY",
                config_key="qwen_api_key", default_model="qwen-coder-plus",
                probe=lambda: _probe_api_key_env("qwen", "DASHSCOPE_API_KEY"),
            ),
            # ── CLI agents ────────────────────────────────────────────
            AgentDescriptor(
                name="jules", display_name="Jules CLI (Google)",
                agent_type="cli", env_var="JULES_COMMAND",
                config_key="jules_command", default_model="n/a",
                probe=lambda: _probe_cli_binary("jules", "jules"),
            ),
            AgentDescriptor(
                name="opencode", display_name="OpenCode CLI",
                agent_type="cli", env_var="OPENCODE_COMMAND",
                config_key="opencode_command", default_model="n/a",
                probe=lambda: _probe_cli_binary("opencode", "opencode"),
            ),
            AgentDescriptor(
                name="gemini", display_name="Gemini CLI (Google)",
                agent_type="cli", env_var="GEMINI_COMMAND",
                config_key="gemini_command", default_model="gemini-2.0-flash",
                probe=lambda: _probe_cli_binary("gemini", "gemini"),
            ),
            AgentDescriptor(
                name="mistral_vibe", display_name="Mistral Vibe CLI",
                agent_type="cli", env_var="MISTRAL_VIBE_COMMAND",
                config_key="mistral_vibe_command", default_model="n/a",
                probe=lambda: _probe_cli_binary("mistral_vibe", "vibe"),
            ),
            AgentDescriptor(
                name="every_code", display_name="Every Code CLI",
                agent_type="cli", env_var="EVERY_CODE_COMMAND",
                config_key="every_code_command", default_model="n/a",
                probe=lambda: _probe_cli_binary("every_code", "code"),
            ),
            # ── Local / Ollama ────────────────────────────────────────
            AgentDescriptor(
                name="ollama", display_name="Ollama (Local LLMs)",
                agent_type="local", env_var="OLLAMA_BASE_URL",
                config_key="ollama_base_url", default_model="llama3.2",
                probe=lambda: _probe_ollama(url),
            ),
        ]
