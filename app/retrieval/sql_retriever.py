from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

class SQLRetriever:
    @staticmethod
    def fetch_data(db: Session, intent: str, query_text: str) -> List[Dict[str, Any]]:
        if intent != "PRODUCT_QUERY":
            return []
        
        # Executes against the SQLite database
        query = text("SELECT id, name, price FROM Products WHERE name LIKE :keyword LIMIT 5")
        keyword = f"%{query_text.split()[-1]}%"
        result = db.execute(query, {"keyword": keyword}).fetchall()

        if not result:
            query_all = text("SELECT id, name, price FROM Products LIMIT 5")
            result = db.execute(query_all).fetchall()

        return [{"id": r[0], "name": r[1], "price": r[2]} for r in result]
