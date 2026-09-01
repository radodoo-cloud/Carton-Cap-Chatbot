# API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## Health Check

### GET /

Returns the service status.

**Response**
```json
{
  "status": "online",
  "service": "Carton Caps AI Chat Agent"
}
```

---

## Conversations

### POST /v1/chat/conversations

Creates a new conversation and returns a greeting from Capper.

**Request Body**
```json
{
  "entry_point": "home_widget"
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| entry_point | string | No | `home_widget` | Where the conversation was initiated |

**Response**
```json
{
  "conversation_id": "c_3f9a1b2c",
  "greeting": "Hi! I am Capper. I can help you find products that support your school!"
}
```

| Field | Type | Description |
|---|---|---|
| conversation_id | string | Unique conversation ID used for subsequent messages |
| greeting | string | Opening message from Capper |

**Status Codes**
| Code | Description |
|---|---|
| 200 | Conversation created successfully |

---

## Messages

### POST /v1/chat/conversations/{conversation_id}/messages

Sends a message to an existing conversation and returns Capper's response.

**Path Parameters**
| Parameter | Type | Description |
|---|---|---|
| conversation_id | string | The conversation ID returned from POST /v1/chat/conversations |

**Request Body**
```json
{
  "content": "What snacks support my school?"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| content | string | Yes | The user's message (max 1000 characters) |

**Response**
```json
{
  "message_id": "m_7c4d2e1f",
  "role": "assistant",
  "intent": "PRODUCT_QUERY",
  "reply": "Here are some products from our catalog that may interest you:\n- Product: Frosted Flakes Cereal, Price: $3.79\n- Product: Granola Cereal Bars, Price: $5.92",
  "retrieved_data": [
    {
      "id": 1,
      "name": "Frosted Flakes Cereal",
      "price": 3.79
    },
    {
      "id": 2,
      "name": "Granola Cereal Bars",
      "price": 5.92
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| message_id | string | Unique ID of the assistant message |
| role | string | Always `assistant` |
| intent | string | Classified intent: `PRODUCT_QUERY`, `FAQ_QUERY`, or `GENERAL` |
| reply | string | Capper's response |
| retrieved_data | array | Data retrieved from SQL or FAQ depending on intent |

**Status Codes**
| Code | Description |
|---|---|
| 200 | Message processed successfully |
| 400 | Empty message, message too long, or FAQ guardrail blocked the query |
| 404 | Conversation not found |

---

## Intent Types

| Intent | Description | Example Query |
|---|---|---|
| `PRODUCT_QUERY` | User is asking about products in the catalog | "What snacks can I buy?" |
| `FAQ_QUERY` | User is asking about referrals or the Carton Caps program | "How do I refer a friend?" |
| `GENERAL` | General conversation not matching other intents | "Hello" |

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Message content cannot be empty."
}
```

| Status Code | Cause |
|---|---|
| 400 | Empty message, message exceeds 1000 characters, or FAQ guardrail rejection |
| 404 | Conversation ID does not exist |

---

## Example Flow

**1. Start a conversation**
```bash
curl -X POST http://localhost:8000/v1/chat/conversations \
  -H "Content-Type: application/json" \
  -d '{"entry_point": "home_widget"}'
```

**2. Send a product query**
```bash
curl -X POST http://localhost:8000/v1/chat/conversations/c_3f9a1b2c/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What cereals do you have?"}'
```

**3. Send a referral question**
```bash
curl -X POST http://localhost:8000/v1/chat/conversations/c_3f9a1b2c/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "How do I refer a friend?"}'
```
