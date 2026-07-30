# Documentation module security

The authoritative module controls are in the
[source security guide](../../../src/codomyrmex/documentation/SECURITY.md).
Report vulnerabilities through the repository
[security policy](../../../SECURITY.md), not public issues.

Key risks are path traversal, broad overwrite, symlink-following aggregation,
untrusted Markdown/HTML, package-manager and browser side effects, dependency
supply chain, network-visible local servers, and secret leakage.

MCP module names are restricted to one lowercase top-level package. PAI
generation defaults to dry-run and reports execution state. Apply mode,
aggregation, dependency installation, site lifecycle, and broad maintenance
require explicit authority.

## Navigation

- [Module overview](README.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [Source security guide](../../../src/codomyrmex/documentation/SECURITY.md)
