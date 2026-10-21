"""Retrieval engine: alias/typo normalisation + BM25 + domain-scope guard + skill-gap analysis."""
import re, math, difflib
from collections import Counter
from .data import ROLES, ALIASES, WORD_ALIASES, CAREER_WORDS
from . import llm

MIN_SCORE = 1.0
STOP = set("a an the is are do does did i me my to for of in on and or what how which can should will they want from with about be it that this at by as tell give please".split())
_pairs = sorted(((a, c) for c, al in ALIASES.items() for a in al), key=lambda x: -len(x[0]))
_rx = [(re.compile(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])"), c) for a, c in _pairs]

def normalize(t):
    t = t.lower()
    for rx, c in _rx: t = rx.sub(c, t)
    return t

def stem(w):
    w = WORD_ALIASES.get(w, w)
    if len(w) > 5 and w.endswith("ing"): return w[:-3]
    if len(w) > 3 and w.endswith("ies"): return w[:-3] + "y"
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")): return w[:-1]
    return w

def tokenize(t):
    return [stem(w) for w in re.findall(r"[a-z0-9+#]+", normalize(t)) if w not in STOP]

DOMAIN = set(tokenize(" ".join([r["title"] + " " + " ".join(r["skills"]) for r in ROLES.values()]) + " " + CAREER_WORDS))

SPECIFIC = DOMAIN - set(tokenize(CAREER_WORDS))
INTENT = {"roadmap": set(tokenize("become learn plan path steps roadmap start")),
          "interview": set(tokenize("interview prepare preparation")),
          "overview": set(tokenize("skills required need"))}

def build_docs():
    docs = []
    for rid, r in ROLES.items():
        t, sk = r["title"], r["skills"]
        docs.append(dict(id=f"{rid}:overview", title=f"{t} - overview", kind="overview", role=rid,
            body=f"{t}: {r['summary']}\nRequired skills: {', '.join(sk)}.",
            index=f"{t} {t} skills required need {r['summary']} {' '.join(sk)}"))
        steps = r["roadmap"]
        docs.append(dict(id=f"{rid}:roadmap", title=f"{t} - roadmap", kind="roadmap", role=rid,
            body=f"{t} roadmap:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)),
            index=f"{t} {t} roadmap learn become plan path steps start career {' '.join(steps)}"))
        qs = r["interview"]
        docs.append(dict(id=f"{rid}:interview", title=f"{t} - interview questions", kind="interview", role=rid,
            body=f"{t} interview questions:\n" + "\n".join(f"- {q}" for q in qs),
            index=f"{t} {t} interview questions asked prepare preparation {' '.join(qs)}"))
    return docs

REFUSAL = ("I don't have verified information on that in my knowledge base. Ask about a role, its skills, "
           "roadmap or interview questions. / Mala hyabaddal mahiti nahi - role, skills, roadmap kiva interview baddal vichara.")

class Engine:
    def __init__(self):
        self.docs = build_docs()
        self.tf = [Counter(tokenize(d["index"])) for d in self.docs]
        self.len = [sum(c.values()) for c in self.tf]
        self.avg = sum(self.len) / len(self.len)
        df = Counter(t for c in self.tf for t in c)
        N = len(self.docs)
        self.vocab = set(df)
        self.idf = {t: math.log(1 + (N - n + .5) / (n + .5)) for t, n in df.items()}

    def _fix(self, t):
        if t in self.vocab or len(t) < 5: return t
        m = difflib.get_close_matches(t, DOMAIN, n=1, cutoff=0.82)
        return m[0] if m else t

    def search(self, q, k=3):
        qt = {self._fix(t) for t in tokenize(q)}
        in_scope = any(t in SPECIFIC for t in qt)
        boost = {k for k, v in INTENT.items() if qt & v}
        out = []
        for i, d in enumerate(self.docs):
            s = sum(self.idf[t] * self.tf[i][t] * 2.5 / (self.tf[i][t] + 1.5 * (0.25 + 0.75 * self.len[i] / self.avg))
                    for t in qt if t in self.tf[i])
            if d["kind"] in boost: s *= 1.5
            out.append((s, d))
        out.sort(key=lambda x: -x[0])
        return in_scope, out[:k]

    def ask(self, q, use_llm=True):
        in_scope, top = self.search(q)
        if not in_scope or top[0][0] < MIN_SCORE:
            return dict(answer=REFUSAL, sources=[], refused=True, mode="refusal")
        srcs = [dict(id=d["id"], title=d["title"], score=round(s, 3)) for s, d in top if s >= MIN_SCORE]
        ans = llm.generate(q, [d for _, d in top[:3]]) if use_llm else None
        if ans:
            if "[" not in ans: ans += "\n\nSources: " + ", ".join(f"[{s['id']}]" for s in srcs)
            return dict(answer=ans, sources=srcs, refused=False, mode="llm")
        ans = top[0][1]["body"] + "\n\nSources: " + ", ".join(f"[{s['id']}]" for s in srcs)
        return dict(answer=ans, sources=srcs, refused=False, mode="extractive")

    @staticmethod
    def _has(text, skill):
        return re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", text) is not None

    def gap(self, resume, role_id):
        r = ROLES[role_id]; n = normalize(resume)
        have = [s for s in r["skills"] if self._has(n, s)]
        miss = [s for s in r["skills"] if s not in have]
        return dict(role=role_id, title=r["title"], score=round(100 * len(have) / len(r["skills"])),
                    matched=have, missing=miss, roadmap=r["roadmap"], interview_focus=r["interview"][:3],
                    sources=[f"{role_id}:overview", f"{role_id}:roadmap", f"{role_id}:interview"])

    def recommend(self, resume, top=3):
        res = [self.gap(resume, rid) for rid in ROLES]
        res = [dict(role=g["role"], title=g["title"], score=g["score"], matched=g["matched"]) for g in res if g["matched"]]
        return sorted(res, key=lambda g: (-g["score"], g["title"]))[:top]

ENGINE = Engine()
