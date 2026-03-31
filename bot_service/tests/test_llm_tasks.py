from app.tasks.llm_tasks import llm_request


def test_llm_request_returns_processed_result(mocker):
    mocked_ask_llm = mocker.patch(
        "app.tasks.llm_tasks.ask_llm",
        return_value="Ответ от модели",
    )
    mocked_send_telegram_message = mocker.patch(
        "app.tasks.llm_tasks.send_telegram_message",
        return_value={"ok": True},
    )

    result = llm_request(
        message_text="Сделай краткое резюме",
        telegram_user_id=777,
        jwt_token="valid.jwt.token",
    )

    mocked_ask_llm.assert_called_once_with("Сделай краткое резюме")
    mocked_send_telegram_message.assert_called_once_with(
        chat_id=777,
        text="Ответ от модели",
    )

    assert result["status"] == "done"
    assert result["telegram_user_id"] == 777
    assert result["answer"] == "Ответ от модели"
    assert result["token_received"] is True