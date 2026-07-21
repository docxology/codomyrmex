# Codomyrmex Agents — ci_cd_automation/build

Build orchestration and artifact synthesis for trusted repository workflows.

## Contracts

- Build commands are argument vectors and execute without shell expansion.
- `copy`, `package`, `archive`, and `executable` are distinct artifact modes;
  language labels do not select an implicit compiler.
- Artifact paths are explicit caller targets; `output_root` is a hard
  containment boundary, and cleanup never scans or deletes a directory
  implicitly or removes the boundary itself.
- Public behavior is covered by `tests/unit/build_synthesis/test_build_synthesis.py`.
- Keep `README.md`, `SPEC.md`, and `PAI.md` aligned with the implementation.

## Navigation

- Parent: [ci_cd_automation](../AGENTS.md)
- README: [README.md](README.md)
- Specification: [SPEC.md](SPEC.md)
