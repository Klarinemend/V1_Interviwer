"""
subdomain_detector.py
Sprint 2 – Detecção de Subdomínios
"""

from typing import List, Dict
import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


class SubdomainDetector:
    """
    Agrupa conceitos semanticamente relacionados em subdomínios.
    """

    def __init__(self, gemini_client=None):
        self.client = gemini_client

    # ------------------------------------------------------------------
    # PIPELINE PRINCIPAL
    # ------------------------------------------------------------------
    def detect(
        self,
        concepts: List[Dict],
        min_clusters: int = 2,
        max_clusters: int = 7,
        use_ai_naming: bool = True
    ) -> Dict:

        if len(concepts) < min_clusters:
            return self._single_subdomain(concepts)

        embeddings = self._generate_embeddings(concepts)
        n_clusters = self._find_best_k(
            embeddings,
            min_clusters,
            max_clusters
        )

        labels, silhouette = self._cluster(
            embeddings,
            n_clusters
        )

        if use_ai_naming and self.client:
            subdomains = self._name_with_ai(concepts, labels)
        else:
            subdomains = self._name_simple(concepts, labels)

        return {
            "subdomains": subdomains,
            "metadata": {
                "num_subdomains": len(subdomains),
                "silhouette_score": float(silhouette),
                "method": "kmeans"
            }
        }

    # ------------------------------------------------------------------
    # EMBEDDINGS
    # ------------------------------------------------------------------
    def _generate_embeddings(self, concepts: List[Dict]) -> np.ndarray:
        texts = [
            f"{c['term']} {c.get('definition', '')}"
            for c in concepts
        ]

        if self.client:
            try:
                return self._embed_with_gemini(texts)
            except Exception:
                pass

        return self._embed_with_tfidf(texts)

    def _embed_with_gemini(self, texts: List[str]) -> np.ndarray:
        vectors = []
        for t in texts:
            r = self.client.models.embed_content(
                model="text-embedding-004",
                content=t
            )
            vectors.append(r["embedding"])
        return np.array(vectors)

    def _embed_with_tfidf(self, texts: List[str]) -> np.ndarray:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(max_features=100)
        return vec.fit_transform(texts).toarray()

    # ------------------------------------------------------------------
    # CLUSTERING
    # ------------------------------------------------------------------
    def _find_best_k(
        self,
        embeddings: np.ndarray,
        min_k: int,
        max_k: int
    ) -> int:

        best_k = min_k
        best_score = -1

        for k in range(min_k, min(max_k, len(embeddings) - 1) + 1):
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = model.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)

            if score > best_score:
                best_score = score
                best_k = k

        return best_k

    def _cluster(self, embeddings, k):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        return labels.tolist(), score

    # ------------------------------------------------------------------
    # NOMEAÇÃO
    # ------------------------------------------------------------------
    def _name_simple(self, concepts, labels):
        subdomains = []

        for cid in set(labels):
            terms = [
                concepts[i]["term"]
                for i, l in enumerate(labels)
                if l == cid
            ]
            subdomains.append({
                "id": f"subdomain_{cid}",
                "name": f"Subdomínio {cid + 1}",
                "description": f"Agrupa {len(terms)} conceitos relacionados",
                "concepts": terms,
                "size": len(terms)
            })

        return subdomains

    def _name_with_ai(self, concepts, labels):
        subdomains = []

        for cid in set(labels):
            cluster = [
                concepts[i]
                for i, l in enumerate(labels)
                if l == cid
            ]

            terms = [c["term"] for c in cluster]

            prompt = f"""
Crie um nome e descrição para um subdomínio.

TERMOS: {', '.join(terms)}

Retorne JSON:
{{ "name": "...", "description": "..." }}
"""

            try:
                r = self.client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                data = json.loads(r.text)

                subdomains.append({
                    "id": f"subdomain_{cid}",
                    "name": data["name"],
                    "description": data["description"],
                    "concepts": terms,
                    "size": len(terms)
                })

            except Exception:
                subdomains.extend(self._name_simple(concepts, labels))
                break

        return subdomains

    # ------------------------------------------------------------------
    # FALLBACK
    # ------------------------------------------------------------------
    def _single_subdomain(self, concepts):
        return {
            "subdomains": [{
                "id": "core",
                "name": "Core",
                "description": "Conceitos centrais do domínio",
                "concepts": [c["term"] for c in concepts],
                "size": len(concepts)
            }],
            "metadata": {"method": "fallback"}
        }
