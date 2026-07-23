# Build Orchestration

The `codomyrmex.ci_cd_automation.build` package provides build-environment
inspection, argument-vector command execution, artifact synthesis, validation,
reporting, and small build-history helpers.

Build commands are intentionally executed with `shell=False` semantics. Pass a
list such as `["python", "-m", "pytest"]`; do not pass an interpolated shell
string.

The `artifact_type` values are explicit: `copy` copies one file or tree,
`package` preserves a source tree, `archive` writes a ZIP archive, and
`executable` creates a file artifact. Language labels are descriptive metadata;
the package does not select or run compilers automatically. Set `output_root`
when a build needs an explicit containment boundary; artifact outputs must be
inside that root and rollback will never remove the root itself.

```python
from codomyrmex.ci_cd_automation.build import orchestrate_build_pipeline

result = orchestrate_build_pipeline(
    {"build_commands": [["python", "-m", "compileall", "src"]]}
)
```

Pipeline results use explicit statuses: `success`, `failed`, `timed_out`,
`invalid`, or intentional `noop`. A rollback may remove only artifacts created
by that recorded build and only beneath its resolved `output_root`; it does not
delete pre-existing outputs merely because they share a destination. Timeout
and malformed-command results are failures for CI purposes even when a caller
chooses to continue collecting diagnostics.
