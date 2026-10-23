import html
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputRichMessage, LinkPreviewOptions
from dishka import AsyncContainer

from koloagent.infrastructure.devin import DevinApiClient, DevinThread, DevinThreads
from koloagent.presentation.formatting import render_devin_turn

logger = logging.getLogger("devin.poller")

_TURN_DONE_DETAILS = {"waiting_for_user", "waiting_for_approval", "finished"}
_TURN_DONE_STATUSES = {"exit", "error"}


async def _persist_turn(bot: Bot, thread: DevinThread) -> None:
    text = render_devin_turn(thread.turn_buffer, thread.url)
    try:
        await bot.send_rich_message(
            chat_id=thread.chat_id, rich_message=InputRichMessage(markdown=text)
        )
    except TelegramBadRequest:
        logger.exception("rich message failed, fallback to plain")
        plain = f"🤖 Devin\n\n{thread.turn_buffer}\n\n—\n{thread.url}"
        await bot.send_message(
            chat_id=thread.chat_id,
            text=html.escape(plain),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    thread.finalized = True


async def poll_devin_thread(container: AsyncContainer) -> None:
    threads = await container.get(DevinThreads)
    thread = threads.get()
    if thread is None:
        return

    bot = await container.get(Bot)

    if threads.is_expired(thread):
        if thread.turn_buffer and not thread.finalized:
            await _persist_turn(bot, thread)
        threads.close()
        await bot.send_message(
            chat_id=thread.chat_id,
            text="⏱ Тред Devin закрыт по таймауту. Новый: /gh &lt;запрос&gt;",
        )
        return

    client = await container.get(DevinApiClient)
    try:
        messages = await client.list_messages(thread.devin_id)
        session = await client.get_session(thread.devin_id)
    except Exception:
        logger.exception("devin poll failed for %s", thread.devin_id)
        return

    new_texts = []
    for msg in messages:
        if msg.event_id in thread.seen_event_ids:
            continue
        thread.seen_event_ids.add(msg.event_id)
        if msg.source == "devin" and msg.message:
            new_texts.append(msg.message)

    if new_texts:
        thread.turn_buffer = "\n\n".join([thread.turn_buffer, *new_texts]).strip()
        thread.finalized = False

    if not thread.turn_buffer or thread.finalized:
        return

    turn_done = (
        session.status in _TURN_DONE_STATUSES
        or session.status_detail in _TURN_DONE_DETAILS
    )
    if turn_done:
        await _persist_turn(bot, thread)
        return

    text = render_devin_turn(thread.turn_buffer, thread.url)
    if text == thread.draft_sent:
        return

    try:
        await bot.send_rich_message_draft(
            chat_id=thread.chat_id,
            draft_id=thread.draft_id,
            rich_message=InputRichMessage(markdown=text),
        )
        thread.draft_sent = text
    except TelegramBadRequest:
        logger.exception("rich draft failed, fallback to plain")
        plain = f"🤖 Devin\n\n{thread.turn_buffer}\n\n—\n{thread.url}"
        await bot.send_message(
            chat_id=thread.chat_id,
            text=html.escape(plain),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        thread.finalized = True
