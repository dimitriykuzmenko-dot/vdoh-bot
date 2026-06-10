"""
Сервис Anthropic Claude.
"""

import logging
from anthropic import AsyncAnthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from services import knowledge_base

logger = logging.getLogger(__name__)

_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT_TEMPLATE = """Ты — вежливый и внимательный помощник эко-отеля «ВДОХ» в Чемальском районе Алтая.

СТРОГИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основании базы знаний ниже.
2. Если информации в базе нет — не придумывай. Отвечай: «У меня пока нет точной информации по этому вопросу. Я передам ваш вопрос сотруднику отеля, чтобы вам ответили корректно.»
3. Не рекомендуй другие отели, не сравнивай с конкурентами.
4. Не обещай скидки, ранний заезд, поздний выезд без прямого указания в базе знаний.
5. Не давай медицинских, юридических или финансовых советов.
6. Если вопрос не связан с отелем — отвечай: «Я могу помочь только по вопросам, связанным с отелем "ВДОХ": проживание, бронирование, услуги, правила, банный комплекс и контакты.»
7. Говори простым, живым языком. Без канцелярита. Будь заботливым и спокойным.
8. Если гость хочет забронировать — предложи воспользоваться кнопкой «Забронировать номер» в главном меню или нажать /start.
9. Отвечай развёрнуто и информативно — гость должен получить полный ответ на свой вопрос.

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
        ]
        needs_escalation = any(m in reply.lower() for m in no_answer_markers)

        return reply, needs_escalation

    except Exception as e:
        logger.error("Claude API error for user %s: %s", user_id, e)
        return (
            "Произошла техническая ошибка. Пожалуйста, попробуйте позже или "
            "напишите нам напрямую — мы всегда на связи.",
            False,
        )


def clear_history(user_id: int) -> None:
    _history.pop(user_id, None)
