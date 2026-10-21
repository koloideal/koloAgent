import asyncio
import os
import sys
from logging import Logger, getLogger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from koloagent.infrastructure.config import load_config
from koloagent.infrastructure.config.models import Config
from koloagent.infrastructure.ioc import DatabaseProvider, SchedulerProvider
from koloagent.infrastructure.logging.logger import setup_logging

config: Config = load_config("secret_data/config.toml")

session = AiohttpSession()
bot: Bot = Bot(
    token=config.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)

logger: Logger = getLogger("main")
os.makedirs("logs", exist_ok=True)
setup_logging("secret_data/logger-config.json")

container = make_async_container(
    DatabaseProvider(),
    SchedulerProvider(),
    context={Config: config, Bot: bot},
)

dp: Dispatcher = Dispatcher(storage=MemoryStorage())


async def main() -> None:
    from koloagent.presentation.business_handlers import business_router
    from koloagent.presentation.error_handlers import error_router
    from koloagent.presentation.owner_handlers import owner_router

    dp.include_routers(error_router, business_router, owner_router)

    setup_dishka(router=dp, container=container, auto_inject=True)

    await bot.delete_webhook(drop_pending_updates=True)

    scheduler = await container.get(AsyncIOScheduler)
    logger.critical("Starting scheduler...")
    scheduler.start()

    logger.critical("Starting koloAgent...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.critical("End of work...")
        sys.exit()
