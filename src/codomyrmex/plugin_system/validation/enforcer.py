"""Plugin interface enforcer — structural and runtime validation.

Provides:
- InterfaceEnforcer: validates plugin classes implement required interfaces
- Method signature checking (argument count)
- Property verification
- Batch enforcement for multiple plugins
- Enforcement report generation
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EnforcementResult:
    """Result of an interface enforcement check."""

    plugin_name: str
    interface_name: str
    passed: bool
    missing_methods: list[str] = field(default_factory=list)
    missing_properties: list[str] = field(default_factory=list)
    signature_mismatches: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class InterfaceEnforcer:
    """Validates that plugin classes implement specific interfaces.

    Checks method presence, property presence, and optionally
    method signature compatibility.

    Example::

        class MyInterface:
            def process(self, data: str) -> str: ...
            def cleanup(self) -> None: ...

        enforcer = InterfaceEnforcer()
        result = enforcer.enforce_detailed(MyPlugin(), MyInterface)
        assert result.passed
    """

    @staticmethod
    def enforce(plugin_obj: Any, interface_class: type) -> bool:
        """Check if plugin_obj satisfies the interface_class requirements.

        Args:
            plugin_obj: The plugin instance to validate.
            interface_class: The interface class defining required methods.

        Returns:
            True if all required methods are present.
        """
        required_methods = [
            m for m in dir(interface_class)
            if not m.startswith("_") and callable(getattr(interface_class, m, None))
        ]

        missing = []
        for method in required_methods:
            if not hasattr(plugin_obj, method) or not callable(getattr(plugin_obj, method)):
                missing.append(method)

        if missing:
            logger.error(
                "Plugin %s is missing required methods: %s",
                type(plugin_obj).__name__, missing,
            )
            return False
        return True

    @staticmethod
    def enforce_detailed(plugin_obj: Any, interface_class: type) -> EnforcementResult:
        """Detailed enforcement check with signature validation.

        Returns an EnforcementResult with missing methods, properties,
        and signature mismatches.
        """
        plugin_name = type(plugin_obj).__name__
        interface_name = interface_class.__name__

        result = EnforcementResult(
            plugin_name=plugin_name,
            interface_name=interface_name,
            passed=True,
        )

        # Check methods
        for name in dir(interface_class):
            if name.startswith("_"):
                continue
            attr = getattr(interface_class, name, None)
            if attr is None:
                continue

            if isinstance(attr, property):
                if not isinstance(getattr(type(plugin_obj), name, None), property):
                    if not hasattr(plugin_obj, name):
                        result.missing_properties.append(name)
                        result.passed = False
                continue

            if callable(attr):
                plugin_attr = getattr(plugin_obj, name, None)
                if plugin_attr is None or not callable(plugin_attr):
                    result.missing_methods.append(name)
                    result.passed = False
                    continue

                # Check argument count (rough signature check)
                try:
                    iface_sig = inspect.signature(attr)
                    plugin_sig = inspect.signature(plugin_attr)
                    iface_params = [p for p in iface_sig.parameters if p != "self"]
                    plugin_params = [p for p in plugin_sig.parameters if p != "self"]
                    if len(iface_params) != len(plugin_params):
                        result.signature_mismatches.append(
                            f"{name}: expected {len(iface_params)} args, got {len(plugin_params)}"
                        )
                        result.notes.append(f"Signature mismatch on {name}")
                except (ValueError, TypeError) as e:
                    logger.debug("Could not compare signatures for %s: %s", name, e)
                    pass

        return result

    @staticmethod
    def enforce_batch(
        plugins: list[Any], interface_class: type
    ) -> list[EnforcementResult]:
        """Enforce an interface across multiple plugins."""
        return [
            InterfaceEnforcer.enforce_detailed(plugin, interface_class)
            for plugin in plugins
        ]

    @staticmethod
    def report(results: list[EnforcementResult]) -> str:
        """Generate a human-readable enforcement report."""
        lines = [f"Plugin Enforcement Report ({len(results)} plugins)"]
        lines.append("=" * 50)
        for r in results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"  {r.plugin_name} → {r.interface_name}: {status}")
            for m in r.missing_methods:
                lines.append(f"    Missing method: {m}")
            for p in r.missing_properties:
                lines.append(f"    Missing property: {p}")
            for s in r.signature_mismatches:
                lines.append(f"    Signature: {s}")
        passed = sum(1 for r in results if r.passed)
        lines.append(f"\n{passed}/{len(results)} plugins passed")
        return "\n".join(lines)
