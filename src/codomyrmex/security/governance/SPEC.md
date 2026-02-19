# governance - Functional Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides governance capabilities for the Codomyrmex platform, including contract lifecycle management with signing and compliance, rule-based policy enforcement and evaluation, dispute filing and resolution workflows, and compliance visualization.

## Design Principles

- **Transparency**: All governance actions are traceable and auditable through structured data models
- **Accountability**: Contracts require explicit signatures from all parties before activation
- **Consistency**: Policy enforcement applies rules uniformly across all contexts
- **Auditability**: All state transitions (contract signing, dispute resolution) are timestamped and recorded

## Functional Requirements

1. **Contract Management**: Create, sign, activate, and terminate contracts with multi-party support
2. **Policy Evaluation**: Define callable policy rules and enforce them against arbitrary contexts
3. **Dispute Workflow**: File disputes against contracts, track status through review and resolution stages
4. **Compliance Visualization**: Render policy compliance metrics as visual charts

## Interface Contracts

### Contracts (`contracts.py`)

- `ContractStatus`: Enum with DRAFT, ACTIVE, TERMINATED, DISPUTED states
- `ContractError`: Base exception for contract-related errors
- `ContractTerm`: Dataclass representing a contract clause with `id`, `description`, and `mandatory` flag
- `Contract(title, text, parties)`: Create a contract in DRAFT status
- `Contract.sign(signer_id, digital_signature)`: Sign the contract; auto-activates when all parties sign
- `Contract.terminate()`: Move contract to TERMINATED status

### Policy (`policy.py`)

- `PolicyError`: Exception raised on policy violations
- `PolicyRule` / `Policy(name, rule, error_message)`: Executable governance rule with a callable check
- `Policy.check(context)`: Evaluate the rule against a context dict; raises `PolicyError` on violation
- `PolicyEngine()`: Manages a collection of policies
- `PolicyEngine.add_policy(policy)`: Register a policy
- `PolicyEngine.enforce(context)`: Run all policies; raises `PolicyError` with aggregated violations

### Dispute Resolution (`dispute_resolution.py`)

- `DisputeStatus`: Enum with OPEN, UNDER_REVIEW, RESOLVED, CLOSED states
- `DisputeError`: Exception for dispute-related errors
- `DisputeResolver()`: Manages dispute lifecycle
- `DisputeResolver.file_dispute(dispute)`: Register a new dispute
- `DisputeResolver.resolve_dispute(dispute_id, resolution)`: Resolve a dispute with a resolution string
- `DisputeResolver.get_dispute(dispute_id)`: Retrieve a dispute by ID

### Visualization (`visualization.py`)

- `plot_policy_compliance(engine)`: Render a pie chart of policy compliance rates

## Error Handling

All operations handle errors gracefully:
- Contract signing validates signer identity and prevents duplicate signatures
- Policy enforcement aggregates all violations before raising a single error
- Dispute filing rejects duplicate dispute IDs
- Visualization handles missing data with default mock values

## Configuration

Module uses default configurations:
- Contracts auto-activate upon receiving all required signatures
- PolicyEngine runs all registered rules on each `enforce()` call
- Dispute resolution tracks status transitions via the `DisputeStatus` enum
- Visualization uses the `data_visualization` module for chart rendering

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
