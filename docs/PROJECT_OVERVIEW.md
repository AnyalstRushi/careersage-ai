# CareerSage AI — Project Overview

CareerSage AI is a lightweight, retrieval-augmented career guidance application. It helps users ask career questions with source references, compare resume skills with role requirements, and discover relevant roles.

## Core capabilities

- **Grounded career Q&A:** retrieves relevant knowledge-base passages and returns source IDs.
- **Resume skill-gap analysis:** compares supplied skills with a target role and identifies missing skills.
- **Role recommendations:** ranks role profiles against the skills found in resume text.
- **Fallback behavior:** supports cited extractive answers when an optional LLM provider is not configured.
- **Optional generation:** supports provider-backed generation as documented in the application configuration.

## Current architecture

1. **Web interface** — lightweight HTML frontend served by the Python application.
2. **HTTP/API layer** — request handling, validation, health reporting, and rate limiting.
3. **Retrieval layer** — token normalization, aliases, typo handling, BM25-style ranking, and intent boosting.
4. **Knowledge base** — curated role information; the current README describes 9 roles and 3 document types (27 documents).
5. **Answer layer** — optional LLM generation with an extractive fallback.
6. **Quality layer** — automated tests and a golden evaluation runner.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web interface |
| GET | `/health` | Application health |
| GET | `/api/roles` | Supported roles |
| POST | `/api/ask` | Career Q&A |
| POST | `/api/gap` | Resume skill-gap analysis |
| POST | `/api/recommend` | Role recommendations |

## Run locally

Use a supported Python version as specified by the repository. From the repository root:

```bash
git clone https://github.com/AnyalstRushi/careersage-ai.git
cd careersage-ai
python -m app.server
```

Then open `http://localhost:8000`.

The core application is designed to run without a third-party API key. Optional LLM credentials should be supplied through environment variables or deployment secrets. Never commit credentials.

## Tests and evaluation

Run the test suite:

```bash
python -m unittest discover -v
```

Run the golden evaluation:

```bash
python eval/run_eval.py
```

The repository's evaluation workflow reports retrieval and grounding signals such as Hit@1, Hit@3, refusal behavior, and citation presence. Treat reported metrics as specific to the checked-in evaluation set, not as a universal quality guarantee.

## Security and operational notes

The current project includes input validation, a request-body size limit, in-memory per-IP rate limiting, a Docker health check, and a non-root container user. For multi-instance deployments, replace in-memory rate limiting with a shared store and review deployment-specific security controls.

## Roadmap

- Expand the golden evaluation set with representative, anonymized user queries.
- Add explicit quality thresholds to CI for retrieval and citation behavior.
- Add structured observability for latency, retrieval scores, and fallback rates.
- Version and govern the curated knowledge base.
- Document threat modeling, privacy boundaries, and incident response.
- Evaluate hybrid lexical/vector retrieval and reranking as optional future improvements.

## Scope

This document describes the implementation and capabilities documented in the repository. It does not claim that optional LLM generation is enabled by default or that the application has been independently audited for production security.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the contribution workflow and [SECURITY.md](../SECURITY.md) for vulnerability reporting.
