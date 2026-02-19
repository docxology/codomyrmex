# DEPRECATED(v0.2.0): Shim module. Import from encryption.keys.hmac_utils instead. Will be removed in v0.3.0.
"""Backward-compatibility shim -- redirects to ``encryption.keys.hmac_utils``."""

from .keys.hmac_utils import *  # noqa: F401,F403
from .keys.hmac_utils import compute_hmac, verify_hmac
