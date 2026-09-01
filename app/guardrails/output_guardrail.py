class OutputGuardrail:
    @staticmethod
    def validate(raw_output: str) -> str:
        if not raw_output or len(raw_output) < 3:
            return "I apologize, but I couldn't generate a proper response."
        return raw_output
