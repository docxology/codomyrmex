"""Colony Kernel — the control plane for the Codomyrmex artificial ecology.

Agent actions earn permission through pressure, consequence, and memory.
The loop: pressure → proposal → gate → action → consequence → memory → role → pressure.

Public surface: shared contract types only. Subsystem classes are imported
from their respective modules to keep import overhead low.
"""

from codomyrmex.colony_kernel.actuation_gate import ActuationGate
from codomyrmex.colony_kernel.authorization import (
    DEFAULT_ACTION_SCOPE,
    AuthorizationError,
    AuthorizationLedger,
    Ed25519Authority,
)
from codomyrmex.colony_kernel.config_loader import (
    COLONY_KERNEL_CONFIG_DIR,
    default_budget_from_yaml,
    default_gate_config_from_yaml,
    load_decay_yaml,
    load_kernel_yaml,
    load_roles_yaml,
)
from codomyrmex.colony_kernel.consequence_memory import ConsequenceMemory
from codomyrmex.colony_kernel.executor import ExecutionRun, RegisteredActionExecutor
from codomyrmex.colony_kernel.falsification_worker import FalsificationWorker
from codomyrmex.colony_kernel.invariants import (
    all_invariants_hold,
    check_enum_values_no_conflict,
    check_gate_weights_sum_to_one,
    check_pheromone_strength_bounds,
    check_role_ladder_monotonic,
    check_trust_score_in_range,
)
from codomyrmex.colony_kernel.kernel import ColonyKernel, ColonyKernelConfig
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    AuthorizationStatus,
    ColonySignal,
    ConsequenceRecord,
    DecayRate,
    ExecutionAuthorization,
    ExecutionReceipt,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    GateResult,
    OutcomeEvidence,
    PruningCandidate,
    ResourceCost,
    SignalSource,
    SignalType,
    SupervisedEvaluatorEvidence,
    compute_trust_delta,
    make_trace_key,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
from codomyrmex.colony_kernel.pruning_daemon import PruningDaemon
from codomyrmex.colony_kernel.resource_ledger import (
    ResourceBudget,
    ResourceLedger,
    ThreadSafeResourceLedger,
)
from codomyrmex.colony_kernel.role_adapter import RoleAdapter
from codomyrmex.colony_kernel.sqlite_signal_store import SQLiteSignalStore

__all__ = [
    "COLONY_KERNEL_CONFIG_DIR",
    "DEFAULT_ACTION_SCOPE",
    "ActionProposal",
    "ActuationGate",
    "AgentRole",
    "AgentTrustProfile",
    "AuthorizationError",
    "AuthorizationLedger",
    "AuthorizationStatus",
    "ColonyKernel",
    "ColonyKernelConfig",
    "ColonySignal",
    "ConsequenceMemory",
    "ConsequenceRecord",
    "DecayRate",
    "Ed25519Authority",
    "ExecutionAuthorization",
    "ExecutionReceipt",
    "ExecutionRun",
    "FalsificationFinding",
    "FalsificationSeverity",
    "FalsificationWorker",
    "GateDecision",
    "GateResult",
    "OutcomeEvidence",
    "PheromoneStore",
    "PruningCandidate",
    "PruningDaemon",
    "RegisteredActionExecutor",
    "ResourceBudget",
    "ResourceCost",
    "ResourceLedger",
    "RoleAdapter",
    "SQLiteSignalStore",
    "SignalSource",
    "SignalType",
    "SupervisedEvaluatorEvidence",
    "ThreadSafeResourceLedger",
    "all_invariants_hold",
    "check_enum_values_no_conflict",
    "check_gate_weights_sum_to_one",
    "check_pheromone_strength_bounds",
    "check_role_ladder_monotonic",
    "check_trust_score_in_range",
    "compute_trust_delta",
    "default_budget_from_yaml",
    "default_gate_config_from_yaml",
    "load_decay_yaml",
    "load_kernel_yaml",
    "load_roles_yaml",
    "make_trace_key",
]
