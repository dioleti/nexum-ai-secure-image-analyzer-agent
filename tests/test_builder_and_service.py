from unittest.mock import MagicMock, patch
from src.application.graph.builder import DockerfileGraphBuilder
from src.application.graph.nodes import (
    ParsedDockerfileOutput,
    SecurityAnalysisOutput,
)
from src.application.services.agent_service import DockerSecurityService
from src.config import settings
from src.domain.models import DockerfileInput, SecurityAuditReport


def test_graph_builder_builds_and_executes():
    mock_llm = MagicMock()

    parsed_mock = MagicMock()
    parsed_mock.invoke.return_value = ParsedDockerfileOutput(
        base_image="node:18",
        parsed_steps=["FROM node:18", "COPY . ."],
    )

    security_mock = MagicMock()
    security_mock.invoke.return_value = SecurityAnalysisOutput(
        vulnerabilities=["Vulnerabilidade X"],
        harmful_practices=["Prática Y"],
    )

    def side_effect(schema):
        if schema == ParsedDockerfileOutput:
            return parsed_mock
        return security_mock

    mock_llm.with_structured_output.side_effect = side_effect

    builder = DockerfileGraphBuilder(llm=mock_llm)
    graph = builder.build()

    initial_state = {
        "dockerfile_content": "FROM node:18\nCOPY . .",
        "base_image": "",
        "parsed_steps": [],
        "vulnerabilities": [],
        "harmful_practices": [],
        "report": "",
    }

    final_state = graph.invoke(initial_state)

    assert final_state["base_image"] == "node:18"
    assert final_state["parsed_steps"] == ["FROM node:18", "COPY . ."]
    assert final_state["vulnerabilities"] == ["Vulnerabilidade X"]
    assert final_state["harmful_practices"] == ["Prática Y"]
    assert "`node:18`" in final_state["report"]


@patch("src.application.services.agent_service.ChatGoogleGenerativeAI")
@patch("src.application.services.agent_service.DockerfileGraphBuilder")
def test_docker_security_service_audit_dockerfile_custom_model(
    mock_builder_cls, mock_chat_genai_cls
):
    mock_llm_instance = MagicMock()
    mock_chat_genai_cls.return_value = mock_llm_instance

    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "base_image": "python:3.11-slim",
        "parsed_steps": ["FROM python:3.11-slim", "CMD ['python']"],
        "vulnerabilities": ["Baixo risco"],
        "harmful_practices": ["Sem USER definido"],
        "report": "# Relatório Mock",
    }

    mock_builder_instance = MagicMock()
    mock_builder_instance.build.return_value = mock_agent
    mock_builder_cls.return_value = mock_builder_instance

    service = DockerSecurityService(model_name="gemini-test-model")

    mock_chat_genai_cls.assert_called_once_with(
        model="gemini-test-model", temperature=0
    )
    mock_builder_cls.assert_called_once_with(mock_llm_instance)
    mock_builder_instance.build.assert_called_once()

    input_data = DockerfileInput(content="FROM python:3.11-slim\nCMD ['python']")
    report = service.audit_dockerfile(input_data)

    assert isinstance(report, SecurityAuditReport)
    assert report.base_image == "python:3.11-slim"
    assert report.parsed_steps == ["FROM python:3.11-slim", "CMD ['python']"]
    assert report.vulnerabilities == ["Baixo risco"]
    assert report.harmful_practices == ["Sem USER definido"]
    assert report.markdown_report == "# Relatório Mock"


@patch("src.application.services.agent_service.ChatGoogleGenerativeAI")
@patch("src.application.services.agent_service.DockerfileGraphBuilder")
def test_docker_security_service_default_model_from_settings(
    mock_builder_cls, mock_chat_genai_cls
):
    mock_llm_instance = MagicMock()
    mock_chat_genai_cls.return_value = mock_llm_instance

    service = DockerSecurityService()

    mock_chat_genai_cls.assert_called_once_with(
        model=settings.MODEL_NAME, temperature=0
    )
    assert service.llm == mock_llm_instance
