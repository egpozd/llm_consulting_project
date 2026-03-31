from typing import Any, AsyncGenerator, Dict, Optional, cast

import httpx
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType


class HttpxSession(BaseSession):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client: httpx.AsyncClient | None = None

    async def create_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def make_request(
        self,
        bot,
        method: TelegramMethod[TelegramType],
        timeout: Optional[int] = None,
    ) -> TelegramType:
        client = await self.create_client()
        url = self.api.api_url(token=bot.token, method=method.__api_method__)

        files: Dict[str, Any] = {}
        data: Dict[str, Any] = {}

        for key, value in method.model_dump(warnings=False).items():
            prepared = self.prepare_value(value, bot=bot, files=files)
            if prepared is None:
                continue
            data[key] = prepared

        if files:
            raise NotImplementedError(
                "This HttpxSession demo does not support file uploads"
            )

        response = await client.post(
            url,
            data=data,
            timeout=self.timeout if timeout is None else timeout,
        )
        raw_result = response.text

        parsed = self.check_response(
            bot=bot,
            method=method,
            status_code=response.status_code,
            content=raw_result,
        )
        return cast(TelegramType, parsed.result)

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        client = await self.create_client()

        async with client.stream("GET", url, headers=headers, timeout=timeout) as response:
            if raise_for_status:
                response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size):
                yield chunk