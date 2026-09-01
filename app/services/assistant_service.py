from sqlalchemy.orm import Session
from app.services.recommendation_service import RecommendationService
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.faq_retriever import FAQRetriever
from app.services.context_service import ContextService
from app.llm.client import LLMClient
from app.guardrails.output_guardrail import OutputGuardrail
from app.guardrails.faq_guardrail import FAQGuardrail
from app.db.repository import Repository

class AssistantService:
    @staticmethod
    def process_message(db: Session, conversation_id: str, user_message: str):
        # 1. Classify Intent
        intent = RecommendationService.classify_intent(user_message)

        # 2. Route to correct retriever + apply FAQ guardrail if needed
        if intent == "FAQ_QUERY":
            FAQGuardrail.validate_query(user_message)
            facts = FAQRetriever.fetch(user_message)
        else:
            facts = HybridRetriever.retrieve(db, intent, user_message)

        # 3. Build Context
        context = ContextService.prepare_context(intent, facts)

        # 4. LLM Response Generation
        raw_reply = LLMClient.generate(context, user_message)

        # 5. Output Guardrails
        if intent == "FAQ_QUERY":
            clean_reply = FAQGuardrail.validate_response(raw_reply, facts)
        else:
            clean_reply = OutputGuardrail.validate(raw_reply)

        # 6. Save Turn to Conversation Store
        Repository.save_message(db, conversation_id, "user", user_message)
        assistant_msg = Repository.save_message(db, conversation_id, "assistant", clean_reply, intent)

        return assistant_msg, intent, clean_reply, facts
