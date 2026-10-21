"""Роутер прямых сообщений боту (чат владельца с ботом, без business_connection)."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

owner_router = Router(name="owner")


@owner_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    # TODO: приветствие/справка для владельца
    await message.answer("koloAgent на связи. Бизнес-логика пока не реализована.")
