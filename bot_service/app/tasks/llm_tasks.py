import asyncio

from app.infra.celery_app import celery_app
from app.services.openrouter_client import ask_llm
from app.services.telegram_client import send_telegram_message


@celery_app.task(name="app.tasks.llm_tasks.llm_request")
def llm_request(message_text: str, telegram_user_id: int, jwt_token: str) -> dict:
    answer = asyncio.run(ask_llm(message_text))
    asyncio.run(
        send_telegram_message(
            chat_id=telegram_user_id,
            text=answer,
        )
    )

    return {
        "status": "done",
        "telegram_user_id": telegram_user_id,
        "answer": answer,
        "token_received": bool(jwt_token),
    }
    