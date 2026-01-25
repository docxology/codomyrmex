"""Deployment module for Codomyrmex."""

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .manager.manager import DeploymentManager
except ImportError:
    DeploymentManager = None

try:
    from .gitops.gitops import GitOpsSynchronizer
except ImportError:
    GitOpsSynchronizer = None

# Submodule exports  
from . import health_checks
from . import strategies
from . import rollback

# Try optional submodules
try:
    from . import manager
except ImportError:
    pass

try:
    from . import gitops
except ImportError:
    pass

__all__ = [
    "health_checks",
    "strategies",
    "rollback",
]

if DeploymentManager:
    __all__.append("DeploymentManager")
if GitOpsSynchronizer:
    __all__.append("GitOpsSynchronizer")

__version__ = "0.1.0"
