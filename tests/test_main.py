from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
import src.main as main_module
from src.config import settings
from src.domain.models import SecurityAuditReport


def test_lifespan_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "")
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY not found"):
        with TestClient(main_module.app):
            pass


@patch("src.main.DockerSecurityService")
def test_lifespan_with_api_key(mock_service_cls, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "fake-api-key")
    mock_instance = MagicMock()
    mock_service_cls.return_value = mock_instance

    with TestClient(main_module.app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "service": "docker-security-agent",
        }
        mock_service_cls.assert_called_once_with()


def test_audit_endpoint_success(monkeypatch):
    mock_service = MagicMock()
    expected_report = SecurityAuditReport(
        base_image="alpine:latest",
        parsed_steps=["FROM alpine:latest", "RUN apk update"],
        vulnerabilities=["Tag latest"],
        harmful_practices=["Execução como root"],
        markdown_report="# Relatório",
    )
    mock_service.audit_dockerfile.return_value = expected_report
    monkeypatch.setattr(main_module, "security_service", mock_service)

    client = TestClient(main_module.app)
    files = {"file": ("Dockerfile", b"FROM alpine:latest\nRUN apk update", "text/plain")}
    response = client.post("/audit", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["base_image"] == "alpine:latest"
    assert data["vulnerabilities"] == ["Tag latest"]
    mock_service.audit_dockerfile.assert_called_once()


def test_audit_endpoint_empty_file():
    client = TestClient(main_module.app)
    files = {"file": ("Dockerfile", b"   \n  ", "text/plain")}
    response = client.post("/audit", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "O arquivo enviado está vazio."


def test_audit_endpoint_invalid_utf8():
    client = TestClient(main_module.app)
    files = {"file": ("Dockerfile", b"\xff\xfe\x00\x00invalid", "application/octet-stream")}
    response = client.post("/audit", files=files)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "O arquivo enviado não é um texto válido codificado em UTF-8."
    )


def test_audit_endpoint_internal_error(monkeypatch):
    mock_service = MagicMock()
    mock_service.audit_dockerfile.side_effect = ValueError("Falha na conexão com LLM")
    monkeypatch.setattr(main_module, "security_service", mock_service)

    client = TestClient(main_module.app)
    files = {"file": ("Dockerfile", b"FROM ubuntu:22.04", "text/plain")}
    response = client.post("/audit", files=files)

    assert response.status_code == 500
    assert "Erro interno ao processar a auditoria do Dockerfile: Falha na conexão com LLM" in response.json()["detail"]
