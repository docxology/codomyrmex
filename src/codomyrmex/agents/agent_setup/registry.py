"""Agent Registry — declarative catalog and live health probes.

Every known agent is described by an ``AgentDescriptor`` that captures its
type (``api``, ``cli``, or ``local``), environment variable for the primary
credential, and a probe function that returns a ``ProbeResult``.
"""

from __future__ import annotations

import importlib
import os
import shutil
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL
from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

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
    client_module: str | None = None
    client_class: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-safe descriptor without exposing the probe callable."""
        client_path = None
        if self.client_module and self.client_class:
            client_path = f"{self.client_module}.{self.client_class}"
        return {
            "name": self.name,
            "display_name": self.display_name,
            "agent_type": self.agent_type,
            "env_var": self.env_var,
            "config_key": self.config_key,
            "default_model": self.default_model,
            "client_path": client_path,
        }


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
            name=name,
            status="operative",
            detail=f"Key present ({env_var}={key[:4]}...)",
            latency_ms=round(elapsed, 2),
        )
    return ProbeResult(
        name=name,
        status="key_missing",
        detail=f"set {env_var} to enable",
    )


def _probe_cli_binary(name: str, binary: str) -> ProbeResult:
    """Check if a CLI binary is on PATH."""
    start = time.time()
    path = shutil.which(binary)
    elapsed = (time.time() - start) * 1000
    if path:
        return ProbeResult(
            name=name,
            status="operative",
            detail=f"Found at {path}",
            latency_ms=round(elapsed, 2),
        )
    return ProbeResult(
        name=name,
        status="unavailable",
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
            name="ollama",
            status="operative",
            detail=f"{count} model(s): {summary}"
            if count
            else "Server up, no models pulled",
            latency_ms=round(elapsed, 2),
        )
    except (urllib.error.URLError, OSError, Exception) as exc:
        elapsed = (time.time() - start) * 1000
        return ProbeResult(
            name="ollama",
            status="unreachable",
            detail=f"Cannot reach {base_url}: {exc}",
            latency_ms=round(elapsed, 2),
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class AgentRegistry:
    """Central catalog of all known agents with live probing."""

    def __init__(self, ollama_base_url: str = ""):
        ollama_base_url = ollama_base_url or os.getenv(
            "OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL
        )
        self._ollama_base_url = ollama_base_url
        self._descriptors: list[AgentDescriptor] = self._build_catalog()

    # -- public API ---------------------------------------------------------

    def list_agents(self) -> list[AgentDescriptor]:
        """Return all known agent descriptors."""
        return list(self._descriptors)

    def get_descriptor(self, name: str) -> AgentDescriptor | None:
        """Return a descriptor by stable name, or ``None`` when unknown."""
        normalized = name.strip().lower()
        return next(
            (
                descriptor
                for descriptor in self._descriptors
                if descriptor.name == normalized
            ),
            None,
        )

    def create_agent(
        self, name: str, config: dict[str, object] | None = None
    ) -> object:
        """Instantiate a registered agent client without running a live probe.

        Construction is deliberately separate from :meth:`probe_agent`: a probe
        answers "is the integration configured?", while this method resolves the
        actual client used by ``execute_agent``. Provider constructors are allowed
        to fail with their normal configuration error so callers can report an
        actionable dispatch failure instead of claiming success.
        """
        descriptor = self.get_descriptor(name)
        if descriptor is None:
            raise ValueError(f"Unknown agent '{name}'.")

        # OllamaClient is a lightweight local client with a deliberately
        # different constructor (model/base_url rather than config).  Keep it
        # in the same executable catalog as the other providers instead of
        # advertising a descriptor that root MCP dispatch cannot instantiate.
        if descriptor.name == "ollama":
            from codomyrmex.agents.llm_client import OllamaClient

            supplied = config or {}
            model = str(supplied.get("model", descriptor.default_model))
            base_url = str(supplied.get("base_url", self._ollama_base_url))
            return OllamaClient(model=model, base_url=base_url)

        if not descriptor.client_module or not descriptor.client_class:
            raise RuntimeError(
                f"Agent '{descriptor.name}' is catalogued but has no executable client."
            )

        try:
            module = importlib.import_module(descriptor.client_module)
            client_class = getattr(module, descriptor.client_class)
        except (ImportError, AttributeError) as exc:
            raise RuntimeError(
                f"Agent '{descriptor.name}' client is unavailable: {exc}"
            ) from exc

        if not callable(client_class):
            raise RuntimeError(
                f"Agent '{descriptor.name}' client target is not callable."
            )
        try:
            return client_class(config=config or {})
        except TypeError as exc:
            raise RuntimeError(
                f"Agent '{descriptor.name}' client could not be constructed: {exc}"
            ) from exc

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
                results.append(
                    ProbeResult(
                        name=desc.name,
                        status="unreachable",
                        detail=f"Probe error: {exc}",
                    )
                )
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
                name="claude",
                display_name="Claude (Anthropic)",
                agent_type="api",
                env_var="ANTHROPIC_API_KEY",
                config_key="claude_api_key",
                default_model="claude-3-opus-20240229",
                probe=lambda: _probe_api_key_env("claude", "ANTHROPIC_API_KEY"),
                client_module="codomyrmex.agents.claude",
                client_class="ClaudeClient",
            ),
            AgentDescriptor(
                name="codex",
                display_name="Codex (OpenAI)",
                agent_type="api",
                env_var="OPENAI_API_KEY",
                config_key="codex_api_key",
                default_model="code-davinci-002",
                probe=lambda: _probe_api_key_env("codex", "OPENAI_API_KEY"),
                client_module="codomyrmex.agents.codex",
                client_class="CodexClient",
            ),
            AgentDescriptor(
                name="o1",
                display_name="O1/O3 (OpenAI)",
                agent_type="api",
                env_var="OPENAI_API_KEY",
                config_key="o1_api_key",
                default_model="o1",
                probe=lambda: _probe_api_key_env("o1", "OPENAI_API_KEY"),
                client_module="codomyrmex.agents.o1",
                client_class="O1Client",
            ),
            AgentDescriptor(
                name="deepseek",
                display_name="DeepSeek Coder",
                agent_type="api",
                env_var="DEEPSEEK_API_KEY",
                config_key="deepseek_api_key",
                default_model="deepseek-coder",
                probe=lambda: _probe_api_key_env("deepseek", "DEEPSEEK_API_KEY"),
                client_module="codomyrmex.agents.deepseek",
                client_class="DeepSeekClient",
            ),
            AgentDescriptor(
                name="qwen",
                display_name="Qwen-Coder (Alibaba)",
                agent_type="api",
                env_var="DASHSCOPE_API_KEY",
                config_key="qwen_api_key",
                default_model="qwen-coder-plus",
                probe=lambda: _probe_api_key_env("qwen", "DASHSCOPE_API_KEY"),
                client_module="codomyrmex.agents.qwen",
                client_class="QwenClient",
            ),
            AgentDescriptor(
                name="perplexity",
                display_name="Perplexity API",
                agent_type="api",
                env_var="PERPLEXITY_API_KEY",
                config_key="perplexity_api_key",
                default_model="sonar",
                probe=lambda: _probe_api_key_env("perplexity", "PERPLEXITY_API_KEY"),
                client_module="codomyrmex.agents.perplexity",
                client_class="PerplexityClient",
            ),
            # ── CLI agents ────────────────────────────────────────────
            AgentDescriptor(
                name="jules",
                display_name="Jules CLI (Google)",
                agent_type="cli",
                env_var="JULES_COMMAND",
                config_key="jules_command",
                default_model="n/a",
                probe=lambda: _probe_cli_binary("jules", "jules"),
                client_module="codomyrmex.agents.jules",
                client_class="JulesClient",
            ),
            AgentDescriptor(
                name="opencode",
                display_name="OpenCode CLI",
                agent_type="cli",
                env_var="OPENCODE_COMMAND",
                config_key="opencode_command",
                default_model="n/a",
                probe=lambda: _probe_cli_binary("opencode", "opencode"),
                client_module="codomyrmex.agents.opencode",
                client_class="OpenCodeClient",
            ),
            AgentDescriptor(
                name="gemini",
                display_name="Gemini CLI (Google)",
                agent_type="cli",
                env_var="GEMINI_COMMAND",
                config_key="gemini_command",
                default_model="gemini-2.0-flash",
                probe=lambda: _probe_cli_binary("gemini", "gemini"),
                client_module="codomyrmex.agents.gemini",
                client_class="GeminiClient",
            ),
            AgentDescriptor(
                name="mistral_vibe",
                display_name="Mistral Vibe CLI",
                agent_type="cli",
                env_var="MISTRAL_VIBE_COMMAND",
                config_key="mistral_vibe_command",
                default_model="n/a",
                probe=lambda: _probe_cli_binary("mistral_vibe", "vibe"),
                client_module="codomyrmex.agents.mistral_vibe",
                client_class="MistralVibeClient",
            ),
            AgentDescriptor(
                name="hermes",
                display_name="Hermes Agent CLI (NousResearch)",
                agent_type="cli",
                env_var="HERMES_COMMAND",
                config_key="hermes_command",
                default_model="n/a",
                probe=lambda: _probe_cli_binary("hermes", "hermes"),
                client_module="codomyrmex.agents.hermes",
                client_class="HermesClient",
            ),
            AgentDescriptor(
                name="every_code",
                display_name="Every Code CLI",
                agent_type="cli",
                env_var="EVERY_CODE_COMMAND",
                config_key="every_code_command",
                default_model="n/a",
                probe=lambda: _probe_cli_binary("every_code", "code"),
                client_module="codomyrmex.agents.every_code",
                client_class="EveryCodeClient",
            ),
            # ── Local / Ollama ────────────────────────────────────────
            AgentDescriptor(
                name="ollama",
                display_name="Ollama (Local LLMs)",
                agent_type="local",
                env_var="OLLAMA_BASE_URL",
                config_key="ollama_base_url",
                default_model="llama3.2",
                probe=lambda: _probe_ollama(url),
                client_module="codomyrmex.agents.llm_client",
                client_class="OllamaClient",
            ),
        ]
