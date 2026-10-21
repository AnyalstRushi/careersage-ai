# CareerSage AI

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="Tests" src="https://img.shields.io/badge/Tests-automated-brightgreen">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-blue">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white">
  <img alt="RAG" src="https://img.shields.io/badge/RAG-grounded%20answers-8A2BE2">
</p>

**CareerSage AI** is a zero-dependency, production-ready RAG career intelligence API that answers career questions using a curated knowledge base, provides explainable citations, performs resume skill-gap analysis, and refuses out-of-scope questions instead of hallucinating.

Unlike a normal chatbot, every answer is grounded in retrieved documents and includes source citations such as `[data-analyst:roadmap]`.

## Why This Project Matters

Most AI career tools generate confident but unverifiable answers. CareerSage uses a retrieval-first design:

1. Normalizes the user query, including aliases and common typos.
2. Applies a scope guard so unrelated questions are refused.
3. Retrieves the most relevant documents using BM25 and intent boosting.
4. Generates an answer only from retrieved context.
5. Returns inline citations and falls back safely to extractive mode when no LLM key is configured.

## Features

- Grounded career Q&A with inline document citations
- Resume skill-gap analysis for target roles
- Role recommendation engine based on resume skills
- Out-of-scope refusal to reduce hallucination risk
- Query normalization for aliases such as `ML -> machine learning` and `k8s -> kubernetes`
- Typo tolerance using `difflib`
- Rate limiting per client IP
- Optional LLM mode using Gemini or Anthropic Claude
- Zero third-party runtime dependencies for the core API
- Docker-ready and deployable to Render, Railway, Fly.io, or Cloud Run
- Automated tests and golden-set evaluation

## Architecture

```text
User Question
     |
     v
Input Validation + Rate Limiting
     |
     v
Query Normalization
  - Alias expansion
  - Typo correction
     |
     v
Scope Guard
  - Career/role/skill intent required
     |
     v
BM25 Retrieval + Intent Boosting
     |
     v
Top-K Context Selection
     |
     +---------------------------+
     |                           |
     v                           v
Optional LLM Generation     Extractive Fallback
(Gemini / Claude)           Always cited
     |                           |
     +---------------------------+
     |
     v
Cited Answer + Sources
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `GET` | `/health` | Health, document count, and LLM status |
| `GET` | `/api/roles` | Supported career roles and skills |
| `POST` | `/api/ask` | Ask a career question |
| `POST` | `/api/gap` | Analyze resume against a target role |
| `POST` | `/api/recommend` | Recommend suitable roles from resume text |

## Quick Start

### 1. Clone

```bash
git clone https://github.com/AnyalstRushi/careersage-ai.git
cd careersage-ai
```

### 2. Run Without Installation

The core project uses only the Python standard library.

```bash
python -m app.server
```

Open:

```text
http://localhost:8000
```

### 3. Enable LLM Answers

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.5-flash
RATE_LIMIT=60
PORT=8000
```

Then run:

```bash
python -m app.server
```

The health endpoint should return:

```json
{"status":"ok","docs":27,"llm":true}
```

Never commit `.env` or expose API keys in source code.

## Example Requests

### Ask a Career Question

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What skills are required for a data analyst role?"}'
```

### Resume Skill Gap

```bash
curl -X POST http://localhost:8000/api/gap \
  -H "Content-Type: application/json" \
  -d '{"resume":"Python SQL Excel Power BI dashboards","role":"data-analyst"}'
```

### Role Recommendation

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"resume":"Python SQL Azure ETL data pipelines"}'
```

## Testing

Run all unit and API tests:

```bash
python -m unittest discover -v
```

Run golden-set evaluation:

```bash
python eval/run_eval.py
```

The evaluation suite measures retrieval quality, citation coverage, and out-of-scope refusal behavior.

## Deployment

### Docker

```bash
docker build -t careersage-ai .
docker run -p 8000:8000 --env-file .env careersage-ai
```

### Render

1. Push this repository to GitHub.
2. Create a new Render Blueprint deployment.
3. Set `GEMINI_API_KEY` as an environment variable.
4. Deploy.

The included `render.yaml` supports one-click infrastructure configuration.

## Security

- API keys are read from environment variables.
- `.env` is excluded through `.gitignore`.
- Request bodies are capped at 100 KB.
- Inputs are validated before processing.
- Per-IP rate limiting protects the API.
- Docker image runs as a non-root user.
- No secrets are baked into the container image.

## Project Structure

```text
careersage-ai/
├── app/
│   ├── server.py
│   ├── rag.py
│   ├── llm.py
│   ├── data.py
│   └── static/
│       └── index.html
├── tests/
│   ├── test_api.py
│   └── test_engine.py
├── eval/
│   ├── run_eval.py
│   └── golden.json
├── docs/
│   └── ARCHITECTURE.md
├── .github/workflows/
│   └── ci.yml
├── Dockerfile
├── render.yaml
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Roadmap

- Dense embeddings with Qdrant or pgvector
- Hybrid BM25 + vector retrieval
- Cross-encoder reranking
- Live job-posting ingestion
- User accounts and conversation memory
- Resume PDF parsing
- RAGAS faithfulness evaluation in CI
- Marathi and Hindi query support

## License

MIT License. See [LICENSE](LICENSE).
