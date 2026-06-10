"""
Менеджер базы знаний.
Загружает данные из Google Sheets, кэширует в памяти,
формирует текстовый контекст для промпта OpenAI.
"""

import logging
from typing import Optional

from services.sheets import load_knowledge_base

logger = logging.getLogger(__name__)

_cache: dict = {}


def refresh() -> None:
    """Перечитывает базу знаний из Google Sheets."""
    global _cache
    try:
        _cache = load_knowledge_base()
        logger.info("База знаний обновлена")
    except Exception as e:
        logger.error("Не удалось обновить базу знаний: %s", e)


def get_context_for_ai() -> str:
    """
    Формирует текстовый блок для системного промпта.
    Каждый лист превращается в читаемый текст.
    """
    if not _cache:
        return "База знаний пока не загружена."

    parts: list[str] = []

    # --- Общая информация ---
    if _cache.get("hotel_info"):
        lines = ["## Общая информация об отеле"]
        for row in _cache["hotel_info"]:
            k = row.get("ключ", "")
            v = row.get("значение", "")
            if k and v:
                lines.append(f"- {k}: {v}")
        parts.append("\n".join(lines))

    # --- Номера ---
    if _cache.get("rooms"):
        lines = ["## Номера"]
        for row in _cache["rooms"]:
            name = row.get("категория", "")
            desc = row.get("описание", "")
            area = row.get("площадь_кв_м", "")
            base = row.get("основных_мест", "")
            extra = row.get("доп_мест", "")
            price_wday = row.get("цена_будни", "")
            price_wend = row.get("цена_выходные", "")
            features = row.get("особенности", "")
            lines.append(f"\n### {name}")
            lines.append(f"Описание: {desc}")
            if area:
                lines.append(f"Площадь: {area} кв.м.")
            if base:
                lines.append(f"Основных мест: {base}, дополнительных: {extra}")
            if price_wday:
                lines.append(f"Цена: будни — {price_wday}, выходные — {price_wend}")
            if features:
                lines.append(f"Особенности: {features}")
        parts.append("\n".join(lines))

    # --- Условия бронирования ---
    if _cache.get("booking_info"):
        lines = ["## Условия бронирования и заселения"]
        for row in _cache["booking_info"]:
            p = row.get("параметр", "")
            d = row.get("описание", "")
            if p and d:
                lines.append(f"- {p}: {d}")
        parts.append("\n".join(lines))

    # --- Услуги ---
    if _cache.get("services"):
        lines = ["## Услуги"]
        for row in _cache["services"]:
            name = row.get("название", "")
            desc = row.get("описание", "")
            price = row.get("стоимость", "")
            cond = row.get("условия", "")
            if name:
                entry = f"- {name}"
                if desc:
                    entry += f": {desc}"
                if price:
                    entry += f" | Стоимость: {price}"
                if cond:
                    entry += f" | Условия: {cond}"
                lines.append(entry)
        parts.append("\n".join(lines))

    # --- Правила ---
    if _cache.get("rules"):
        lines = ["## Правила проживания"]
        for row in _cache["rules"]:
            t = row.get("тема", "")
            r = row.get("правило", "")
            if t and r:
                lines.append(f"- {t}: {r}")
        parts.append("\n".join(lines))

    # --- FAQ ---
    if _cache.get("faq"):
        lines = ["## Частые вопросы и ответы"]
        for row in _cache["faq"]:
            q = row.get("вопрос", "")
            a = row.get("ответ", "")
            if q and a:
                lines.append(f"В: {q}\nО: {a}")
        parts.append("\n".join(lines))

    # --- Акции ---
    if _cache.get("promos"):
        lines = ["## Акции и специальные предложения"]
        for row in _cache["promos"]:
            name = row.get("название", "")
            desc = row.get("описание", "")
            discount = row.get("скидка", "")
            period = row.get("срок_акции", "")
            cond = row.get("условия", "")
            if name:
                entry = f"- {name}"
                if desc:
                    entry += f": {desc}"
                if discount:
                    entry += f" | Скидка: {discount}"
                if period:
                    entry += f" | Действует: {period}"
                if cond:
                    entry += f" | Условия: {cond}"
                lines.append(entry)
        parts.append("\n".join(lines))

    return "\n\n".join(parts)


def is_loaded() -> bool:
    return bool(_cache)
