"""
concept_extractor.py
Sprint 2 – Extração de Conceitos de Domínio
"""

from typing import List, Dict
import json
import spacy


class ConceptExtractor:
    """
    Extrai conceitos relevantes de um histórico de conversa.
    Combina NLP (spaCy) com enriquecimento opcional via IA (Gemini).
    """

    def __init__(
        self,
        gemini_client=None,
        language_model: str = "pt_core_news_lg"
    ):
        self.client = gemini_client

        try:
            self.nlp = spacy.load(language_model)
        except OSError:
            raise RuntimeError(
                f"Modelo spaCy '{language_model}' não encontrado.\n"
                f"Execute: python -m spacy download {language_model}"
            )

    # ------------------------------------------------------------------
    # PIPELINE PRINCIPAL
    # ------------------------------------------------------------------
    def extract_from_messages(
        self,
        messages: List[Dict],
        min_frequency: int = 2,
        max_concepts: int = 30,
        use_ai_enrichment: bool = True
    ) -> List[Dict]:

        raw_concepts = self._extract_with_spacy(messages, min_frequency)
        filtered = self._filter_concepts(raw_concepts)
        filtered = filtered[:max_concepts]

        if use_ai_enrichment and self.client:
            return self._enrich_with_ai(filtered, messages)

        # Fallback sem IA
        return [
            {
                "term": c["term"],
                "definition": "Definição pendente",
                "instances": c["instances"],
                "related_terms": [],
                "frequency": c["frequency"],
                "source_messages": c["sources"],
                "classification": "unknown",
                "confidence": 0.0
            }
            for c in filtered
        ]

    # ------------------------------------------------------------------
    # EXTRAÇÃO COM SPACY
    # ------------------------------------------------------------------
    def _extract_with_spacy(
        self,
        messages: List[Dict],
        min_frequency: int
    ) -> List[Dict]:

        term_data = {}

        for idx, msg in enumerate(messages):
            if msg.get("role") != "user":
                continue

            doc = self.nlp(msg["content"])

            # Entidades Nomeadas
            for ent in doc.ents:
                term = self._normalize_term(ent.text)
                self._add_term(term_data, term, ent.text, idx)

            # Grupos Nominais
            for chunk in doc.noun_chunks:
                if 1 <= len(chunk.text.split()) <= 3:
                    if chunk.root.pos_ in ("NOUN", "PROPN"):
                        term = self._normalize_term(chunk.text)
                        self._add_term(term_data, term, chunk.text, idx)

        concepts = []
        for term, data in term_data.items():
            if data["frequency"] >= min_frequency:
                concepts.append({
                    "term": term,
                    "frequency": data["frequency"],
                    "instances": list(data["instances"])[:5],
                    "sources": list(data["sources"])
                })

        concepts.sort(key=lambda x: x["frequency"], reverse=True)
        return concepts

    # ------------------------------------------------------------------
    # FILTROS
    # ------------------------------------------------------------------
    def _filter_concepts(self, concepts: List[Dict]) -> List[Dict]:

        stopwords = {
            "sistema", "dados", "informação", "processo",
            "parte", "tipo", "forma", "exemplo"
        }

        filtered = []
        for c in concepts:
            term = c["term"].lower()

            if len(term) < 3:
                continue
            if term in stopwords:
                continue
            if term.isdigit():
                continue

            filtered.append(c)

        return filtered

    # ------------------------------------------------------------------
    # ENRIQUECIMENTO COM IA
    # ------------------------------------------------------------------
    def _enrich_with_ai(
        self,
        concepts: List[Dict],
        messages: List[Dict]
    ) -> List[Dict]:

        context = self._build_context(messages)
        enriched = []

        for c in concepts:
            try:
                enriched.append(self._enrich_single(c, context))
            except Exception:
                enriched.append({
                    **c,
                    "definition": "Definição não disponível",
                    "related_terms": [],
                    "classification": "unknown",
                    "confidence": 0.0
                })

        return enriched

    def _build_context(self, messages: List[Dict], max_chars: int = 3000) -> str:
        parts = []
        total = 0

        for m in messages:
            if m["role"] == "user":
                if total + len(m["content"]) > max_chars:
                    break
                parts.append(m["content"])
                total += len(m["content"])

        return "\n".join(parts)

    def _enrich_single(self, concept: Dict, context: str) -> Dict:

        prompt = f"""
CONTEXTO:
{context}

TERMO: {concept['term']}
EXEMPLOS: {', '.join(concept['instances'])}

Retorne JSON:
{{
  "definition": "...",
  "instances": [],
  "related_terms": [],
  "classification": "entidade|acao|qualidade|evento",
  "confidence": 0.0
}}
"""

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        )

        data = json.loads(response.text)

        return {
            **concept,
            "definition": data.get("definition", ""),
            "instances": data.get("instances", concept["instances"]),
            "related_terms": data.get("related_terms", []),
            "classification": data.get("classification", "unknown"),
            "confidence": data.get("confidence", 0.5)
        }

    # ------------------------------------------------------------------
    # UTILITÁRIOS
    # ------------------------------------------------------------------
    def _normalize_term(self, text: str) -> str:
        return " ".join(text.split()).capitalize()

    def _add_term(self, store, term, instance, source_idx):
        if term not in store:
            store[term] = {
                "frequency": 0,
                "instances": set(),
                "sources": set()
            }

        store[term]["frequency"] += 1
        store[term]["instances"].add(instance)
        store[term]["sources"].add(source_idx)
