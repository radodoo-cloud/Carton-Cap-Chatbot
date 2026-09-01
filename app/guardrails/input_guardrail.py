from fastapi import HTTPException

class InputGuardrail:
    @staticmethod
    def validate(content: str) -> str:
        sanitized = content.strip()
        if not sanitized:
            raise HTTPException(status_code=400, detail="Message content cannot be empty.")
        if len(sanitized) > 1000:
            raise HTTPException(status_code=400, detail="Message exceeds maximum allowed length.")
        return sanitized
