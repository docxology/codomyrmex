"""Colony Kernel — the control plane for the Codomyrmex artificial ecology.

Agent actions earn permission through pressure, consequence, and memory.
The loop: pressure → proposal → gate → action → consequence → memory → role → pressure.

Public surface: shared contract types only. Subsystem classes are imported
from their respective modules to keep import overhead low.
"""

from codomyrmex.colony_kernel.actuation_gate import ActuationGate
from codomyrmex.colony_kernel.config_loader import (
    COLONY_KERNEL_CONFIG_DIR,
    default_budget_from_yaml,
    default_gate_config_from_yaml,
    load_decay_yaml,
    load_kernel_yaml,
    load_roles_yaml,
)
from codomyrmex.colony_kernel.consequence_memory import ConsequenceMemory
from codomyrmex.colony_kernel.falsification_worker import FalsificationWorker
from codomyrmex.colony_kernel.kernel import ColonyKernel, ColonyKernelConfig
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ColonySignal,
    ConsequenceRecord,
    DecayRate,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    GateResult,
    PruningCandidate,
    ResourceCost,
    SignalSource,
    SignalType,
    compute_trust_delta,
    make_trace_key,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
from codomyrmex.colony_kernel.pruning_daemon import PruningDaemon
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger
from codomyrmex.colony_kernel.role_adapter import RoleAdapter

__all__ = [
    # Config loader
    "COLONY_KERNEL_CONFIG_DIR",
    # Value objects
    "ActionProposal",
    # Subsystem classes
    "ActuationGate",
    # Enums
    "AgentRole",
    "AgentTrustProfile",
    # Integration
    "ColonyKernel",
    "ColonyKernelConfig",
    "ColonySignal",
    "ConsequenceMemory",
    "ConsequenceRecord",
    "DecayRate",
    "FalsificationFinding",
    "FalsificationSeverity",
    "FalsificationWorker",
    "GateDecision",
    "GateResult",
    "PheromoneStore",
    "PruningCandidate",
    "PruningDaemon",
    "ResourceBudget",
    "ResourceCost",
    "ResourceLedger",
    "RoleAdapter",
    "SignalSource",
    "SignalType",
    "compute_trust_delta",
    # Config loader functions
    "default_budget_from_yaml",
    "default_gate_config_from_yaml",
    "load_decay_yaml",
    "load_kernel_yaml",
    "load_roles_yaml",
    "make_trace_key",
]
