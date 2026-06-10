"""
Обработчик свободных вопросов через Claude.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from services import claude_service
from services.sheets import append_unanswered, increment_stat

logger = logging.getLogger(__name__)

BOOK_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏔 Забронировать номер", callback_data="menu_book")],
    [InlineKeyboardButton("← Главное меню", callback_data="menu_main")],
])


async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not text:
        return

    await update.message.chat.send_action(ChatAction.TYPING)

    reply, needs_escalation = await claude_service.get_reply(user_id, text)

    await update.message.reply_text(reply, reply_markup=BOOK_BUTTON)

    increment_stat("диалогов")
    if needs_escalation:
        append_unanswered(user_id, text)
        increment_stat("вопросов_без_ответа")
        logger.info("Вопрос без ответа от %s: %s", user_id, text)
