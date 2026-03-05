"""Knowledge Distillation -- teacher-student training pipeline."""

from .pipeline import DistillationLoss, distillation_loss, soft_labels

__all__ = ["DistillationLoss", "distillation_loss", "soft_labels"]
