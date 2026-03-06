"""
Cognitive Security Submodule for Codomyrmex Security Module.

The Cognitive Security submodule provides cognitive security practices, social engineering
defense, phishing detection and analysis, security awareness training, cognitive threat
assessment, and human factor security analysis.
"""

try:
    from .social_engineering_detector import (
        SocialEngineeringDetector,
        analyze_communication,
        detect_social_engineering,
    )

    SOCIAL_ENGINEERING_AVAILABLE = True
except ImportError:
    SOCIAL_ENGINEERING_AVAILABLE = False

try:
    from .phishing_analyzer import (
        PhishingAnalyzer,
        analyze_email,
        detect_phishing_attempt,
    )

    PHISHING_ANALYSIS_AVAILABLE = True
except ImportError:
    PHISHING_ANALYSIS_AVAILABLE = False

try:
    from .awareness_training import (
        AwarenessTrainer,
        assess_training_effectiveness,
        create_training_module,
    )

    AWARENESS_TRAINING_AVAILABLE = True
except ImportError:
    AWARENESS_TRAINING_AVAILABLE = False

try:
    from .cognitive_threat_assessment import (
        CognitiveThreatAssessor,
        assess_cognitive_threats,
        evaluate_human_factors,
    )

    COGNITIVE_THREAT_AVAILABLE = True
except ImportError:
    COGNITIVE_THREAT_AVAILABLE = False

try:
    from .behavior_analysis import (
        BehaviorAnalyzer,
        analyze_user_behavior,
        detect_anomalous_behavior,
    )

    BEHAVIOR_ANALYSIS_AVAILABLE = True
except ImportError:
    BEHAVIOR_ANALYSIS_AVAILABLE = False

__all__ = []

if SOCIAL_ENGINEERING_AVAILABLE:
    __all__.extend(
        [
            "SocialEngineeringDetector",
            "analyze_communication",
            "detect_social_engineering",
        ]
    )

if PHISHING_ANALYSIS_AVAILABLE:
    __all__.extend(
        [
            "PhishingAnalyzer",
            "analyze_email",
            "detect_phishing_attempt",
        ]
    )

if AWARENESS_TRAINING_AVAILABLE:
    __all__.extend(
        [
            "AwarenessTrainer",
            "assess_training_effectiveness",
            "create_training_module",
        ]
    )

if COGNITIVE_THREAT_AVAILABLE:
    __all__.extend(
        [
            "CognitiveThreatAssessor",
            "assess_cognitive_threats",
            "evaluate_human_factors",
        ]
    )

if BEHAVIOR_ANALYSIS_AVAILABLE:
    __all__.extend(
        [
            "BehaviorAnalyzer",
            "analyze_user_behavior",
            "detect_anomalous_behavior",
        ]
    )
