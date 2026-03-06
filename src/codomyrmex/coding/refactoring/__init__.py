"""Code refactoring tools — rename, extract, and inline operations."""

from .extract import ExtractFunctionRefactoring
from .inline import InlineRefactoring
from .models import Change, Location, Refactoring, RefactoringResult, RefactoringType
from .rename import RenameRefactoring


def create_refactoring(refactoring_type: RefactoringType, **kwargs) -> Refactoring:
    """Factory function for refactoring operations."""
    refactorings: dict[RefactoringType, type[Refactoring]] = {
        RefactoringType.RENAME: RenameRefactoring,
        RefactoringType.EXTRACT_FUNCTION: ExtractFunctionRefactoring,
        RefactoringType.INLINE: InlineRefactoring,
    }
    cls = refactorings.get(refactoring_type)
    if not cls:
        raise ValueError(f"Unsupported refactoring type: {refactoring_type}")
    return cls(**kwargs)


__all__ = [
    "Change",
    "ExtractFunctionRefactoring",
    "InlineRefactoring",
    "Location",
    "Refactoring",
    "RefactoringResult",
    "RefactoringType",
    "RenameRefactoring",
    "create_refactoring",
]
