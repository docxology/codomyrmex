"""Colony Kernel — a deterministic proposal-evaluation control plane.

The loop combines pressure, proposal context, gate policy, caller-reported
consequences, memory, and deterministic role labels. The kernel returns an
advisory verdict; it does not execute actions or attest caller reports.

Public surface: shared contract types only. Subsystem classes are imported
from their respective modules to keep import overhead low.
"""

from codomyrmex.colony_kernel.actuation_gate import ActuationGate
from codomyrmex.colony_kernel.attestation import (
    AttestationLedger,
    Ed25519Signer,
    Ed25519Verifier,
    HMACSigner,
    LedgerEvent,
    LedgerEventType,
    LedgerValidationResult,
    LedgerValidationStatus,
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
from codomyrmex.colony_kernel.falsification_worker import FalsificationWorker
from codomyrmex.colony_kernel.formal import (
    FormalResult,
    FormalStatus,
    KernelFormalSnapshot,
    prove_kernel_obligations,
    runtime_obligations,
    z3_available,
)
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
from codomyrmex.colony_kernel.reference import (
    ReferenceDecision,
    ReferenceGate,
    ReferenceInput,
    ReferencePolicy,
    ReferenceResult,
    ReferenceState,
)
from codomyrmex.colony_kernel.replay import (
    REPLAY_SCHEMA_VERSION,
    run_paired_locality_replay,
    write_replay_artifact,
)
from codomyrmex.colony_kernel.resource_ledger import (
    ResourceBudget,
    ResourceLedger,
    ThreadSafeResourceLedger,
)
from codomyrmex.colony_kernel.role_adapter import RoleAdapter

__all__ = [
    "COLONY_KERNEL_CONFIG_DIR",
    "REPLAY_SCHEMA_VERSION",
    "ActionProposal",
    "ActuationGate",
    "AgentRole",
    "AgentTrustProfile",
    "AttestationLedger",
    "ColonyKernel",
    "ColonyKernelConfig",
    "ColonySignal",
    "ConsequenceMemory",
    "ConsequenceRecord",
    "DecayRate",
    "Ed25519Signer",
    "Ed25519Verifier",
    "FalsificationFinding",
    "FalsificationSeverity",
    "FalsificationWorker",
    "FormalResult",
    "FormalStatus",
    "GateDecision",
    "GateResult",
    "HMACSigner",
    "KernelFormalSnapshot",
    "LedgerEvent",
    "LedgerEventType",
    "LedgerValidationResult",
    "LedgerValidationStatus",
    "PheromoneStore",
    "PruningCandidate",
    "PruningDaemon",
    "ReferenceDecision",
    "ReferenceGate",
    "ReferenceInput",
    "ReferencePolicy",
    "ReferenceResult",
    "ReferenceState",
    "ResourceBudget",
    "ResourceCost",
    "ResourceLedger",
    "RoleAdapter",
    "SignalSource",
    "SignalType",
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
    "prove_kernel_obligations",
    "run_paired_locality_replay",
    "runtime_obligations",
    "write_replay_artifact",
    "z3_available",
]
