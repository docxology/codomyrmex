"""Tests for new pipeline components: Builder, Generator, and ArtifactManager."""

import os
from pathlib import Path
import pytest
import yaml
from codomyrmex.ci_cd_automation.pipeline import (
    PipelineBuilder,
    WorkflowGenerator,
    ArtifactManager,
    PipelineStatus,
    JobStatus
)

@pytest.mark.unit
class TestPipelineBuilder:
    def test_build_simple_pipeline(self):
        builder = PipelineBuilder("test-p")
        builder.add_stage("build", ["echo 'building'"])
        pipeline = builder.build()
        
        assert pipeline.name == "test-p"
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].name == "build"
        assert pipeline.stages[0].jobs[0].commands == ["echo 'building'"]

    def test_build_with_dependencies(self):
        builder = PipelineBuilder("deps-p")
        builder.add_stage("build", ["echo 'b'"])
        builder.add_stage("test", ["echo 't'"], dependencies=["build"])
        pipeline = builder.build()
        
        assert len(pipeline.stages) == 2
        assert pipeline.stages[1].dependencies == ["build"]

    def test_on_branch_constraint(self):
        builder = PipelineBuilder("branch-p")
        builder.add_stage("deploy", ["echo 'd'"], on_branch="main")
        pipeline = builder.build()
        
        assert pipeline.variables["STAGE_deploy_BRANCH"] == "main"

@pytest.mark.unit
class TestWorkflowGenerator:
    def test_github_workflow_generation(self):
        builder = PipelineBuilder("gh-p")
        builder.add_stage("build", ["echo 'b'"])
        pipeline = builder.build()
        
        generator = WorkflowGenerator("github")
        workflow = generator.from_pipeline(pipeline)
        wd = workflow.to_dict()
        
        assert wd["name"] == "gh-p"
        assert "build" in wd["jobs"]
        assert wd["jobs"]["build"]["steps"][-1]["run"] == "echo 'b'"

    def test_gitlab_workflow_generation(self):
        builder = PipelineBuilder("gl-p")
        builder.add_stage("build", ["echo 'b'"])
        pipeline = builder.build()
        
        generator = WorkflowGenerator("gitlab")
        workflow = generator.from_pipeline(pipeline)
        wd = workflow.to_dict()
        
        assert "build" in wd
        assert wd["build"]["stage"] == "build"
        assert "echo 'b'" in wd["build"]["script"]

    def test_save_workflow(self, tmp_path):
        builder = PipelineBuilder("save-p")
        builder.add_stage("build", ["echo 'b'"])
        pipeline = builder.build()
        
        generator = WorkflowGenerator("github")
        workflow = generator.from_pipeline(pipeline)
        
        wf_path = tmp_path / "ci.yml"
        workflow.save(str(wf_path))
        
        assert wf_path.exists()
        with open(wf_path) as f:
            data = yaml.safe_load(f)
        assert data["name"] == "save-p"

@pytest.mark.unit
class TestArtifactManager:
    def test_upload_and_download(self, tmp_path):
        storage = tmp_path / "storage"
        am = ArtifactManager(str(storage))
        
        # Create a dummy file
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        dummy_file = work_dir / "app.txt"
        dummy_file.write_text("hello")
        
        # Upload
        am.upload(str(dummy_file), "1.0.0")
        assert (storage / "1.0.0" / "app.txt").exists()
        
        # Download
        target = tmp_path / "target"
        am.download("app.txt", "1.0.0", str(target))
        assert (target / "app.txt").exists()
        assert (target / "app.txt").read_text() == "hello"

    def test_download_missing_raises(self, tmp_path):
        am = ArtifactManager(str(tmp_path / "storage"))
        with pytest.raises(FileNotFoundError):
            am.download("missing.txt", "1.0.0", str(tmp_path / "target"))
