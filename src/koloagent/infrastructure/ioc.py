from collections.abc import AsyncIterable
from datetime import timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import AsyncContainer, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from koloagent.infrastructure.config.models import Config, DevinConfig
from koloagent.infrastructure.database.config import new_session_maker
from koloagent.infrastructure.devin import DevinApiClient, DevinThreads
from koloagent.infrastructure.scheduling.tasks import poll_devin_thread


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres.dsn)

    @provide
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session, session.begin():
            yield session


class SchedulerProvider(Provider):
    @provide(scope=Scope.APP)
    def get_scheduler(
        self, config: Config, async_container: AsyncContainer
    ) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler()
        if config.devin is not None:
            scheduler.add_job(
                func=poll_devin_thread,
                trigger=IntervalTrigger(seconds=config.devin.poll_interval_seconds),
                kwargs={"container": async_container},
                name="poll_devin_thread",
            )
        return scheduler


class DevinProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_devin_client(self, config: Config) -> AsyncIterable[DevinApiClient]:
        client = DevinApiClient(config.devin or DevinConfig())
        try:
            yield client
        finally:
            await client.close()

    @provide(scope=Scope.APP)
    def get_devin_threads(self, config: Config) -> DevinThreads:
        ttl_minutes = config.devin.session_ttl_minutes if config.devin else 30
        return DevinThreads(timedelta(minutes=ttl_minutes))
