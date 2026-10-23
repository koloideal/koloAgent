from logging import getLogger

from aiogram import Router
from aiogram.types import BusinessConnection, BusinessMessagesDeleted, Message

logger = getLogger("business")

business_router = Router(name="business")


@business_router.business_connection()
async def on_business_connection(connection: BusinessConnection) -> None:
    logger.info(
        "business_connection %s: user=%s enabled=%s can_reply=%s",
        connection.id,
        connection.user.id,
        connection.is_enabled,
        connection.can_reply,
    )


@business_router.business_message()
async def on_business_message(message: Message) -> None:
    logger.info(
        "business_message conn=%s chat=%s from=%s",
        message.business_connection_id,
        message.chat.id,
        message.from_user.id if message.from_user else None,
    )


@business_router.edited_business_message()
async def on_edited_business_message(message: Message) -> None:
    logger.info(
        "edited_business_message conn=%s chat=%s msg=%s",
        message.business_connection_id,
        message.chat.id,
        message.message_id,
    )


@business_router.deleted_business_messages()
async def on_deleted_business_messages(deleted: BusinessMessagesDeleted) -> None:
    logger.info(
        "deleted_business_messages conn=%s chat=%s ids=%s",
        deleted.business_connection_id,
        deleted.chat.id,
        deleted.message_ids,
    )
