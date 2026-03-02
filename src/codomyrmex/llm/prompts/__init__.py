"""
LLM Prompts Module

Prompt versioning, template management, and prompt engineering utilities.
"""

__version__ = "0.1.0"

import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union


class PromptRole(Enum):
    """Standard message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"

@dataclass
class Message:
    """A message in a prompt."""
    role: PromptRole
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to API-compatible dict."""
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result

@dataclass
class PromptVersion:
    """A version of a prompt template."""
    version: str
    template: str
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        """Get hash of template content."""
        return hashlib.sha256(self.template.encode()).hexdigest()[:12]

class PromptTemplate:
    """
    Template for generating prompts with variable substitution.

    Supports:
    - Simple variable substitution: {variable}
    - Default values: {variable:default}
    - Conditionals: {?variable}content{/variable}
    - Loops: {#items}...{item}...{/items}

    Usage:
        template = PromptTemplate(
            "You are a {role}. Help the user with {task}."
        )
        prompt = template.render(role="helpful assistant", task="coding")
    """

    def __init__(
        self,
        template: str,
        name: str | None = None,
        description: str = "",
    ):
        self.template = template
        self.name = name or f"template_{id(self)}"
        self.description = description
        self._variables = self._extract_variables()

    def _extract_variables(self) -> list[str]:
        """Extract variable names from template."""
        # Match {variable} and {variable:default}
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)(?::[^}]*)?\}'
        matches = re.findall(pattern, self.template)
        return list(set(matches))

    @property
    def variables(self) -> list[str]:
        """Get list of variable names in template."""
        return self._variables.copy()

    def render(self, **kwargs: Any) -> str:
        """
        Render template with variable substitution.

        Args:
            **kwargs: Variable values

        Returns:
            Rendered prompt string
        """
        result = self.template

        # Handle conditionals: {?var}content{/var}
        for var in self._variables:
            pattern = r'\{\?' + var + r'\}(.*?)\{/' + var + r'\}'
            if var in kwargs and kwargs[var]:
                result = re.sub(pattern, r'\1', result, flags=re.DOTALL)
            else:
                result = re.sub(pattern, '', result, flags=re.DOTALL)

        # Handle simple variables with defaults: {var:default}
        for match in re.finditer(r'\{([a-zA-Z_][a-zA-Z0-9_]*):([^}]*)\}', result):
            var_name = match.group(1)
            default = match.group(2)
            value = kwargs.get(var_name, default)
            result = result.replace(match.group(0), str(value))

        # Handle simple variables: {var}
        for var in self._variables:
            if var in kwargs:
                result = result.replace(f'{{{var}}}', str(kwargs[var]))

        return result

    def validate(self, **kwargs: Any) -> list[str]:
        """
        Validate that all required variables are provided.

        Returns:
            List of missing variable names
        """
        # Variables with defaults are optional
        required = set()
        for var in self._variables:
            pattern = r'\{' + var + r':[^}]*\}'
            if not re.search(pattern, self.template):
                required.add(var)

        return [v for v in required if v not in kwargs]

class PromptBuilder:
    """
    Fluent builder for constructing multi-message prompts.

    Usage:
        prompt = (PromptBuilder()
            .system("You are a helpful assistant.")
            .user("Hello!")
            .assistant("Hi! How can I help you?")
            .user("Write some code.")
            .build()
        )
    """

    def __init__(self):
        self._messages: list[Message] = []

    def system(self, content: str, **metadata) -> "PromptBuilder":
        """Add a system message."""
        self._messages.append(Message(
            role=PromptRole.SYSTEM,
            content=content,
            metadata=metadata,
        ))
        return self

    def user(self, content: str, name: str | None = None, **metadata) -> "PromptBuilder":
        """Add a user message."""
        self._messages.append(Message(
            role=PromptRole.USER,
            content=content,
            name=name,
            metadata=metadata,
        ))
        return self

    def assistant(self, content: str, **metadata) -> "PromptBuilder":
        """Add an assistant message."""
        self._messages.append(Message(
            role=PromptRole.ASSISTANT,
            content=content,
            metadata=metadata,
        ))
        return self

    def message(self, role: PromptRole, content: str, **kwargs) -> "PromptBuilder":
        """Add a message with any role."""
        self._messages.append(Message(role=role, content=content, **kwargs))
        return self

    def template(self, tmpl: PromptTemplate, role: PromptRole = PromptRole.USER, **kwargs) -> "PromptBuilder":
        """Add a message from a template."""
        content = tmpl.render(**kwargs)
        return self.message(role, content)

    def build(self) -> list[dict[str, Any]]:
        """Build the final message list."""
        return [msg.to_dict() for msg in self._messages]

    def build_string(self, separator: str = "\n\n") -> str:
        """Build as a single string (for models without message API)."""
        parts = []
        for msg in self._messages:
            prefix = msg.role.value.upper() + ": "
            parts.append(prefix + msg.content)
        return separator.join(parts)

    @property
    def messages(self) -> list[Message]:
        """Get raw message objects."""
        return self._messages.copy()

