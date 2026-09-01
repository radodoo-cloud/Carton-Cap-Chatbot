from sqlalchemy.orm import Session
from app.db.repository import Repository

class ConversationService:
    @staticmethod
    def create_new_conversation(db: Session, user_id: str, entry_point: str):
        conv = Repository.create_conversation(db, user_id, entry_point)
        greeting = "Hi! I am Capper. I can help you find products that support your school!"
        Repository.save_message(db, conv.id, "assistant", greeting, "GREETING")
        return conv.id, greeting
