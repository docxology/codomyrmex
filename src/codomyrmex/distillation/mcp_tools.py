"""MCP tools for the knowledge distillation module."""

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="distillation")
def distillation_compute_loss(
    num_classes: int = 10,
    batch_size: int = 4,
    temperature: float = 4.0,
    alpha: float = 0.7,
    seed: int = 42,
) -> dict:
    """Compute knowledge distillation loss on synthetic teacher-student data.

    Args:
        num_classes: Number of output classes
        batch_size: Number of samples
        temperature: Distillation temperature T (higher = softer)
        alpha: Weight for distillation vs hard-label loss
        seed: Random seed for reproducibility

    Returns:
        dict with: total_loss, distillation_loss, ce_loss, teacher_accuracy
    """
    from .pipeline import distillation_loss

    np.random.seed(seed)

    # Teacher: confident logits. Student: noisier logits.
    teacher_logits = np.random.randn(batch_size, num_classes) * 3.0
    student_logits = teacher_logits + np.random.randn(batch_size, num_classes)
    true_labels = np.argmax(teacher_logits, axis=-1)

    result = distillation_loss(
        student_logits, teacher_logits, true_labels, temperature, alpha
    )
    result["status"] = "success"
    return result
