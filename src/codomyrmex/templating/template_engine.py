"""Backward-compatible import surface for the templating engine.

The implementation lives in :mod:`codomyrmex.templating.engines` after the
templating package was split into engines and loaders.  Keep this module as a
small, dependency-free compatibility shim for existing integrations.
"""

from .engines.template_engine import Template, TemplateEngine, TemplatingError

__all__ = ["Template", "TemplateEngine", "TemplatingError"]
