"""Code generation from specifications.

Produces code bundles from task descriptions using
template-based generation with anti-pattern validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class CodeBundle:
    """Generated code bundle.

    Attributes:
        filename: Target filename.
        source: Generated source code.
        language: Programming language.
        imports: Required imports.
        functions: Function names generated.
        classes: Class names generated.
    """

    filename: str = "generated.py"
    source: str = ""
    language: str = "python"
    imports: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)

    @property
    def line_count(self) -> int:
        """Execute Line Count operations natively."""
        return len(self.source.strip().splitlines())

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "filename": self.filename,
            "language": self.language,
            "lines": self.line_count,
            "functions": self.functions,
            "classes": self.classes,
        }


class CodeGenerator:
    """Generate Python code from specifications.

    Usage::

        gen = CodeGenerator()
        bundle = gen.generate("Create a calculator with add and multiply")
        print(bundle.source)
    """

    def generate(self, spec: str, filename: str = "generated.py") -> CodeBundle:
        """Generate code from a specification string.

        Uses keyword analysis to determine structure.

        Args:
            spec: Natural language specification.
            filename: Target filename.

        Returns:
            ``CodeBundle`` with generated source.
        """
        spec_lower = spec.lower()
        imports: list[str] = []
        functions: list[str] = []
        classes: list[str] = []
        lines: list[str] = [f'"""Auto-generated from spec: {spec[:60]}."""', "", "from __future__ import annotations", ""]

        # Extract operation names from spec
        ops = self._extract_operations(spec)

        # Determine if class-based
        class_keywords = {"class", "object", "model", "entity", "service"}
        use_class = any(kw in spec_lower for kw in class_keywords)

        # Extract a class name from spec
        class_name = self._extract_class_name(spec) if use_class else ""

        if use_class and class_name:
            classes.append(class_name)
            lines.append(f"class {class_name}:")
            lines.append(f'    """Auto-generated {class_name}."""')
            lines.append("")
            for op in ops:
                func_name = self._to_snake_case(op)
                functions.append(func_name)
                lines.append(f"    def {func_name}(self, *args, **kwargs):")
                lines.append(f'        """Perform {op}."""')
                lines.append(f"        raise NotImplementedError('{func_name}')")
                lines.append("")
        else:
            for op in ops:
                func_name = self._to_snake_case(op)
                functions.append(func_name)
                lines.append(f"def {func_name}(*args, **kwargs):")
                lines.append(f'    """Perform {op}."""')
                lines.append(f"    raise NotImplementedError('{func_name}')")
                lines.append("")

        if not ops:
            functions.append("main")
            lines.append("def main():")
            lines.append('    """Entry point."""')
            lines.append("    pass")
            lines.append("")

        bundle = CodeBundle(
            filename=filename,
            source="\n".join(lines),
            imports=imports,
            functions=functions,
            classes=classes,
        )

        logger.info("Code generated", extra={"funcs": len(functions), "classes": len(classes)})
        return bundle

    @staticmethod
    def _extract_operations(spec: str) -> list[str]:
        """Extract operation names from spec via keyword detection."""
        ops = []
        # Look for "with X and Y" or "X, Y, and Z" patterns
        pattern = r'\b(?:with|including|that can|to)\s+(.+?)(?:\.|$)'
        match = re.search(pattern, spec, re.IGNORECASE)
        if match:
            part = match.group(1)
            items = re.split(r',\s*(?:and\s+)?|\s+and\s+', part)
            ops = [item.strip() for item in items if item.strip()]
        return ops

    @staticmethod
    def _extract_class_name(spec: str) -> str:
        """Execute  Extract Class Name operations natively."""
        pattern = r'\b(?:create|build|make)\s+(?:a\s+)?(\w+)'
        match = re.search(pattern, spec, re.IGNORECASE)
        if match:
            name = match.group(1)
            return name[0].upper() + name[1:]
        return "Generated"

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Execute  To Snake Case operations natively."""
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        return "_".join(clean.lower().split())


__all__ = ["CodeBundle", "CodeGenerator"]
