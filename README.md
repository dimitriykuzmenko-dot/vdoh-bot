# Telegram-бот отеля «ВДОХ» — на Claude Sonnet

## Структура проекта

```
vdoh_bot/
├── bot.py                      # Точка входа
├── config.py                   # Настройки (читает .env)
├── requirements.txt
├── .env.example                # Шаблон переменных окружения
├── .gitignore
├── google_credentials.json     # НЕ коммитить! Ключ сервисного аккаунта Google
├── handlers/
│   ├── menu.py                 # Главное меню и статичные разделы
│   ├── booking.py              # Пошаговый сценарий бронирования
│   └── ai_chat.py              # Свободные вопросы → Claude API
└── services/
    ├── claude_service.py       # Запросы к Anthropic Claude API
    ├── sheets.py               # Чтение/запись Google Sheets
    └── knowledge_base.py       # Кэш базы знаний + контекст для промпта
```

## Быстрый старт

### 1. Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Переменные окружения

```bash
cp .env.example .env
```

Заполни `.env`:

| Переменная | Где взять |
|---|---|
| `BOT_TOKEN` | @BotFather в Telegram |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `SPREADSHEET_ID` | Из URL таблицы: `https://docs.google.com/spreadsheets/d/<ID>/edit` |
| `BOOKING_GROUP_ID` | Добавить бота в группу → `https://api.telegram.org/bot<TOKEN>/getUpdates` → найти `"chat": {"id": -100...}` |
| `ADMIN_IDS` | Твой Telegram user_id (узнать у @userinfobot) |

### 3. Google Service Account

1. console.cloud.google.com → создай проект
2. API и сервисы → Включить: **Google Sheets API** + **Google Drive API**
3. Учётные данные → Создать → Сервисный аккаунт
4. Скачай JSON-ключ → переименуй в `google_credentials.json`
5. В Google Sheets → Настройки доступа → добавить email сервисного аккаунта как **Редактор**

### 4. Google Sheets

Создай таблицу с 11 листами (имена точно как в `config.py → SHEETS`):
`hotel_info`, `rooms`, `booking_info`, `services`, `rules`, `faq`, `promos`,
`applications`, `unanswered`, `stats`, `settings`

Заполни из готовых CSV-файлов базы знаний.

### 5. Запуск

```bash
python bot.py
```

## Деплой на Railway

1. railway.app → новый проект → Deploy from GitHub
2. Variables → добавить все переменные из `.env`
3. Содержимое `google_credentials.json` добавить как переменную `GOOGLE_CREDENTIALS_JSON`
   и адаптировать `config.py` для чтения из переменной вместо файла (см. ниже)
4. Создать `Procfile`:
   ```
   worker: python bot.py
   ```

### Чтение google_credentials из переменной окружения (для Railway)

В `services/sheets.py` замени инициализацию клиента:

```python
import json, os
from google.oauth2.service_account import Credentials

def _get_spreadsheet():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
    ...
```

## Модель

По умолчанию используется `claude-sonnet-4-6`.
Изменить можно через переменную окружения `CLAUDE_MODEL`.
