"""Antigravity Skills Adapter.

Wraps individual Antigravity IDE tools as ``Skill`` objects so they can
participate in ``SkillComposer`` chains, parallel groups, and conditional
branches alongside other Codomyrmex skills.

Example::

    >>> from codomyrmex.ide.antigravity.skill_adapter import AntigravityToolSkill
    >>> from codomyrmex.skills.composition import SkillComposer
    >>> composer = SkillComposer()
    >>> pipeline = composer.chain(
    ...     AntigravityToolSkill("grep_search", SearchPath="/src", Query="TODO"),
    ...     AntigravityToolSkill("view_file"),  # receives path from previous
    ... )
    >>> result = pipeline.execute()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Metadata for an Antigravity tool skill.

    Attributes:
        name: Skill name (tool name prefixed with ``antigravity.``).
        description: Human-readable description.
        category: Skill category.
    """
    name: str
    description: str = ""
    category: str = "antigravity"


class AntigravityToolSkill:
    """Wraps a single Antigravity tool as a composable Skill.

    Implements the ``execute(**kwargs)`` interface expected by
    ``SkillExecutor`` and ``SkillComposer``.

    Attributes:
        tool_name: Name of the Antigravity tool.
        defaults: Default keyword arguments for the tool.
        metadata: Skill metadata for registry compatibility.
    """

    def __init__(
        self,
        tool_name: str,
        client: Any | None = None,
        **defaults: Any,
    ) -> None:
        """Initialize the skill.

        Args:
            tool_name: Name of the Antigravity tool (e.g. ``"grep_search"``).
            client: Optional ``AntigravityClient``. Lazy-created if None.
            **defaults: Default arguments for the tool invocation.
        """
        self.tool_name = tool_name
        self._client = client
        self.defaults = defaults

        # Schema lookup
        from codomyrmex.ide.antigravity.tool_provider import (
            AntigravityToolProvider,
        )
        schema = AntigravityToolProvider.get_tool_schema(tool_name)
        desc = schema["description"] if schema else f"Antigravity tool: {tool_name}"

        self.metadata = SkillMetadata(
            name=f"antigravity.{tool_name}",
            description=desc,
        )

    @property
    def client(self) -> Any:
        """Lazy-initialize the AntigravityClient.

        Returns:
            The AntigravityClient instance.
        """
        if self._client is None:
            from codomyrmex.ide.antigravity import AntigravityClient
            self._client = AntigravityClient()
        return self._client

    def validate_params(self, **kwargs: Any) -> list[str]:
        """Validate parameters against the tool schema.

        Args:
            **kwargs: Parameters to validate.

        Returns:
            List of validation error strings (empty if valid).
        """
        from codomyrmex.ide.antigravity.tool_provider import AntigravityToolProvider
        schema = AntigravityToolProvider.get_tool_schema(self.tool_name)
        if schema is None:
            return [f"Unknown tool: {self.tool_name}"]

        merged = {**self.defaults, **kwargs}
        params = schema.get("parameters", {})
        required = params.get("required", [])
        errors = []

        for req in required:
            if req not in merged:
                # Allow 'input' from chain results to satisfy first required param
                if "input" in merged and len(errors) == 0:
                    continue
                errors.append(f"Missing required parameter: {req}")

        return errors

    def execute(self, **kwargs: Any) -> Any:
        """Execute the Antigravity tool.

        Merges defaults with provided kwargs. If called from a chain,
        the ``input`` kwarg from the previous skill can be used to populate
        the first required parameter.

        Args:
            **kwargs: Parameters for the tool. ``input`` is a special key
                used by ``SkillComposer.chain()`` to pass previous results.

        Returns:
            Tool execution result.
        """
        merged = {**self.defaults, **kwargs}

        # Chain support: map 'input' to appropriate param
        if "input" in merged:
            chain_input = merged.pop("input")
            self._apply_chain_input(merged, chain_input)

        logger.info(f"Executing skill: {self.metadata.name}")
        return self.client.invoke_tool(self.tool_name, merged)

    def _apply_chain_input(
        self, args: dict[str, Any], chain_input: Any
    ) -> None:
        """Map chain input to appropriate tool parameter.

        Inspects the tool schema to determine which parameter should
        receive the chained input.

        Args:
            args: Current arguments dict (mutated in place).
            chain_input: Result from the previous skill in the chain.
        """
        from codomyrmex.ide.antigravity.tool_provider import AntigravityToolProvider
        schema = AntigravityToolProvider.get_tool_schema(self.tool_name)
        if schema is None:
            return

        params = schema.get("parameters", {})
        required = params.get("required", [])

        # Map to first missing required parameter
        for req in required:
            if req not in args:
                args[req] = str(chain_input) if not isinstance(chain_input, str) else chain_input
                logger.debug(f"Chain: mapped input to {req}")
                break

    def __repr__(self) -> str:
        return f"AntigravityToolSkill({self.tool_name!r})"


class AntigravitySkillFactory:
    """Factory for creating AntigravityToolSkill instances.

    Shares a single client across all created skills.

    Attributes:
        client: The shared AntigravityClient.
    """

    def __init__(self, client: Any | None = None) -> None:
        """Initialize the factory.

        Args:
            client: Optional ``AntigravityClient``. Lazy-created if None.
        """
        self._client = client

    @property
    def client(self) -> Any:
        """Lazy-initialize the shared client.

        Returns:
            The AntigravityClient instance.
        """
        if self._client is None:
            from codomyrmex.ide.antigravity import AntigravityClient
            self._client = AntigravityClient()
        return self._client

    def create(self, tool_name: str, **defaults: Any) -> AntigravityToolSkill:
        """Create a skill for the given tool.

        Args:
            tool_name: Antigravity tool name.
            **defaults: Default arguments.

        Returns:
            A configured ``AntigravityToolSkill``.
        """
        return AntigravityToolSkill(tool_name, client=self.client, **defaults)

    def search_pipeline(
        self,
        query: str,
        path: str,
    ) -> Any:
        """Create a pre-built search → view pipeline.

        Args:
            query: Search query string.
            path: Path to search in.

        Returns:
            A ``ComposedSkill`` that greps then views matching files.
        """
        from codomyrmex.skills.composition import SkillComposer
        composer = SkillComposer()
        return composer.chain(
            self.create("grep_search", SearchPath=path, Query=query),
            self.create("view_file"),
        )


__all__ = [
    "AntigravityToolSkill",
    "AntigravitySkillFactory",
    "SkillMetadata",
]
