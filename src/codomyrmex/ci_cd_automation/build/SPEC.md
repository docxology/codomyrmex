# Build Orchestration Specification

## Scope

This package supplies the documented build-synthesis compatibility surface for
CI/CD workflows. It does not install dependencies, execute shell strings, or
perform implicit workspace cleanup.

## Safety and reliability

- Commands use argument vectors and `subprocess.run(..., shell=False)`.
- Commands have bounded timeouts.
- Missing sources, invalid configurations, and failed commands return explicit
  errors in the pipeline result.
- `copy`, `package`, `archive`, and `executable` have distinct semantics;
  archives include files and directories as ZIP members.
- Language labels do not imply compiler support. Compilers and packagers must
  be supplied explicitly through argument-vector build commands.
- Artifact cleanup accepts only explicitly supplied paths and can enforce an
  `output_root` containment boundary; rollback never removes that root itself.
- Build history is bounded to the most recent 100 in-process records.
- A language label is descriptive only. Compiler support exists only when the
  caller supplies an explicit compiler command in `build_commands`.
- The result schema distinguishes `success`, `failed`, `timed_out`, `invalid`,
  and `noop`; these states must not be collapsed into a boolean.
