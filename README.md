# CareerSage AI - RAG-Powered Career & Skill Intelligence Agent

Grounded career guidance: ask about any role's **skills, roadmap, interview questions**, run a **resume skill-gap analysis**, and get **role recommendations**. Every answer is retrieved from a curated knowledge base and **cited**; out-of-scope questions are **refused** instead of hallucinated.

## Architecture
```
Question -> normalize (aliases: ML->machine learning, k8s->kubernetes) -> typo-fix (difflib)
         -> scope guard (must mention a role/skill term, else refuse)
         -> BM25 retrieval over 27 docs (9 roles x overview/roadmap/interview) + intent boost
         -> [optional] LLM (Claude API) answers ONLY from top-3 context, with [doc-id] citations
         -> fallback: extractive answer from top doc (always cited)
Resume  -> alias-normalized phrase matching -> skill-gap score, missing skills, roadmap, sources
```
Zero third-party dependencies (Python stdlib). UI: `app/static/index.html`, API: `app/server.py`.

## Run (2 min)
```bash
python -m app.server            # http://localhost:8000
```
Optional LLM mode: `export ANTHROPIC_API_KEY=...` (model via `LLM_MODEL`). Without a key it runs in extractive mode.

## Test
```bash
python -m unittest discover -v  # 23 tests: engine, API, validation, rate limit
python eval/run_eval.py         # golden-set evaluation, exits 1 on regression
```
**Current results** (35 golden questions: 28 answerable, 7 out-of-scope, incl. typos and aliases):
hit@1 100% | hit@3 100% | out-of-scope refusal 100% | citation rate 100%.
These are measured on the included golden set; extend `eval/golden.json` with your own questions - real-world accuracy will be lower on unseen phrasing. That is why the eval gate exists.

## API
| Method | Path | Body |
|---|---|---|
| GET | `/health`, `/api/roles` | - |
| POST | `/api/ask` | `{"question": "..."}` (3-500 chars) |
| POST | `/api/gap` | `{"resume": "...", "role": "data-analyst"}` |
| POST | `/api/recommend` | `{"resume": "..."}` |

Security: 100 KB body cap, input validation, per-IP rate limit (`RATE_LIMIT`/min), non-root Docker user, no secrets in image.

## Deploy
**Render (free):** push to GitHub -> New > Blueprint (uses `render.yaml`) -> optionally set `ANTHROPIC_API_KEY` -> deploy. Public URL appears in ~3 min; health check is `/health`.
**Docker:** `docker build -t careersage . && docker run -p 8000:8000 careersage`
**Railway / Fly.io / Cloud Run:** point at the Dockerfile; it honours `$PORT`.

## Roadmap (production upgrades)
Dense embeddings + Qdrant/pgvector hybrid search, cross-encoder reranker, live job-posting ingestion, user accounts + memory, Langfuse tracing, RAGAS faithfulness scoring in CI, Marathi/Hindi query support.
