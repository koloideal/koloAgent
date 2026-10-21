from collections.abc import AsyncIterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from koloagent.infrastructure.config.models import Config
from koloagent.infrastructure.database.config import new_session_maker

# ==========================================
# 1. INFRASTRUCTURE LAYER
# ==========================================


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
    def get_scheduler(self) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler()
        # Джобы регистрируются здесь:
        # scheduler.add_job(func=my_task, trigger=IntervalTrigger(minutes=5), kwargs={"container": async_container})
        return scheduler


# ==========================================
# 2. APPLICATION LAYER
# ==========================================
# Сервисы и интеракторы добавляются сюда по мере появления бизнес-логики.
