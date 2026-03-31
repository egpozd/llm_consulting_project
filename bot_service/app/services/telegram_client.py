import httpx

from app.core.config import settings


async def send_telegram_message(chat_id: int, text: str) -> dict:
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is empty. Add it to bot_service/.env"
        )

    url = (
        f"https://api.telegram.org/"
        f"bot{settings.telegram_bot_token}/sendMessage"
    )
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    if not data.get("ok", False):
        raise RuntimeError("Telegram API returned ok=false")

    return data