from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from src.application.services.agent_service import DockerSecurityService
from src.config import settings
from src.domain.models import DockerfileInput, SecurityAuditReport

security_service: DockerSecurityService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
  global security_service

  if not settings.GOOGLE_API_KEY:
    print(
        "⚠️ ATENÇÃO: A variável de ambiente GOOGLE_API_KEY não foi encontrada!"
    )
    raise RuntimeError("GOOGLE_API_KEY not found")
  else:
    print("🚀 Chave da API do Google detectada com sucesso.")

  print(
      "🔄 Inicializando o DockerSecurityService com o modelo"
      f" {settings.MODEL_NAME}..."
  )
  security_service = DockerSecurityService()
  print("✅ API de Auditoria de Dockerfiles pronta para receber requisições!")

  yield

  print("🛑 Encerrando a aplicação e liberando recursos...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API baseada em LangGraph e Gemini para auditoria de segurança de"
        " Dockerfiles via upload de arquivo."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
)


@app.post(
    "/audit",
    response_model=SecurityAuditReport,
    status_code=status.HTTP_200_OK,
    summary="Auditar Dockerfile por Arquivo",
    description=(
        "Recebe um arquivo Dockerfile via upload (multipart/form-data), lê o"
        " stream e executa a auditoria de segurança."
    ),
)
async def audit_dockerfile_endpoint(file: UploadFile = File(...)):
  try:
    content_bytes = await file.read()
    dockerfile_content = content_bytes.decode("utf-8")

    if not dockerfile_content.strip():
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="O arquivo enviado está vazio.",
      )

    input_data = DockerfileInput(content=dockerfile_content)
    report = security_service.audit_dockerfile(input_data)
    return report

  except UnicodeDecodeError:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "O arquivo enviado não é um texto válido codificado em UTF-8."
        ),
    )
  except HTTPException as he:
    raise he
  except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=(
            "Erro interno ao processar a auditoria do Dockerfile:"
            f" {str(e)}"
        ),
    )


@app.get("/health", status_code=status.HTTP_200_OK, summary="Health Check")
async def health_check():
  return {"status": "healthy", "service": "docker-security-agent"}


if __name__ == "__main__":
  import uvicorn

  load_dotenv()
  uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)