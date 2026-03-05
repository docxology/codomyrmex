# Scripts package marker
"""Codomyrmex scripts — thin orchestrators.

This package contains entry-point wrappers that import and invoke business
logic from ``src/codomyrmex/`` modules. No substantial logic, data models,
or core functionality should exist in this directory.

All business logic lives in ``src/codomyrmex/``. Scripts here are CLI
wrappers following the Thin Orchestrator Pattern:
  1. Parse CLI arguments
  2. Import from ``codomyrmex.<module>``
  3. Call the imported function
  4. Exit with the return code
"""
