import pytest
from pydantic import ValidationError
from src.application.graph.state import DockerfileState
from src.domain.models import DockerfileInput, SecurityAuditReport


def test_dockerfile_input_valid():
    data = DockerfileInput(content="FROM python:3.12\nCMD ['python']")
    assert data.content == "FROM python:3.12\nCMD ['python']"


def test_dockerfile_input_missing_content():
    with pytest.raises(ValidationError):
        DockerfileInput()


def test_security_audit_report_valid():
    report = SecurityAuditReport(
        base_image="python:3.12",
        parsed_steps=["FROM python:3.12", "RUN pip install flask"],
        vulnerabilities=["None"],
        harmful_practices=["Running as root"],
        markdown_report="# Report",
    )
    assert report.base_image == "python:3.12"
    assert len(report.parsed_steps) == 2
    assert report.vulnerabilities == ["None"]
    assert report.harmful_practices == ["Running as root"]
    assert report.markdown_report == "# Report"


def test_security_audit_report_missing_fields():
    with pytest.raises(ValidationError):
        SecurityAuditReport(base_image="python:3.12")


def test_dockerfile_state_structure():
    state: DockerfileState = {
        "dockerfile_content": "FROM alpine",
        "base_image": "alpine",
        "parsed_steps": ["FROM alpine"],
        "vulnerabilities": [],
        "harmful_practices": [],
        "report": "",
    }
    assert state["base_image"] == "alpine"
