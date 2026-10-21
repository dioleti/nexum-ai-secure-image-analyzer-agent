from typing import List
from pydantic import BaseModel, Field


class DockerfileInput(BaseModel):
  content: str = Field(..., description="Conteúdo textual do Dockerfile")


class SecurityAuditReport(BaseModel):
  base_image: str = Field(..., description="Imagem base identificada")
  parsed_steps: List[str] = Field(..., description="Passos extraídos")
  vulnerabilities: List[str] = Field(
      ..., description="Vulnerabilidades da imagem base"
  )
  harmful_practices: List[str] = Field(
      ..., description="Práticas nocivas ou inseguras detectadas"
  )
  markdown_report: str = Field(..., description="Relatório final em Markdown")