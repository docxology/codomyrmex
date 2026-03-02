"""MCP tools for the security module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="security")
def scan_vulnerabilities(path: str = ".") -> dict:
    """Scan a project directory for known security vulnerabilities.

    Args:
        path: Root path to scan (default: current directory)

    Returns:
        Structured security report of identified vulnerabilities.
    """
    from codomyrmex.security import scan_vulnerabilities as _scan

    try:
        results = _scan(path)
        # Convert response objects to dicts if necessary
        if hasattr(results, "to_dict"):
            results = results.to_dict()
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="security")
def scan_secrets(file_path: str) -> dict:
    """Scan a specific file for leaked secrets, API keys, or credentials.

    Args:
        file_path: Path to the file to scan

    Returns:
        A dictionary containing identified secrets or confirmation of validation.
    """
    from codomyrmex.security import scan_file_for_secrets as _scan_secrets

    try:
        results = _scan_secrets(file_path)
        if hasattr(results, "to_dict"):
            results = results.to_dict()
        return {"status": "success", "findings": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="security")
def audit_code_security(path: str) -> dict:
    """Audit code quality and security for a specific file or directory.

    Args:
        path: Path to file or directory

    Returns:
        Audit results and security grade.
    """
    from codomyrmex.security import security_audit_code as _audit

    try:
        results = _audit(path)
        if hasattr(results, "to_dict"):
            results = results.to_dict()
        return {"status": "success", "audit": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}
