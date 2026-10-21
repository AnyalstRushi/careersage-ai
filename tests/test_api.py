import json, threading, unittest, urllib.request, urllib.error
from app.server import make_server, RateLimiter
def call(base, path, body=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(base + path, data, {"Content-Type": "application/json"} if data is not None else {})
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
class T(unittest.TestCase):
    @classmethod
    def setUpClass(c):
        c.srv = make_server(0); c.base = f"http://127.0.0.1:{c.srv.server_address[1]}"
        threading.Thread(target=c.srv.serve_forever, daemon=True).start()
    @classmethod
    def tearDownClass(c): c.srv.shutdown()
    def j(self, *a, **k): s, b = call(self.base, *a, **k); return s, json.loads(b)
    def test_health(self): s, j = self.j("/health"); self.assertEqual((s, j["status"]), (200, "ok"))
    def test_ui(self): s, b = call(self.base, "/"); self.assertEqual(s, 200); self.assertIn(b"CareerSage", b)
    def test_roles(self): s, j = self.j("/api/roles"); self.assertEqual((s, len(j)), (200, 9))
    def test_ask(self):
        s, j = self.j("/api/ask", {"question": "Interview questions for AI engineer"}); self.assertEqual(s, 200)
        self.assertEqual(j["sources"][0]["id"], "ai-engineer:interview"); self.assertEqual(j["mode"], "extractive")
    def test_ask_refuse(self): s, j = self.j("/api/ask", {"question": "Give me a recipe for biryani"}); self.assertTrue(j["refused"])
    def test_ask_validation(self):
        self.assertEqual(self.j("/api/ask", {"question": "hi"})[0], 400)
        self.assertEqual(self.j("/api/ask", {"question": "x" * 501})[0], 400)
        self.assertEqual(self.j("/api/ask", {"question": 123})[0], 400)
    def test_bad_json(self): self.assertEqual(self.j("/api/ask", raw=b"{bad")[0], 400); self.assertEqual(self.j("/api/ask", raw=b"[1]")[0], 400)
    def test_too_large(self): self.assertEqual(self.j("/api/gap", {"resume": "a" * 100_001, "role": "data-analyst"})[0], 413)
    def test_gap(self):
        s, j = self.j("/api/gap", {"resume": "Python, SQL, Docker, Git, FastAPI, testing", "role": "backend-developer"})
        self.assertEqual((s, j["score"]), (200, 75)); self.assertEqual(j["missing"], ["rest apis", "system design"])
    def test_gap_unknown_role(self): self.assertEqual(self.j("/api/gap", {"resume": "Python developer here", "role": "astronaut"})[0], 404)
    def test_recommend(self): s, j = self.j("/api/recommend", {"resume": "linux bash docker kubernetes terraform aws"}); self.assertEqual(j["roles"][0]["role"], "devops-engineer")
    def test_404(self): self.assertEqual(self.j("/nope")[0], 404); self.assertEqual(self.j("/nope", {})[0], 404)
    def test_rate_limiter(self):
        r = RateLimiter(2, 60); self.assertEqual([r.allow("a"), r.allow("a"), r.allow("a"), r.allow("b")], [True, True, False, True])
if __name__ == "__main__": unittest.main()
