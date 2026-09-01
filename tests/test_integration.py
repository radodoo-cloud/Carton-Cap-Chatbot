import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"


def test_create_conversation():
    res = client.post("/v1/chat/conversations", json={"entry_point": "test"})
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    assert "greeting" in data
    assert "Capper" in data["greeting"]


def test_send_message_general():
    conv_res = client.post("/v1/chat/conversations", json={"entry_point": "test"})
    conv_id = conv_res.json()["conversation_id"]

    msg_res = client.post(
        f"/v1/chat/conversations/{conv_id}/messages",
        json={"content": "Hello there"}
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    assert data["intent"] == "GENERAL"
    assert data["role"] == "assistant"
    assert len(data["reply"]) > 0


def test_send_message_product_query():
    conv_res = client.post("/v1/chat/conversations", json={"entry_point": "test"})
    conv_id = conv_res.json()["conversation_id"]

    msg_res = client.post(
        f"/v1/chat/conversations/{conv_id}/messages",
        json={"content": "What snacks can I buy?"}
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    assert data["intent"] == "PRODUCT_QUERY"
    assert len(data["retrieved_data"]) > 0


def test_send_message_invalid_conversation():
    res = client.post(
        "/v1/chat/conversations/invalid_id/messages",
        json={"content": "Hello"}
    )
    assert res.status_code == 404


def test_send_message_empty_content():
    conv_res = client.post("/v1/chat/conversations", json={"entry_point": "test"})
    conv_id = conv_res.json()["conversation_id"]

    res = client.post(
        f"/v1/chat/conversations/{conv_id}/messages",
        json={"content": "   "}
    )
    assert res.status_code == 400


def test_multi_turn_conversation():
    conv_res = client.post("/v1/chat/conversations", json={"entry_point": "test"})
    conv_id = conv_res.json()["conversation_id"]

    first = client.post(
        f"/v1/chat/conversations/{conv_id}/messages",
        json={"content": "What snacks do you have?"}
    )
    assert first.status_code == 200

    second = client.post(
        f"/v1/chat/conversations/{conv_id}/messages",
        json={"content": "Tell me more about your products"}
    )
    assert second.status_code == 200
    assert second.json()["intent"] == "PRODUCT_QUERY"
