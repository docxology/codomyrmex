from dataclasses import dataclass
from datetime import datetime

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Security awareness training."""

logger = get_logger(__name__)


@dataclass
class TrainingModule:
    """Represents a security awareness training module."""

    module_id: str
    title: str
    description: str
    content: str
    created_at: datetime
    difficulty: str  # beginner, intermediate, advanced


@dataclass
class TrainingResult:
    """Results from training assessment."""

    user_id: str
    module_id: str
    score: float  # 0.0 to 1.0
    completed_at: datetime
    effectiveness: str  # low, medium, high


class AwarenessTrainer:
    """Manages security awareness training."""

    def __init__(self):

        self.modules: dict[str, TrainingModule] = {}
        self.results: list[TrainingResult] = []
        logger.info("AwarenessTrainer initialized")

    def create_module(
        self,
        module_id: str,
        title: str,
        description: str,
        content: str,
        difficulty: str = "intermediate",
    ) -> TrainingModule:
        """Create a new training module."""
        module = TrainingModule(
            module_id=module_id,
            title=title,
            description=description,
            content=content,
            created_at=datetime.now(),
            difficulty=difficulty,
        )
        self.modules[module_id] = module
        logger.info(f"Created training module: {title}")
        return module

    def assess_effectiveness(self, user_id: str) -> dict:
        """Assess training effectiveness for a user."""
        user_results = [r for r in self.results if r.user_id == user_id]

        if not user_results:
            return {
                "user_id": user_id,
                "modules_completed": 0,
                "average_score": 0.0,
                "effectiveness": "unknown",
            }

        avg_score = sum(r.score for r in user_results) / len(user_results)

        effectiveness = "high" if avg_score > 0.8 else "medium" if avg_score > 0.6 else "low"

        return {
            "user_id": user_id,
            "modules_completed": len(user_results),
            "average_score": avg_score,
            "effectiveness": effectiveness,
        }


def create_training_module(
    module_id: str,
    title: str,
    description: str,
    content: str,
    difficulty: str = "intermediate",
    trainer: AwarenessTrainer | None = None,
) -> TrainingModule:
    """Create a training module."""
    if trainer is None:
        trainer = AwarenessTrainer()
    return trainer.create_module(module_id, title, description, content, difficulty)


def assess_training_effectiveness(
    user_id: str,
    trainer: AwarenessTrainer | None = None,
) -> dict:
    """Assess training effectiveness."""
    if trainer is None:
        trainer = AwarenessTrainer()
    return trainer.assess_effectiveness(user_id)

