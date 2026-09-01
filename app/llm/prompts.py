class PromptTemplates:
    @staticmethod
    def build_system_prompt(intent: str, facts: list) -> str:
        prompt = f"You are Capper, a helpful assistant for the Carton Caps app.\n"
        prompt += f"Intent: {intent}\n"
        if intent == "PRODUCT_QUERY" and facts:
            prompt += "Database Facts:\n"
            for item in facts:
                prompt += f"- Product: {item['name']}, Price: ${item['price']:.2f}\n"
        elif intent == "FAQ_QUERY" and facts:
            prompt += "Relevant FAQ Information:\n"
            for item in facts:
                prompt += f"{item['content']}\n\n"
        return prompt
