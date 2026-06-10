"""
Сценарий бронирования.
Пошагово собирает данные гостя и отправляет заявку сотрудникам.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import BOOKING_GROUP_ID
from services.sheets import append_application, increment_stat

logger = logging.getLogger(__name__)

# Состояния разговора
BOOKING_STATES = {
    "NAME":      1,
    "PHONE":     2,
    "CHECKIN":   3,
    "CHECKOUT":  4,
    "GUESTS":    5,
    "CHILDREN":  6,
    "PETS":      7,
    "ROOM_TYPE": 8,
    "BATH":      9,
    "COMMENT":   10,
}

YES_NO_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("Да", callback_data="yes"),
     InlineKeyboardButton("Нет", callback_data="no")],
])


# ── Старт сценария ───────────────────────────────────────────

async def booking_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    await query.edit_message_text(
        "Отлично! Давайте оформим заявку на бронирование.\n\n"
        "Шаг 1 из 10 — Как вас зовут? (имя и фамилия)",
    )
    return BOOKING_STATES["NAME"]


# ── Шаги сценария ────────────────────────────────────────────

async def booking_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        f"Приятно познакомиться, {context.user_data['name']}!\n\n"
        "Шаг 2 из 10 — Ваш номер телефона для связи:"
    )
    return BOOKING_STATES["PHONE"]


async def booking_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 3 из 10 — Дата заезда (например: 15.07.2025):"
    )
    return BOOKING_STATES["CHECKIN"]


async def booking_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["checkin"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 4 из 10 — Дата выезда (например: 18.07.2025):"
    )
    return BOOKING_STATES["CHECKOUT"]


async def booking_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["checkout"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 5 из 10 — Сколько гостей? (взрослых)"
    )
    return BOOKING_STATES["GUESTS"]


async def booking_guests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["guests"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 6 из 10 — Будут ли дети?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Да", callback_data="children_yes"),
             InlineKeyboardButton("Нет", callback_data="children_no")],
        ]),
    )
    return BOOKING_STATES["CHILDREN"]


async def booking_children(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["children"] = "да" if query.data == "children_yes" else "нет"
    await query.edit_message_text(
        "Шаг 7 из 10 — Будете с животными?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Да", callback_data="pets_yes"),
             InlineKeyboardButton("Нет", callback_data="pets_no")],
        ]),
    )
    return BOOKING_STATES["PETS"]


async def booking_pets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["pets"] = "да" if query.data == "pets_yes" else "нет"
    await query.edit_message_text(
        "Шаг 8 из 10 — Предпочтительный тип номера:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Гео-купол",                callback_data="room_dome")],
            [InlineKeyboardButton("Нео-юрта",                 callback_data="room_yurta")],
            [InlineKeyboardButton("Нео-юрта с горячим чаном", callback_data="room_yurta_chan")],
            [InlineKeyboardButton("Спейс Люкс",               callback_data="room_space")],
            [InlineKeyboardButton("Не важно / помогите выбрать", callback_data="room_any")],
        ]),
    )
    return BOOKING_STATES["ROOM_TYPE"]


async def booking_room_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    room_map = {
        "room_dome":       "Гео-купол",
        "room_yurta":      "Нео-юрта",
        "room_yurta_chan":  "Нео-юрта с горячим чаном",
        "room_space":      "Спейс Люкс",
        "room_any":        "Не важно / помогите выбрать",
    }
    context.user_data["room_type"] = room_map.get(query.data, query.data)
    await query.edit_message_text(
        "Шаг 9 из 10 — Интересует банный комплекс «Воспарение»?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Да, хочу добавить",     callback_data="bath_yes")],
            [InlineKeyboardButton("Нет, только проживание", callback_data="bath_no")],
            [InlineKeyboardButton("Расскажите подробнее",   callback_data="bath_info")],
        ]),
    )
    return BOOKING_STATES["BATH"]


async def booking_bath(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    bath_map = {
        "bath_yes":  "да",
        "bath_no":   "нет",
        "bath_info": "хочет узнать подробнее",
    }
    context.user_data["bath"] = bath_map.get(query.data, "нет")
    await query.edit_message_text(
        "Шаг 10 из 10 — Есть пожелания или комментарии? "
        "(особые даты, конкретный номер, дети, аллергии и т.д.)\n\n"
        "Если нет — напишите «нет»."
    )
    return BOOKING_STATES["COMMENT"]


async def booking_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["comment"] = update.message.text.strip()
    data = context.user_data

    # Формируем сводку для гостя
    summary = (
        "✅ *Заявка принята!*\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"📅 Заезд: {data.get('checkin')}\n"
        f"📅 Выезд: {data.get('checkout')}\n"
        f"👥 Гостей: {data.get('guests')}\n"
        f"👦 Дети: {data.get('children')}\n"
        f"🐾 Животные: {data.get('pets')}\n"
        f"🏠 Номер: {data.get('room_type')}\n"
        f"🔥 Баня: {data.get('bath')}\n"
        f"💬 Комментарий: {data.get('comment')}\n\n"
        "Сотрудник отеля проверит доступность и свяжется с вами для подтверждения.\n"
        "_Обычно отвечаем в течение нескольких часов._"
    )

    await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)

    # Уведомление в группу отдела бронирования
    staff_text = (
        "🔔 *Новая заявка на бронирование*\n\n"
        f"👤 {data.get('name')}\n"
        f"📞 {data.get('phone')}\n"
        f"📅 {data.get('checkin')} → {data.get('checkout')}\n"
        f"👥 Взрослых: {data.get('guests')}, дети: {data.get('children')}, животные: {data.get('pets')}\n"
        f"🏠 Номер: {data.get('room_type')}\n"
        f"🔥 Баня: {data.get('bath')}\n"
        f"💬 {data.get('comment')}"
    )
    try:
        await update.message.get_bot().send_message(
            chat_id=BOOKING_GROUP_ID,
            text=staff_text,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.error("Не удалось отправить в группу бронирования: %s", e)

    # Запись в Google Sheets
    data["source"] = f"telegram_bot:{update.effective_user.id}"
    append_application(data)
    increment_stat("заявок")

    return ConversationHandler.END


# ── Отмена ───────────────────────────────────────────────────

async def booking_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    msg = update.message or (update.callback_query and update.callback_query.message)
    if msg:
        await msg.reply_text(
            "Бронирование отменено. Напишите /start чтобы вернуться в меню."
        )
    return ConversationHandler.END
