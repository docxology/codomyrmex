"""MCP tools for the documentation module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="documentation")
def generate_module_docs(module_name: str) -> dict:
    """Generate or update the RASP documentation suite for a specific module.
    
    Args:
        module_name: Name of the module to generate documentation for (e.g. 'core')
        
    Returns:
        Status and paths of generated documentation.
    """
    from pathlib import Path

    from codomyrmex.documentation import generate_pai_md

    module_path = Path(f"src/codomyrmex/{module_name}")
    if not module_path.exists():
        return {"status": "error", "message": f"Module {module_name} not found."}

    try:
        generate_pai_md(str(module_path))
        return {
            "status": "success",
            "message": f"Documentation generated for {module_name}",
            "paths": [
                f"{module_path}/PAI.md"
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="documentation")
def audit_rasp_compliance(module_name: str | None = None) -> dict:
    """Audit the repository for RASP (README, AGENTS, SPEC, PAI) compliance.
    
    Args:
        module_name: Optional module name to audit specifically. If not provided, audits the whole repo.
        
    Returns:
        Audit report detailing missing files.
    """
    from pathlib import Path

    from codomyrmex.documentation import audit_rasp

    try:
        if module_name:
            missing_count = audit_rasp(Path(f"src/codomyrmex/{module_name}"))
        else:
            missing_count = audit_rasp(Path("src/codomyrmex"))

        success = missing_count == 0

        return {
            "status": "success",
            "compliant": success,
            "missing_count": missing_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
