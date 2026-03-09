"""
Rich terminal rendering implementation.

Provides high-level wrappers for the 'rich' library to create
engaging terminal interfaces with colors, tables, and progress.
"""

from typing import Any, Optional, TypeVar

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm, Prompt
from rich.status import Status
from rich.table import Table
from rich.theme import Theme

T = TypeVar("T")


class RichRenderer:
    """
    High-level renderer using the 'rich' library.
    """

    def __init__(
        self,
        theme: Optional[dict[str, str]] = None,
        force_terminal: Optional[bool] = None,
    ):
        """
        Initialize the Rich renderer.

        Args:
            theme: Optional dictionary of style names to rich styles.
            force_terminal: Force terminal output even if not a TTY.
        """
        custom_theme = Theme(theme) if theme else None
        self.console = Console(theme=custom_theme, force_terminal=force_terminal)
        self.error_console = Console(
            theme=custom_theme, force_terminal=force_terminal, stderr=True
        )

    def print(self, *args: Any, style: Optional[str] = None, **kwargs: Any) -> None:
        """Print styled text to the console."""
        self.console.print(*args, style=style, **kwargs)

    def error(self, *args: Any, style: str = "bold red", **kwargs: Any) -> None:
        """Print styled error message to stderr."""
        self.error_console.print(*args, style=style, **kwargs)

    def heading(self, text: str, style: str = "bold cyan") -> None:
        """Print a heading with a rule."""
        self.console.rule(f"[{style}]{text}[/{style}]")

    def panel(
        self, content: Any, title: Optional[str] = None, style: str = "blue"
    ) -> None:
        """Print content inside a panel."""
        self.console.print(Panel(content, title=title, border_style=style))

    def table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        title: Optional[str] = None,
        box_style: Any = None,
    ) -> None:
        """Print a formatted table."""
        table = Table(title=title, box=box_style)
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*[str(item) for item in row])
        self.console.print(table)

    def progress_bar(
        self,
        total: Optional[float] = None,
        transient: bool = True,
    ) -> Progress:
        """
        Create a progress bar context manager.

        Example:
            with renderer.progress_bar(total=100) as progress:
                task = progress.add_task("Downloading", total=100)
                while not progress.finished:
                    progress.update(task, advance=1)
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=transient,
        )

    def status(self, message: str, spinner: str = "dots") -> Status:
        """
        Create a status spinner context manager.

        Example:
            with renderer.status("Working..."):
                do_work()
        """
        return self.console.status(message, spinner=spinner)

    def prompt(
        self,
        message: str,
        default: Optional[str] = None,
        choices: Optional[list[str]] = None,
        password: bool = False,
        stream: Optional[Any] = None,
    ) -> str:
        """Prompt the user for input."""
        return __import__("typing").cast(
            str,
            Prompt.ask(
                message,
                console=self.console,
                default=default,
                choices=choices,
                password=password,
                stream=stream,
            ),
        )

    def confirm(
        self, message: str, default: bool = False, stream: Optional[Any] = None
    ) -> bool:
        """Ask the user for a yes/no confirmation."""
        return Confirm.ask(
            message, console=self.console, default=default, stream=stream
        )

    def live(self, renderable: Any, transient: bool = True) -> Live:
        """Create a live display context manager."""
        return Live(renderable, console=self.console, transient=transient)
