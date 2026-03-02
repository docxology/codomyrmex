"""
Documentation management and audit utilities.
"""
from . import quality
from .documentation_website import (
    aggregate_docs,
    assess_site,
    build_static_site,
    check_doc_environment,
    install_dependencies,
    serve_static_site,
    start_dev_server,
    validate_doc_versions,
)
from .maintenance import finalize_docs, update_root_docs, update_spec
from .pai import generate_pai_md, update_pai_docs, write_pai_md
from .quality.audit import ModuleAudit, audit_documentation, audit_rasp
from .quality.consistency_checker import (
    ConsistencyIssue,
    ConsistencyReport,
    DocumentationConsistencyChecker,
    check_documentation_consistency,
)
from .quality.quality_assessment import (
    DocumentationQualityAnalyzer,
    generate_quality_report,
)

__all__ = [
    "quality",
    "ModuleAudit",
    "audit_documentation",
    "audit_rasp",
    "update_root_docs",
    "finalize_docs",
    "update_spec",
    "update_pai_docs",
    "generate_pai_md",
    "write_pai_md",
    "check_doc_environment",
    "install_dependencies",
    "start_dev_server",
    "build_static_site",
    "serve_static_site",
    "aggregate_docs",
    "validate_doc_versions",
    "assess_site",
    "DocumentationQualityAnalyzer",
    "generate_quality_report",
    "DocumentationConsistencyChecker",
    "ConsistencyIssue",
    "ConsistencyReport",
    "check_documentation_consistency",
]
