from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CreateConversationRequest(BaseModel):
    entry_point: str = "home_widget"

class ConversationResponse(BaseModel):
    conversation_id: str
    greeting: str

class SendMessageRequest(BaseModel):
    content: str = Field(..., json_schema_extra={"example": "What snacks support my school?"})

class ChatMessageResponse(BaseModel):
    message_id: str
    role: str = "assistant"
    intent: str
    reply: str
    retrieved_data: List[Dict[str, Any]]
