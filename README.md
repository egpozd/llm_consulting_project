# LLM Consulting Project

Проект состоит из двух сервисов:

- `auth_service` — FastAPI-сервис для регистрации, логина и выдачи JWT
- `bot_service` — Telegram-бот, который принимает JWT, ставит LLM-задачи в очередь Celery и отправляет ответ пользователю

Также используются:

- `RabbitMQ` — брокер сообщений
- `Redis` — хранилище токенов и backend для Celery
- `OpenRouter` — LLM API

---

## Структура проекта

```text
.
├── auth_service/
├── bot_service/
└── compose.yml
```

---

## Требования

- Python 3.12
- Docker Desktop
- Telegram Bot Token
- OpenRouter API Key

---

## Настройка переменных окружения

### `auth_service/.env`

```env
APP_NAME=auth-service
ENV=local

JWT_SECRET=change_me_super_secret
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

SQLITE_PATH=./auth.db
```

### `bot_service/.env`

```env
APP_NAME=bot-service
ENV=local

TELEGRAM_BOT_TOKEN=your_telegram_bot_token

JWT_SECRET=change_me_super_secret
JWT_ALG=HS256

REDIS_URL=redis://127.0.0.1:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=stepfun/step-3.5-flash:free
OPENROUTER_SITE_URL=https://example.com
OPENROUTER_APP_NAME=bot-service
```

> `JWT_SECRET` и `JWT_ALG` в обоих сервисах должны совпадать.

---

## Установка зависимостей

### `auth_service`

```bash
cd auth_service
uv sync
```

### `bot_service`

```bash
cd bot_service
uv sync
```

---

## Запуск инфраструктуры

Из корня проекта:

```bash
docker compose up -d
```

### Проверка

RabbitMQ Management:

```text
http://localhost:15672
```

Логин/пароль:

```text
guest / guest
```

---

## Запуск сервисов

Нужно открыть **3 отдельных терминала**.

### 1. Auth Service

```bash
cd auth_service
uv run --no-active uvicorn app.main:app --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 2. Celery Worker

```bash
cd bot_service
uv run --no-active celery -A app.infra.celery_app:celery_app worker --loglevel=info --pool=solo
```

### 3. Telegram Bot

```bash
cd bot_service
uv run --no-active python -m app.bot.run_bot
```

---

## Сценарий проверки

1. Зарегистрировать пользователя через Swagger `auth_service`
2. Выполнить логин и получить `access_token`
3. Отправить боту команду:

```text
/token <access_token>
```

4. После ответа **«Токен сохранён...»** отправить обычное сообщение
5. Бот должен:
   - принять задачу
   - отправить её в очередь
   - получить ответ от LLM
   - вернуть ответ в Telegram

---

## Тесты

### `auth_service`

```bash
cd auth_service
uv run --no-active pytest -q
```

### `bot_service`

```bash
cd bot_service
uv run --no-active pytest -q tests/test_handlers.py tests/test_openrouter_client.py tests/test_llm_tasks.py tests/test_telegram_client.py
```

---

## Примечания

- На Windows для Celery используется `--pool=solo`
- Для Telegram-бота используется кастомная `HttpxSession`, потому что стандартный `aiohttp`-вариант на данной машине работал нестабильно
- `Redis` и `RabbitMQ` должны быть запущены до старта `bot_service`

---

## Скриншоты

### 1. Swagger Auth Service

![Swagger Auth Service](screenshots/01_auth_swagger.png)

### 2. Успешный логин и получение JWT

![JWT Login](screenshots/02_auth_login_token.png)

### 3. Получение данных текущего пользователя

![Auth me](screenshots/03_auth_me.png)

### 4. Бот сохранил токен

![Bot token saved](screenshots/04_bot_token_saved.png)

### 5. Бот поставил задачу в очередь и итоговый ответ бота

![Bot task queued](screenshots/05_bot_task_queued_and_response.png)

### 6. Celery worker обрабатывает задачу

![Worker processing](screenshots/06_worker_processing.png)
