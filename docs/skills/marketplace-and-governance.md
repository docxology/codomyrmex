# The Tool Supplier and the Lockout Cabinet

Two systems govern what enters the workshop and what is permitted once inside.
The **marketplace** manages external sources of skills -- the supplier
showroom where new tools are browsed, evaluated, and installed. The
**permissions** module is the lockout cabinet: a controlled access system that
determines which skills may perform which actions, with a full audit trail.
Between them, **versioning** tracks compatibility so that upgrading one tool
does not break the jigs that depend on it.

## Marketplace: The Supplier Showroom

### Remote Skill Sources

`SkillMarketplace` maintains a list of remote sources from which skills can
be discovered and installed. Each source is a dictionary with `name`, `url`,
and `type` fields:

```python
from codomyrmex.skills.marketplace import SkillMarketplace

market = SkillMarketplace()
sources = market.list_sources()
# [{"name": "vibeship-spawner-skills", "url": "https://...", "type": "git"}]
```

Source types map to the `SourceType` concept:

| Type | Description |
|---|---|
| `git` | Git repository cloned locally |
| `local` | Local filesystem directory |
| `http` | HTTP endpoint serving skill manifests |
| `registry` | Centralized skill registry service |

### Search and Install Workflow

The marketplace search and install workflow follows a deliberate sequence:

1. **Search** -- `search_remote(query)` queries configured sources for
   matching skills and returns metadata summaries.
2. **Evaluate** -- Review the returned metadata (name, description, source)
   before committing to installation.
3. **Install** -- `install(skill_id, source)` fetches the skill from the
   named source and places it in the local workshop.
4. **Verify** -- After installation, the skill passes through the standard
   validation pipeline before it enters the registry.

```python
results = market.search_remote("code formatting")
market.install("format_python", source="vibeship-spawner-skills")
```

### Source Management

Sources can be added and removed dynamically:

```python
market.add_source("internal-tools", "https://tools.internal.dev", source_type="http")
market.remove_source("internal-tools")
```

## Version Management

`SkillVersionManager` in `versioning/__init__.py` tracks skill versions and
checks compatibility using semver conventions.

### Version Status

The `VersionStatus` concept describes where a version sits in its lifecycle:

| Status | Meaning |
|---|---|
| `CURRENT` | Active, recommended version |
| `DEPRECATED` | Still functional, scheduled for removal |
| `YANKED` | Removed due to defect, should not be used |
| `PRERELEASE` | Available for testing, not production-ready |

### Compatibility Checking

Versions are compatible when they share the same major version and the
installed version is greater than or equal to the required version:

```python
from codomyrmex.skills.versioning import SkillVersionManager

vm = SkillVersionManager()
result = vm.check_compatibility(my_skill, required_version="1.2.0")
# {"compatible": True, "current_version": "1.3.1", "required_version": "1.2.0"}
```

Version history is tracked per skill ID:

```python
vm.register_version("abc123", "1.0.0")
vm.register_version("abc123", "1.1.0")
versions = vm.list_versions("abc123")  # ["1.0.0", "1.1.0"]
```

## Permissions: The Lockout Cabinet

### Actions and Permission Levels

`SkillPermissionManager` controls what operations a skill is allowed to
perform. The `SkillAction` concept covers the action space:

| Action | Description |
|---|---|
| `execute` | Run the skill |
| `read` | Access data without modification |
| `write` | Create or modify data |
| `delete` | Remove data |
| `modify` | Alter skill configuration |
| `admin` | Full control including permission changes |

The `PermissionLevel` concept defines escalating trust tiers:

| Level | Scope |
|---|---|
| `NONE` | No access |
| `READ` | Read-only operations |
| `EXECUTE` | Run skills |
| `WRITE` | Modify data |
| `ADMIN` | Full access |

### Grant and Revoke

```python
from codomyrmex.skills.permissions import SkillPermissionManager

pm = SkillPermissionManager()
pm.grant("skill_abc123", "execute")
pm.grant("skill_abc123", "read")

can_run = pm.check_permission("skill_abc123", "execute")  # True
can_delete = pm.check_permission("skill_abc123", "delete")  # False

pm.revoke("skill_abc123", "execute")
```

### Audit Trails

Every `grant` and `revoke` operation is logged through the structured logging
system. This produces an audit trail that records who changed what permission
and when, which is essential for security reviews and compliance.

## Trust Considerations

The marketplace and permissions systems interact at a trust boundary. Skills
installed from remote sources enter the workshop with no permissions by
default. The operator must explicitly grant each action, following the
principle of least privilege. This mirrors the physical workshop: a new tool
from a supplier sits on the receiving bench until the craftsperson inspects
it and decides where it belongs.

## Key Source Paths

- `src/codomyrmex/skills/marketplace/__init__.py` -- `SkillMarketplace`
- `src/codomyrmex/skills/versioning/__init__.py` -- `SkillVersionManager`,
  `parse_version`
- `src/codomyrmex/skills/permissions/__init__.py` -- `SkillPermissionManager`

## Cross-References

- For the full API specification, see the
  [Module Documentation](../modules/skills/README.md).
- Return to the [Workshop Overview](./index.md) for the full reading guide.
- For skill loading and validation internals, see
  [Skill Lifecycle](./skill-lifecycle.md).
