<!-- readme: generated -->

# colony_kernel

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/colony_kernel/`

## Overview

Colony Kernel — a deterministic proposal-evaluation control plane.

The loop combines pressure, proposal context, gate policy, caller-reported
consequences, memory, and deterministic role labels. The kernel returns an
advisory verdict; it does not execute actions or attest caller reports.

## Public Exports

`colony_kernel` exports 62 public symbols via `__all__`:

`COLONY_KERNEL_CONFIG_DIR`, `REPLAY_SCHEMA_VERSION`, `ActionProposal`, `ActuationGate`, `AgentRole`, `AgentTrustProfile`, `AttestationLedger`, `ColonyKernel`, `ColonyKernelConfig`, `ColonySignal`, `ConsequenceMemory`, `ConsequenceRecord`, `DecayRate`, `Ed25519Signer`, `Ed25519Verifier`, `FalsificationFinding`, `FalsificationSeverity`, `FalsificationWorker`, `FormalResult`, `FormalStatus`, `GateDecision`, `GateResult`, `HMACSigner`, `KernelFormalSnapshot` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../colony_kernel/](../../../../colony_kernel/)
