<!-- readme: curated -->

# Configuration examples

This tree contains versioned defaults, schemas, and examples for Codomyrmex
modules. It must not contain live credentials, personal endpoints, or
machine-specific absolute paths.

## Usage boundary

- Treat files here as examples or repository defaults, not as a secret store.
- Copy user-specific overrides outside version control or into documented
  ignored locations.
- Environment variables and secret managers take precedence where the owning
  module documents them.
- Validate a configuration through the owning module's public loader or schema;
  do not assume every YAML file shares one global schema.
- Keep configuration, source defaults, tests, and module README/SPEC/security
  documentation aligned.

The Hermes skills profile is an example:
[`hermes_skills_profile.example.yaml`](hermes_skills_profile.example.yaml).
Its destination and precedence are documented in
[`docs/agents/hermes/skills.md`](../docs/agents/hermes/skills.md).

## Editing

Before changing a default:

1. locate all consumers and environment overrides;
2. run GitNexus impact analysis for affected loader symbols;
3. update schema and negative validation tests;
4. document compatibility and security effects;
5. run the owning module tests and package gates.

## Navigation

- [Agent guidance](AGENTS.md)
- [Configuration specification](SPEC.md)
- [Configuration management source](../src/codomyrmex/config_management/)
- [Repository root](../README.md)
