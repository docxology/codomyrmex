from enum import Enum


class Command(Enum):
    """CLI command name constants used for routing in the codomyrmex CLI."""

    CHECK = "check"
    INFO = "info"
    MODULES = "modules"
    STATUS = "status"
    DOCTOR = "doctor"
    SHELL = "shell"
    CHAT = "chat"
    WORKFLOW = "workflow"
    PROJECT = "project"
    ORCHESTRATION = "orchestration"
    AI = "ai"
    ANALYZE = "analyze"
    BUILD = "build"
    MODULE = "module"
    FPF = "fpf"
    SKILLS = "skills"
    RUN = "run"
    PIPE = "pipe"
    BATCH = "batch"
    CHAIN = "chain"
    EXEC = "exec"
    MOD = "mod"
