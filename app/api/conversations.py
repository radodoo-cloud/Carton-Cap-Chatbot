from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models.response import CreateConversationRequest, ConversationResponse
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/v1/chat/conversations", tags=["conversations"])

@router.post("", response_model=ConversationResponse)
def create_conversation(req: CreateConversationRequest, db: Session = Depends(get_db)):
    # Mock hardcoded user ID from Auth context
    user_id = "user_demo_123"
    conv_id, greeting = ConversationService.create_new_conversation(db, user_id, req.entry_point)
    return ConversationResponse(conversation_id=conv_id, greeting=greeting)
