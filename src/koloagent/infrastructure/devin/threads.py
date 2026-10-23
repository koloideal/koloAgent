from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass
class DevinThread:
    devin_id: str
    url: str
    chat_id: int
    last_activity: datetime
    seen_event_ids: set[str] = field(default_factory=set)
    turn_buffer: str = ""
    draft_id: int = 0
    draft_sent: str = ""
    finalized: bool = True

    def reset_turn(self) -> None:
        self.turn_buffer = ""
        self.draft_id += 1
        self.draft_sent = ""
        self.finalized = True


class DevinThreads:
    def __init__(self, ttl: timedelta) -> None:
        self._ttl = ttl
        self._thread: DevinThread | None = None

    def open(self, devin_id: str, url: str, chat_id: int) -> DevinThread:
        self._thread = DevinThread(
            devin_id=devin_id,
            url=url,
            chat_id=chat_id,
            last_activity=datetime.now(tz=UTC),
            draft_id=1,
        )
        return self._thread

    def get(self) -> DevinThread | None:
        return self._thread

    def touch(self) -> None:
        if self._thread is not None:
            self._thread.last_activity = datetime.now(tz=UTC)

    def close(self) -> None:
        self._thread = None

    def is_expired(self, thread: DevinThread) -> bool:
        return datetime.now(tz=UTC) - thread.last_activity > self._ttl
