"""
Обработчик свободных вопросов через Claude.
Сюда попадают все текстовые сообщения вне активного сценария бронирования.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from services import claude_service
from services.sheets import append_unanswered, increment_stat

logger = logging.getLogger(__name__)


async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not text:
        return

    await update.message.chat.send_action(ChatAction.TYPING)

    reply, needs_escalation = await claude_service.get_reply(user_id, text)

    await update.message.reply_text(reply)

    increment_stat("диалогов")
    if needs_escalation:
        append_unanswered(user_id, text)
        increment_stat("вопросов_без_ответа")
        logger.info("Вопрос без ответа от %s: %s", user_id, text)
