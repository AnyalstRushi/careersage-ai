import unittest
from app.rag import ENGINE, ROLES, normalize, tokenize
class T(unittest.TestCase):
    def test_alias(self): self.assertIn("machine learning", normalize("I know ML and K8s")); self.assertIn("kubernetes", normalize("k8s"))
    def test_stem_consistent(self): self.assertEqual(tokenize("developers testing"), tokenize("developer test"))
    def test_all_roles_have_three_docs(self): self.assertEqual(len(ENGINE.docs), 3 * len(ROLES))
    def test_refusal(self):
        r = ENGINE.ask("What is the weather in Pune today?"); self.assertTrue(r["refused"]); self.assertEqual(r["sources"], [])
    def test_generic_word_not_enough(self): self.assertTrue(ENGINE.ask("How do I learn to cook pasta?")["refused"])
    def test_cited(self):
        r = ENGINE.ask("Roadmap to become a data analyst"); self.assertFalse(r["refused"]); self.assertIn("[data-analyst:roadmap]", r["answer"])
    def test_typo(self): self.assertEqual(ENGINE.ask("how to become a cybersecurty analyst")["sources"][0]["id"], "cybersecurity-analyst:roadmap")
    def test_gap_math(self):
        g = ENGINE.gap("I know Python, Postgres, pandas and Excel. Built dashboards in Power BI.", "data-analyst")
        self.assertEqual(g["matched"], ["sql", "excel", "python", "pandas", "power bi"]); self.assertEqual(g["score"], 62)
        self.assertEqual(g["missing"], ["statistics", "data visualization", "data cleaning"])
    def test_gap_zero_and_full(self):
        self.assertEqual(ENGINE.gap("I like cooking", "devops-engineer")["score"], 0)
        self.assertEqual(ENGINE.gap(" ".join(ROLES["devops-engineer"]["skills"]), "devops-engineer")["score"], 100)
    def test_recommend(self):
        r = ENGINE.recommend("html css javascript react typescript git"); self.assertEqual(r[0]["role"], "frontend-developer")
        self.assertEqual(ENGINE.recommend("I like cooking"), [])
if __name__ == "__main__": unittest.main()
