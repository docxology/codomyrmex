# Agent Instructions for `logit_processor`

- Ensure strict zero-mock testing policy is followed for any tests in this module.
- All processors must subclass `LogitProcessor` and implement the `__call__` method.
- Docstrings are required for all classes, methods, and functions.
- The `mcp_tools.py` exposes tools that can be consumed by external agents or the PAI system. Avoid changing the signatures unless necessary.
