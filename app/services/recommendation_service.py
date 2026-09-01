class RecommendationService:
    @staticmethod
    def classify_intent(message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["product", "buy", "item", "snack", "mac", "cereal", "food", "eat", "granola", "oatmeal", "pasta", "cracker", "rice", "trail", "fruit", "canned", "box", "pack"]):
            return "PRODUCT_QUERY"
        elif any(w in msg for w in ["referral", "invite", "code", "bonus", "refer", "friend", "link", "onboarding", "reward", "track", "restriction", "abuse", "faq", "how does", "what is"]):
            return "FAQ_QUERY"
        return "GENERAL"
