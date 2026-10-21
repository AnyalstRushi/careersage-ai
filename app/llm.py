"""Optional LLM generation. Supports Gemini and Anthropic via urllib. Falls back silently to extractive mode."""
import os, json, urllib.request

SYSTEM = ("You are CareerSage AI, a career advisor. Answer ONLY from the provided context. "
          "Cite sources inline like [data-analyst:roadmap]. If the context is insufficient, say you don't know. Max 150 words.")

def enabled():
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

def _gemini_answer(question, docs):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None

    ctx = "\n\n".join(f"[{d['id']}]\n{d['body']}" for d in docs)
    prompt = f"{SYSTEM}\n\nContext:\n{ctx}\n\nQuestion: {question}"

    model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={key}"
    )

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 500
        }
    }).encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None
    except Exception:
        return None

def _claude_answer(question, docs):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None

    ctx = "\n\n".join(f"[{d['id']}]\n{d['body']}" for d in docs)
    body = json.dumps({
        "model": os.getenv("LLM_MODEL", "claude-sonnet-5-5"),
        "max_tokens": 500,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {question}"}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        body,
        {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)["content"][0]["text"].strip() or None
    except Exception:
        return None

def generate(question, docs):
    if not enabled():
        return None

    # Prefer Gemini when its key is present; otherwise Claude.
    if os.getenv("GEMINI_API_KEY"):
        answer = _gemini_answer(question, docs)
        if answer:
            return answer

    return _claude_answer(question, docs)