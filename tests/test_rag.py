import unittest
from app.rag.retriever import MedicalKnowledgeRetriever

class TestRAGRetriever(unittest.TestCase):
    def setUp(self):
        self.retriever = MedicalKnowledgeRetriever()

    def test_rag_retrieval_amr(self):
        results = self.retriever.retrieve("WHO recommendations on antimicrobial resistance and antibiotics", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn("Antimicrobial Resistance", results[0]["title"])

    def test_rag_retrieval_hypertension(self):
        results = self.retriever.retrieve("WHO guidelines for hypertension treatment", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn("Hypertension", results[0]["title"])

if __name__ == "__main__":
    unittest.main()
