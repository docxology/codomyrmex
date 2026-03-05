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
    "ConsistencyIssue",
    "ConsistencyReport",
    "DocumentationConsistencyChecker",
    "DocumentationQualityAnalyzer",
    "ModuleAudit",
    "aggregate_docs",
    "assess_site",
    "audit_documentation",
    "audit_rasp",
    "build_static_site",
    "check_doc_environment",
    "check_documentation_consistency",
    "finalize_docs",
    "generate_pai_md",
    "generate_quality_report",
    "install_dependencies",
    "quality",
    "serve_static_site",
    "start_dev_server",
    "update_pai_docs",
    "update_root_docs",
    "update_spec",
    "validate_doc_versions",
    "write_pai_md",
]
