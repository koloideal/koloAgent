# koloAgent

Персональный Telegram Business бот-ассистент (подключается к аккаунту через Telegram Business).

Архитектура и конвенции повторяют [Tunnex](https://github.com/koloideal/Tunnex):
слои `domain` / `application` / `infrastructure` / `presentation`, DI через dishka,
конфиг — TOML + dature, БД — PostgreSQL + SQLAlchemy + alembic, планировщик — APScheduler.

## Структура

```text
src/koloagent/
├── __main__.py                    # entrypoint: python -m koloagent
├── domain/                        # сущности, исключения (бизнес-логика)
├── application/                   # интеракторы, фасады, сервисы, DTO
├── infrastructure/
│   ├── ioc.py                     # dishka-провайдеры
│   ├── config/                    # TOML-конфиг (dature)
│   ├── database/                  # engine, модели, DAO
│   ├── devin/                     # клиент Devin API + состояние тредов
│   ├── logging/                   # JSON/текстовый логгер
│   └── scheduling/tasks.py        # фоновые задачи APScheduler
└── presentation/
    ├── business_handlers.py       # business_* апдейты (клиентские чаты)
    ├── owner_handlers.py          # прямые сообщения боту
    ├── devin_handlers.py          # /gh и форвардинг в тред Devin
    ├── formatting.py              # markdown → Telegram HTML
    ├── middlewares/only_owner.py  # доступ только владельцу
    └── error_handlers.py          # глобальная обработка ошибок
```

## Запуск

```bash
cp secret_data/config.example.toml secret_data/config.toml  # заполнить token и owner_id
just install-dev   # uv sync --all-groups
just run           # uv run python -m koloagent
just watch         # автоперезапуск при изменениях
```

Далее бот добавляется в Telegram: Настройки → Telegram Business → Чат-боты.

## Devin-панель (/gh)

Команда `/gh <запрос>` в личке с ботом (только owner_id) создаёт сессию через
Devin API v3 и возвращает ссылку. Дальше просто пишешь в чат — сообщения
форвардятся в тот же тред Devin, а его ответы прилетают обратно
(APScheduler поллит `GET .../messages` каждые `poll_interval_seconds`).

Ответ Devin стримится через `sendRichMessageDraft` (Bot API 10.x) — живое
эфемерное превью в чате, а по завершении хода (`waiting_for_user`/`finished`)
финализируется `sendRichMessage`: полноценный markdown — таблицы, заголовки,
сворачиваемые блоки, формулы. Если клиент Telegram старый и rich-сообщение не
принимается — фолбэк на обычный текст.

Тред живёт `session_ttl_minutes` от последнего сообщения — по таймауту
закрывается, нужен новый `/gh`. Настройка — секция `[devin]` в `config.toml`
(`api_key` — service user token `cog_…`, `org_id` — из Settings → Devin API).

## Миграции

```bash
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```
