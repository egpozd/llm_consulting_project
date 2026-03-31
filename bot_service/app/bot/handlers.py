from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request


router = Router(name=__name__)


def _token_key(telegram_user_id: int) -> str:
    return f"tg_token:{telegram_user_id}"


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Бот запущен.\n"
        "1) Получи JWT в Auth Service через Swagger.\n"
        "2) Отправь его сюда командой:\n"
        "/token <jwt>\n"
        "3) После этого присылай обычный текстовый запрос."
    )


@router.message(Command("token"))
async def token_handler(message: Message) -> None:
    if message.from_user is None or message.text is None:
        await message.answer("Не удалось определить пользователя или текст сообщения.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Используй команду так: /token <jwt>")
        return

    token = parts[1].strip()

    try:
        payload = decode_and_validate(token)
    except ValueError as exc:
        await message.answer(
            f"Токен отклонён: {exc}. Получи новый токен в Auth Service."
        )
        return

    redis_client = get_redis()
    await redis_client.set(_token_key(message.from_user.id), token)

    await message.answer(
        "Токен сохранён.\n"
        f"sub={payload.get('sub')}, role={payload.get('role', 'unknown')}.\n"
        "Теперь можешь присылать текстовый запрос."
    )


@router.message(F.text)
async def text_handler(message: Message) -> None:
    if message.from_user is None or message.text is None:
        await message.answer("Не удалось обработать сообщение.")
        return

    if message.text.startswith("/"):
        return

    redis_client = get_redis()
    token = await redis_client.get(_token_key(message.from_user.id))

    if not token:
        await message.answer(
            "Нет сохранённого JWT. Сначала получи токен в Auth Service "
            "и отправь команду /token <jwt>."
        )
        return

    try:
        decode_and_validate(token)
    except ValueError as exc:
        await message.answer(
            f"Сохранённый токен больше не подходит: {exc}. "
            "Получи новый JWT в Auth Service и отправь /token <jwt>."
        )
        return

    task = llm_request.delay(
        message_text=message.text,
        telegram_user_id=message.from_user.id,
        jwt_token=token,
    )

    await message.answer(
        "Запрос принят в обработку.\n"
        f"task_id={task.id}"
    )