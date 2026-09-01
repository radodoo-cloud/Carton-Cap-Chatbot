from app.llm.prompts import PromptTemplates

class ContextService:
    @staticmethod
    def prepare_context(intent: str, retrieved_data: list) -> str:
        return PromptTemplates.build_system_prompt(intent, retrieved_data)
