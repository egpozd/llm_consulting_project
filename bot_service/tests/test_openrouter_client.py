import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.openrouter_client import ask_llm


@pytest.mark.asyncio
@respx.mock
async def test_ask_llm_success(mocker):
    mocker.patch.object(settings, "openrouter_api_key", "test-api-key")

    route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Готовый ответ модели"
                        }
                    }
                ]
            },
        )
    )

    result = await ask_llm("Привет")

    assert route.called is True
    assert result == "Готовый ответ модели"