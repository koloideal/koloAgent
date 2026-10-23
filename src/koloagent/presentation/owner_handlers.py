from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

owner_router = Router(name="owner")


@owner_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer("koloAgent на связи.")
