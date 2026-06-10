"""
Конфигурация бота.
Все секреты — только через переменные окружения, не хардкодить.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Обязательные ────────────────────────────────────────────
BOT_TOKEN           = os.environ["BOT_TOKEN"]
ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]

# ── Google Sheets ────────────────────────────────────────────
GOOGLE_CREDENTIALS_FILE = os.environ.get(
    "GOOGLE_CREDENTIALS_FILE", "google_credentials.json"
)
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

# ── Telegram-группа отдела бронирования ─────────────────────
BOOKING_GROUP_ID = int(os.environ["BOOKING_GROUP_ID"])

# ── Администраторы бота ──────────────────────────────────────
_admin_ids_raw = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS: set[int] = {
    int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip()
}

# ── Модель Claude ────────────────────────────────────────────
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

# ── Имена листов Google Sheets ───────────────────────────────
SHEETS = {
    "hotel_info":    "hotel_info",
    "rooms":         "rooms",
    "booking_info":  "booking_info",
    "services":      "services",
    "rules":         "rules",
    "faq":           "faq",
    "promos":        "promos",
    "applications":  "applications",
    "unanswered":    "unanswered",
    "stats":         "stats",
    "settings":      "settings",
}
