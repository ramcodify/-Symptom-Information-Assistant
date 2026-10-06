import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class MedicalKnowledgeRetriever:
    """Semantic RAG Knowledge Base indexing WHO fact sheets and drug leaflets."""

    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            data_path = Path(__file__).resolve().parent.parent.parent / "data" / "who_guidelines.json"
        
        self.documents: List[Dict[str, Any]] = []
        self._load_documents(data_path)
        self._build_index()

    def _load_documents(self, path: Path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.documents = data.get("documents", [])
        
        # Also index drug monographs as RAG documents
        drugs_path = path.parent / "drugs_database.json"
        if drugs_path.exists():
            with open(drugs_path, "r", encoding="utf-8") as f:
                drugs_data = json.load(f).get("drugs", {})
                for k, v in drugs_data.items():
                    doc_text = (
                        f"{v['generic_name']} (Brands: {', '.join(v.get('brand_names', []))}). "
                        f"Class: {v.get('class')}. Uses: {'; '.join(v.get('indications', []))}. "
                        f"Side effects: {'; '.join(v.get('common_side_effects', []))}. "
                        f"Warnings: {'; '.join(v.get('warnings', []))}."
                    )
                    self.documents.append({
                        "id": f"drug_leaf_{k}",
                        "title": f"Patient Information Leaflet: {v['generic_name']}",
                        "source": "Clinical Drug Monograph Leaflet",
                        "category": "Medication Guide",
                        "content": doc_text
                    })

    def _build_index(self):
        if not self.documents:
            self.vectorizer = None
            self.tfidf_matrix = None
            return

        corpus = [f"{d['title']} {d['category']} {d['content']}" for d in self.documents]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve most relevant medical knowledge chunks with relevance scores."""
        if not self.documents or self.vectorizer is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05:  # Relevance threshold
                doc = self.documents[idx]
                results.append({
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "source": doc.get("source"),
                    "category": doc.get("category"),
                    "content": doc.get("content"),
                    "relevance_score": round(score, 4)
                })
        return results

retriever = MedicalKnowledgeRetriever()
