from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models.response import SendMessageRequest, ChatMessageResponse
from app.guardrails.input_guardrail import InputGuardrail
from app.services.assistant_service import AssistantService
from app.db.repository import Repository

router = APIRouter(prefix="/v1/chat/conversations", tags=["messages"])

@router.post("/{conversation_id}/messages", response_model=ChatMessageResponse)
def send_message(conversation_id: str, req: SendMessageRequest, db: Session = Depends(get_db)):
    conv = Repository.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    sanitized_text = InputGuardrail.validate(req.content)
    msg_db, intent, reply, facts = AssistantService.process_message(db, conversation_id, sanitized_text)
    
    return ChatMessageResponse(
        message_id=msg_db.id,
        role="assistant",
        intent=intent,
        reply=reply,
        retrieved_data=facts
    )
