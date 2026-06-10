"""
Сервис Anthropic Claude.
"""

import logging
from anthropic import AsyncAnthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from services import knowledge_base

logger = logging.getLogger(__name__)

_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT_TEMPLATE = """Ты — помощник эко-отеля «ВДОХ» в Чемальском районе Горного Алтая.

СТИЛЬ ОБЩЕНИЯ:
- Пиши как живой человек, который хорошо знает отель и искренне рад гостям
- Короткие абзацы, простые предложения, разговорный тон
- Без официоза и канцелярита
- Можно использовать один-два эмодзи уместно, но не перебарщивай
- НЕ используй markdown: никаких **, ##, ---, списков с дефисами через строку
- Пиши сплошным текстом или простыми абзацами
- Если перечисляешь — пиши через запятую или с новой строки без символов

СТРОГИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основании базы знаний ниже
2. Если информации нет — скажи честно: «Точно не знаю, лучше уточнить у ребят на ресепшн — они всё расскажут»
3. Не придумывай цены, услуги, условия которых нет в базе
4. Если гость хочет забронировать — предложи нажать кнопку «Забронировать номер» в меню или написать напрямую
5. Не сравнивай с другими отелями

БАЗА ЗНАНИЙ ОТЕЛЯ «ВДОХ»:
{knowledge_context}
"""

_history: dict[int, list[dict]] = {}
MAX_HISTORY = 10


def _system_prompt() -> str:
    if not knowledge_base.is_loaded():
        logger.info("База знаний не загружена, загружаем...")
        knowledge_base.refresh()
    ctx = knowledge_base.get_context_for_ai()
    logger.info("Длина контекста для Claude: %d символов", len(ctx))
    return SYSTEM_PROMPT_TEMPLATE.format(knowledge_context=ctx)


async def get_reply(user_id: int, user_message: str) -> tuple[str, bool]:
    history = _history.setdefault(user_id, [])
    history.append({"role": "user", "content": user_message})

    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    system = _system_prompt()

    try:
        response = await _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            system=system,
            messages=history,
        )

        reply = response.content[0].text.strip()
        history.append({"role": "assistant", "content": reply})

        no_answer_markers = [
            "нет точной информации",
            "передам ваш вопрос",
            "не могу помочь по этому вопросу",
            "уточнить у ребят",
        ]
        needs_escalation = any(m in reply.lower() for m in no_answer_markers)

        return reply, needs_escalation

    except Exception as e:
        logger.error("Claude API error for user %s: %s", user_id, e)
        return (
            "Что-то пошло не так на нашей стороне. Попробуйте чуть позже или напишите нам напрямую 🙏",
            False,
        )


def clear_history(user_id: int) -> None:
    _history.pop(user_id, None)
