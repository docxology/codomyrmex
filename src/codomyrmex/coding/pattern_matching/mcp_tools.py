"""MCP tools for the pattern_matching module.

Exposes code pattern detection and pattern listing capabilities
as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:

    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func

        return decorator


@mcp_tool(category="pattern_matching")
def match_pattern(
    code: str,
    pattern: str = "",
) -> dict[str, Any]:
    """Match a named pattern or detect all design patterns in Python code.

    When a specific pattern name is given (e.g. 'singleton', 'factory',
    'decorator', 'context_manager'), searches for that structural pattern
    using the ASTMatcher.  When the pattern is empty or 'all', runs the
    full PatternDetector to find all recognised design patterns.

    Args:
        code: Python source code to analyse.
        pattern: Pattern name to search for. Use an empty string or 'all'
            to detect every known pattern.

    Returns:
        Dictionary with matched patterns or error information.
    """
    try:
        if pattern and pattern != "all":
            from codomyrmex.coding.pattern_matching.ast_matcher import ASTMatcher

            matcher = ASTMatcher()
            results = matcher.find_pattern(code, pattern)
            return {
                "status": "success",
                "pattern": pattern,
                "match_count": len(results),
                "matches": [
                    {
                        "pattern_name": r.pattern_name,
                        "node_type": r.node_type,
                        "line": r.line,
                        "col": r.col,
                        "name": r.name,
                        "details": r.details,
                    }
                    for r in results
                ],
            }
        else:
            from codomyrmex.coding.pattern_matching.code_patterns import (
                PatternDetector,
            )

            detector = PatternDetector()
            results = detector.detect_patterns(code)
            return {
                "status": "success",
                "pattern": "all",
                "match_count": len(results),
                "matches": results,
            }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except SyntaxError as exc:
        return {"status": "error", "message": f"syntax error in code: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="pattern_matching")
def list_patterns() -> dict[str, Any]:
    """List all available code patterns that can be detected.

    Returns both the design patterns from PatternDetector (singleton,
    factory, observer, etc.) and the structural patterns from ASTMatcher
    (singleton, factory, decorator, context_manager).

    Returns:
        Dictionary with available patterns grouped by source.
    """
    try:
        from codomyrmex.coding.pattern_matching.code_patterns import PATTERNS

        design_patterns = {
            name: {
                "description": info.get("description", ""),
                "category": info.get("category", "general"),
                "indicators": info.get("indicators", []),
            }
            for name, info in PATTERNS.items()
        }

        ast_patterns = [
            "singleton",
            "factory",
            "decorator",
            "context_manager",
        ]

        anti_patterns = [
            "bare_except",
            "mutable_default_arg",
            "star_import",
            "deep_nesting",
        ]

        return {
            "status": "success",
            "design_patterns": design_patterns,
            "ast_patterns": ast_patterns,
            "anti_patterns": anti_patterns,
            "total_count": len(design_patterns) + len(ast_patterns) + len(anti_patterns),
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
