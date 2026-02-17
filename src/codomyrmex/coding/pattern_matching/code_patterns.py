"""Predefined code pattern definitions and detector.

Defines structural signatures for common design patterns and provides a
detector that scans Python source code for their presence using AST analysis.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class PatternDefinition:
    """Definition of a recognisable code pattern.

    Attributes:
        name: Pattern name (e.g. ``"singleton"``).
        description: What the pattern does.
        indicators: AST-level heuristics used for detection.
        category: Grouping label (``"creational"``, ``"structural"``,
            ``"behavioral"``).
    """

    name: str
    description: str
    indicators: list[str]
    category: str = "general"


# ------------------------------------------------------------------
# Built-in pattern catalogue
# ------------------------------------------------------------------

PATTERNS: dict[str, dict[str, Any]] = {
    "singleton": {
        "description": "Ensures a class has only one instance.",
        "category": "creational",
        "indicators": [
            "ClassDef with __new__ override",
            "ClassDef with _instance class variable",
        ],
    },
    "factory": {
        "description": "Creates objects without specifying exact class.",
        "category": "creational",
        "indicators": [
            "Function named create_*/make_*/build_*",
            "Function returning different types based on input",
        ],
    },
    "observer": {
        "description": "Defines a one-to-many dependency so that when one object changes state, all dependents are notified.",
        "category": "behavioral",
        "indicators": [
            "Class with subscribe/attach/register + notify/emit methods",
            "Class maintaining a list of listeners/observers/callbacks",
        ],
    },
    "strategy": {
        "description": "Defines a family of algorithms and makes them interchangeable.",
        "category": "behavioral",
        "indicators": [
            "Abstract base class with a single execute/run/apply method",
            "Multiple subclasses overriding the same method",
            "Context class holding a reference to a strategy object",
        ],
    },
    "decorator_pattern": {
        "description": "Attaches additional responsibilities to an object dynamically.",
        "category": "structural",
        "indicators": [
            "Class wrapping another instance of the same interface",
            "Constructor taking an instance of the wrapped type",
        ],
    },
    "template_method": {
        "description": "Defines the skeleton of an algorithm, deferring steps to subclasses.",
        "category": "behavioral",
        "indicators": [
            "Base class method calling abstract/hook methods",
            "Methods raising NotImplementedError",
        ],
    },
}


def _to_definition(name: str, info: dict) -> PatternDefinition:
    return PatternDefinition(
        name=name,
        description=info.get("description", ""),
        indicators=info.get("indicators", []),
        category=info.get("category", "general"),
    )


class PatternDetector:
    """Detect design patterns in Python source code.

    Uses AST inspection plus naming/structural heuristics.

    Usage::

        detector = PatternDetector()
        results = detector.detect_patterns(source_code)
        for r in results:
            print(r["pattern"], r["location"])
    """

    def __init__(self, patterns: Optional[dict[str, dict]] = None) -> None:
        """Initialise with an optional custom pattern catalogue.

        Args:
            patterns: Dict mapping pattern names to definition dicts.
                Falls back to the built-in :data:`PATTERNS` if ``None``.
        """
        raw = patterns if patterns is not None else PATTERNS
        self._definitions: dict[str, PatternDefinition] = {
            name: _to_definition(name, info)
            for name, info in raw.items()
        }

    def register_pattern(self, name: str, definition: dict) -> None:
        """Register a new pattern definition at runtime.

        Args:
            name: Unique pattern name.
            definition: Dict with ``description``, ``indicators``, and
                optionally ``category``.
        """
        self._definitions[name] = _to_definition(name, definition)
        logger.info("Registered pattern '%s'", name)

    def detect_patterns(self, code: str) -> list[dict]:
        """Scan Python source code for known design patterns.

        Args:
            code: Python source code string.

        Returns:
            A list of dicts, each with ``pattern`` (name), ``category``,
            ``location`` (dict with ``line``, ``name``), and ``confidence``
            (float 0-1).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            logger.error("Failed to parse code: %s", exc)
            return []

        results: list[dict] = []

        # Collect class and function metadata for matching
        class_info = self._collect_class_info(tree)
        func_info = self._collect_func_info(tree)

        # Run each detector
        results.extend(self._detect_singleton(class_info))
        results.extend(self._detect_factory(func_info))
        results.extend(self._detect_observer(class_info))
        results.extend(self._detect_strategy(class_info))
        results.extend(self._detect_template_method(class_info))

        return results

    # ------------------------------------------------------------------
    # Metadata collection
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_class_info(tree: ast.Module) -> list[dict]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                attrs = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attrs.append(target.id)
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "attrs": attrs,
                    "bases": [
                        getattr(b, "id", getattr(b, "attr", ""))
                        for b in node.bases
                    ],
                    "decorator_list": [
                        getattr(d, "id", getattr(d, "attr", ""))
                        for d in node.decorator_list
                    ],
                })
        return classes

    @staticmethod
    def _collect_func_info(tree: ast.Module) -> list[dict]:
        funcs = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.append({
                    "name": node.name,
                    "line": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                })
        return funcs

    # ------------------------------------------------------------------
    # Individual pattern detectors
    # ------------------------------------------------------------------

    def _detect_singleton(self, classes: list[dict]) -> list[dict]:
        if "singleton" not in self._definitions:
            return []
        results = []
        for cls in classes:
            if "__new__" in cls["methods"] or "_instance" in cls["attrs"]:
                results.append({
                    "pattern": "singleton",
                    "category": "creational",
                    "location": {"line": cls["line"], "name": cls["name"]},
                    "confidence": 0.85,
                })
        return results

    def _detect_factory(self, funcs: list[dict]) -> list[dict]:
        if "factory" not in self._definitions:
            return []
        results = []
        keywords = ("create", "make", "build", "factory", "construct")
        for fn in funcs:
            name_lower = fn["name"].lower()
            if any(kw in name_lower for kw in keywords):
                results.append({
                    "pattern": "factory",
                    "category": "creational",
                    "location": {"line": fn["line"], "name": fn["name"]},
                    "confidence": 0.70,
                })
        return results

    def _detect_observer(self, classes: list[dict]) -> list[dict]:
        if "observer" not in self._definitions:
            return []
        results = []
        subscribe_keywords = {"subscribe", "attach", "register", "add_listener", "on"}
        notify_keywords = {"notify", "emit", "dispatch", "fire", "trigger"}
        for cls in classes:
            method_set = set(cls["methods"])
            has_subscribe = bool(method_set & subscribe_keywords)
            has_notify = bool(method_set & notify_keywords)
            # Also check for _listeners/_observers/_callbacks attributes
            listener_attrs = {"_listeners", "_observers", "_callbacks", "_subscribers"}
            has_listener_list = bool(set(cls["attrs"]) & listener_attrs)

            if (has_subscribe and has_notify) or (has_listener_list and has_notify):
                results.append({
                    "pattern": "observer",
                    "category": "behavioral",
                    "location": {"line": cls["line"], "name": cls["name"]},
                    "confidence": 0.80,
                })
        return results

    def _detect_strategy(self, classes: list[dict]) -> list[dict]:
        if "strategy" not in self._definitions:
            return []
        results = []
        strategy_method_names = {"execute", "run", "apply", "compute", "process"}
        for cls in classes:
            method_set = set(cls["methods"])
            if method_set & strategy_method_names:
                # Heuristic: has an abstract-looking base or ABC in bases
                if "ABC" in cls["bases"] or "abstractmethod" in cls["decorator_list"]:
                    results.append({
                        "pattern": "strategy",
                        "category": "behavioral",
                        "location": {"line": cls["line"], "name": cls["name"]},
                        "confidence": 0.75,
                    })
        return results

    def _detect_template_method(self, classes: list[dict]) -> list[dict]:
        if "template_method" not in self._definitions:
            return []
        # This is a heuristic: classes with methods that are prefixed with _
        # alongside a public "template" method
        results = []
        for cls in classes:
            public_methods = [m for m in cls["methods"] if not m.startswith("_")]
            hook_methods = [
                m for m in cls["methods"]
                if m.startswith("_") and not m.startswith("__")
            ]
            if public_methods and len(hook_methods) >= 2:
                results.append({
                    "pattern": "template_method",
                    "category": "behavioral",
                    "location": {"line": cls["line"], "name": cls["name"]},
                    "confidence": 0.55,
                })
        return results
