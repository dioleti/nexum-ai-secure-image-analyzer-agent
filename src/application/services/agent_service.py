from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings
from src.application.graph.builder import DockerfileGraphBuilder
from src.domain.models import DockerfileInput, SecurityAuditReport


class DockerSecurityService:

    def __init__(self, model_name: str | None = None):
        model = model_name or settings.MODEL_NAME
        self.llm = ChatGoogleGenerativeAI(model=model, temperature=0)
        self.agent = DockerfileGraphBuilder(self.llm).build()

    def audit_dockerfile(self, input_data: DockerfileInput) -> SecurityAuditReport:
        initial_state = {
            "dockerfile_content": input_data.content,
            "base_image": "",
            "parsed_steps": [],
            "vulnerabilities": [],
            "harmful_practices": [],
            "report": "",
        }

        result = self.agent.invoke(initial_state)

        return SecurityAuditReport(
            base_image=result["base_image"],
            parsed_steps=result["parsed_steps"],
            vulnerabilities=result["vulnerabilities"],
            harmful_practices=result["harmful_practices"],
            markdown_report=result["report"],
        )