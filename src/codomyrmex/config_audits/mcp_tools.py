"""MCP tools for the config_audits module.

Exposes configuration auditing capabilities via the PAI MCP bridge.
"""

from codomyrmex.config_audits.auditor import ConfigAuditor
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    name="config_audit_file",
    description="Audit a single configuration file for security and compliance issues.",
)
def config_audit_file(file_path: str) -> str:
    """Audit a single configuration file.

    Args:
        file_path: The path to the configuration file to audit.

    Returns:
        A formatted report string detailing the audit results.
    """
    auditor = ConfigAuditor()
    result = auditor.audit_file(file_path)
    return auditor.generate_report([result])


@mcp_tool(
    name="config_audit_directory",
    description="Audit an entire directory of configuration files.",
)
def config_audit_directory(directory_path: str, pattern: str = "*.json") -> str:
    """Audit all matching configuration files in a directory.

    Args:
        directory_path: The path to the directory to audit.
        pattern: The file glob pattern to match (e.g., "*.json", "*.yaml").

    Returns:
        A formatted report string detailing the audit results for all files.
    """
    auditor = ConfigAuditor()
    results = auditor.audit_directory(directory_path, pattern=pattern)
    return auditor.generate_report(results)
