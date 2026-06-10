"""
Главное меню бота.
"""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

MENU_TEXT = (
    "Добро пожаловать в эко-отель *«ВДОХ»* 🌿\n\n"
    "Горный Алтай, Чемальский район.\n\n"
    "Выберите категорию или напишите вопрос в чат — я отвечу сразу же 👇"
)

MAIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏔 Забронировать номер",     callback_data="menu_book")],
    [InlineKeyboardButton("🛏 Номера и цены",           callback_data="menu_rooms"),
     InlineKeyboardButton("🔥 Банный комплекс",         callback_data="menu_bath")],
    [InlineKeyboardButton("✨ Услуги",                  callback_data="menu_services"),
     InlineKeyboardButton("📋 Правила",                 callback_data="menu_rules")],
    [InlineKeyboardButton("🗺 Как добраться",           callback_data="menu_directions"),
     InlineKeyboardButton("🎁 Акции",                   callback_data="menu_promos")],
    [InlineKeyboardButton("💬 Связаться с администратором", callback_data="menu_contact")],
])

BACK_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("← Главное меню", callback_data="menu_main")],
])


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        MENU_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=MAIN_KEYBOARD,
    )


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await query.edit_message_text(
            MENU_TEXT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=MAIN_KEYBOARD,
        )

    elif data == "menu_rooms":
        text = (
            "*Номера отеля «ВДОХ»*\n\n"
            "🔵 *Гео-купол* (28 кв.м, номера 1–8)\n"
            "Футуристический купол с чугунным камином и террасой. "
            "Высота до 4 м. До 3 гостей.\n\n"
            "🟢 *Нео-юрта* (40 кв.м, номера 9–10)\n"
            "Просторная юрта с печью «Сибирь». До 4 гостей. Комфортна круглый год.\n\n"
            "🟡 *Нео-юрта с горячим чаном* (40 кв.м, номера 11–12)\n"
            "Как нео-юрта, но с фурако (горячим чаном) — включён в стоимость 1 раз в день.\n\n"
            "🔴 *Спейс Люкс* (50 кв.м, номера 13–16)\n"
            "Двухуровневый люкс с итальянским камином, сейфом и потолком 5,5 м.\n\n"
            "Во всех номерах: камин, кондиционер, тёплый пол, санузел, терраса.\n\n"
            "По ценам и наличию — напишите мне или нажмите «Забронировать номер»."
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏔 Забронировать номер", callback_data="menu_book")],
                [InlineKeyboardButton("← Назад", callback_data="menu_main")],
            ]),
        )

    elif data == "menu_bath":
        text = (
            "*Банный комплекс «Воспарение»* 🔥\n\n"
            "Первое премиальное банное пространство Горного Алтая. "
            "Построен из кедровых брёвен возрастом 350+ лет по канадской технологии.\n\n"
            "Работает: 11:00–23:00\n\n"
            "*Популярные программы:*\n"
            "• 1 гость — «Огненный Феникс» (1,5 ч) — 12 600 руб.\n"
            "• 2 гостя — «Воспарение» (2,5 ч) — 35 000 руб.\n"
            "• 3–4 гостя — «Перезагрузка» (3 ч) — 50 000 руб.\n"
            "• До 8 гостей — «Алтай начинается с бани» (2 ч) — 32 000 руб.\n\n"
            "Аренда бани: от 9900 руб./час (мин. 2 часа).\n\n"
            "Хотите узнать о конкретной программе? Просто напишите мне."
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=BACK_KEYBOARD,
        )

    elif data == "menu_services":
        text = (
            "*Услуги и удобства* ✨\n\n"
            "🏊 *Бассейн* — включён в проживание, 7:00–22:00\n"
            "🚲 *Велосипеды* — бесплатно (4 шт., есть детский)\n"
            "🔥 *Мангал* — у каждого номера, уголь от 500 руб.\n"
            "🌹 *Украшение номера* — лепестки, шары, цветы (от 1000 руб. + декор)\n"
            "💆 *Стирка* — 200 руб. за загрузку\n"
            "📽 *Проектор* — 4 штуки, по запросу бесплатно\n"
            "🎲 *Настольные игры* — в ресторане в свободном доступе\n"
            "🚙 *Трансфер* — через партнёра, от 4300 руб.\n"
            "🏔 *Экскурсии* — Чуйский тракт, квадроциклы, сплавы, вертолёты\n"
            "🎤 *Аренда зала кафе* — для мероприятий, 5000 руб./час\n\n"
            "Есть вопрос по конкретной услуге? Напишите — отвечу."
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=BACK_KEYBOARD,
        )

    elif data == "menu_rules":
        text = (
            "*Правила проживания* 📋\n\n"
            "🕙 *Заезд* — с 14:00 | *Выезд* — до 12:00\n"
            "🔇 *Тишина* — с 22:00\n"
            "🚫 *Запрещено*: тусовки, алкоголь в бане, шум\n"
            "🐾 *Животные* — до 40 см в холке, 2500 руб. за весь период\n"
            "🎆 *Фейерверки* — только за территорией отеля\n"
            "🚗 *Парковка* — на территории, открытая, ворота закрываются ночью\n\n"
            "*Отмена бронирования:*\n"
            "За сутки и раньше — полный возврат.\n"
            "Позже или незаезд — удержание за 1 сутки.\n\n"
            "Есть вопросы по правилам? Напишите мне."
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=BACK_KEYBOARD,
        )

    elif data == "menu_directions":
        text = (
            "*Как добраться* 🗺\n\n"
            "📍 *Адрес:* село Анос, ул. Центральная 127, Чемальский район, Республика Алтай\n\n"
            "✈️ *От аэропорта Горно-Алтайска:* 89 км, ~1,2 часа\n\n"
            "*Два варианта въезда:*\n"
            "• Бесплатный мост — через с. Аскат\n"
            "• Платный мост «Зубы дракона» — 100 руб. наличными (только наличные!). "
            "Авто с низкой посадкой — лучше через бесплатный.\n\n"
            "*Рядом с отелем:*\n"
            "• Река Катунь — 200–300 м\n"
            "• Подвесной мост — 700 м\n"
            "• Зубы дракона — 1,5 км\n\n"
            "Нужен трансфер? Организуем через ресепшн."
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=BACK_KEYBOARD,
        )

    elif data == "menu_promos":
        text = (
            "*Акции и спецпредложения* 🎁\n\n"
            "🎂 *Скидка именинника —10%*\n"
            "На проживание и баню в день рождения ±3 дня. Постоянная акция.\n\n"
            "👨‍👩‍👧 *Дети до 6 лет — бесплатно* (всегда)\n\n"
            "🏘 *От 5 номеров — скидка 10%*\n\n"
            "🌸 *Раннее бронирование на лето — скидка 10–20%*\n"
            "Уточняйте актуальные сроки у менеджера.\n\n"
            "💆 *Скидка 30% женщинам на банные программы*\n"
            "Будние дни, 10:00–16:00 (уточнить срок у менеджера)\n\n"
            "Хотите уточнить условия акции? Напишите мне или свяжитесь с администратором."
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Связаться с администратором", callback_data="menu_contact")],
                [InlineKeyboardButton("← Назад", callback_data="menu_main")],
            ]),
        )

    elif data == "menu_contact":
        text = (
            "*Связь с администратором* 💬\n\n"
            "Напишите ваш вопрос прямо здесь — я передам его сотруднику отеля, "
            "и вам ответят в ближайшее время.\n\n"
            "Или свяжитесь напрямую:\n"
            "📞 Кафе «Вдох»: +7 (999) 333-80-13\n\n"
            "_Ресепшн работает с 8:00 до 23:00. Бронирование — 24/7._"
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=BACK_KEYBOARD,
        )
