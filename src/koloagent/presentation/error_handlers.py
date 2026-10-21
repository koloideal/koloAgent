from logging import getLogger

from aiogram import Router
from aiogram.types import ErrorEvent

logger = getLogger("errors")

error_router = Router(name="error_handler")


@error_router.error()
async def on_error(event: ErrorEvent) -> None:
    logger.exception(
        "Unhandled error while processing update %s",
        event.update.update_id,
        exc_info=event.exception,
    )
