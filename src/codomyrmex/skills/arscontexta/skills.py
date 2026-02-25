import hashlib
import json
import logging
from collections.abc import Callable

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)
try:
    from codomyrmex.skills.discovery import (
        DEFAULT_REGISTRY,
        FunctionSkill,
        ParameterSchema,
        SkillCategory,
        SkillMetadata,
    )
    _HAS_DISCOVERY = True
except ImportError:
    _HAS_DISCOVERY = False

from .core import ArsContextaManager

# ============================================================================
# Skill registration (into discovery.DEFAULT_REGISTRY)
# ============================================================================


def _register_arscontexta_skills() -> None:
    """Register 6 MCP-ready skills into the global discovery registry."""
    if not _HAS_DISCOVERY:
        logger.debug("Skipping arscontexta skill registration — discovery module unavailable")
        return

    manager = ArsContextaManager()

    # --- skill functions ---

    def arscontexta_setup(vault_path: str) -> dict:
        """Initialise an Ars Contexta vault at the given path."""
        cfg = manager.setup(vault_path)
        return cfg.to_dict()

    def arscontexta_health(vault_path: str) -> dict:
        """Run vault health diagnostics."""
        report = manager.health(vault_path)
        return report.to_dict()

    def arscontexta_process(content: str, context: str = "{}") -> list:
        """Run the 6R processing pipeline on content."""
        ctx = json.loads(context) if isinstance(context, str) else context
        results = manager.process_content(content, ctx)
        return [r.to_dict() for r in results]

    def arscontexta_derive(user_text: str) -> dict:
        """Extract configuration dimension signals from user text."""
        return manager.derive_config(user_text)

    def arscontexta_primitives(layer: str = "") -> list:
        """List kernel primitives, optionally filtered by layer name."""
        return manager.get_primitives(layer or None)

    def arscontexta_stats() -> dict:
        """Get methodology graph statistics."""
        return manager.get_methodology_stats()

    _SKILL_DEFS: list[tuple[Callable, str, str, list[ParameterSchema]]] = [
        (
            arscontexta_setup,
            "arscontexta_setup",
            "Initialise an Ars Contexta vault at the given path.",
            [ParameterSchema(name="vault_path", param_type="string", description="Filesystem path for the vault")],
        ),
        (
            arscontexta_health,
            "arscontexta_health",
            "Run vault health diagnostics.",
            [ParameterSchema(name="vault_path", param_type="string", description="Filesystem path of the vault")],
        ),
        (
            arscontexta_process,
            "arscontexta_process",
            "Run the 6R processing pipeline on content.",
            [
                ParameterSchema(name="content", param_type="string", description="Content to process"),
                ParameterSchema(name="context", param_type="string", description="JSON context object", required=False, default="{}"),
            ],
        ),
        (
            arscontexta_derive,
            "arscontexta_derive",
            "Extract configuration dimension signals from user text.",
            [ParameterSchema(name="user_text", param_type="string", description="Free-form user text")],
        ),
        (
            arscontexta_primitives,
            "arscontexta_primitives",
            "List kernel primitives, optionally filtered by layer.",
            [ParameterSchema(name="layer", param_type="string", description="Layer filter", required=False, default="")],
        ),
        (
            arscontexta_stats,
            "arscontexta_stats",
            "Get methodology graph statistics.",
            [],
        ),
    ]

    tags = ["arscontexta", "knowledge-management", "cognitive-architecture"]

    for func, name, desc, params in _SKILL_DEFS:
        skill_id = hashlib.md5(f"arscontexta.{name}".encode()).hexdigest()[:12]
        meta = SkillMetadata(
            id=skill_id,
            name=name,
            description=desc,
            version="1.0.0",
            category=SkillCategory.REASONING,
            tags=list(tags),
            parameters=params,
        )
        skill_obj = FunctionSkill(func, metadata=meta)
        DEFAULT_REGISTRY.register(skill_obj)
        logger.debug("Registered arscontexta skill: %s", name)


# Auto-register on import
_register_arscontexta_skills()


