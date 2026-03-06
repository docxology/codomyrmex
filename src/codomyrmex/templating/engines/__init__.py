"""Template engine implementations."""

from .base import TemplateContext, TemplateEngine
from .jinja2_like import Jinja2LikeEngine
from .mustache import MustacheEngine
from .simple import SimpleTemplateEngine


def create_engine(engine_type: str = "simple", **kwargs) -> TemplateEngine:
    """Factory function for template engines."""
    engines: dict[str, type[TemplateEngine]] = {
        "simple": SimpleTemplateEngine,
        "jinja2": Jinja2LikeEngine,
        "mustache": MustacheEngine,
    }
    engine_class = engines.get(engine_type)
    if not engine_class:
        raise ValueError(f"Unknown engine type: {engine_type}")
    return engine_class(**kwargs)


__all__ = [
    "Jinja2LikeEngine",
    "MustacheEngine",
    "SimpleTemplateEngine",
    "TemplateContext",
    "TemplateEngine",
    "create_engine",
]
