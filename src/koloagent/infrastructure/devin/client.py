from dataclasses import dataclass

import aiohttp

from koloagent.infrastructure.config.models import DevinConfig


@dataclass(frozen=True, slots=True)
class DevinSession:
    devin_id: str
    url: str
    status: str
    status_detail: str | None = None


@dataclass(frozen=True, slots=True)
class DevinMessage:
    event_id: str
    source: str
    message: str
    created_at: int


class DevinApiClient:
    def __init__(self, config: DevinConfig) -> None:
        self._session = aiohttp.ClientSession(
            base_url=f"{config.api_base_url}/organizations/{config.org_id}/",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=aiohttp.ClientTimeout(total=30),
        )

    async def create_session(self, prompt: str) -> DevinSession:
        async with self._session.post(
            "sessions", json={"prompt": prompt, "title": prompt[:80]}
        ) as response:
            response.raise_for_status()
            data = await response.json()
        return DevinSession(
            devin_id=data["session_id"],
            url=data["url"],
            status=data["status"],
            status_detail=data.get("status_detail"),
        )

    async def get_session(self, devin_id: str) -> DevinSession:
        async with self._session.get(f"sessions/{devin_id}") as response:
            response.raise_for_status()
            data = await response.json()
        return DevinSession(
            devin_id=data["session_id"],
            url=data["url"],
            status=data["status"],
            status_detail=data.get("status_detail"),
        )

    async def send_message(self, devin_id: str, message: str) -> None:
        async with self._session.post(
            f"sessions/{devin_id}/messages", json={"message": message}
        ) as response:
            response.raise_for_status()

    async def list_messages(
        self, devin_id: str, first: int = 200
    ) -> list[DevinMessage]:
        async with self._session.get(
            f"sessions/{devin_id}/messages", params={"first": first}
        ) as response:
            response.raise_for_status()
            data = await response.json()
        return [
            DevinMessage(
                event_id=item["event_id"],
                source=item["source"],
                message=item["message"],
                created_at=item["created_at"],
            )
            for item in data["items"]
        ]

    async def close(self) -> None:
        await self._session.close()
