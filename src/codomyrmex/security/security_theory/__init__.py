"""
Security Theory Submodule for Codomyrmex Security Module.

The Security Theory submodule provides generic security considerations, principles,
frameworks, threat modeling methodologies, risk assessment methods, security architecture
patterns, and security best practices.
"""

try:
    from .principles import (
        SecurityPrinciple,
        get_security_principles,
        apply_principle,
    )
    PRINCIPLES_AVAILABLE = True
except ImportError:
    SecurityPrinciple = None
    get_security_principles = None
    apply_principle = None
    PRINCIPLES_AVAILABLE = False

try:
    from .frameworks import (
        SecurityFramework,
        get_framework,
        apply_framework,
    )
    FRAMEWORKS_AVAILABLE = True
except ImportError:
    SecurityFramework = None
    get_framework = None
    apply_framework = None
    FRAMEWORKS_AVAILABLE = False

try:
    from .threat_modeling import (
        ThreatModel,
        create_threat_model,
        analyze_threats,
    )
    THREAT_MODELING_AVAILABLE = True
except ImportError:
    ThreatModel = None
    create_threat_model = None
    analyze_threats = None
    THREAT_MODELING_AVAILABLE = False

try:
    from .risk_assessment import (
        RiskAssessment,
        assess_risk,
        calculate_risk_score,
    )
    RISK_ASSESSMENT_AVAILABLE = True
except ImportError:
    RiskAssessment = None
    assess_risk = None
    calculate_risk_score = None
    RISK_ASSESSMENT_AVAILABLE = False

try:
    from .architecture_patterns import (
        SecurityPattern,
        get_security_patterns,
        apply_pattern,
    )
    ARCHITECTURE_PATTERNS_AVAILABLE = True
except ImportError:
    SecurityPattern = None
    get_security_patterns = None
    apply_pattern = None
    ARCHITECTURE_PATTERNS_AVAILABLE = False

try:
    from .best_practices import (
        SecurityBestPractice,
        get_best_practices,
        check_compliance_with_practices,
    )
    BEST_PRACTICES_AVAILABLE = True
except ImportError:
    SecurityBestPractice = None
    get_best_practices = None
    check_compliance_with_practices = None
    BEST_PRACTICES_AVAILABLE = False

__all__ = []

if PRINCIPLES_AVAILABLE:
    __all__.extend([
        "SecurityPrinciple",
        "get_security_principles",
        "apply_principle",
    ])

if FRAMEWORKS_AVAILABLE:
    __all__.extend([
        "SecurityFramework",
        "get_framework",
        "apply_framework",
    ])

if THREAT_MODELING_AVAILABLE:
    __all__.extend([
        "ThreatModel",
        "create_threat_model",
        "analyze_threats",
    ])

if RISK_ASSESSMENT_AVAILABLE:
    __all__.extend([
        "RiskAssessment",
        "assess_risk",
        "calculate_risk_score",
    ])

if ARCHITECTURE_PATTERNS_AVAILABLE:
    __all__.extend([
        "SecurityPattern",
        "get_security_patterns",
        "apply_pattern",
    ])

if BEST_PRACTICES_AVAILABLE:
    __all__.extend([
        "SecurityBestPractice",
        "get_best_practices",
        "check_compliance_with_practices",
    ])