class PromptRegistry:
    """
    Registry for managing prompt templates with versioning.

    Usage:
        registry = PromptRegistry()

        # Register a template
        registry.register(
            name="code_review",
            template="Review this code:\n```{language}\n{code}\n```",
            version="1.0.0",
        )

        # Get and use template
        template = registry.get("code_review")
        prompt = template.render(language="python", code="print('hello')")
    """

    def __init__(self):
        self._templates: dict[str, dict[str, PromptVersion]] = {}
        self._active_versions: dict[str, str] = {}

    def register(
        self,
        name: str,
        template: str,
        version: str = "1.0.0",
        description: str = "",
        set_active: bool = True,
    ) -> PromptVersion:
        """
        Register a prompt template.

        Args:
            name: Template name
            template: Template string
            version: Version string
            description: Template description
            set_active: Whether to set as active version

        Returns:
            Created PromptVersion
        """
        if name not in self._templates:
            self._templates[name] = {}

        # Extract variables
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)(?::[^}]*)?\}'
        variables = list(set(re.findall(pattern, template)))

        version_obj = PromptVersion(
            version=version,
            template=template,
            description=description,
            variables=variables,
        )

        self._templates[name][version] = version_obj

        if set_active:
            self._active_versions[name] = version

        return version_obj

    def get(
        self,
        name: str,
        version: str | None = None
    ) -> PromptTemplate | None:
        """
        Get a prompt template.

        Args:
            name: Template name
            version: Specific version (or active version if None)

        Returns:
            PromptTemplate or None if not found
        """
        if name not in self._templates:
            return None

        v = version or self._active_versions.get(name)
        if not v or v not in self._templates[name]:
            return None

        version_obj = self._templates[name][v]
        return PromptTemplate(
            template=version_obj.template,
            name=f"{name}@{v}",
            description=version_obj.description,
        )

    def get_version(self, name: str, version: str) -> PromptVersion | None:
        """Get a specific version object."""
        if name in self._templates and version in self._templates[name]:
            return self._templates[name][version]
        return None

    def list_templates(self) -> list[str]:
        """List all registered template names."""
        return list(self._templates.keys())

    def list_versions(self, name: str) -> list[str]:
        """List all versions of a template."""
        if name in self._templates:
            return list(self._templates[name].keys())
        return []

    def set_active(self, name: str, version: str) -> bool:
        """Set the active version of a template."""
        if name in self._templates and version in self._templates[name]:
            self._active_versions[name] = version
            return True
        return False

    def export_to_json(self) -> str:
        """Export all templates to JSON."""
        export = {}
        for name, versions in self._templates.items():
            export[name] = {
                "active": self._active_versions.get(name),
                "versions": {
                    v: {
                        "template": pv.template,
                        "description": pv.description,
                        "variables": pv.variables,
                        "created_at": pv.created_at.isoformat(),
                    }
                    for v, pv in versions.items()
                }
            }
        return json.dumps(export, indent=2)

    def import_from_json(self, json_str: str) -> int:
        """Import templates from JSON. Returns count of imported templates."""
        data = json.loads(json_str)
        count = 0

        for name, info in data.items():
            for version, vinfo in info.get("versions", {}).items():
                self.register(
                    name=name,
                    template=vinfo["template"],
                    version=version,
                    description=vinfo.get("description", ""),
                    set_active=(version == info.get("active")),
                )
                count += 1

        return count

# Common prompt templates
COMMON_TEMPLATES = {
    "code_review": PromptTemplate(
        "Review this code and provide feedback:\n\n```{language}\n{code}\n```",
        name="code_review",
    ),
    "summarize": PromptTemplate(
        "Summarize the following text in {length:a few sentences}:\n\n{text}",
        name="summarize",
    ),
    "translate": PromptTemplate(
        "Translate the following from {source_lang:English} to {target_lang}:\n\n{text}",
        name="translate",
    ),
    "explain": PromptTemplate(
        "Explain {topic} in simple terms{?audience} for {audience}{/audience}.",
        name="explain",
    ),
    "json_output": PromptTemplate(
        "Respond with valid JSON only. Do not include any text outside the JSON.\n\n{instructions}",
        name="json_output",
    ),
}

def get_common_template(name: str) -> PromptTemplate | None:
    """Get a common built-in template."""
    return COMMON_TEMPLATES.get(name)

__all__ = [
    # Enums
    "PromptRole",
    # Data classes
    "Message",
    "PromptVersion",
    # Classes
    "PromptTemplate",
    "PromptBuilder",
    "PromptRegistry",
    # Constants
    "COMMON_TEMPLATES",
    # Functions
    "get_common_template",
]
