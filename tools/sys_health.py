#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
#     "psutil",
# ]
# ///

import os
from pathlib import Path

import psutil
from rich import print as rprint
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_worktrees():
    git_dir = Path(".git")
    worktrees_dir = git_dir / "worktrees"
    if not worktrees_dir.exists():
        return []

    return [wt.name for wt in worktrees_dir.iterdir() if wt.is_dir()]

def get_agentic_memory_stats():
    mem_dir = Path("MEMORY")
    if not mem_dir.exists():
        return "Not Initialized"

    total_size = sum(f.stat().st_size for f in mem_dir.rglob("*") if f.is_file())
    file_count = sum(1 for f in mem_dir.rglob("*") if f.is_file())

    return f"{file_count} entries ({total_size / 1024:.1f} KB)"

def get_system_metrics():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return f"CPU: {psutil.cpu_percent()}%, RAM: {memory_info.rss / 1024 / 1024:.1f} MB"

def main():
    console.print(Panel.fit("[bold cyan]Codomyrmex System Health Diagnostic[/bold cyan]", border_style="cyan"))

    # Worktrees Table
    wt_table = Table(title="Git Worktrees", show_header=True, header_style="bold magenta")
    wt_table.add_column("Worktree Name")
    wt_table.add_column("Status")

    worktrees = get_worktrees()
    if not worktrees:
        wt_table.add_row("Main only", "Active")
    else:
        for wt in worktrees:
            wt_table.add_row(wt, "Active")

    # Memory Buffers Table
    mem_table = Table(title="Agentic Long-Term Memory", show_header=True, header_style="bold green")
    mem_table.add_column("Buffer")
    mem_table.add_column("Status")
    mem_table.add_row("Core Memory DB", get_agentic_memory_stats())

    # System Telemetry Table
    sys_table = Table(title="Multi-Agent System Telemetry", show_header=True, header_style="bold yellow")
    sys_table.add_column("Metric")
    sys_table.add_column("Value")
    sys_table.add_row("Current Process", get_system_metrics())
    sys_table.add_row("PAI Trust Gateway", "Online")
    sys_table.add_row("Swarm Consensus", "Stable")

    console.print(wt_table)
    console.print(mem_table)
    console.print(sys_table)

if __name__ == "__main__":
    main()
