import pytest
import asyncio
from unittest.mock import patch, MagicMock
from httpx import Response
from app.main import app

@pytest.mark.anyio
async def test_talk_endpoint_valid_request():
    with patch('app.services.groq_talk_service.httpx.AsyncClient.post') as mock_post, \
         patch('app.api.talk.groq_talk_service.api_key', 'dummy_key'):
        mock_post.return_value = Response(
            200,
            json={
                "choices": [{
                    "message": {
                        "content": '{"message": "I hear you.", "tone": "gentle", "should_suggest_music": false}'
                    }
                }]
            }
        )
        
        # We use testclient to send request
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.post("/api/talk", json={"message": "I had a bad day."})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "I hear you."
        assert data["tone"] == "gentle"

@pytest.mark.anyio
async def test_talk_endpoint_rate_limit():
    with patch('app.services.groq_talk_service.httpx.AsyncClient.post') as mock_post, \
         patch('app.api.talk.groq_talk_service.api_key', 'dummy_key'):
        mock_post.return_value = Response(429)
        
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.post("/api/talk", json={"message": "Hello"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "pause" in data["message"]
