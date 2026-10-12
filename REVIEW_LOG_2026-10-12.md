# Repository review — 2026-10-12

Base revision: `b4400093247c028feaa9139967c68c43f47723fe`.
The initial GitHub snapshot had no open issues and nine open PRs.

## PR dispositions

| PR | Reviewed result |
| --- | --- |
| #568 | Specification validators, shared lint configuration and corrected source specifications integrated. Unresolved/undocumented inventories remain explicit. |
| #569 / #573 | Overlapping accessibility proposals consolidated; visible labels associated and omitted forms covered. |
| #570 | Original denylist insufficient; replaced by explicit capabilities and negative controls, including constructor file logging. |
| #571 | Import/test hygiene integrated; unmanaged Ruff cache and failed snapshot observations corrected without weakening guards. |
| #572 | Local-deque cleanup integrated with boundary, weighted-quota, clock and concurrency regressions. |
| #574 | Journal only; current STT implementation already uses argument lists. |
| #575 | Empty diff; referenced component is absent. |
| #576 | Journal only; referenced components are absent. |

Original proposal branches are retained. The consolidated source change carries
independent review findings and their corrections rather than merging stale,
duplicate or insufficient patches.

## Verification

- Colony Kernel: 889 passed, 2 existing skips in the final scoped run.
- Final focused documentation/limiter/SPA corrections: 156 passed.
- Independent final documentation/limiter review: 128 passed.
- Z3 capability regressions use bounded real subprocesses; supported models
  include integers, arrays, bitvectors, functions, quantifiers and optimization.
- Final connected audio suite: 230 passed, 3 existing remote-service skips.
  Nineteen dedicated connector/preflight/discovery controls passed. Whisper/Hermes
  use pinned public tiny/base assets; the remote Edge service returned HTTP 403.
- Package-wide Ruff, formatting and ty checks passed without suppressions added
  or checker rules relaxed. Architecture/export gates passed.
- Strict documentation/link/structure/MkDocs gate passed; final metadata refresh
  passed again before publication.
- Complete declared local profile: 36,173 passed, 722 skipped, 57 performance/
  benchmark items excluded by the unchanged Makefile selection. Total coverage
  74.87% exceeds the unchanged 60% floor. Python 3.13.16, four pytest-xdist workers,
  all locked extras plus docs group, isolated account/configuration inputs and
  pinned cached public tiny/base speech assets. All 4,516 source/test/toolchain
  input hashes remained unchanged through the run.
- Public model revisions used locally: tiny
  `d90ca5fe260221311c53c58e660288d3deb8d356`, base
  `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`. Model bytes/cache stay outside the
  repository; this is local execution evidence, not speech-accuracy validation.
- The completed first isolated full run retained 6 failures, 7 manuscript setup
  errors and a skills-test worker crash: 36,139 passed and 723 skipped. Its 25%
  coverage result failed the unchanged 60% floor. This is negative evidence.
  Real SDK namespace contamination, async loop ownership and the one-time
  listener race, failed Fabric listing, stale active metadata, an adjacent
  template revision mismatch and a remote clone in a local skills test were
  reproduced and corrected. The corrected full gate passed as recorded above.
- Event/Fabric corrections: 588 passed, 3 explicit live-workflow skips;
  independent final controls: 27 passed.
- Corrected SDK controls under full four-worker collection: 15 passed;
  five existing module-collection skips. Genuine local SDK signing/metadata
  does not establish successful cloud reads or writes.
- Standalone manuscript controls: 37 passed, with actual temporary generation,
  configured revision and explicit strict-successor/unknown-Git provenance.
  Wrong revision, dirty checkout, missing module and missing selected path
  remain real Git-backed negative controls. No sibling checkout was changed.
- Skills local Git controls: 8 passed without remote cloning.
- Locked audit: 496 distinct pins, both NumPy versions, zero unexcepted
  advisories and two existing exact-version exceptions retained as evidence.
- Built wheel and source archive include research/falsification `py.typed`.
- Local Chromium static-SPA checks cover accessible form names, initial focus,
  hidden/disabled/empty dialogs, Tab/Shift+Tab, background shortcuts, Escape,
  original focus and restoration of prior inert states.
- All 130 renamed README snapshots remain byte-identical to the base revision.

## Limits and remaining gates

Static browser evidence does not establish live backend or screen-reader
acceptance. Composite/QuotaManager operations are not cross-limiter transactions.
Z3 model construction/native code still requires process/resource isolation for
untrusted input. Zero broken resolved spec references does not resolve the
remaining unknown API signatures or document every MCP tool.

R2–R7/F5 scientific studies require independently sourced workloads, execution
outcomes and replication. Local diagnostics do not supply that evidence, change
published release receipts or grant deployment/provider authority.

First failures were retained: the clone's case-collision diff; the original PR571
CI cache failure; a concurrent MkDocs `site/` observation during an otherwise
passing colony run; malformed invariant inputs and integer precision controls;
constructor logging; modal focus/shortcut failures; and earlier full runs
interrupted for review corrections. These are superseded by corrected scoped
runs, not erased or relabeled as successful acceptance.

The original changed-file Markdown check reported 3,285 errors, principally
in the legacy generated Docusaurus mirror. `.markdownlintignore` already
declared generated-content exclusions; the missing precise mirror path was
added to that boundary. Its 130 verbatim snapshots remain unchanged. Edited
canonical documents were formatted and linted without relaxing rule settings.
