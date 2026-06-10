"""
Telegram-бот отеля ВДОХ
Точка входа — запускать именно этот файл: python bot.py
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from config import BOT_TOKEN
from handlers.menu import start_handler, menu_callback_handler
from handlers.booking import (
    booking_start,
    booking_name,
    booking_phone,
    booking_checkin,
    booking_checkout,
    booking_guests,
    booking_children,
    booking_pets,
    booking_room_type,
    booking_bath,
    booking_comment,
    booking_cancel,
    BOOKING_STATES,
)
from handlers.ai_chat import ai_message_handler
from services import knowledge_base

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Загружаем базу знаний сразу после старта бота."""
    logger.info("Загружаем базу знаний из Google Sheets...")
    knowledge_base.refresh()
    if knowledge_base.is_loaded():
        logger.info("База знаний успешно загружена")
    else:
        logger.warning("База знаний не загружена — бот будет отвечать 'не знаю'")


def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Сценарий бронирования
    booking_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(booking_start, pattern="^menu_book$"),
        ],
        states={
            BOOKING_STATES["NAME"]:      [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_name)],
            BOOKING_STATES["PHONE"]:     [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_phone)],
            BOOKING_STATES["CHECKIN"]:   [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_checkin)],
            BOOKING_STATES["CHECKOUT"]:  [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_checkout)],
            BOOKING_STATES["GUESTS"]:    [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_guests)],
            BOOKING_STATES["CHILDREN"]:  [CallbackQueryHandler(booking_children, pattern="^children_")],
            BOOKING_STATES["PETS"]:      [CallbackQueryHandler(booking_pets, pattern="^pets_")],
            BOOKING_STATES["ROOM_TYPE"]: [CallbackQueryHandler(booking_room_type, pattern="^room_")],
            BOOKING_STATES["BATH"]:      [CallbackQueryHandler(booking_bath, pattern="^bath_")],
            BOOKING_STATES["COMMENT"]:   [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_comment)],
        },
        fallbacks=[
            CommandHandler("cancel", booking_cancel),
            CommandHandler("start", booking_cancel),
        ],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(booking_conv)
    app.add_handler(CallbackQueryHandler(menu_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_message_handler))

    logger.info("Бот запущен")
    app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,   # сбрасываем накопившиеся апдейты при старте
    )


if __name__ == "__main__":
    main()
