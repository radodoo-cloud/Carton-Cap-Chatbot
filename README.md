# Carton Caps AI Chat Agent

A conversational AI service built with FastAPI that powers the Carton Caps chatbot — Capper. The service supports multi-turn conversations, product queries against a SQLite database, and referral/FAQ questions answered via a RAG pipeline backed by OpenAI GPT-4o-mini.

---

## Features

- Multi-turn conversation management with persistent storage
- Intent classification routing messages to the correct pipeline
- SQL retrieval for product catalog queries
- FAQ retrieval (RAG) for referral and program questions
- Input and output guardrails for safety and relevance
- OpenAI GPT-4o-mini LLM integration
- REST API built with FastAPI

---

## Project Structure

```
app/
├── api/                  # FastAPI route handlers
│   ├── conversations.py
│   └── messages.py
├── db/                   # Database connection and repository
│   ├── connection.py
│   └── repository.py
├── guardrails/           # Input, output, and FAQ guardrails
│   ├── input_guardrail.py
│   ├── output_guardrail.py
│   └── faq_guardrail.py
├── llm/                  # LLM client and prompt templates
│   ├── client.py
│   └── prompts.py
├── models/               # SQLAlchemy and Pydantic models
│   ├── conversation.py
│   ├── message.py
│   └── response.py
├── retrieval/            # SQL, FAQ, and hybrid retrievers
│   ├── sql_retriever.py
│   ├── faq_retriever.py
│   ├── hybrid_retriever.py
│   └── knowledge_retriever.py
├── services/             # Business logic layer
│   ├── assistant_service.py
│   ├── conversation_service.py
│   ├── context_service.py
│   └── recommendation_service.py
└── main.py               # FastAPI app entry point
data/
├── Carton Caps Data.sqlite
└── faqs.txt
tests/
├── test_unit.py
└── test_integration.py
```

---

## Requirements

- Python 3.12+
- OpenAI API key

---

## Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd "Carton Caps Chatbot"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=<your-openai-api-key>
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs available at `http://localhost:8000/docs`.

---

## Running Tests

```bash
python3 -m pytest tests/ -v
```

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes |
| `DATABASE_URL` | SQLAlchemy database URL | No (defaults to SQLite) |
