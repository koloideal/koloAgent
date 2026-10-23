from dataclasses import dataclass


@dataclass
class PostgresConfig:
    host: str
    port: int
    user: str
    password: str
    name: str

    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class BotConfig:
    token: str
    owner_id: int


@dataclass
class DevinConfig:
    api_key: str = ""
    org_id: str = ""
    api_base_url: str = "https://api.devin.ai/v3"
    session_ttl_minutes: int = 30
    poll_interval_seconds: int = 20


@dataclass
class Config:
    postgres: PostgresConfig
    bot: BotConfig
    devin: DevinConfig | None = None
