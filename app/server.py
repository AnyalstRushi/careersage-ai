"""HTTP API + UI. Zero dependencies. Run: python -m app.server"""
import json, os, time, threading
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .rag import ENGINE
from .data import ROLES
from . import llm

MAX_BODY = 100_000
INDEX = (Path(__file__).parent / "static" / "index.html").read_bytes()

class RateLimiter:
    def __init__(self, limit, window): self.limit, self.window, self.h, self.lock = limit, window, defaultdict(deque), threading.Lock()
    def allow(self, key):
        now = time.time()
        with self.lock:
            q = self.h[key]
            while q and now - q[0] > self.window: q.popleft()
            if len(q) >= self.limit: return False
            q.append(now); return True

LIMITER = RateLimiter(int(os.getenv("RATE_LIMIT", "60")), 60)

class Handler(BaseHTTPRequestHandler):
    server_version = "CareerSage/1.0"
    def log_message(self, *a): pass
    def _send(self, code, obj, ctype="application/json"):
        data = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code)
        for k, v in {"Content-Type": ctype + "; charset=utf-8", "Content-Length": str(len(data)), "X-Content-Type-Options": "nosniff",
                     "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type", "Cache-Control": "no-store"}.items():
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(data)
    def _ip(self): return (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
    def do_OPTIONS(self): self._send(204, b"")
    def do_GET(self):
        if self.path in ("/", "/index.html"): return self._send(200, INDEX, "text/html")
        if self.path == "/health": return self._send(200, {"status": "ok", "docs": len(ENGINE.docs), "llm": llm.enabled()})
        if self.path == "/api/roles": return self._send(200, [dict(id=k, title=v["title"], skills=v["skills"]) for k, v in ROLES.items()])
        self._send(404, {"error": "not found"})
    def do_POST(self):
        if not LIMITER.allow(self._ip()): return self._send(429, {"error": "rate limit exceeded"})
        try: n = int(self.headers.get("Content-Length", 0))
        except ValueError: return self._send(400, {"error": "bad Content-Length"})
        if n > MAX_BODY: return self._send(413, {"error": "payload too large"})
        try:
            b = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(b, dict): raise ValueError
        except ValueError: return self._send(400, {"error": "invalid JSON object"})
        s = lambda k: b.get(k) if isinstance(b.get(k), str) else ""
        if self.path == "/api/ask":
            q = s("question").strip()
            if not 3 <= len(q) <= 500: return self._send(400, {"error": "question must be 3-500 characters"})
            return self._send(200, ENGINE.ask(q))
        if self.path in ("/api/gap", "/api/recommend"):
            r = s("resume").strip()
            if len(r) < 10: return self._send(400, {"error": "resume text too short"})
            if self.path == "/api/recommend": return self._send(200, {"roles": ENGINE.recommend(r)})
            if s("role") not in ROLES: return self._send(404, {"error": "unknown role", "valid": list(ROLES)})
            return self._send(200, ENGINE.gap(r, s("role")))
        self._send(404, {"error": "not found"})

def make_server(port=0, host="127.0.0.1"): return ThreadingHTTPServer((host, port), Handler)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"CareerSage AI on :{port}  (LLM {'on' if llm.enabled() else 'off - extractive mode'})")
    make_server(port, "0.0.0.0").serve_forever()
