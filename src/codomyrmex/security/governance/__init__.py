"""Governance Module for Codomyrmex.

Provides contracts management, policy enforcement, and dispute resolution.

Submodules:
    contracts -- Contract lifecycle management with terms, signing, and compliance
    policy -- Rule-based policy engine with evaluation and enforcement
    dispute_resolution -- Dispute filing, evidence, mediation, and resolution workflow
"""

from .contracts import Contract, ContractError, ContractStatus, ContractTerm
from .dispute_resolution import DisputeError, DisputeResolver, DisputeStatus
from .policy import PolicyEngine, PolicyError, PolicyRule

__all__ = [
    # Contracts
    "Contract",
    "ContractTerm",
    "ContractStatus",
    "ContractError",
    # Policy
    "PolicyRule",
    "PolicyEngine",
    "PolicyError",
    # Dispute Resolution
    "DisputeResolver",
    "DisputeStatus",
    "DisputeError",
]
