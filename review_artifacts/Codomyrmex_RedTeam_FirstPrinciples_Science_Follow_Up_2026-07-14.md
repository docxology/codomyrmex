# Codomyrmex Red-Team / First-Principles / Science Follow-Up

**Date:** 2026-07-14
**Candidate:** `v1.4.0-rc16`
**Historical audit anchor:** `v1.4.0-rc1` at `471f998719bcbbdd756cedb66a2d8e95762dd542`
**Current revision:** recorded in the clean-clone manifest for tag `v1.4.0-rc16`
**Execution mode:** internal specialist panel; no independent subagents were available in the host

## Scope and goal

This follow-up audits the publication verifier, strict authorization lifecycle, generated evidence, and
the remaining TODO/release claims. The success condition is narrower than “the system is safe”: a clean
immutable checkout must be able to show that the manifest, source inputs, generated artifacts, test
evidence, and declared enforcement semantics are the same release.

The provider-backed controlled/SWE-bench evaluation remains a required external experiment. It is not
fabricated or replaced by the deterministic fixture adapter.

## First-principles decomposition

The release claim consists of five irreducible evidence links:

1. checkout identity — current `HEAD`, exact tag, and clean status;
2. input identity — source, lockfile, configuration, and benchmark hashes;
3. output identity — independently recomputed artifact hashes and freshness;
4. measurement identity — JUnit, status JSON, and coverage agree;
5. scope identity — a declared action request is authorized, consumed once, and linked to a signed receipt.

The following are policy choices rather than physical constraints: the 60% coverage floor, the RC/final
release sequence, the 0.20-inch manuscript side margins, and the use of SQLite. They are retained because
they serve reproducibility and auditability, not because they are immutable. The hard evidence boundary
is that a manifest or receipt cannot prove truth merely by existing; it can only prove the signed and
measured facts it actually binds.

## Verifier-first findings and repairs

| Finding | Evidence location | Negative control | Result |
|---|---|---|---|
| Manifest could be evaluated against a different checkout | `scripts/verify_release_candidate.py`, `verify()` | Substitute another commit while retaining artifact hashes | Fixed: current `HEAD`, dirty state, and exact tag are compared |
| Source/config claims were trusted | `scripts/generate_release_manifest.py` and verifier | Change a source or lock/config input without regenerating artifacts | Fixed: aggregate hashes and freshness are recomputed |
| Status artifact could disagree with claimed status | release verifier | Hand-edit status JSON and refresh only its hash | Fixed: manifest, status JSON, and independently parsed JUnit must agree |
| Empty strict scope could silently widen to defaults | `authorization.py` and `executor.py` constructors | Provision `action_scope={}` and attempt a default action | Fixed: explicit empty maps remain empty and fail closed |
| Outcome could be relinked to same-ID, different-target proposal context | `ColonyKernel.record_attested_outcome` | Reuse a consumed receipt with altered action/target | Fixed: action, target, agent, proposal, receipt, and request digest must match |
| Ledger could record a receipt-free attested report directly | `AuthorizationLedger.record_outcome_report` | Call ledger report insertion after consumption but before receipt | Fixed: consumed authorization and linked receipt are required |
| Valid authorization payload could be altered at execution | `ExecutionAuthorization`, `RegisteredActionExecutor` | Sign an `action_payload`, execute a different payload | Fixed: optional explicit payload digest is signed and receipt-linked |
| Benchmark row could report a different task partition than the manifest | `evaluations/colony_kernel/stages.py`, `parse_result()` and `render_report()` | Change a development row to `held_out` while retaining the task ID | Fixed: instance ID and partition are normalized and checked |
| Enforced receipt identities could be reused across rows | `evaluations/colony_kernel/stages.py`, `render_report()` | Reuse an authorization, proposal, or request digest in a second enforced row | Fixed: each enforced identity is single-use in the report |
| Receipt verification metadata could be self-asserted | `evaluations/colony_kernel/stages.py`, `parse_result()` | Tamper a signed receipt while leaving `signature_valid=true` | Fixed: release runs verify Ed25519 against the pinned public-key registry |
| Release package hash could be recorded without being checked | `scripts/verify_release_candidate.py` | Alter the transport archive after writing its manifest | Fixed: package hash, declared members, and sidecar manifest consistency are checked |

## Scientific cycle

### Pre-registered hypotheses

- **H1 — verifier binding:** a candidate bound to another commit or changed source must fail verification.
- **H2 — lifecycle integrity:** altered scope, payload, receipt, or proposal context must not update enforced state.
- **H3 — evidence separation:** policy rejection, prospective risk, caller reports, and attested execution remain distinct.
- **H4 — reproducible build:** after regenerating from the pinned revision, the canonical PDF and evidence data hashes remain stable.
- **H5 — external effectiveness:** the gate improves measured outcomes against baselines. This remains untested until a concrete provider/model configuration and signed benchmark receipts are supplied.

### Experiments and observed results

The verifier and enforcement negative controls passed with real components. The final scoped release
suite completed after artifact regeneration with 840 JUnit-collected and passed tests, zero skipped,
failed, or errored tests, 74.37185929648241% branch coverage (592/796), and 82.59604190919674% line
coverage (2,246/2,640). Its machine-readable status, JUnit, and coverage artifacts remain the release
authority.

H1–H4 are supported for the tested contracts and clean-clone replay. H5 is
**inconclusive/unrun**, not a failed or successful benchmark result.

## Remaining blockers and TODOs

- **A-001 / A-016:** immutable release publication and final manuscript/evidence attachment remain open.
- **R-20:** provider-backed controlled and pinned SWE-bench Lite execution remains open.
- The provider configuration must supply a trusted executor public-key registry; receipt metadata alone
  is not benchmark evidence.
- The strict boundary still governs only the declared action-scope map; unregistered mutating paths are
  explicit bypasses and must not be described as repository-wide enforcement.
- Signed receipts attest the executor’s recorded request/result linkage; they do not independently validate
  semantic truth, human understanding, or production safety.

## Re-review gate

The clean-clone PDF/evidence replay and required test gate are complete. Re-review remains contingent on
the provider benchmark supplying its pinned configuration, raw rows, cryptographically verified receipts,
environment digest, and reports, followed by public immutable evidence attachment. Until then, this
candidate is an auditable RC15 with a publication hold, not a completed production-safety release.
