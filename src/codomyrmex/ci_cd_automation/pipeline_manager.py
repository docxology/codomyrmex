# DEPRECATED(v0.2.0): Shim module. Import from ci_cd_automation.pipeline instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: ci_cd_automation.pipeline"""
from .pipeline import *  # noqa: F401,F403
from .pipeline import (
    AsyncPipelineManager,
    AsyncPipelineResult,
    JobStatus,
    Pipeline,
    PipelineJob,
    PipelineManager,
    PipelineStage,
    PipelineStatus,
    StageStatus,
    async_get_pipeline_status,
    async_trigger_pipeline,
    async_wait_for_completion,
    create_pipeline,
    run_pipeline,
)
