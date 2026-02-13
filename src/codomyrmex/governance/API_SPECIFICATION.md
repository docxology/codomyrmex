# Governance - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Governance module. The primary purpose of this API is to provide contract management, policy-as-code enforcement, and dispute resolution capabilities for decentralized agent operations within the Codomyrmex ecosystem.

## Endpoints / Functions / Interfaces

### Enum: `ContractStatus`

- **Description**: Lifecycle states for a contract.
- **Module**: `codomyrmex.governance.contracts`
- **Values**:
    - `DRAFT` - Contract has been created but not all parties have signed
    - `ACTIVE` - All parties have signed; contract is in effect
    - `TERMINATED` - Contract has been terminated
    - `DISPUTED` - Contract is under dispute

### Class: `Party` (dataclass)

- **Description**: Represents a party to a contract.
- **Module**: `codomyrmex.governance.contracts`
- **Parameters/Arguments** (constructor):
    - `id` (str): Unique identifier for the party
    - `name` (str): Display name of the party
    - `role` (str): Role of the party in the contract (e.g., "buyer", "seller")

### Class: `Signature` (dataclass)

- **Description**: Represents a digital signature on a contract.
- **Module**: `codomyrmex.governance.contracts`
- **Parameters/Arguments** (constructor):
    - `signer_id` (str): ID of the signing party
    - `timestamp` (datetime, optional): When the signature was applied. Defaults to `datetime.now()`
    - `digital_signature` (str, optional): The digital signature string. Defaults to `""`

### Class: `Contract`

- **Description**: Represents a legal or smart contract between agents. Manages the full lifecycle from draft through signing to activation or termination. Auto-activates when all parties have signed.
- **Module**: `codomyrmex.governance.contracts`
- **Parameters/Arguments** (constructor):
    - `title` (str): Title of the contract
    - `text` (str): Full text/body of the contract
    - `parties` (List[Party]): List of parties to the contract
- **Attributes**:
    - `id` (UUID): Auto-generated unique identifier
    - `title` (str): Contract title
    - `text` (str): Contract body text
    - `parties` (List[Party]): Parties to the contract
    - `signatures` (List[Signature]): Collected signatures, initially empty
    - `status` (ContractStatus): Current lifecycle state, initialized to `DRAFT`
    - `created_at` (datetime): Timestamp of contract creation
- **Methods**:
    - `sign(signer_id: str, digital_signature: str = "") -> None`: Sign the contract. Validates that: (1) the contract is in DRAFT status, (2) the signer is a valid party, and (3) the signer has not already signed. Raises `ValueError` on any validation failure. Auto-transitions status to `ACTIVE` when all parties have signed.
    - `terminate() -> None`: Sets the contract status to `TERMINATED`.
    - `__repr__() -> str`: Returns `Contract(id=..., title='...', status=DRAFT)`.

### Class: `PolicyError`

- **Description**: Exception raised when a policy rule is violated or fails to execute.
- **Module**: `codomyrmex.governance.policy`
- **Inherits**: `Exception`

### Class: `Policy`

- **Description**: An executable governance rule. Encapsulates a callable rule function that evaluates a context dictionary and raises `PolicyError` on violation.
- **Module**: `codomyrmex.governance.policy`
- **Parameters/Arguments** (constructor):
    - `name` (str): Name of the policy
    - `rule` (Callable[[Dict[str, Any]], bool]): A callable that takes a context dict and returns `True` if the policy passes, `False` if it is violated
    - `error_message` (str): Message to display when the policy is violated
- **Methods**:
    - `check(context: Dict[str, Any]) -> None`: Evaluate the rule against the context. Raises `PolicyError` if the rule returns `False` or if the rule execution itself raises an exception.

### Class: `PolicyEngine`

- **Description**: Manages and enforces a collection of policies. Runs all registered policies against a context and aggregates violations.
- **Module**: `codomyrmex.governance.policy`
- **Parameters/Arguments** (constructor): None
- **Methods**:
    - `add_policy(policy: Policy) -> None`: Register a policy with the engine.
    - `enforce(context: Dict[str, Any]) -> None`: Run all registered policies against the given context. Collects all violations and raises a single `PolicyError` with all error messages joined by newlines if any policies fail.

### Function: `plot_policy_compliance(engine: PolicyEngine) -> str`

- **Description**: Renders a pie chart of policy compliance (pass vs fail). Currently uses mock data for demonstration.
- **Module**: `codomyrmex.governance.visualization`
- **Parameters/Arguments**:
    - `engine` (PolicyEngine): The policy engine to visualize
- **Returns/Response**: `str` - Rendered HTML string of a pie chart showing compliance rate.

## Data Models

### Party (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | required | Unique party identifier |
| `name` | `str` | required | Display name |
| `role` | `str` | required | Role in the contract |

### Signature (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `signer_id` | `str` | required | ID of the signing party |
| `timestamp` | `datetime` | `datetime.now()` | When the signature was applied |
| `digital_signature` | `str` | `""` | Digital signature string |

## Authentication & Authorization

Not applicable for this internal governance module.

## Rate Limiting

Not applicable for this internal governance module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
