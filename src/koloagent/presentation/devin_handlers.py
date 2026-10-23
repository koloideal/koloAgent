import contextlib
import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import LinkPreviewOptions, Message, ReactionTypeEmoji
from dishka import FromDishka

from koloagent.infrastructure.config.models import Config
from koloagent.infrastructure.devin import DevinApiClient, DevinThreads

logger = logging.getLogger("devin")

devin_router = Router(name="devin")


@devin_router.message(Command("gh"))
async def cmd_gh(
    message: Message,
    command: CommandObject,
    config: FromDishka[Config],
    client: FromDishka[DevinApiClient],
    threads: FromDishka[DevinThreads],
) -> None:
    prompt = (command.args or "").strip()
    if not prompt:
        await message.answer("Формат: /gh &lt;запрос для Devin&gt;")
        return

    if config.devin is None:
        await message.answer("Devin не настроен — заполни секцию [devin] в config.toml")
        return

    try:
        session = await client.create_session(prompt)
    except Exception:
        logger.exception("devin create_session failed")
        await message.answer("Devin API не ответил — смотри логи")
        return

    threads.open(
        devin_id=session.devin_id, url=session.url, chat_id=message.chat.id
    )

    await message.answer(
        "🚀 <b>Сессия Devin создана</b>\n\n"
        f'<a href="{session.url}">{session.url}</a>\n\n'
        "Просто пиши сюда — сообщения улетят в тред. "
        f"Тред живёт {config.devin.session_ttl_minutes} мин после последнего сообщения.",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@devin_router.message(F.text & ~F.text.startswith("/"))
async def on_owner_text(
    message: Message,
    config: FromDishka[Config],
    client: FromDishka[DevinApiClient],
    threads: FromDishka[DevinThreads],
) -> None:
    thread = threads.get()

    if thread is None:
        await message.answer("Нет активного треда Devin. Начни: /gh &lt;запрос&gt;")
        return

    if threads.is_expired(thread):
        threads.close()
        ttl = config.devin.session_ttl_minutes if config.devin else 0
        await message.answer(
            f"Тред истёк ({ttl} мин без сообщений). Новый: /gh &lt;запрос&gt;"
        )
        return

    if not message.text:
        return

    try:
        await client.send_message(thread.devin_id, message.text)
    except Exception:
        logger.exception("devin send_message failed for %s", thread.devin_id)
        await message.answer("Не смог отправить сообщение Devin'у — смотри логи")
        return

    if thread.finalized:
        thread.reset_turn()
    threads.touch()
    with contextlib.suppress(Exception):
        await message.react([ReactionTypeEmoji(emoji="👀")])
