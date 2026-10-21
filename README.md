# Nexum AI: Secure Image Analyzer Agent 

O **Nexum AI: Secure Image Analyzer Agent** é uma aplicação baseada em **LangGraph** e **Google Gemini (`gemini-3.6-flash`)** estruturada em camadas. 

O agente automatiza a auditoria de segurança de arquivos `Dockerfile`, analisando a imagem base, identificando vulnerabilidades e detectando práticas nocivas (como execução de processos como `root` e uso de tags instáveis como `latest`).

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Release](https://img.shields.io/badge/Release-v1.0.0-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)


---

## 📂 Estrutura do Projeto

```text
docker-security-agent/
├── .env.example
├── pyproject.toml / requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                     # Servidor FastAPI e rotas
│   ├── config.py                   # Configurações do ambiente
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py               # Modelos Pydantic (Entidades)
│   └── application/
│       ├── __init__.py
│       ├── services/
│       │   └── agent_service.py    # Orquestração do LangGraph
│       └── graph/
│           ├── __init__.py
│           ├── state.py            # Estado do LangGraph
│           ├── nodes.py            # Nós do Grafo (Parser, Análise, Relatório)
│           └── builder.py          # Construtor e compilador do Grafo
└── tests/
    └── test_agent.py
```
---

## ⚙️ Pré-requisitos e Configuração
Antes de executar a aplicação, certifique-se de configurar a sua chave de API do Google Gemini.

1. Clone o repositório e acesse a pasta do projeto.
2. Crie e configure o arquivo de ambiente: \
Na raiz do projeto, renomeie o arquivo de exemplo `.env.example` para `.env`:
```bash
cp .env.example .env
```
3. Adicione sua chave de API: \
Abra o arquivo `.env` recém-criado e insira a sua chave da API do Google Gemini:
```
GOOGLE_API_KEY="sua-chave-da-api-do-google-aqui"
```

---

## 🚀 Instalação e Execução
1. Instale as dependências:
```bash
uv pip install .
```
2. Inicie a aplicação FastAPI:
```bash
python -m src.main
```
O servidor será iniciado em: `http://localhost:8000`

---

## 🧪 Testando

Para executar os testes automatizados da aplicação utilizando o `uv`, execute o seguinte comando na raiz do projeto:

```bash
uv run pytest
```

---

## 🔍 Como Utilizar
Via Documentação Interativa (Swagger UI) \
Abra seu navegador e acesse:
👉 `http://localhost:8000/docs`

Lá você encontrará a rota `/audit`, onde poderá fazer o upload direto (`multipart/form-data`) de qualquer arquivo `Dockerfile` para receber o relatório completo de auditoria em JSON/Markdown.

Via `cURL`
Você também pode enviar o arquivo diretamente via linha de comando:
```bash
curl -X 'POST' \
  'http://localhost:8000/audit' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@Dockerfile'
```

---

## 🛠️ Tecnologias Utilizadas
- Python
- FastAPI (API Web moderna e assíncrona)
- LangGraph (Orquestração de agentes de IA baseados em grafos)
- Google Gemini (gemini-3.6-flash) (Motor LLM para análise inteligente de código)
- Pydantic (Validação rigorosa de dados e tipagem)

---
## 📄 Licença
Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

`(C) 2026 - Dioleti(R) - Fabricio Paulo`