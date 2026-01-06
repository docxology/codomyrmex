"""
Theory Submodule for Codomyrmex Security Module.

The Theory submodule provides generic security considerations, principles,
frameworks, threat modeling methodologies, risk assessment methods, security architecture
patterns, and security best practices.
"""

try:
    from .principles import (
        SecurityPrinciple,
        PrincipleCategory,
        get_security_principles,
        get_principle,
        get_principles_by_category,
        apply_principle,
        validate_principle_application,
    )
    PRINCIPLES_AVAILABLE = True
except ImportError:
    SecurityPrinciple = None
    PrincipleCategory = None
    get_security_principles = None
    get_principle = None
    get_principles_by_category = None
    apply_principle = None
    validate_principle_application = None
    PRINCIPLES_AVAILABLE = False

try:
    from .frameworks import (
        SecurityFramework,
        FrameworkStandard,
        FrameworkCategory,
        get_framework,
        get_all_frameworks,
        get_frameworks_by_category,
        apply_framework,
        check_framework_compliance,
    )
    FRAMEWORKS_AVAILABLE = True
except ImportError:
    SecurityFramework = None
    FrameworkStandard = None
    FrameworkCategory = None
    get_framework = None
    get_all_frameworks = None
    get_frameworks_by_category = None
    apply_framework = None
    check_framework_compliance = None
    FRAMEWORKS_AVAILABLE = False

try:
    from .threat_modeling import (
        Threat,
        ThreatModel,
        ThreatSeverity,
        ThreatCategory,
        ThreatModelBuilder,
        create_threat_model,
        analyze_threats,
        prioritize_threats,
    )
    THREAT_MODELING_AVAILABLE = True
except ImportError:
    Threat = None
    ThreatModel = None
    ThreatSeverity = None
    ThreatCategory = None
    ThreatModelBuilder = None
    create_threat_model = None
    analyze_threats = None
    prioritize_threats = None
    THREAT_MODELING_AVAILABLE = False

try:
    from .risk_assessment import (
        Risk,
        RiskAssessment,
        RiskLevel,
        LikelihoodLevel,
        ImpactLevel,
        RiskAssessor,
        assess_risk,
        calculate_risk_score,
        prioritize_risks,
        calculate_aggregate_risk,
    )
    RISK_ASSESSMENT_AVAILABLE = True
except ImportError:
    Risk = None
    RiskAssessment = None
    RiskLevel = None
    LikelihoodLevel = None
    ImpactLevel = None
    RiskAssessor = None
    assess_risk = None
    calculate_risk_score = None
    prioritize_risks = None
    calculate_aggregate_risk = None
    RISK_ASSESSMENT_AVAILABLE = False

try:
    from .architecture_patterns import (
        SecurityPattern,
        PatternCategory,
        get_security_patterns,
        get_pattern,
        get_patterns_by_category,
        apply_pattern,
        validate_pattern_application,
    )
    ARCHITECTURE_PATTERNS_AVAILABLE = True
except ImportError:
    SecurityPattern = None
    PatternCategory = None
    get_security_patterns = None
    get_pattern = None
    get_patterns_by_category = None
    apply_pattern = None
    validate_pattern_application = None
    ARCHITECTURE_PATTERNS_AVAILABLE = False

try:
    from .best_practices import (
        SecurityBestPractice,
        PracticeCategory,
        PracticePriority,
        get_best_practices,
        get_practice,
        get_practices_by_priority,
        get_practices_for_category,
        check_compliance_with_practices,
        prioritize_practices,
    )
    BEST_PRACTICES_AVAILABLE = True
except ImportError:
    SecurityBestPractice = None
    PracticeCategory = None
    PracticePriority = None
    get_best_practices = None
    get_practice = None
    get_practices_by_priority = None
    get_practices_for_category = None
    check_compliance_with_practices = None
    prioritize_practices = None
    BEST_PRACTICES_AVAILABLE = False

__all__ = []

if PRINCIPLES_AVAILABLE:
    __all__.extend([
        "SecurityPrinciple",
        "PrincipleCategory",
        "get_security_principles",
        "get_principle",
        "get_principles_by_category",
        "apply_principle",
        "validate_principle_application",
    ])

if FRAMEWORKS_AVAILABLE:
    __all__.extend([
        "SecurityFramework",
        "FrameworkStandard",
        "FrameworkCategory",
        "get_framework",
        "get_all_frameworks",
        "get_frameworks_by_category",
        "apply_framework",
        "check_framework_compliance",
    ])

if THREAT_MODELING_AVAILABLE:
    __all__.extend([
        "Threat",
        "ThreatModel",
        "ThreatSeverity",
        "ThreatCategory",
        "ThreatModelBuilder",
        "create_threat_model",
        "analyze_threats",
        "prioritize_threats",
    ])

if RISK_ASSESSMENT_AVAILABLE:
    __all__.extend([
        "Risk",
        "RiskAssessment",
        "RiskLevel",
        "LikelihoodLevel",
        "ImpactLevel",
        "RiskAssessor",
        "assess_risk",
        "calculate_risk_score",
        "prioritize_risks",
        "calculate_aggregate_risk",
    ])

if ARCHITECTURE_PATTERNS_AVAILABLE:
    __all__.extend([
        "SecurityPattern",
        "PatternCategory",
        "get_security_patterns",
        "get_pattern",
        "get_patterns_by_category",
        "apply_pattern",
        "validate_pattern_application",
    ])

if BEST_PRACTICES_AVAILABLE:
    __all__.extend([
        "SecurityBestPractice",
        "PracticeCategory",
        "PracticePriority",
        "get_best_practices",
        "get_practice",
        "get_practices_by_priority",
        "get_practices_for_category",
        "check_compliance_with_practices",
        "prioritize_practices",
    ])
