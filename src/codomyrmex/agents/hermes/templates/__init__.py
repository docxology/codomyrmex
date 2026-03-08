"""Prompt template library for the Hermes agent.

Provides reusable, parameterized prompt templates for common
Hermes agent tasks: code review, task decomposition, documentation.
"""

from .models import PromptTemplate

# ── Built-in templates ────────────────────────────────────────────────

CODE_REVIEW = PromptTemplate(
    name="code_review",
    system_prompt=(
        "You are an expert code reviewer. Analyze the provided code for "
        "correctness, performance, security, and style. Provide specific, "
        "actionable feedback organized by severity."
    ),
    user_template=(
        "Review the following {language} code:\n\n"
        "```{language}\n{code}\n```\n\n"
        "Focus areas: {focus_areas}\n"
        "Severity levels: critical, major, minor, suggestion"
    ),
    variables=["language", "code", "focus_areas"],
)

TASK_DECOMPOSITION = PromptTemplate(
    name="task_decomposition",
    system_prompt=(
        "You are a project management expert. Break down complex tasks "
        "into clear, actionable subtasks with estimated effort and dependencies."
    ),
    user_template=(
        "Decompose the following task into subtasks:\n\n"
        "Task: {task_description}\n"
        "Context: {context}\n"
        "Constraints: {constraints}\n\n"
        "For each subtask provide: description, estimated hours, dependencies."
    ),
    variables=["task_description", "context", "constraints"],
)

DOCUMENTATION = PromptTemplate(
    name="documentation",
    system_prompt=(
        "You are a technical writer. Generate clear, comprehensive documentation "
        "following best practices. Include examples where appropriate."
    ),
    user_template=(
        "Generate {doc_type} documentation for:\n\n"
        "Component: {component_name}\n"
        "Description: {description}\n"
        "Target audience: {audience}\n\n"
        "Include: overview, usage examples, API reference, and common patterns."
    ),
    variables=["doc_type", "component_name", "description", "audience"],
)

DEBUGGING = PromptTemplate(
    name="debugging",
    system_prompt=(
        "You are an expert debugger. Systematically analyze the issue, "
        "identify root cause, and provide a fix with explanation."
    ),
    user_template=(
        "Debug this issue:\n\n"
        "Error: {error_message}\n"
        "Context: {context}\n"
        "Code:\n```{language}\n{code}\n```\n\n"
        "Expected behavior: {expected}\n"
        "Actual behavior: {actual}"
    ),
    variables=["error_message", "context", "language", "code", "expected", "actual"],
)

_BUILTIN_TEMPLATES: dict[str, PromptTemplate] = {
    t.name: t for t in [CODE_REVIEW, TASK_DECOMPOSITION, DOCUMENTATION, DEBUGGING]
}


class TemplateLibrary:
    """Library of prompt templates for the Hermes agent.

    Provides access to built-in templates and supports registering
    custom templates.

    Example::

        lib = TemplateLibrary()
        template = lib.get("code_review")
        prompt = template.render(language="python", code="...", focus_areas="security")
    """

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = dict(_BUILTIN_TEMPLATES)

    def get(self, name: str) -> PromptTemplate:
        """Get a template by name.

        Args:
            name: Template name.

        Returns:
            The :class:`PromptTemplate`.

        Raises:
            KeyError: If template not found.
        """
        if name not in self._templates:
            msg = f"Template '{name}' not found. Available: {self.list_templates()}"
            raise KeyError(msg)
        return self._templates[name]

    def list_templates(self) -> list[str]:
        """List all available template names."""
        return sorted(self._templates.keys())

    def register(self, template: PromptTemplate) -> None:
        """Register a custom template.

        Args:
            template: The template to register.
        """
        self._templates[template.name] = template

    def has(self, name: str) -> bool:
        """Check if a template exists."""
        return name in self._templates


__all__ = [
    "CODE_REVIEW",
    "DEBUGGING",
    "DOCUMENTATION",
    "TASK_DECOMPOSITION",
    "TemplateLibrary",
]
