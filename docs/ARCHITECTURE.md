# CareerSage AI Architecture

CareerSage follows a retrieval-first, citation-grounded architecture.

## Request Flow

1. Client sends a question to `/api/ask`.
2. Server validates input and applies per-IP rate limiting.
3. Query is normalized using aliases and typo correction.
4. Scope guard rejects non-career questions.
5. BM25 retrieval selects relevant documents.
6. Intent boosting prioritizes roadmap, interview, or overview documents.
7. If an LLM key exists, the model answers strictly from retrieved context.
8. If LLM generation fails or is disabled, the system returns an extractive answer.
9. Every response includes source citations.

## Design Principles

- **Grounding first:** the model cannot answer beyond retrieved context.
- **Safe fallback:** missing API keys do not break the product.
- **Explainability:** every answer is traceable to source documents.
- **Operational readiness:** validation, rate limits, health checks, Docker, and CI are included.
- **Zero-dependency core:** the base API uses only Python's standard library.

## Future Retrieval Upgrade

The current BM25 engine can be upgraded to hybrid retrieval:

```text
Query -> BM25 + Dense Vector Search
      -> Reciprocal Rank Fusion
      -> Cross-Encoder Reranking
      -> Top-K Context
```

This improves semantic matching while retaining exact keyword precision.
