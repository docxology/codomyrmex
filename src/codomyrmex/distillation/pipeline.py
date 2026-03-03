"""
Knowledge Distillation implementation.

Implements the knowledge distillation framework from Hinton et al. (2015).
A student network learns from both hard labels and soft targets produced
by a teacher network at elevated temperature.

L = alpha * T^2 * KL(student_soft || teacher_soft) + (1 - alpha) * CE(student, labels)

Pure Python + NumPy. No PyTorch dependency.
"""

import numpy as np


def soft_labels(logits: np.ndarray, temperature: float = 4.0) -> np.ndarray:
    """
    Convert teacher logits to soft probability targets using temperature.

    High temperature softens the distribution (dark knowledge):
    p(y|x, T) = exp(z_i / T) / sum(exp(z_j / T))

    Args:
        logits: Teacher model logits (batch, vocab_size) or (batch, seq, vocab_size)
        temperature: Temperature T (>1 = softer distribution)

    Returns:
        Soft probabilities
    """
    scaled = logits / temperature
    scaled_max = np.max(scaled, axis=-1, keepdims=True)
    exp = np.exp(scaled - scaled_max)
    return exp / (np.sum(exp, axis=-1, keepdims=True) + 1e-9)


def distillation_loss(
    student_logits: np.ndarray,
    teacher_logits: np.ndarray,
    true_labels: np.ndarray | None = None,
    temperature: float = 4.0,
    alpha: float = 0.7,
) -> dict:
    """
    Knowledge distillation loss (Hinton et al. 2015).

    L = alpha * T^2 * KL(student_soft || teacher_soft) + (1-alpha) * CE(student, labels)

    The T^2 factor normalizes the gradient magnitude (standard practice).

    Args:
        student_logits: Student model outputs (batch, num_classes)
        teacher_logits: Teacher model outputs (batch, num_classes)
        true_labels: Ground truth class indices (batch,), optional
        temperature: Distillation temperature T
        alpha: Weight for distillation loss (1-alpha for CE loss)

    Returns:
        dict with: total_loss, distillation_loss, ce_loss, teacher_accuracy
    """
    # Soft targets
    teacher_soft = soft_labels(teacher_logits, temperature)
    student_soft = soft_labels(student_logits, temperature)

    # KL divergence: KL(student || teacher) = sum(teacher * log(teacher/student))
    # We use: sum(teacher_soft * log(teacher_soft / student_soft + eps))
    kl_loss = float(
        np.mean(
            np.sum(
                teacher_soft * np.log(teacher_soft / (student_soft + 1e-9) + 1e-9),
                axis=-1,
            )
        )
    ) * (temperature**2)  # T^2 normalization

    # Cross-entropy with hard labels
    ce_loss = 0.0
    if true_labels is not None:
        # log-softmax of student
        student_lse = student_logits - np.max(student_logits, axis=-1, keepdims=True)
        log_probs = student_lse - np.log(
            np.sum(np.exp(student_lse), axis=-1, keepdims=True) + 1e-9
        )
        batch_size = len(true_labels)
        ce_loss = float(
            -np.mean([log_probs[b, true_labels[b]] for b in range(batch_size)])
        )

    total_loss = alpha * kl_loss + (1 - alpha) * ce_loss

    # Teacher accuracy for comparison
    teacher_preds = np.argmax(teacher_logits, axis=-1)
    teacher_acc = (
        float(np.mean(teacher_preds == true_labels)) if true_labels is not None else 0.0
    )

    return {
        "total_loss": total_loss,
        "distillation_loss": kl_loss,
        "ce_loss": ce_loss,
        "teacher_accuracy": teacher_acc,
        "temperature": temperature,
        "alpha": alpha,
    }


class DistillationLoss:
    """Stateful knowledge distillation loss."""

    def __init__(self, temperature: float = 4.0, alpha: float = 0.7):
        self.temperature = temperature
        self.alpha = alpha

    def __call__(self, student_logits, teacher_logits, labels=None):
        """Compute distillation loss."""
        return distillation_loss(
            student_logits,
            teacher_logits,
            labels,
            self.temperature,
            self.alpha,
        )
