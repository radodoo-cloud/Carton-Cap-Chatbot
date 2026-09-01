from sqlalchemy.orm import Session
from app.models.conversation import ConversationDB
from app.models.message import MessageDB

class Repository:
    @staticmethod
    def create_conversation(db: Session, user_id: str, entry_point: str) -> ConversationDB:
        conv = ConversationDB(user_id=user_id, entry_point=entry_point)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def get_conversation(db: Session, conversation_id: str):
        return db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()

    @staticmethod
    def save_message(db: Session, conversation_id: str, role: str, content: str, intent: str = None) -> MessageDB:
        msg = MessageDB(conversation_id=conversation_id, role=role, content=content, intent=intent)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
