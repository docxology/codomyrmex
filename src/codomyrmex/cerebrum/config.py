from typing import Any, Optional

from dataclasses import dataclass, field







"""Configuration management for CEREBRUM module."""



@dataclass
class CerebrumConfig:
    """Configuration for CEREBRUM engine."""

    # Case-based reasoning settings
    case_similarity_threshold: float = 0.7
    max_retrieved_cases: int = 10
    case_weighting_strategy: str = "distance"  # "distance", "frequency", "hybrid"

    # Bayesian inference settings
    inference_method: str = "variable_elimination"  # "variable_elimination", "mcmc", "belief_propagation"
    mcmc_samples: int = 10000
    mcmc_burn_in: int = 1000
    convergence_threshold: float = 1e-6

    # Active inference settings
    free_energy_precision: float = 1.0
    policy_horizon: int = 5
    exploration_weight: float = 0.1

    # Model transformation settings
    adaptation_rate: float = 0.1
    learning_rate: float = 0.01
    regularization_weight: float = 0.001

    # Visualization settings
    figure_size: tuple[int, int] = (12, 8)
    dpi: int = 100
    style: str = "default"

    # General settings
    debug_mode: bool = False
    log_level: str = "INFO"
    cache_enabled: bool = True
    cache_size: int = 1000

    # Additional configuration
    extra_config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "case_similarity_threshold": self.case_similarity_threshold,
            "max_retrieved_cases": self.max_retrieved_cases,
            "case_weighting_strategy": self.case_weighting_strategy,
            "inference_method": self.inference_method,
            "mcmc_samples": self.mcmc_samples,
            "mcmc_burn_in": self.mcmc_burn_in,
            "convergence_threshold": self.convergence_threshold,
            "free_energy_precision": self.free_energy_precision,
            "policy_horizon": self.policy_horizon,
            "exploration_weight": self.exploration_weight,
            "adaptation_rate": self.adaptation_rate,
            "learning_rate": self.learning_rate,
            "regularization_weight": self.regularization_weight,
            "figure_size": self.figure_size,
            "dpi": self.dpi,
            "style": self.style,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level,
            "cache_enabled": self.cache_enabled,
            "cache_size": self.cache_size,
            "extra_config": self.extra_config,
        }

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "CerebrumConfig":
        """Create config from dictionary."""
        return cls(**config_dict)



