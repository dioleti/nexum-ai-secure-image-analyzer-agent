from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.application.graph.state import DockerfileState


class ParsedDockerfileOutput(BaseModel):
    base_image: str = Field(
        ..., description="A imagem base exata extraída da instrução FROM."
    )
    parsed_steps: list[str] = Field(
        ..., description="Lista contendo todas as instruções/comandos do Dockerfile."
    )


class SecurityAnalysisOutput(BaseModel):
    vulnerabilities: list[str] = Field(
        ...,
        description=(
            "Vulnerabilidades encontradas na imagem base (ex: uso de tags latest,"
            " imagens desatualizadas)."
        ),
    )
    harmful_practices: list[str] = Field(
        ...,
        description=(
            "Passos nocivos ou más práticas (ex: rodar como root, falta de pinning"
            " de versões)."
        ),
    )


class DockerfileAnalysisNodes:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm

    def parse_dockerfile(self, state: DockerfileState) -> dict:
        """Extrai dinamicamente a imagem base e os passos do Dockerfile usando o Gemini."""
        content = state["dockerfile_content"]

        prompt = f"""
    Analise o seguinte Dockerfile linha por linha e extraia:
    1. A imagem base exata (instrução FROM, incluindo tags ou digests se houver).
    2. Uma lista completa com todas as instruções executadas (FROM, RUN, COPY, WORKDIR, CMD, etc.).

    Dockerfile:
    {content}
    """

        structured_llm = self.llm.with_structured_output(ParsedDockerfileOutput)
        result: ParsedDockerfileOutput = structured_llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            "base_image": result.base_image,
            "parsed_steps": result.parsed_steps,
        }

    def analyze_security(self, state: DockerfileState) -> dict:
        """Analisa dinamicamente os riscos e vulnerabilidades com base nos dados extraídos."""
        base_image = state["base_image"]
        steps = state["parsed_steps"]

        prompt = f"""
    Você é um engenheiro sênior de DevSecOps e segurança de containers especializado em Docker. 
    Analise os seguintes elementos extraídos de um Dockerfile:
    - Imagem Base: {base_image}
    - Passos do Dockerfile: {steps}

    Identifique e liste detalhadamente:
    1. **Vulnerabilidades da Imagem Base**: Riscos associados à imagem escolhida (ex: tags 'latest', vulnerabilidades conhecidas em versões genéricas).
    2. **Passos Nocivos / Más Práticas**: Verifique se há comandos rodando como root (falta de USER), ausência de versionamento fixo em pacotes (pip install sem versões), cópias excessivas ou exposição de dados sensíveis.
    """

        structured_llm = self.llm.with_structured_output(SecurityAnalysisOutput)
        result: SecurityAnalysisOutput = structured_llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return {
            "vulnerabilities": result.vulnerabilities,
            "harmful_practices": result.harmful_practices,
        }

    def generate_report(self, state: DockerfileState) -> dict:
        """Gera o relatório final consolidadado em Markdown."""
        vulns = state["vulnerabilities"]
        harms = state["harmful_practices"]
        base = state["base_image"]

        vulns_md = (
            '\n'.join([f'- {v}' for v in vulns])
            if vulns
            else '- Nenhuma vulnerabilidade crítica apontada.'
        )
        harms_md = (
            '\n'.join([f'- {h}' for h in harms])
            if harms
            else '- Nenhuma prática nociva direta identificada.'
        )

        report = f"""
# 🛡️ Relatório de Auditoria de Segurança para Dockerfile

**Imagem Base Analisada:** `{base}`

## 🚨 Vulnerabilidades Encontradas na Imagem Base:
{vulns_md}

## ⚠️ Passos Nocivos / Riscos de Configuração:
{harms_md}

## 🛠️ Recomendações de Correção:
1. **Fixar Versão da Imagem:** Evite tags genéricas ou `latest`; utilize versões específicas e enxutas (ex: `python:3.11-slim`).
2. **Adicionar Usuário Não-Privilegiado:** Nunca execute aplicações como `root`. Crie um usuário dedicado (ex: `RUN useradd -u 1001 appuser` e `USER appuser`).
3. **Fixar Dependências:** Utilize versões exatas nas instalações de pacotes (`pip install flask==3.0.2`).
"""
        return {"report": report}