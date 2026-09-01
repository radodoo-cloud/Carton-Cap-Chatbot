from fastapi import FastAPI
from app.db.connection import engine, Base
from app.api.conversations import router as conversations_router
from app.api.messages import router as messages_router

# Create Database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Carton Caps AI Chat Agent",
    description="Production conversational AI architecture service.",
    version="1.0.0"
)

app.include_router(conversations_router)
app.include_router(messages_router)

@app.get("/")
def health_check():
    return {"status": "online", "service": "Carton Caps AI Chat Agent"}
