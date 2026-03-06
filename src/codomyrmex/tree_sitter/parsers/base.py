"""Abstract Parser base class."""

from abc import ABC, abstractmethod

from .models import ASTNode


class Parser(ABC):
    """Abstract base class for source code parsers."""

    @property
    @abstractmethod
    def language(self) -> str:
        """Get the language this parser handles."""

    @abstractmethod
    def parse(self, source: str) -> ASTNode:
        """Parse source code into an AST."""

    @abstractmethod
    def get_functions(self, root: ASTNode) -> list[ASTNode]:
        """Extract function definitions."""

    @abstractmethod
    def get_classes(self, root: ASTNode) -> list[ASTNode]:
        """Extract class definitions."""

    @abstractmethod
    def get_imports(self, root: ASTNode) -> list[ASTNode]:
        """Extract imports."""
