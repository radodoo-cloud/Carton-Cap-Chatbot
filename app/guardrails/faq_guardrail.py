from fastapi import HTTPException
from app.retrieval.faq_retriever import FAQRetriever

ALLOWED_TOPICS = [
    "referral", "invite", "bonus", "friend", "link", "onboarding",
    "reward", "track", "restriction", "abuse", "sign up", "code",
    "carton caps", "program", "account", "school", "points"
]

class FAQGuardrail:
    @staticmethod
    def validate_query(query: str) -> str:
        lowered = query.lower()
        if not any(topic in lowered for topic in ALLOWED_TOPICS):
            raise HTTPException(
                status_code=400,
                detail="I can only answer questions about the Carton Caps referral program. Please ask about referrals, bonuses, or how the program works."
            )
        return query

    @staticmethod
    def validate_response(reply: str, facts: list) -> str:
        if not facts:
            return "I'm sorry, I couldn't find relevant information in our FAQ. Please ask about the Carton Caps referral program."
        faq_content = " ".join(f["content"].lower() for f in facts)
        reply_words = set(reply.lower().split())
        faq_words = set(faq_content.split())
        overlap = reply_words & faq_words
        if len(overlap) < 5:
            return "I can only provide information based on the Carton Caps referral FAQ. Please ask a question related to referrals or the program."
        return reply
