"""Golden-set evaluation. Exit code 1 if any threshold is missed (used in CI)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.rag import ENGINE
G = json.load(open(Path(__file__).with_name("golden.json")))
THRESH = dict(hit1=0.95, hit3=1.0, refusal=1.0, citation=1.0)
ans = [(g, ENGINE.ask(g["q"], use_llm=False)) for g in G if g["expect"]]
oos = [(g, ENGINE.ask(g["q"], use_llm=False)) for g in G if not g["expect"]]
m = dict(hit1=sum(bool(r["sources"]) and r["sources"][0]["id"] == g["expect"] for g, r in ans) / len(ans),
         hit3=sum(g["expect"] in [s["id"] for s in r["sources"]] for g, r in ans) / len(ans),
         refusal=sum(r["refused"] for _, r in oos) / len(oos),
         citation=sum(bool(r["sources"]) and "[" in r["answer"] for _, r in ans) / len(ans))
for g, r in ans + oos:
    ok = r["refused"] if not g["expect"] else bool(r["sources"]) and r["sources"][0]["id"] == g["expect"]
    if not ok: print("FAIL:", g["q"], "->", [s["id"] for s in r["sources"]])
print(f"Questions: {len(ans)} answerable + {len(oos)} out-of-scope")
for k, v in m.items(): print(f"  {k:9s} {v:6.1%}  (target >= {THRESH[k]:.0%})")
sys.exit(0 if all(m[k] >= THRESH[k] for k in THRESH) else 1)
