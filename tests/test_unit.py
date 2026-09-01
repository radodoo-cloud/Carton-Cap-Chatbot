import pytest
from unittest.mock import patch, MagicMock
from app.guardrails.input_guardrail import InputGuardrail
from app.guardrails.output_guardrail import OutputGuardrail
from app.services.recommendation_service import RecommendationService
from app.llm.prompts import PromptTemplates
from app.llm.client import LLMClient
from fastapi import HTTPException


# --- InputGuardrail ---

def test_input_guardrail_valid():
    assert InputGuardrail.validate("Hello") == "Hello"

def test_input_guardrail_strips_whitespace():
    assert InputGuardrail.validate("  hello  ") == "hello"

def test_input_guardrail_empty_raises():
    with pytest.raises(HTTPException) as exc:
        InputGuardrail.validate("   ")
    assert exc.value.status_code == 400

def test_input_guardrail_too_long_raises():
    with pytest.raises(HTTPException) as exc:
        InputGuardrail.validate("a" * 1001)
    assert exc.value.status_code == 400


# --- OutputGuardrail ---

def test_output_guardrail_valid():
    assert OutputGuardrail.validate("Here are some products.") == "Here are some products."

def test_output_guardrail_empty_returns_fallback():
    result = OutputGuardrail.validate("")
    assert "apologize" in result.lower()

def test_output_guardrail_too_short_returns_fallback():
    result = OutputGuardrail.validate("Hi")
    assert "apologize" in result.lower()


# --- RecommendationService ---

def test_intent_product_query():
    assert RecommendationService.classify_intent("What snacks can I buy?") == "PRODUCT_QUERY"

def test_intent_referral_query():
    assert RecommendationService.classify_intent("How do I use my referral code?") == "FAQ_QUERY"

def test_intent_general():
    assert RecommendationService.classify_intent("Hello there") == "GENERAL"


# --- PromptTemplates ---

def test_prompt_no_facts():
    prompt = PromptTemplates.build_system_prompt("GENERAL", [])
    assert "GENERAL" in prompt
    assert "Database Facts" not in prompt
    assert "FAQ" not in prompt

def test_prompt_with_facts():
    facts = [{"name": "Granola Bar", "price": 5.99}]
    prompt = PromptTemplates.build_system_prompt("PRODUCT_QUERY", facts)
    assert "Granola Bar" in prompt
    assert "$5.99" in prompt


# --- LLMClient ---

def _mock_openai_response(content: str):
    mock_msg = MagicMock()
    mock_msg.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response

def test_llm_client_general_response():
    with patch("app.llm.client._client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_openai_response("Hi! I am Capper. How can I help?")
        reply = LLMClient.generate("System Intent Scope: GENERAL\n", "Hello")
        assert len(reply) > 0
        mock_client.chat.completions.create.assert_called_once()

def test_llm_client_product_response():
    with patch("app.llm.client._client") as mock_client:
        mock_client.chat.completions.create.return_value = _mock_openai_response("Here are some products: Granola Bar at $5.99.")
        system_prompt = "System Intent Scope: PRODUCT_QUERY\nDatabase Facts:\n- Product: Granola Bar, Price: $5.99\n"
        reply = LLMClient.generate(system_prompt, "What snacks do you have?")
        assert "Granola Bar" in reply
        mock_client.chat.completions.create.assert_called_once()
