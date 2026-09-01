from sqlalchemy.orm import Session
from app.retrieval.sql_retriever import SQLRetriever

class HybridRetriever:
    @staticmethod
    def retrieve(db: Session, intent: str, query: str):
        return SQLRetriever.fetch_data(db, intent, query)
