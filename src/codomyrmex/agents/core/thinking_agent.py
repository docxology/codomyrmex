"""ThinkingAgent — deliberative agent with Chain-of-Thought reasoning.

Extends the ``AgentProtocol`` plan → act → observe lifecycle with an
explicit reasoning loop: **observe → think → reason → act → reflect**.

The agent:
1. Observes the request and any prior context.
2. Thinks via the ``ChainOfThought`` pipeline (producing a ``ReasoningTrace``).
3. Reasons about the conclusion to decide on an action.
4. Acts by executing the chosen action.
5. Reflects on the result to update its reasoning trace.

All traces are stored for later retrieval, distillation, or debugging.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentInterface,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.llm.chain_of_thought import ChainOfThought
from codomyrmex.llm.context_manager import ContextManager
from codomyrmex.llm.models.reasoning import (
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ThinkingAgentConfig:
    """Configuration for the ThinkingAgent.

    Attributes:
        depth: Default reasoning depth.
        max_context_tokens: Token budget for the context window.
        max_traces: Maximum number of traces to retain.
        reflect_on_errors: Whether to add a reflection step on failures.
    """

    depth: ThinkingDepth = ThinkingDepth.NORMAL
    max_context_tokens: int = 4096
    max_traces: int = 100
    reflect_on_errors: bool = True


class ThinkingAgent(AgentInterface):
    """Agent that reasons before acting using Chain-of-Thought.

    Implements the full ``AgentProtocol`` lifecycle with an injected
    ``ChainOfThought`` pipeline and ``ContextManager``.

    Usage::

        agent = ThinkingAgent()
        request = AgentRequest(prompt="Explain the observer pattern")
        response = agent.execute(request)
        print(response.content)
        print(agent.last_trace.to_json())
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        thinking_config: ThinkingAgentConfig | None = None,
        knowledge_retriever: Any | None = None,
    ) -> None:
        super().__init__(config)
        self._thinking_config = thinking_config or ThinkingAgentConfig()
        self._cot = ChainOfThought(depth=self._thinking_config.depth)
        self._context = ContextManager(
            max_tokens=self._thinking_config.max_context_tokens,
        )
        self._traces: list[ReasoningTrace] = []
        self._knowledge_retriever = knowledge_retriever

    # ── AgentInterface implementation ─────────────────────────────

    def get_capabilities(self) -> list[AgentCapabilities]:
        """Return supported capabilities."""
        return [
            AgentCapabilities.TEXT_COMPLETION,
            AgentCapabilities.CODE_ANALYSIS,
            AgentCapabilities.EXTENDED_THINKING,
        ]

    def supports_capability(self, capability: AgentCapabilities) -> bool:
        """Check if the agent supports a specific capability."""
        return capability in self.get_capabilities()

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the observe → think → reason → act → reflect loop.

        Args:
            request: The agent request.

        Returns:
            AgentResponse with the reasoning-informed output.
        """
        import time
        t0 = time.monotonic()

        # 1. Observe — add request to context
        self._context.add_message("user", request.prompt)
        context_data = {
            "prompt": request.prompt,
            "context_messages": self._context.message_count,
        }
        if request.context:
            context_data.update(request.context)

        # 1b. Knowledge retrieval — inject graph context if available
        if self._knowledge_retriever is not None:
            try:
                graph_ctx = self._knowledge_retriever.retrieve(request.prompt)
                context_data["knowledge_entities"] = [
                    {"name": e.name, "type": e.entity_type.value if hasattr(e.entity_type, "value") else str(e.entity_type)}
                    for e in graph_ctx.entities[:10]
                ]
                context_data["knowledge_relationships"] = [
                    {"source": r.source_id, "target": r.target_id, "type": r.relation_type.value if hasattr(r.relation_type, "value") else str(r.relation_type)}
                    for r in graph_ctx.relationships[:10]
                ]
                context_data["knowledge_confidence"] = graph_ctx.confidence
                logger.info(
                    "ThinkingAgent: knowledge retrieved",
                    extra={"entities": len(graph_ctx.entities), "confidence": round(graph_ctx.confidence, 3)},
                )
            except Exception as exc:
                logger.warning(
                    "ThinkingAgent: knowledge retrieval failed (non-fatal)",
                    extra={"error": str(exc)[:100]},
                )

        logger.info(
            "ThinkingAgent: observe",
            extra={"prompt_len": len(request.prompt)},
        )

        # 2. Think — run CoT pipeline
        trace = self._cot.think(
            prompt=request.prompt,
            context=context_data,
        )

        # 3. Reason — extract the conclusion
        if not trace.is_complete or trace.conclusion is None:
            return AgentResponse(
                content="Unable to reach a conclusion.",
                error="Reasoning incomplete",
                execution_time=time.monotonic() - t0,
            )

        conclusion = trace.conclusion
        action = conclusion.action
        justification = conclusion.justification

        logger.info(
            "ThinkingAgent: concluded",
            extra={
                "action": action[:100],
                "confidence": round(trace.total_confidence, 3),
                "steps": trace.step_count,
            },
        )

        # 4. Act — produce the response
        response_content = (
            f"{action}\n\n"
            f"Justification: {justification}\n"
            f"Confidence: {trace.total_confidence:.1%}\n"
            f"Reasoning steps: {trace.step_count}"
        )

        # 5. Reflect — store trace and update context
        self._context.add_message("assistant", response_content)
        self._store_trace(trace)

        if self._thinking_config.reflect_on_errors and conclusion.risks:
            reflection = ReasoningStep(
                thought=f"Risks identified: {', '.join(conclusion.risks)}",
                step_type="reflection",
                confidence=conclusion.confidence * 0.9,
            )
            trace.add_step(reflection)

        elapsed = time.monotonic() - t0
        return AgentResponse(
            content=response_content,
            execution_time=elapsed,
            tokens_used=trace.token_count,
            metadata={
                "trace_id": trace.trace_id,
                "confidence": trace.total_confidence,
                "steps": trace.step_count,
                "depth": trace.depth.value,
            },
        )

    def stream(self, request: AgentRequest) -> Any:
        """Stream is not supported — falls back to execute."""
        yield self.execute(request)

    def setup(self) -> None:
        """No external setup required."""
        logger.info("ThinkingAgent setup complete (no external dependencies)")

    def test_connection(self) -> bool:
        """Always returns True — no external service dependency."""
        return True

    # ── AgentProtocol implementation ──────────────────────────────

    def plan(self, request: AgentRequest) -> list[str]:
        """Generate a plan using CoT reasoning."""
        trace = self._cot.think(request.prompt)
        return [step.thought for step in trace.steps]

    def act(self, action: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Execute a single action."""
        return AgentResponse(content=f"Executed: {action}")

    def observe(self, response: AgentResponse) -> dict[str, Any]:
        """Observe the result of an action."""
        return {
            "success": response.is_success,
            "content_length": len(response.content),
        }

    # ── Trace management ──────────────────────────────────────────

    @property
    def last_trace(self) -> ReasoningTrace | None:
        """Return the most recent reasoning trace."""
        return self._traces[-1] if self._traces else None

    @property
    def all_traces(self) -> list[ReasoningTrace]:
        """Return all stored reasoning traces."""
        return list(self._traces)

    @property
    def thinking_depth(self) -> ThinkingDepth:
        """Current thinking depth."""
        return self._cot.depth

    @thinking_depth.setter
    def thinking_depth(self, depth: ThinkingDepth) -> None:
        """Set thinking depth."""
        self._cot.depth = depth

    @property
    def context_summary(self) -> dict[str, Any]:
        """Get context window summary."""
        return self._context.summary()

    @property
    def knowledge_retriever(self) -> Any | None:
        """Return the attached knowledge retriever, if any."""
        return self._knowledge_retriever

    @knowledge_retriever.setter
    def knowledge_retriever(self, retriever: Any | None) -> None:
        """Set or replace the knowledge retriever at runtime."""
        self._knowledge_retriever = retriever

    def _store_trace(self, trace: ReasoningTrace) -> None:
        """Store a trace, respecting the max_traces limit."""
        self._traces.append(trace)
        while len(self._traces) > self._thinking_config.max_traces:
            self._traces.pop(0)


__all__ = [
    "ThinkingAgent",
    "ThinkingAgentConfig",
]
