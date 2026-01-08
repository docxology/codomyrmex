"""
Cognitive Security Submodule for Codomyrmex Security Module.

The Cognitive Security submodule provides cognitive security practices, social engineering
defense, phishing detection and analysis, security awareness training, cognitive threat
assessment, and human factor security analysis.
"""

try:
    from .social_engineering_detector import (
        SocialEngineeringDetector,
        detect_social_engineering,
        analyze_communication,
    )
    SOCIAL_ENGINEERING_AVAILABLE = True
except ImportError:
    SocialEngineeringDetector = None
    detect_social_engineering = None
    analyze_communication = None
    SOCIAL_ENGINEERING_AVAILABLE = False

try:
    from .phishing_analyzer import (
        PhishingAnalyzer,
        analyze_email,
        detect_phishing_attempt,
    )
    PHISHING_ANALYSIS_AVAILABLE = True
except ImportError:
    PhishingAnalyzer = None
    analyze_email = None
    detect_phishing_attempt = None
    PHISHING_ANALYSIS_AVAILABLE = False

try:
    from .awareness_training import (
        AwarenessTrainer,
        create_training_module,
        assess_training_effectiveness,
    )
    AWARENESS_TRAINING_AVAILABLE = True
except ImportError:
    AwarenessTrainer = None
    create_training_module = None
    assess_training_effectiveness = None
    AWARENESS_TRAINING_AVAILABLE = False

try:
    from .cognitive_threat_assessment import (
        CognitiveThreatAssessor,
        assess_cognitive_threats,
        evaluate_human_factors,
    )
    COGNITIVE_THREAT_AVAILABLE = True
except ImportError:
    CognitiveThreatAssessor = None
    assess_cognitive_threats = None
    evaluate_human_factors = None
    COGNITIVE_THREAT_AVAILABLE = False

try:
    from .behavior_analysis import (
        BehaviorAnalyzer,
        analyze_user_behavior,
        detect_anomalous_behavior,
    )
    BEHAVIOR_ANALYSIS_AVAILABLE = True
except ImportError:
    BehaviorAnalyzer = None
    analyze_user_behavior = None
    detect_anomalous_behavior = None
    BEHAVIOR_ANALYSIS_AVAILABLE = False

__all__ = []

if SOCIAL_ENGINEERING_AVAILABLE:
    __all__.extend([
        "SocialEngineeringDetector",
        "detect_social_engineering",
        "analyze_communication",
    ])

if PHISHING_ANALYSIS_AVAILABLE:
    __all__.extend([
        "PhishingAnalyzer",
        "analyze_email",
        "detect_phishing_attempt",
    ])

if AWARENESS_TRAINING_AVAILABLE:
    __all__.extend([
        "AwarenessTrainer",
        "create_training_module",
        "assess_training_effectiveness",
    ])

if COGNITIVE_THREAT_AVAILABLE:
    __all__.extend([
        "CognitiveThreatAssessor",
        "assess_cognitive_threats",
        "evaluate_human_factors",
    ])

if BEHAVIOR_ANALYSIS_AVAILABLE:
    __all__.extend([
        "BehaviorAnalyzer",
        "analyze_user_behavior",
        "detect_anomalous_behavior",
    ])



