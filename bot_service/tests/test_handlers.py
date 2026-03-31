from types import SimpleNamespace

import pytest

from app.bot import handlers


class DummyMessage:
    def __init__(self, text: str, user_id: int = 12345):
        self.text = text
        self.from_user = SimpleNamespace(id=user_id)
        self.answers: list[str] = []

    async def answer(self, text: str) -> None:
        self.answers.append(text)


@pytest.mark.asyncio
async def test_token_handler_saves_token(mocker, fake_redis):
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)
    mocker.patch(
        "app.bot.handlers.decode_and_validate",
        return_value={"sub": "1", "role": "user"},
    )

    message = DummyMessage("/token valid.jwt.token", user_id=111)

    await handlers.token_handler(message)

    saved_token = await fake_redis.get("tg_token:111")

    assert saved_token == "valid.jwt.token"
    assert len(message.answers) == 1
    assert "Токен сохранён" in message.answers[0]
    assert "sub=1" in message.answers[0]


@pytest.mark.asyncio
async def test_text_handler_without_saved_token(mocker, fake_redis):
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)

    message = DummyMessage("Привет, бот", user_id=222)

    await handlers.text_handler(message)

    assert len(message.answers) == 1
    assert "Нет сохранённого JWT" in message.answers[0]


@pytest.mark.asyncio
async def test_text_handler_with_saved_token_sends_task(mocker, fake_redis):
    await fake_redis.set("tg_token:333", "valid.jwt.token")

    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)
    mocker.patch(
        "app.bot.handlers.decode_and_validate",
        return_value={"sub": "1", "role": "user"},
    )

    mocked_delay = mocker.patch("app.bot.handlers.llm_request.delay")
    mocked_delay.return_value = SimpleNamespace(id="task-123")

    message = DummyMessage("Сделай краткий ответ", user_id=333)

    await handlers.text_handler(message)

    mocked_delay.assert_called_once_with(
        message_text="Сделай краткий ответ",
        telegram_user_id=333,
        jwt_token="valid.jwt.token",
    )

    assert len(message.answers) == 1
    assert "Запрос принят в обработку" in message.answers[0]
    assert "task_id=task-123" in message.answers[0]