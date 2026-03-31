import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.services.telegram_client import send_telegram_message


@pytest.mark.asyncio
@respx.mock
async def test_send_telegram_message_success(mocker):
    mocker.patch.object(settings, "telegram_bot_token", "test-bot-token")

    route = respx.post(
        "https://api.telegram.org/bottest-bot-token/sendMessage"
    ).mock(
        return_value=Response(
            200,
            json={
                "ok": True,
                "result": {
                    "message_id": 1,
                    "chat": {"id": 777},
                    "text": "Ответ готов",
                },
            },
        )
    )

    result = await send_telegram_message(chat_id=777, text="Ответ готов")

    assert route.called is True
    assert result["ok"] is True
    assert result["result"]["chat"]["id"] == 777