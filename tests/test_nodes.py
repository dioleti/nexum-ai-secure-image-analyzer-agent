from unittest.mock import MagicMock
from src.application.graph.nodes import (
    DockerfileAnalysisNodes,
    ParsedDockerfileOutput,
    SecurityAnalysisOutput,
)
from src.application.graph.state import DockerfileState


def test_parse_dockerfile():
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    expected_output = ParsedDockerfileOutput(
        base_image="python:latest",
        parsed_steps=["FROM python:latest", "RUN pip install fastapi"],
    )
    mock_structured_llm.invoke.return_value = expected_output

    nodes = DockerfileAnalysisNodes(llm=mock_llm)
    state: DockerfileState = {
        "dockerfile_content": "FROM python:latest\nRUN pip install fastapi",
        "base_image": "",
        "parsed_steps": [],
        "vulnerabilities": [],
        "harmful_practices": [],
        "report": "",
    }

    result = nodes.parse_dockerfile(state)

    mock_llm.with_structured_output.assert_called_once_with(ParsedDockerfileOutput)
    mock_structured_llm.invoke.assert_called_once()
    assert result == {
        "base_image": "python:latest",
        "parsed_steps": ["FROM python:latest", "RUN pip install fastapi"],
    }


def test_analyze_security():
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm

    expected_output = SecurityAnalysisOutput(
        vulnerabilities=["Uso da tag 'latest' na imagem base."],
        harmful_practices=["Ausência de instrução USER (execução como root)."],
    )
    mock_structured_llm.invoke.return_value = expected_output

    nodes = DockerfileAnalysisNodes(llm=mock_llm)
    state: DockerfileState = {
        "dockerfile_content": "FROM python:latest\nRUN pip install fastapi",
        "base_image": "python:latest",
        "parsed_steps": ["FROM python:latest", "RUN pip install fastapi"],
        "vulnerabilities": [],
        "harmful_practices": [],
        "report": "",
    }

    result = nodes.analyze_security(state)

    mock_llm.with_structured_output.assert_called_once_with(SecurityAnalysisOutput)
    mock_structured_llm.invoke.assert_called_once()
    assert result == {
        "vulnerabilities": ["Uso da tag 'latest' na imagem base."],
        "harmful_practices": ["Ausência de instrução USER (execução como root)."],
    }


def test_generate_report_with_findings():
    mock_llm = MagicMock()
    nodes = DockerfileAnalysisNodes(llm=mock_llm)

    state: DockerfileState = {
        "dockerfile_content": "FROM ubuntu:latest",
        "base_image": "ubuntu:latest",
        "parsed_steps": ["FROM ubuntu:latest"],
        "vulnerabilities": ["Tag latest instável", "Imagem base pesada"],
        "harmful_practices": ["Rodando como root"],
        "report": "",
    }

    result = nodes.generate_report(state)
    report = result["report"]

    assert "`ubuntu:latest`" in report
    assert "- Tag latest instável" in report
    assert "- Imagem base pesada" in report
    assert "- Rodando como root" in report
    assert "Recomendações de Correção" in report


def test_generate_report_without_findings():
    mock_llm = MagicMock()
    nodes = DockerfileAnalysisNodes(llm=mock_llm)

    state: DockerfileState = {
        "dockerfile_content": "FROM python:3.12-slim\nUSER appuser",
        "base_image": "python:3.12-slim",
        "parsed_steps": ["FROM python:3.12-slim", "USER appuser"],
        "vulnerabilities": [],
        "harmful_practices": [],
        "report": "",
    }

    result = nodes.generate_report(state)
    report = result["report"]

    assert "`python:3.12-slim`" in report
    assert "- Nenhuma vulnerabilidade crítica apontada." in report
    assert "- Nenhuma prática nociva direta identificada." in report
