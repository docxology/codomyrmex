"""Shell completion generation for bash, zsh, and fish.

Generates shell completion scripts for the codomyrmex CLI,
supporting argument and subcommand tab-completion.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_bash_completion(commands: dict[str, dict[str, Any]],
                             program_name: str = "codomyrmex") -> str:
    """Generate bash completion script."""
    cmd_names = " ".join(commands.keys())
    lines = [
        f'_{program_name}_completions() {{',
        '    local cur prev opts',
        '    COMPREPLY=()',
        '    cur="${COMP_WORDS[COMP_CWORD]}"',
        '    prev="${COMP_WORDS[COMP_CWORD-1]}"',
        f'    opts="{cmd_names}"',
        '',
        '    if [[ ${COMP_CWORD} -eq 1 ]]; then',
        '        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )',
        '        return 0',
        '    fi',
        '',
        '    case "${prev}" in',
    ]
    for cmd, info in commands.items():
        subopts = info.get("options", [])
        if subopts:
            opts_str = " ".join(subopts)
            lines.append(f'        {cmd})')
            lines.append(f'            COMPREPLY=( $(compgen -W "{opts_str}" -- ${{cur}}) )')
            lines.append('            return 0 ;;')
    lines.extend([
        '        *) ;;',
        '    esac',
        '}',
        f'complete -F _{program_name}_completions {program_name}',
    ])
    return "\n".join(lines) + "\n"


def generate_zsh_completion(commands: dict[str, dict[str, Any]],
                            program_name: str = "codomyrmex") -> str:
    """Generate zsh completion script."""
    lines = [
        f'#compdef {program_name}',
        '',
        f'_{program_name}() {{',
        '    local -a commands',
        '    commands=(',
    ]
    for cmd, info in commands.items():
        desc = info.get("description", cmd)
        lines.append(f'        "{cmd}:{desc}"')
    lines.extend([
        '    )',
        '',
        '    _describe "command" commands',
        '}',
        '',
        f'_{program_name}',
    ])
    return "\n".join(lines) + "\n"


def generate_fish_completion(commands: dict[str, dict[str, Any]],
                             program_name: str = "codomyrmex") -> str:
    """Generate fish completion script."""
    lines = []
    for cmd, info in commands.items():
        desc = info.get("description", cmd)
        lines.append(
            f"complete -c {program_name} -n '__fish_use_subcommand' "
            f"-a '{cmd}' -d '{desc}'"
        )
        for opt in info.get("options", []):
            lines.append(
                f"complete -c {program_name} -n '__fish_seen_subcommand_from {cmd}' "
                f"-l '{opt.lstrip('-')}'"
            )
    return "\n".join(lines) + "\n"


def install_completion(shell: str, output_path: Path | None = None,
                       commands: dict[str, dict[str, Any]] | None = None,
                       program_name: str = "codomyrmex") -> Path:
    """Generate and write a completion script for the given shell."""
    cmds = commands or {}
    if shell == "bash":
        content = generate_bash_completion(cmds, program_name)
        default_path = Path.home() / f".{program_name}-completion.bash"
    elif shell == "zsh":
        content = generate_zsh_completion(cmds, program_name)
        default_path = Path.home() / f".zsh/completions/_{program_name}"
    elif shell == "fish":
        content = generate_fish_completion(cmds, program_name)
        default_path = Path.home() / f".config/fish/completions/{program_name}.fish"
    else:
        raise ValueError(f"Unsupported shell: {shell}")

    path = output_path or default_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path
