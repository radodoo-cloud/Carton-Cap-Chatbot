import os
from typing import List, Dict

FAQ_PATH = os.path.join(os.path.dirname(__file__), "../../data/faqs.txt")

class FAQRetriever:
    _faq_text: str = None

    @classmethod
    def _load(cls) -> str:
        if cls._faq_text is None:
            with open(FAQ_PATH, "r") as f:
                cls._faq_text = f.read()
        return cls._faq_text

    @classmethod
    def fetch(cls, query: str) -> List[Dict[str, str]]:
        text = cls._load()
        keywords = [w.lower() for w in query.split() if len(w) > 3]
        sections = text.strip().split("\n\n")
        matches = []
        for section in sections:
            if any(kw in section.lower() for kw in keywords):
                matches.append({"content": section.strip()})
        if not matches:
            matches = [{"content": section.strip()} for section in sections[:3]]
        return matches
