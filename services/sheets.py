"""
Работа с Google Sheets.
Два режима:
  - чтение базы знаний (при старте бота и по расписанию)
  - запись заявок, вопросов без ответа, статистики
"""

import logging
from datetime import datetime
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID, SHEETS

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

_client: gspread.Client | None = None
_spreadsheet: gspread.Spreadsheet | None = None


def _get_spreadsheet() -> gspread.Spreadsheet:
    global _client, _spreadsheet
    if _spreadsheet is None:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        _client = gspread.authorize(creds)
        _spreadsheet = _client.open_by_key(SPREADSHEET_ID)
    return _spreadsheet


def load_knowledge_base() -> dict[str, list[dict]]:
    """
    Читает все листы базы знаний и возвращает словарь:
      { "hotel_info": [ {"ключ": "название", "значение": "ВДОХ"}, ... ], ... }
    """
    kb: dict[str, list[dict]] = {}
    sheets_to_read = [
        "hotel_info", "rooms", "booking_info",
        "services", "rules", "faq", "promos",
    ]
    ss = _get_spreadsheet()

    for sheet_name in sheets_to_read:
        try:
            ws = ss.worksheet(SHEETS[sheet_name])
            records = ws.get_all_records()
            kb[sheet_name] = records
            logger.info("Загружен лист '%s': %d строк", sheet_name, len(records))
        except Exception as e:
            logger.error("Ошибка загрузки листа '%s': %s", sheet_name, e)
            kb[sheet_name] = []

    return kb


def append_application(data: dict[str, Any]) -> bool:
    """Добавляет строку с заявкой на бронирование в лист applications."""
    try:
        ss = _get_spreadsheet()
        ws = ss.worksheet(SHEETS["applications"])
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            data.get("name", ""),
            data.get("phone", ""),
            data.get("checkin", ""),
            data.get("checkout", ""),
            data.get("guests", ""),
            data.get("children", ""),
            data.get("pets", ""),
            data.get("room_type", ""),
            data.get("bath", ""),
            data.get("comment", ""),
            "новая",
            data.get("source", "telegram_bot"),
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        logger.info("Заявка записана: %s", data.get("name"))
        return True
    except Exception as e:
        logger.error("Ошибка записи заявки: %s", e)
        return False


def append_unanswered(user_id: int, question: str) -> None:
    """Фиксирует вопрос, на который бот не нашёл ответа."""
    try:
        ss = _get_spreadsheet()
        ws = ss.worksheet(SHEETS["unanswered"])
        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            str(user_id),
            question,
            "нет",
        ], value_input_option="USER_ENTERED")
    except Exception as e:
        logger.error("Ошибка записи unanswered: %s", e)


def increment_stat(field: str) -> None:
    """Увеличивает счётчик в листе stats на 1 за сегодня."""
    try:
        ss = _get_spreadsheet()
        ws = ss.worksheet(SHEETS["stats"])
        today = datetime.now().strftime("%Y-%m-%d")
        records = ws.get_all_records()

        # Ищем строку за сегодня
        for i, rec in enumerate(records):
            if str(rec.get("дата")) == today:
                row_num = i + 2  # +1 заголовок, +1 индексация с 1
                headers = ws.row_values(1)
                if field in headers:
                    col = headers.index(field) + 1
                    current = ws.cell(row_num, col).value or "0"
                    ws.update_cell(row_num, col, int(current) + 1)
                return

        # Строки за сегодня нет — создаём новую
        headers = ws.row_values(1)
        new_row = [today] + ["0"] * (len(headers) - 1)
        if field in headers:
            new_row[headers.index(field)] = "1"
        ws.append_row(new_row, value_input_option="USER_ENTERED")

    except Exception as e:
        logger.error("Ошибка обновления stats: %s", e)
