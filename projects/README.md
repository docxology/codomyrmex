<!-- readme: curated -->

# Project workspaces

`projects/` holds integration and example workspaces that are not part of the
top-level `codomyrmex` Python package. The current checkout contains
[`test_project/`](test_project/), which is a standalone nested Git worktree.

Workspace membership can change independently of package modules. Inspect the
filesystem and nested Git status rather than relying on an old static list.

## Safety

```bash
git status --short
git -C projects/test_project status --short
```

Do not pull, reset, clean, format, or commit a nested repository as part of a
package-wide maintenance pass unless that repository is explicitly in scope.

## Navigation

- [Agent guidance](AGENTS.md)
- [Workspace specification](SPEC.md)
- [Repository root](../README.md)
